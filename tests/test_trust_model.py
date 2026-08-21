from nanobot.core.trust_model import TrustLevel, CalibratedField

def test_trust_levels():
    f = CalibratedField(name="serial_no", value="T24002390", trust_level=TrustLevel.VERIFIED_FACT, confidence=1.0)
    assert f.trust_level == TrustLevel.VERIFIED_FACT
    assert f.value == "T24002390"
