from typing import List, Optional, Any
from pydantic import BaseModel, Field
from nanobot.core.trust_model import TrustLevel

class Evidence(BaseModel):
    source: str
    page: int
    bbox: Optional[List[float]] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class ExtractedField(BaseModel):
    field_name: str
    value: Any
    trust_level: TrustLevel = TrustLevel.RAW_OCR
    evidence: Optional[Evidence] = None

class NormalizedDocument(BaseModel):
    document_id: str
    doc_type: str
    raw_text: str
    fields: List[ExtractedField] = []
