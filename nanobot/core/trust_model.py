from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field

class TrustLevel(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"  # Authoritative DB record / verified certificate
    RAW_OCR = "RAW_OCR"              # Direct unvalidated text from OCR scan
    INFERRED = "INFERRED"            # Inferred via LLM reasoning
    PROPOSAL = "PROPOSAL"            # Suggested AI recommendation
    UNKNOWN = "UNKNOWN"              # Missing or unverified data

class ProvenanceMetadata(BaseModel):
    source_type: str                 # 'SQLITE_DB', 'MISTRAL_OCR', 'NOTION_API', 'MANUAL_VERIFIED'
    record_id: Optional[str] = None
    file_path: Optional[str] = None
    page: Optional[int] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    verified_at: Optional[str] = None

class CalibratedField(BaseModel):
    name: str
    value: Any
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    provenance: Optional[ProvenanceMetadata] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
