import uuid
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RequestTelemetry(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    intent: str
    route: str
    confidence: float
    confidence_source: str
    agent: Optional[str] = None
    tool: Optional[str] = None
    tool_success: bool = True
    latency_ms: float = 0.0
    escalated: bool = False
    cloud_provider: Optional[str] = None
    trust_level: str = "UNKNOWN"
    provenance: Optional[str] = None
    error_code: Optional[str] = None

class ObservabilityTracer:
    def __init__(self):
        self.logs: list[RequestTelemetry] = []

    def log_event(self, telemetry: RequestTelemetry):
        self.logs.append(telemetry)
