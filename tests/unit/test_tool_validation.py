import pytest
from nanobot.tools.registry import CapabilityRegistry
from nanobot.tools.catalog import ToolDefinition
from nanobot.core.trust_model import TrustLevel

def test_tool_definition_schema_validation():
    reg = CapabilityRegistry()
    tool = reg.get_tool("lookup_device_by_serial")
    assert tool is not None
    
    # Valid call
    valid_res = tool.validate_and_execute({"serial_no": "T24002396"})
    assert valid_res["status"] == "success"
    assert valid_res["trust_level"] == TrustLevel.VERIFIED_FACT

    # Invalid call (missing required serial_no)
    invalid_res = tool.validate_and_execute({})
    assert invalid_res["status"] == "validation_error"
    assert "serial_no" in invalid_res["error"]
