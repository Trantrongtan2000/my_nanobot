from typing import Dict, Any
from nanobot.core.security import Permission, SecurityGuard
from nanobot.core.router import IntentRouter
from nanobot.services.device_service import DeviceService
from .base_agent import NOOABaseAgent

class NanobotCoordinator(NOOABaseAgent):
    """Main coordinator agent implementing NOOA and 2026 execution rules."""
    def __init__(self):
        super().__init__(required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL})
        self.security = SecurityGuard()
        self.router = IntentRouter()
        self.device_service = DeviceService()

    def process_message(self, text: str, user_id: int = 1449852069) -> Dict[str, Any]:
        if not self.security.is_user_authorized(user_id):
            return {"status": "error", "message": "Unauthorized user."}
            
        routing = self.router.route_intent(text)
        if routing["route"] == "FAST_PATH":
            return {"status": "success", "response": "🐈 Nanobot sẵn sàng hỗ trợ bạn."}
            
        if routing["route"] == "MEDICAL_DEVICE":
            rec = self.device_service.query_equipment_reconciliation(text)
            return {"status": "success", "routing": routing, "result": rec}
            
        return {"status": "success", "routing": routing, "response": "Đang chuyển tiếp xử lý..."}
