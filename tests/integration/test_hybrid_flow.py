import pytest
from nanobot.agents.coordinator import NanobotCoordinator
from nanobot.core.trust_model import TrustLevel

def test_e2e_local_equipment_flow():
    bot = NanobotCoordinator()
    res = bot.process_message("Tra cứu vị trí cân MS4980 tại khoa Da Liễu", user_id=1449852069)
    assert res["status"] == "success"
    assert res["routing"]["route"] == "LOCAL_EDGE"
    assert res["routing"]["tool"] == "lookup_device"
    assert res["telemetry"]["trust_level"] == "VERIFIED_FACT"

def test_e2e_cloud_escalation_flow():
    bot = NanobotCoordinator()
    # Complex query requiring clinical/ISO reasoning -> must escalate to cloud
    res = bot.process_message("Tại sao monitor V100 báo lỗi tuột áp lực NIBP và phân tích rủi ro theo ISO 14971?", user_id=1449852069)
    assert res["status"] == "success"
    assert res["routing"]["route"] == "CLOUD_FRONTIER"
    assert res["telemetry"]["escalated"] is True
    assert res["telemetry"]["trust_level"] == "INFERRED"
