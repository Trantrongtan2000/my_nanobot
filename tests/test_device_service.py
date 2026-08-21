from nanobot.services.device_service import DeviceService
from nanobot.core.trust_model import TrustLevel

def test_medical_equipment_reconciliation():
    svc = DeviceService()
    res = svc.query_equipment_reconciliation("Cân MS4980")
    assert res["trust_level"] == TrustLevel.VERIFIED_FACT
    assert len(res["data"]) == 15
    assert any(d["serial_no"] == "T24002396" for d in res["data"])
    assert any(d["serial_no"] == "T24002390" for d in res["data"])
