from typing import Set, Any
from nanobot.core.security import Permission

class NOOABaseAgent:
    """Base class for all Object-Oriented Agents with permission control."""
    def __init__(self, required_permissions: Set[Permission]):
        self.permissions = required_permissions

    def has_permission(self, perm: Permission) -> bool:
        return perm in self.permissions or Permission.ADMIN in self.permissions
