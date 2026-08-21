import re
from enum import Enum
from typing import Set, List, Optional, Dict, Any

class Permission(str, Enum):
    READ_ONLY = "READ_ONLY"
    WRITE_LOCAL = "WRITE_LOCAL"
    WRITE_DATABASE = "WRITE_DATABASE"
    WRITE_NOTION = "WRITE_NOTION"
    EXECUTE_TOOL = "EXECUTE_TOOL"
    ADMIN = "ADMIN"

class ActionRiskLevel(str, Enum):
    LOW = "LOW"            # Read-only lookups
    MEDIUM = "MEDIUM"      # Local temp writes, Notion inbox note
    HIGH = "HIGH"          # Database updates, device status mutations
    CRITICAL = "CRITICAL"  # Database wipe, arbitrary shell, admin escalation

class SecurityPolicyEngine:
    def __init__(self, allowed_telegram_users: Optional[List[int]] = None):
        self.allowed_users: Set[int] = set(allowed_telegram_users or [1449852069])
        self.injection_patterns = [
            re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
            re.compile(r"system\s*prompt", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
            re.compile(r"reveal\s+(your\s+)?(api_key|token|password|secret)", re.IGNORECASE),
            re.compile(r"drop\s+table", re.IGNORECASE),
            re.compile(r"delete\s+from", re.IGNORECASE)
        ]

    def is_user_authorized(self, user_id: int) -> bool:
        return user_id in self.allowed_users

    def evaluate_risk(self, action: str, params: Dict[str, Any]) -> ActionRiskLevel:
        a = action.lower()
        if any(w in a for w in ["drop", "delete", "format", "wipe", "shutdown", "kill"]):
            return ActionRiskLevel.CRITICAL
        if any(w in a for w in ["update", "mutate", "insert", "modify"]):
            return ActionRiskLevel.HIGH
        if any(w in a for w in ["write", "create_note", "export"]):
            return ActionRiskLevel.MEDIUM
        return ActionRiskLevel.LOW

    def sanitize_untrusted_content(self, text: str) -> str:
        clean = text
        for pat in self.injection_patterns:
            if pat.search(clean):
                clean = pat.sub("[FLAGGED_INJECTION_REMOVED]", clean)
        return f"<UNTRUSTED_DOCUMENT_DATA>\n{clean}\n</UNTRUSTED_DOCUMENT_DATA>"

# Backward compatibility alias
SecurityGuard = SecurityPolicyEngine
