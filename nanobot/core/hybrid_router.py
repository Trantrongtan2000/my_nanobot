import re
from typing import Dict, Any, Optional
from .routing_contract import RoutingDecision
from .confidence_policy import ConfidencePolicy, ConfidenceSource

class CactusHybridRouter:
    """
    Production Semantic Edge-Cloud Hybrid Router (Cactus Hybrid Architecture).
    Evaluates query complexity, semantic intent, and assigns calibrated confidence scores.
    """
    def __init__(self, policy: Optional[ConfidencePolicy] = None):
        self.policy = policy or ConfidencePolicy()

        # Semantic complexity patterns requiring Cloud Frontier reasoning
        self.complex_reasoning_patterns = [
            re.compile(r"tại\s+sao|nguyên\s+nhân|lý\s+do|phân\s+tích|đánh\s+giá|tư\s+vấn", re.IGNORECASE),
            re.compile(r"iso\s*13485|iso\s*14971|iec\s*60601|qcvn|thông\s+tư\s*30|tiêu\s+chuẩn", re.IGNORECASE),
            re.compile(r"hướng\s+dẫn\s+sửa|khắc\s+phục|báo\s+lỗi|error\s*\d+|troubleshoot|nhảy\s+số|hút\s+yếu|lệch|hỏng", re.IGNORECASE),
            re.compile(r"so\s+sánh|ưu\s+nhược\s+điểm|đề\s+xuất\s+kế\s+hoạch|phương\s+pháp|quy\s+trình", re.IGNORECASE),
            re.compile(r"có\s+được\s+tiếp\s+tục|có\s+an\s+toàn|rủi\s+ro|tuổi\s+thọ|đủ\s+điều\s+kiện|đáp\s+ứng", re.IGNORECASE)
        ]

        # Deterministic local fast-path patterns
        self.local_lookup_patterns = [
            re.compile(r"tra\s+cứu|tìm|số\s+seri|s/n|model|vị\s+trí|ở\s+đâu|phòng", re.IGNORECASE),
            re.compile(r"cân|ms4980|spo2|rad-5v|hút\s+dịch|askir|ecart|thiết\s+bị", re.IGNORECASE),
            re.compile(r"hết\s+hạn|kiểm\s+định|hiệu\s+chuẩn|danh\s+sách|số\s+lượng", re.IGNORECASE),
            re.compile(r"notion|inbox|lưu|ghi\s+chú", re.IGNORECASE),
            re.compile(r"ocr|scan|bóc\s+tách", re.IGNORECASE)
        ]

    def evaluate_query(self, query: str) -> RoutingDecision:
        q = query.strip()
        q_lower = q.lower()

        # Fast Greeting check
        if q_lower in ["hi", "hello", "ê", "e", "ok", "ping", "status"]:
            return RoutingDecision(
                route="LOCAL_EDGE",
                intent="GREETING_FAST_PATH",
                confidence=1.0,
                confidence_source=ConfidenceSource.ROUTER,
                agent="NanobotCoordinator",
                tool=None,
                reason="Direct greeting / ping."
            )
        
        # 1. Check for Complex Reasoning Traps
        complexity_matches = [p.pattern for p in self.complex_reasoning_patterns if p.search(q)]
        if complexity_matches:
            confidence = 0.40
            return RoutingDecision(
                route="CLOUD_FRONTIER",
                intent="CLINICAL_ENGINEERING_REASONING",
                confidence=confidence,
                confidence_source=ConfidenceSource.CACTUS_HYBRID,
                agent="CloudReasoningAgent",
                tool=None,
                reason="Query contains deep troubleshooting, standard compliance, or risk analysis factors.",
                escalation_reason=f"Matched complex patterns: {complexity_matches}",
                metadata={"complexity_score": 0.95}
            )

        # 2. Check for Routine Local Edge Lookup
        local_matches = [p.pattern for p in self.local_lookup_patterns if p.search(q)]
        if local_matches:
            confidence = 0.96
            selected_tool = "lookup_device"
            if "hết hạn" in q_lower or "kiểm định" in q_lower or "hiệu chuẩn" in q_lower:
                selected_tool = "get_calibration_status"
            elif "notion" in q_lower or "inbox" in q_lower or "lưu" in q_lower:
                selected_tool = "create_notion_note"
            elif "s/n" in q_lower or "seri" in q_lower:
                selected_tool = "lookup_device_by_serial"

            return RoutingDecision(
                route="LOCAL_EDGE",
                intent="LOCAL_EQUIPMENT_LOOKUP",
                confidence=confidence,
                confidence_source=ConfidenceSource.CACTUS_HYBRID,
                agent="MedicalEquipmentAgent",
                tool=selected_tool,
                reason="Query matched deterministic medical equipment lookup domain.",
                escalation_reason=None,
                metadata={"local_patterns": local_matches}
            )

        # 3. Default General Fallback
        return RoutingDecision(
            route="LOCAL_EDGE",
            intent="GENERAL_ASSISTANCE",
            confidence=0.85,
            confidence_source=ConfidenceSource.ROUTER,
            agent="NanobotCoordinator",
            tool=None,
            reason="Standard conversational intent.",
            escalation_reason=None
        )
