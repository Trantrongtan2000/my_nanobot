from typing import Dict, Optional, List
from .catalog import ToolDefinition, TOOL_REGISTRY

class CapabilityRegistry:
    """Production Capability Registry managing typed ToolDefinitions."""
    def __init__(self):
        self._tools = TOOL_REGISTRY

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_definitions(self) -> List[ToolDefinition]:
        return list(self._tools.values())
