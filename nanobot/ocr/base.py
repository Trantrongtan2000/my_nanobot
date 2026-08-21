from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class OCRProvider(ABC):
    """Abstract base class for OCR engines."""
    @abstractmethod
    def process_document(self, file_path: str, lang: str = "vi") -> Dict[str, Any]:
        pass
