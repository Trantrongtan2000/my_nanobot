import re
from enum import Enum
from typing import Set, List, Optional

class Permission(str, Enum):
    READ_ONLY = "READ_ONLY"
    WRITE_LOCAL = "WRITE_LOCAL"
    WRITE_DATABASE = "WRITE_DATABASE"
    WRITE_NOTION = "WRITE_NOTION"
    EXECUTE_TOOL = "EXECUTE_TOOL"
    ADMIN = "ADMIN"

class SecurityGuard:
    def __init__(self, allowed_telegram_users: Optional[List[int]] = None):
        self.allowed_users: Set[int] = set(allowed_telegram_users or [1449852069])
        self.injection_patterns = [
            re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
            re.compile(r"system\s*prompt", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
            re.compile(r"reveal\s+(your\s+)?(api_key|token|password|secret)", re.IGNORECASE)
        ]

    def is_user_authorized(self, user_id: int) -> bool:
        return user_id in self.allowed_users

    def sanitize_untrusted_content(self, text: str) -> str:
        """
        Sanitizes text extracted from OCR or external web sources to prevent prompt injection.
        Wraps content in strict data delimiters.
        """
        for pat in self.injection_patterns:
            if pat.search(text):
                text = pat.sub("[FLAGGED_INJECTION_REMOVED]", text)
        return f"<UNTRUSTED_DOCUMENT_DATA>\n{text}\n</UNTRUSTED_DOCUMENT_DATA>"
