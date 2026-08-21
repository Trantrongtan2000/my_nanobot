from typing import Dict, Callable, List, Any
from .catalog import TOOL_CATALOG

class CapabilityRegistry:
    """Registry mapping tool names to callable execution targets."""
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        for fn in TOOL_CATALOG:
            self._tools[fn.__name__] = fn

    def get_tool(self, name: str) -> Callable:
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_catalog(self) -> List[Callable]:
        return list(self._tools.values())
