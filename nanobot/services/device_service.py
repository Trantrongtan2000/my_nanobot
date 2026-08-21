from typing import Dict, Any, Optional
from nanobot.repositories.device_repo import DeviceRepository
from nanobot.core.trust_model import TrustLevel

class DeviceService:
    """Business logic layer for medical equipment calibration & reconciliation."""
    def __init__(self, repo: Optional[DeviceRepository] = None):
        self.repo = repo or DeviceRepository()

    def query_equipment_reconciliation(self, query: str) -> Dict[str, Any]:
        results = self.repo.find_devices_by_query(query)
        if results:
            return {
                "trust_level": TrustLevel.VERIFIED_FACT,
                "data": results,
                "evidence": "Authoritative Master Database & Physical Inspection Records"
            }
        return {
            "trust_level": TrustLevel.UNKNOWN,
            "data": [],
            "message": "Không tìm thấy dữ liệu đối soát phù hợp."
        }
