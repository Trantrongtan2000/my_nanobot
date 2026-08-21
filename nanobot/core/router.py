from typing import Dict, Any

class IntentRouter:
    """
    Dual-Path Edge Router (Needle 2 / 9Router Routing)
    Fast-path for simple intent (<50ms on Raspberry Pi), 9Router for reasoning.
    """
    def __init__(self):
        self.fast_keywords = ["hi", "hello", "ê", "e", "ok", "được", "ping", "status"]
        self.medical_keywords = ["cân", "monitor", "spo2", "hút dịch", "thiết bị", "phòng", "khoa", "kiểm định", "hết hạn"]
        self.ocr_keywords = ["ocr", "scan", "pdf", "bàn giao", "nghiệm thu", "chứng nhận"]

    def route_intent(self, text: str) -> Dict[str, Any]:
        t = text.lower().strip()
        if t in self.fast_keywords:
            return {"route": "FAST_PATH", "engine": "LOCAL", "target": "CORE"}
        if any(k in t for k in self.medical_keywords):
            return {"route": "MEDICAL_DEVICE", "engine": "LOCAL_SQLITE", "target": "MEDICAL_AGENT"}
        if any(k in t for k in self.ocr_keywords):
            return {"route": "OCR_PIPELINE", "engine": "MISTRAL_OCR", "target": "OCR_AGENT"}
        if "notion" in t or "inbox" in t or "lưu" in t:
            return {"route": "NOTION_SYNC", "engine": "NOTION_MCP", "target": "NOTION_AGENT"}
        return {"route": "REASONING", "engine": "9ROUTER", "target": "CLOUD_LLM"}
