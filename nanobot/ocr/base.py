from typing import Protocol, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from nanobot.core.trust_model import TrustLevel, ProvenanceMetadata

class DocumentBlock(BaseModel):
    block_type: str # 'TEXT', 'TABLE', 'KEY_VALUE', 'HEADER'
    content: str
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    page_number: int = 1
    bbox: Optional[List[float]] = None

class NormalizedDocument(BaseModel):
    document_id: str
    file_name: str
    total_pages: int
    blocks: List[DocumentBlock]
    raw_markdown: str
    trust_level: TrustLevel = TrustLevel.RAW_OCR
    provenance: ProvenanceMetadata

class OCRProvider(Protocol):
    def process_document(self, file_path: str) -> NormalizedDocument:
        ...
