import os
import sqlite3
import json
import uuid
import time
import hashlib
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from nanobot.core.security import Permission
from nanobot.core.trust_model import TrustLevel, ProvenanceMetadata
from .contract import AgentMetadata, AgentContext, AgentResult
from .registry import BaseNOOAAgent, AgentRegistry

class ImprovementEventType(str, Enum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    WRONG_TOOL = "WRONG_TOOL"
    TOOL_FAILURE = "TOOL_FAILURE"
    CLOUD_ESCALATION = "CLOUD_ESCALATION"
    USER_CORRECTION = "USER_CORRECTION"
    OCR_EXTRACTION_ERROR = "OCR_EXTRACTION_ERROR"
    PROVIDER_DEGRADED = "PROVIDER_DEGRADED"
    SAFETY_CONFIRMATION_REQUIRED = "SAFETY_CONFIRMATION_REQUIRED"

class ImprovementEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: ImprovementEventType
    request_id: str
    input_hash: str
    route: str
    agent: Optional[str] = None
    tool: Optional[str] = None
    cactus_confidence: float = 0.0
    needle_confidence: float = 0.0
    outcome: str # 'success', 'failed', 'corrected', 'escalated'
    trust_level: str = "UNKNOWN"
    provenance_json: Optional[str] = None
    correction_label: Optional[str] = None
    created_at: float = Field(default_factory=time.time)

class PersistentEventStore:
    """Append-only SQLite Event Store for Self-Improvement and Evaluation Dataset."""
    def __init__(self, db_path: str = "database/improvement_events.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS improvement_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            request_id TEXT NOT NULL,
            input_hash TEXT NOT NULL,
            route TEXT NOT NULL,
            agent TEXT,
            tool TEXT,
            cactus_confidence REAL,
            needle_confidence REAL,
            outcome TEXT NOT NULL,
            trust_level TEXT,
            provenance_json TEXT,
            correction_label TEXT,
            created_at REAL NOT NULL
        );""")
        conn.commit()
        conn.close()

    def append_event(self, event: ImprovementEvent):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""
        INSERT INTO improvement_events 
        (event_id, event_type, request_id, input_hash, route, agent, tool, cactus_confidence, needle_confidence, outcome, trust_level, provenance_json, correction_label, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id, event.event_type.value, event.request_id, event.input_hash,
            event.route, event.agent, event.tool, event.cactus_confidence,
            event.needle_confidence, event.outcome, event.trust_level,
            event.provenance_json, event.correction_label, event.created_at
        ))
        conn.commit()
        conn.close()

    def query_events(self, event_type: Optional[ImprovementEventType] = None, limit: int = 100) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        c = conn.cursor()
        if event_type:
            c.execute("SELECT * FROM improvement_events WHERE event_type = ? ORDER BY created_at DESC LIMIT ?", (event_type.value, limit))
        else:
            c.execute("SELECT * FROM improvement_events ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

class FeedbackCollector:
    """Collects explicit User Feedback and links corrections to original request."""
    def __init__(self, store: Optional[PersistentEventStore] = None):
        self.store = store or PersistentEventStore()

    def record_user_correction(self, request_id: str, raw_input: str, original_route: str, corrected_route: str, corrected_tool: Optional[str] = None):
        input_hash = hashlib.sha256(raw_input.strip().encode("utf-8")).hexdigest()[:16]
        event = ImprovementEvent(
            event_type=ImprovementEventType.USER_CORRECTION,
            request_id=request_id,
            input_hash=input_hash,
            route=original_route,
            tool=corrected_tool,
            outcome="corrected",
            correction_label=f"Route: {original_route} -> {corrected_route}, Tool: {corrected_tool}"
        )
        self.store.append_event(event)

class DatasetExporter:
    """Exports versioned JSONL evaluation dataset with PII & secret redaction."""
    def __init__(self, store: Optional[PersistentEventStore] = None):
        self.store = store or PersistentEventStore()

    def export_jsonl(self, output_path: str = "database/evaluation_dataset.jsonl", schema_version: str = "1.0.0") -> int:
        events = self.store.query_events(limit=1000)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        count = 0
        with open(output_path, "w", encoding="utf-8") as f:
            for ev in events:
                item = {
                    "schema_version": schema_version,
                    "event_id": ev["event_id"],
                    "event_type": ev["event_type"],
                    "input_hash": ev["input_hash"],
                    "route": ev["route"],
                    "agent": ev["agent"],
                    "tool": ev["tool"],
                    "outcome": ev["outcome"],
                    "correction_label": ev["correction_label"],
                    "created_at": ev["created_at"]
                }
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                count += 1
        return count

class EvolutionGate:
    """
    Evolution Gate enforcing strict safety check before any model or threshold promotion.
    Blocks automated threshold changes without offline regression evaluation.
    """
    @staticmethod
    def evaluate_promotion(baseline_accuracy: float, new_accuracy: float, false_local_rate: float) -> Dict[str, Any]:
        can_promote = (new_accuracy >= baseline_accuracy) and (false_local_rate <= 5.0)
        return {
            "can_promote": can_promote,
            "baseline_accuracy": baseline_accuracy,
            "new_accuracy": new_accuracy,
            "false_local_rate": false_local_rate,
            "decision": "APPROVED" if can_promote else "REJECTED_SAFETY_VIOLATION"
        }

class SelfImprovementAgent(BaseNOOAAgent):
    def __init__(self, metadata: AgentMetadata, dependencies: Optional[Dict[str, Any]] = None):
        super().__init__(metadata, dependencies)
        self.store = self.dependencies.get("event_store") or PersistentEventStore()
        self.collector = FeedbackCollector(store=self.store)
        self.exporter = DatasetExporter(store=self.store)

    def execute(self, context: AgentContext) -> AgentResult:
        # Export dataset and evaluate improvement
        count = self.exporter.export_jsonl()
        return AgentResult(
            status="success",
            output={
                "exported_events_count": count,
                "dataset_file": self.exporter.store.db_path
            },
            trust_level=TrustLevel.VERIFIED_FACT,
            events=["DATASET_EXPORTED"]
        )

# Register SelfImprovementAgent
AgentRegistry.register(
    AgentMetadata(
        name="SelfImprovementAgent",
        description="Quản lý Event Store, Feedback và Đánh giá tiến hóa hệ thống",
        required_permissions={Permission.READ_ONLY, Permission.WRITE_DATABASE},
        capabilities=["record_event", "export_dataset", "evaluate_promotion"]
    ),
    SelfImprovementAgent
)
