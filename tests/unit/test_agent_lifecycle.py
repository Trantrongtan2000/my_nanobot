import os
import pytest
from nanobot.agents.contract import AgentMetadata, AgentContext, AgentResult
from nanobot.agents.registry import AgentRegistry, AgentFactory, BaseNOOAAgent
from nanobot.agents.specialized_agents import MedicalEquipmentAgent
from nanobot.agents.self_improvement_agent import (
    PersistentEventStore, ImprovementEvent, ImprovementEventType,
    FeedbackCollector, DatasetExporter, EvolutionGate
)
from nanobot.core.security import Permission
from nanobot.core.trust_model import TrustLevel

def test_agent_registry_and_factory():
    agents = AgentRegistry.list_agents()
    names = [a.name for a in agents]
    assert "MedicalEquipmentAgent" in names
    assert "NotionWorkspaceAgent" in names
    assert "OCRPipelineAgent" in names
    assert "SelfImprovementAgent" in names

    # Create agent through factory
    agent = AgentFactory.create_agent("MedicalEquipmentAgent")
    assert isinstance(agent, MedicalEquipmentAgent)
    assert agent._is_initialized is True

def test_agent_execution_lifecycle():
    agent = AgentFactory.create_agent("MedicalEquipmentAgent")
    ctx = AgentContext(
        request_id="req-test-01",
        user_id=1449852069,
        input_text="Cân MS4980"
    )
    result = agent.execute(ctx)
    assert result.status == "success"
    assert result.trust_level == TrustLevel.VERIFIED_FACT
    assert len(result.output) >= 15

def test_self_improvement_event_store_and_feedback():
    store = PersistentEventStore(db_path="database/test_improvement_events.db")
    collector = FeedbackCollector(store=store)

    # 1. Test append and query events
    ev = ImprovementEvent(
        event_type=ImprovementEventType.LOW_CONFIDENCE,
        request_id="req-123",
        input_hash="hash123",
        route="LOCAL_EDGE",
        agent="MedicalEquipmentAgent",
        cactus_confidence=0.72,
        outcome="flagged",
        trust_level="UNKNOWN"
    )
    store.append_event(ev)

    events = store.query_events(limit=10)
    assert len(events) >= 1
    assert events[0]["event_type"] == "LOW_CONFIDENCE"

    # 2. Test Feedback Collector
    collector.record_user_correction(
        request_id="req-123",
        raw_input="Cân MS4980",
        original_route="CLOUD_FRONTIER",
        corrected_route="LOCAL_EDGE",
        corrected_tool="lookup_device"
    )
    corrections = store.query_events(event_type=ImprovementEventType.USER_CORRECTION)
    assert len(corrections) >= 1
    assert "Route: CLOUD_FRONTIER -> LOCAL_EDGE" in corrections[0]["correction_label"]

    # 3. Test Dataset Exporter
    exporter = DatasetExporter(store=store)
    count = exporter.export_jsonl("database/test_export.jsonl")
    assert count >= 2
    assert os.path.exists("database/test_export.jsonl")

    # 4. Test Evolution Gate
    decision_ok = EvolutionGate.evaluate_promotion(baseline_accuracy=90.0, new_accuracy=97.5, false_local_rate=0.0)
    assert decision_ok["can_promote"] is True
    assert decision_ok["decision"] == "APPROVED"

    decision_fail = EvolutionGate.evaluate_promotion(baseline_accuracy=90.0, new_accuracy=98.0, false_local_rate=12.0)
    assert decision_fail["can_promote"] is False
    assert decision_fail["decision"] == "REJECTED_SAFETY_VIOLATION"
