from nanobot.services.device_service import DeviceService
from nanobot.core.trust_model import TrustLevel

def test_medical_equipment_reconciliation():
    svc = DeviceService()
    res = svc.query_equipment_reconciliation("Cân MS4980")
    assert res["trust_level"] == TrustLevel.VERIFIED_FACT
    assert len(res["data"]) > 0
    assert res["data"][0]["total_units"] == 15
