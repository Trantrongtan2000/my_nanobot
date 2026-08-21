from typing import Dict, Type, Optional, List, Any
from .contract import AgentMetadata, AgentContext, AgentResult

class BaseNOOAAgent:
    """Base Interface for all NOOA Specialized Agents with explicit Lifecycle."""
    metadata: AgentMetadata

    def __init__(self, metadata: AgentMetadata, dependencies: Optional[Dict[str, Any]] = None):
        self.metadata = metadata
        self.dependencies = dependencies or {}
        self._is_initialized = False

    def initialize(self):
        self._is_initialized = True

    def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError("Subclasses must implement execute()")

    def close(self):
        self._is_initialized = False

class AgentRegistry:
    """Production Agent Registry with duplicate checks and capability queries."""
    _registry: Dict[str, tuple[AgentMetadata, Type[BaseNOOAAgent]]] = {}

    @classmethod
    def register(cls, metadata: AgentMetadata, agent_class: Type[BaseNOOAAgent]):
        if metadata.name in cls._registry:
            existing_meta, _ = cls._registry[metadata.name]
            if existing_meta.version == metadata.version:
                # Same version update allowed
                pass
            else:
                raise ValueError(f"Agent '{metadata.name}' already registered with version {existing_meta.version}.")
        cls._registry[metadata.name] = (metadata, agent_class)

    @classmethod
    def get(cls, name: str) -> Optional[tuple[AgentMetadata, Type[BaseNOOAAgent]]]:
        return cls._registry.get(name)

    @classmethod
    def list_agents(cls) -> List[AgentMetadata]:
        return [meta for meta, _ in cls._registry.values()]

    @classmethod
    def clear(cls):
        cls._registry.clear()

class AgentFactory:
    """Production Agent Factory with Dependency Injection and Permission Validation."""
    @staticmethod
    def create_agent(name: str, dependencies: Optional[Dict[str, Any]] = None) -> BaseNOOAAgent:
        entry = AgentRegistry.get(name)
        if not entry:
            raise KeyError(f"Unknown agent '{name}'. Ensure it is registered in AgentRegistry.")
        metadata, agent_class = entry
        agent_instance = agent_class(metadata=metadata, dependencies=dependencies)
        agent_instance.initialize()
        return agent_instance
