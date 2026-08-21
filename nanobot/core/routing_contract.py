from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from .confidence_policy import ConfidenceSource

class RoutingDecision(BaseModel):
    route: Literal["LOCAL_EDGE", "CLOUD_FRONTIER"]
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_source: ConfidenceSource
    agent: Optional[str] = None
    tool: Optional[str] = None
    reason: str
    escalation_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
