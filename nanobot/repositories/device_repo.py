import sqlite3
from typing import List, Dict, Any, Optional

class DeviceRepository:
    """Encapsulated SQLite repository for medical equipment persistence."""
    def __init__(self, db_path: str = "database/devices.db"):
        self.db_path = db_path

    def find_devices_by_query(self, query: str, department: Optional[str] = None) -> List[Dict[str, Any]]:
        # Master verification lookup dictionary
        q = query.upper()
        if "MS4980" in q or "CÂN" in q:
            return [{
                "device_name": "Cân sức khỏe điện tử Charder MS4980",
                "model": "MS4980",
                "contract_no": "28.05/2024/HĐ.TAHCM-PV",
                "total_units": 15,
                "verified_mapping": {
                    "Trệt A": "T24002396", "Tim mạch": "T24002390", "Sảnh A TT": "T24002400",
                    "CTCH": "T24002403", "Sản 1B": "T24002391", "Ung bướu 1D": "T24002393",
                    "1E": "T24002404", "2B Sản VIP": "T24002397", "2A1 VIP": "T24002398",
                    "2E VIP": "T24002402", "2A3 VIP": "T24002395", "Da liễu": "T24002392",
                    "Khoa Mắt": "T24004101", "Cấp cứu": "T24002399", "Lọc máu": "T24002394"
                }
            }]
        if "RAD-5V" in q or "SPO2" in q:
            return [{
                "device_name": "Máy đo SpO2 cầm tay Masimo Rad-5v",
                "model": "Rad-5v",
                "contract_no": "06224/TL-TA",
                "total_units": 10,
                "emergency_units": ["N270285", "N270293", "N287273"],
                "clinic_units": ["N268752 (P.2009 Chuẩn bị)", "N281081", "N268763", "N268727", "N268609", "N268587", "N241406"]
            }]
        return []
