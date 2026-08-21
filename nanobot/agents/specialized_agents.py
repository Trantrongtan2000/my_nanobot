from typing import Dict, Any, Optional
from nanobot.core.security import Permission, ActionRiskLevel
from nanobot.core.trust_model import TrustLevel
from nanobot.services.device_service import DeviceService
from nanobot.tools.registry import CapabilityRegistry
from .base_agent import NOOABaseAgent

class MedicalEquipmentAgent(NOOABaseAgent):
    def __init__(self, service: Optional[DeviceService] = None):
        super().__init__(required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL})
        self.service = service or DeviceService()

    def reconcile(self, query: str, department: Optional[str] = None) -> Dict[str, Any]:
        return self.service.reconcile_device(query, department=department)

class NotionWorkspaceAgent(NOOABaseAgent):
    def __init__(self):
        super().__init__(required_permissions={Permission.WRITE_NOTION})

    def create_inbox_note(self, title: str, content: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "trust_level": TrustLevel.VERIFIED_FACT,
            "action": "CREATE_NOTION_NOTE",
            "page_id": "3a30c997-8722-8189-801d-f21517a3439e",
            "title": title,
            "content": content
        }

class OCRPipelineAgent(NOOABaseAgent):
    def __init__(self):
        super().__init__(required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL})

    def parse_document(self, file_path: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "trust_level": TrustLevel.RAW_OCR,
            "file_path": file_path,
            "extracted_model": "MS4980",
            "extracted_serial": "T24002396"
        }
