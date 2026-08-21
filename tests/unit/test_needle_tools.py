import pytest
from nanobot.tools.catalog import lookup_device, lookup_device_by_serial, get_calibration_status, TOOL_CATALOG
from nanobot.tools.registry import CapabilityRegistry
from nanobot.core.needle_adapter import NeedleToolAdapter
from nanobot.core.trust_model import TrustLevel

def test_tool_catalog_execution():
    registry = CapabilityRegistry()
    assert "lookup_device" in registry.list_tools()
    assert "lookup_device_by_serial" in registry.list_tools()
    
    adapter = NeedleToolAdapter(registry=registry)
    res = adapter.execute_tool_call("lookup_device_by_serial", {"serial_no": "T24002390"})
    assert res["status"] == "success"
    assert res["trust_level"] == TrustLevel.VERIFIED_FACT
    assert res["data"]["serial_no"] == "T24002390"
