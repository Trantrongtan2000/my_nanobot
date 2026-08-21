from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

class TrustLevel(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"  # Confirmed by authoritative DB/certificate records
    RAW_OCR = "RAW_OCR"              # Direct OCR text without semantic validation
    INFERRED = "INFERRED"            # Inferred by LLM reasoning
    PROPOSAL = "PROPOSAL"            # Suggested recommendation
    UNKNOWN = "UNKNOWN"              # Missing or ambiguous data

class CalibratedField(BaseModel):
    name: str
    value: Any
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    evidence: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
