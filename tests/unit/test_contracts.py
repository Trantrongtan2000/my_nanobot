import pytest
from nanobot.core.trust_model import TrustLevel, CalibratedField, ProvenanceMetadata
from nanobot.core.confidence_policy import ConfidencePolicy, ConfidenceSource
from nanobot.core.routing_contract import RoutingDecision
from nanobot.core.security import SecurityPolicyEngine, ActionRiskLevel

def test_trust_levels_and_provenance():
    prov = ProvenanceMetadata(source_type="SQLITE_DB", record_id="101", confidence=1.0)
    field = CalibratedField(name="serial_no", value="T24002390", trust_level=TrustLevel.VERIFIED_FACT, provenance=prov)
    assert field.trust_level == TrustLevel.VERIFIED_FACT
    assert field.provenance.source_type == "SQLITE_DB"

def test_confidence_policy_thresholds():
    policy = ConfidencePolicy(read_threshold=0.80, write_threshold=0.90, mutation_threshold=0.95)
    assert policy.is_action_permitted("READ", 0.85) is True
    assert policy.is_action_permitted("READ", 0.75) is False
    assert policy.is_action_permitted("WRITE", 0.92) is True
    assert policy.is_action_permitted("MUTATE", 0.91) is False

def test_typed_routing_decision():
    dec = RoutingDecision(
        route="LOCAL_EDGE",
        intent="LOCAL_EQUIPMENT_LOOKUP",
        confidence=0.96,
        confidence_source=ConfidenceSource.CACTUS_HYBRID,
        agent="MedicalEquipmentAgent",
        tool="lookup_device",
        reason="Matched deterministic equipment query."
    )
    assert dec.route == "LOCAL_EDGE"
    assert dec.confidence_source == ConfidenceSource.CACTUS_HYBRID
