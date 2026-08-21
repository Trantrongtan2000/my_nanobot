import pytest
import os
from nanobot.repositories.device_repo import DeviceRepository
from nanobot.services.device_service import DeviceService
from nanobot.core.trust_model import TrustLevel

def test_real_sqlite_device_repository():
    repo = DeviceRepository()
    # Test real query for Charder MS4980
    res = repo.search_devices("MS4980")
    assert len(res) >= 15
    assert any(d["serial_no"] == "T24002396" for d in res)
    assert any(d["serial_no"] == "T24002390" for d in res)

def test_find_by_serial_exact():
    repo = DeviceRepository()
    dev = repo.find_by_serial("T24002392")
    assert dev is not None
    assert "Da Liễu" in dev["facility_name"]
    assert dev["model"] == "MS4980"

def test_device_service_trust_attachment():
    svc = DeviceService()
    res = svc.reconcile_device("Rad-5v")
    assert res["status"] == "success"
    assert res["trust_level"] == TrustLevel.VERIFIED_FACT
    assert len(res["data"]) >= 10
