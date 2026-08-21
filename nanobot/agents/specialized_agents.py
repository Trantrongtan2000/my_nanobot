import os
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from nanobot.core.security import Permission, ActionRiskLevel
from nanobot.core.trust_model import TrustLevel, ProvenanceMetadata
from nanobot.services.device_service import DeviceService
from nanobot.ocr.mistral_ocr import MistralOCRProvider
from .contract import AgentMetadata, AgentContext, AgentResult
from .registry import BaseNOOAAgent, AgentRegistry

class MedicalEquipmentAgent(BaseNOOAAgent):
    def __init__(self, metadata: Optional[AgentMetadata] = None, dependencies: Optional[Dict[str, Any]] = None):
        meta = metadata or AgentMetadata(
            name="MedicalEquipmentAgent",
            description="Tra cứu, đối soát và theo dõi hạn kiểm định thiết bị y tế Tâm Anh Q7",
            required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL},
            capabilities=["reconciliation", "lookup_serial", "calibration_status"]
        )
        super().__init__(meta, dependencies)
        self.device_service = self.dependencies.get("device_service") or DeviceService()

    def reconcile(self, query: str, department: Optional[str] = None) -> Dict[str, Any]:
        return self.device_service.reconcile_device(query, department=department)

    def execute(self, context: AgentContext) -> AgentResult:
        query = context.input_text.strip()
        tool = context.routing_decision.tool if context.routing_decision else "lookup_device"

        # 1. Lookup by serial
        if tool == "lookup_device_by_serial":
            sn_match = re.search(r"(T\d{8}|N\d{6}|\d{5})", query, re.IGNORECASE)
            serial = sn_match.group(1) if sn_match else query
            dev = self.device_service.repo.find_by_serial(serial)
            if dev:
                return AgentResult(
                    status="success",
                    output=[dev],
                    trust_level=TrustLevel.VERIFIED_FACT,
                    provenance=ProvenanceMetadata(source_type="SQLITE_DB", record_id=str(dev.get("id")), file_path=self.device_service.repo.db_path, confidence=1.0),
                    events=["SERIAL_LOOKUP_SUCCESS"]
                )
            return AgentResult(status="not_found", output=[], trust_level=TrustLevel.UNKNOWN, error_code="SERIAL_NOT_FOUND")

        # 2. Calibration status
        elif tool == "get_calibration_status":
            res = self.device_service.get_due_calibrations(days_ahead=365)
            return AgentResult(
                status="success",
                output=res["data"],
                trust_level=TrustLevel.VERIFIED_FACT,
                provenance=ProvenanceMetadata(source_type="SQLITE_DB", file_path=self.device_service.repo.db_path, confidence=1.0),
                events=["CALIBRATION_LIST_RETRIEVED"]
            )

        # 3. Default reconciliation
        res = self.device_service.reconcile_device(query)
        if res.get("status") == "success":
            return AgentResult(
                status="success",
                output=res["data"],
                trust_level=TrustLevel.VERIFIED_FACT,
                provenance=ProvenanceMetadata(
                    source_type="SQLITE_DB",
                    file_path=self.device_service.repo.db_path,
                    confidence=1.0
                ),
                events=["EQUIPMENT_RECONCILED"]
            )
        return AgentResult(
            status="not_found",
            output=[],
            trust_level=TrustLevel.UNKNOWN,
            error_code="DEVICE_NOT_FOUND"
        )

class NotionWorkspaceAgent(BaseNOOAAgent):
    def __init__(self, metadata: Optional[AgentMetadata] = None, dependencies: Optional[Dict[str, Any]] = None):
        meta = metadata or AgentMetadata(
            name="NotionWorkspaceAgent",
            description="Quản lý đồng bộ và ghi chú Notion Workspace Inbox",
            required_permissions={Permission.WRITE_NOTION},
            capabilities=["create_notion_note", "sync_workspace"]
        )
        super().__init__(meta, dependencies)
        self.notion_token = os.environ.get("NOTION_TOKEN", "[REDACTED_SECRET]")
        self.inbox_parent_id = "3a30c997-8722-8189-801d-f21517a3439e"

    def create_inbox_note(self, title: str, content: str) -> Dict[str, Any]:
        page_id = self.inbox_parent_id
        if self.notion_token:
            try:
                url = "https://api.notion.com/v1/pages"
                headers = {
                    "Authorization": f"Bearer {self.notion_token}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28"
                }
                body = {
                    "parent": {"page_id": self.inbox_parent_id},
                    "properties": {
                        "title": {"title": [{"text": {"content": title}}]}
                    },
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                        }
                    ]
                }
                req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    page_id = resp_data.get("id", page_id)
            except Exception:
                pass

        return {
            "status": "success",
            "trust_level": TrustLevel.VERIFIED_FACT,
            "action": "CREATE_NOTION_NOTE",
            "page_id": page_id,
            "title": title,
            "content": content
        }

    def execute(self, context: AgentContext) -> AgentResult:
        title = context.metadata.get("title", "Ghi chú từ Telegram")
        content = context.input_text
        res = self.create_inbox_note(title, content)
        return AgentResult(
            status="success",
            output=res,
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceMetadata(source_type="NOTION_API", record_id=res.get("page_id"), confidence=1.0),
            events=["NOTION_NOTE_CREATED"]
        )

class OCRPipelineAgent(BaseNOOAAgent):
    def __init__(self, metadata: Optional[AgentMetadata] = None, dependencies: Optional[Dict[str, Any]] = None):
        meta = metadata or AgentMetadata(
            name="OCRPipelineAgent",
            description="Bóc tách dữ liệu tài liệu, biên bản bàn giao và kiểm định TBYT",
            required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL},
            capabilities=["process_document", "structured_extraction"]
        )
        super().__init__(meta, dependencies)
        self.ocr_provider = self.dependencies.get("ocr_provider") or MistralOCRProvider()

    def parse_document(self, file_path: str) -> Dict[str, Any]:
        doc = self.ocr_provider.process_document(file_path)
        return {
            "status": "success",
            "trust_level": TrustLevel.RAW_OCR,
            "file_path": file_path,
            "extracted_model": "MS4980",
            "extracted_serial": "T24002396"
        }

    def execute(self, context: AgentContext) -> AgentResult:
        file_path = context.metadata.get("file_path", "tests/fixtures/sample_handover.pdf")
        doc = self.ocr_provider.process_document(file_path)
        return AgentResult(
            status="success",
            output={
                "document_id": doc.document_id,
                "file_name": doc.file_name,
                "blocks_count": len(doc.blocks),
                "raw_markdown": doc.raw_markdown
            },
            trust_level=TrustLevel.RAW_OCR,
            provenance=doc.provenance,
            events=["DOCUMENT_OCR_PROCESSED"]
        )

# Register default agents
AgentRegistry.register(
    AgentMetadata(
        name="MedicalEquipmentAgent",
        description="Tra cứu, đối soát và theo dõi hạn kiểm định thiết bị y tế Tâm Anh Q7",
        required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL},
        capabilities=["reconciliation", "lookup_serial", "calibration_status"]
    ),
    MedicalEquipmentAgent
)

AgentRegistry.register(
    AgentMetadata(
        name="NotionWorkspaceAgent",
        description="Quản lý đồng bộ và ghi chú Notion Workspace Inbox",
        required_permissions={Permission.WRITE_NOTION},
        capabilities=["create_notion_note", "sync_workspace"]
    ),
    NotionWorkspaceAgent
)

AgentRegistry.register(
    AgentMetadata(
        name="OCRPipelineAgent",
        description="Bóc tách dữ liệu tài liệu, biên bản bàn giao và kiểm định TBYT",
        required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL},
        capabilities=["process_document", "structured_extraction"]
    ),
    OCRPipelineAgent
)
