import pytest
from nanobot.ocr.mistral_ocr import MistralOCRProvider
from nanobot.ocr.base import NormalizedDocument
from nanobot.core.trust_model import TrustLevel
from nanobot.providers.nine_router import NineRouterClient, CircuitState
from nanobot.agents.specialized_agents import MedicalEquipmentAgent, NotionWorkspaceAgent, OCRPipelineAgent

def test_ocr_provider_evidence_and_trust():
    provider = MistralOCRProvider()
    doc = provider.process_document("tests/fixtures/sample_handover.pdf")
    assert isinstance(doc, NormalizedDocument)
    assert doc.trust_level == TrustLevel.RAW_OCR
    assert doc.provenance.source_type == "MISTRAL_OCR"
    assert len(doc.blocks) >= 2

def test_nine_router_circuit_breaker():
    client = NineRouterClient(api_base="http://127.0.0.1:99999/v1") # non-existent port to test breaker
    res = client.generate_chat_completion("test prompt")
    assert res["status"] == "degraded"
    assert res["provider"] == "LocalFallbackEngine"

def test_specialized_agents_execution():
    med_agent = MedicalEquipmentAgent()
    res = med_agent.reconcile("Rad-5v")
    assert res["status"] == "success"
    assert res["trust_level"] == TrustLevel.VERIFIED_FACT

    notion_agent = NotionWorkspaceAgent()
    n_res = notion_agent.create_inbox_note("Tiêu đề", "Nội dung")
    assert n_res["status"] == "success"
    assert n_res["action"] == "CREATE_NOTION_NOTE"
