from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field

class ConfidenceSource(str, Enum):
    CACTUS_HYBRID = "CACTUS_HYBRID"  # Routing semantic classifier
    NEEDLE = "NEEDLE"                # On-device tool calling model
    OCR = "OCR"                      # Optical character recognition
    ROUTER = "ROUTER"                # Heuristic / fallback router
    UNKNOWN = "UNKNOWN"

class ConfidencePolicy(BaseModel):
    read_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
    write_threshold: float = Field(default=0.90, ge=0.0, le=1.0)
    mutation_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    high_impact_requires_human: bool = True

    def is_action_permitted(self, action_type: str, confidence: float) -> bool:
        if action_type == "READ":
            return confidence >= self.read_threshold
        if action_type == "WRITE":
            return confidence >= self.write_threshold
        if action_type == "MUTATE":
            return confidence >= self.mutation_threshold
        return False
