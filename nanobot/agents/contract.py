from typing import Dict, Any, Optional, List, Set
from enum import Enum
from pydantic import BaseModel, Field
from nanobot.core.security import Permission, ActionRiskLevel
from nanobot.core.trust_model import TrustLevel, ProvenanceMetadata
from nanobot.core.routing_contract import RoutingDecision

class AgentMetadata(BaseModel):
    name: str
    version: str = "2.2.0"
    description: str
    required_permissions: Set[Permission] = Field(default_factory=lambda: {Permission.READ_ONLY})
    capabilities: List[str] = Field(default_factory=list)
    supported_routes: List[str] = Field(default_factory=lambda: ["LOCAL_EDGE"])
    max_iterations: int = 8

class AgentContext(BaseModel):
    request_id: str
    user_id: int
    input_text: str
    routing_decision: Optional[RoutingDecision] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    deadline_seconds: float = 30.0

class AgentResult(BaseModel):
    status: str # 'success', 'error', 'degraded', 'unauthorized'
    output: Any
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    provenance: Optional[ProvenanceMetadata] = None
    events: List[str] = Field(default_factory=list)
    error_code: Optional[str] = None
    telemetry: Dict[str, Any] = Field(default_factory=dict)
