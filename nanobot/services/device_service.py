from typing import Dict, Any, List, Optional
from nanobot.repositories.device_repo import DeviceRepository
from nanobot.core.trust_model import TrustLevel, ProvenanceMetadata

class DeviceService:
    """
    Business Logic Service for Medical Device Reconciliation, Inspection & Maintenance.
    Strictly attaches TrustLevel and ProvenanceMetadata to every result.
    """
    def __init__(self, repo: Optional[DeviceRepository] = None):
        self.repo = repo or DeviceRepository()

    def reconcile_device(self, query: str, department: Optional[str] = None) -> Dict[str, Any]:
        results = self.repo.search_devices(query, department=department)
        if results:
            return {
                "status": "success",
                "count": len(results),
                "trust_level": TrustLevel.VERIFIED_FACT,
                "data": results,
                "provenance": ProvenanceMetadata(
                    source_type="SQLITE_DB",
                    record_id=str(results[0].get("id")),
                    file_path=self.repo.db_path,
                    confidence=1.0
                ).model_dump()
            }
        return {
            "status": "not_found",
            "count": 0,
            "trust_level": TrustLevel.UNKNOWN,
            "data": [],
            "message": f"Không tìm thấy thiết bị y tế khớp với '{query}' trong cơ sở dữ liệu."
        }

    # Backward compatibility alias
    query_equipment_reconciliation = reconcile_device

    def get_due_calibrations(self) -> Dict[str, Any]:
        due_list = self.repo.get_calibration_due_list()
        return {
            "status": "success",
            "count": len(due_list),
            "trust_level": TrustLevel.VERIFIED_FACT,
            "data": due_list,
            "provenance": ProvenanceMetadata(
                source_type="SQLITE_DB",
                file_path=self.repo.db_path,
                confidence=1.0
            ).model_dump()
        }
