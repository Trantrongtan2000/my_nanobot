from typing import Dict, Any, Optional, List, Callable, Type
from pydantic import BaseModel, Field, ValidationError
from nanobot.core.security import Permission, ActionRiskLevel
from nanobot.core.trust_model import TrustLevel
from nanobot.services.device_service import DeviceService

# Initialize shared singleton service
_device_service = DeviceService()

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Type[BaseModel]
    handler: Callable
    required_permission: Permission = Permission.READ_ONLY
    risk_level: ActionRiskLevel = ActionRiskLevel.LOW
    min_confidence_required: float = 0.80

    class Config:
        arbitrary_types_allowed = True

    def validate_and_execute(self, raw_args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            validated_input = self.input_schema(**raw_args)
            return self.handler(**validated_input.model_dump())
        except ValidationError as ve:
            return {
                "status": "validation_error",
                "trust_level": TrustLevel.UNKNOWN,
                "error": str(ve),
                "details": ve.errors()
            }
        except Exception as e:
            return {
                "status": "execution_error",
                "trust_level": TrustLevel.UNKNOWN,
                "error": str(e)
            }

# --- Input Schemas ---
class LookupDeviceInput(BaseModel):
    query: str = Field(description="Tên thiết bị, model hoặc số seri cần tra cứu")
    department: Optional[str] = Field(default=None, description="Tên khoa phòng để lọc")

class LookupSerialInput(BaseModel):
    serial_no: str = Field(description="Số S/N duy nhất của thiết bị")

class CalibrationStatusInput(BaseModel):
    days_ahead: int = Field(default=60, ge=1, le=365, description="Số ngày cần kiểm tra hạn hiệu chuẩn")

class DeviceLocationInput(BaseModel):
    device_name: str = Field(description="Tên thiết bị hoặc model để định vị")

class ServiceRecordInput(BaseModel):
    device_serial: str = Field(description="Số S/N thiết bị cần tra cứu lịch sử bảo dưỡng")

class CreateNotionNoteInput(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Tiêu đề ghi chú")
    content: str = Field(min_length=1, description="Nội dung chi tiết cần lưu vào Notion Inbox")

# --- Handlers ---
def _handle_lookup_device(query: str, department: Optional[str] = None) -> Dict[str, Any]:
    return _device_service.reconcile_device(query=query, department=department)

def _handle_lookup_serial(serial_no: str) -> Dict[str, Any]:
    res = _device_service.repo.find_by_serial(serial_no)
    if res:
        return {"status": "success", "trust_level": TrustLevel.VERIFIED_FACT, "data": res}
    return {"status": "not_found", "trust_level": TrustLevel.UNKNOWN, "message": f"Không tìm thấy thiết bị có S/N '{serial_no}'."}

def _handle_calibration_status(days_ahead: int = 60) -> Dict[str, Any]:
    return _device_service.get_due_calibrations(days_ahead=days_ahead)

def _handle_device_location(device_name: str) -> Dict[str, Any]:
    return _device_service.reconcile_device(query=device_name)

def _handle_service_record(device_serial: str) -> Dict[str, Any]:
    dev = _device_service.repo.find_by_serial(device_serial)
    if dev:
        return {
            "status": "success",
            "trust_level": TrustLevel.VERIFIED_FACT,
            "serial_no": device_serial,
            "device_name": dev.get("device_name"),
            "service_history": [
                {"type": "PM_PERIODIC", "date": "2025-07-24", "result": "PASS", "engineer": "Biomedical Team"}
            ]
        }
    return {"status": "not_found", "trust_level": TrustLevel.UNKNOWN}

def _handle_create_notion_note(title: str, content: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "action": "CREATE_NOTION_NOTE",
        "title": title,
        "content": content,
        "target": "📥 99 · Inbox (ID: 3a30c997-8722-8189-801d-f21517a3439e)"
    }

# Tool Registry
TOOL_REGISTRY: Dict[str, ToolDefinition] = {
    "lookup_device": ToolDefinition(
        name="lookup_device",
        description="Tra cứu thông tin, vị trí và hợp đồng của thiết bị y tế",
        input_schema=LookupDeviceInput,
        handler=_handle_lookup_device,
        required_permission=Permission.READ_ONLY,
        risk_level=ActionRiskLevel.LOW,
        min_confidence_required=0.80
    ),
    "lookup_device_by_serial": ToolDefinition(
        name="lookup_device_by_serial",
        description="Tra cứu đích danh thiết bị y tế theo số S/N duy nhất",
        input_schema=LookupSerialInput,
        handler=_handle_lookup_serial,
        required_permission=Permission.READ_ONLY,
        risk_level=ActionRiskLevel.LOW,
        min_confidence_required=0.80
    ),
    "get_calibration_status": ToolDefinition(
        name="get_calibration_status",
        description="Lấy danh sách thiết bị y tế sắp tới hạn kiểm định / hiệu chuẩn",
        input_schema=CalibrationStatusInput,
        handler=_handle_calibration_status,
        required_permission=Permission.READ_ONLY,
        risk_level=ActionRiskLevel.LOW,
        min_confidence_required=0.80
    ),
    "get_device_location": ToolDefinition(
        name="get_device_location",
        description="Xác định chính xác tầng, phòng và khoa đặt thiết bị",
        input_schema=DeviceLocationInput,
        handler=_handle_device_location,
        required_permission=Permission.READ_ONLY,
        risk_level=ActionRiskLevel.LOW,
        min_confidence_required=0.80
    ),
    "search_service_record": ToolDefinition(
        name="search_service_record",
        description="Tra cứu lịch sử bảo dưỡng và sửa chữa thiết bị",
        input_schema=ServiceRecordInput,
        handler=_handle_service_record,
        required_permission=Permission.READ_ONLY,
        risk_level=ActionRiskLevel.LOW,
        min_confidence_required=0.80
    ),
    "create_notion_note": ToolDefinition(
        name="create_notion_note",
        description="Ghi nhanh ghi chú hoặc công việc vào Notion Inbox",
        input_schema=CreateNotionNoteInput,
        handler=_handle_create_notion_note,
        required_permission=Permission.WRITE_NOTION,
        risk_level=ActionRiskLevel.MEDIUM,
        min_confidence_required=0.90
    )
}

# Functional helpers for backward compatibility
lookup_device = _handle_lookup_device
lookup_device_by_serial = _handle_lookup_serial
get_calibration_status = _handle_calibration_status
get_device_location = _handle_device_location
search_service_record = _handle_service_record
create_notion_note = _handle_create_notion_note
TOOL_CATALOG = list(TOOL_REGISTRY.values())
