import os
import json
import urllib.request
import urllib.error
import time
from enum import Enum
from typing import Dict, Any, Optional

class CircuitState(str, Enum):
    CLOSED = "CLOSED"       # Normal operation
    OPEN = "OPEN"           # Failing, block requests
    HALF_OPEN = "HALF_OPEN" # Testing recovery

class NineRouterClient:
    """
    Production 9Router LLM Client with Circuit Breaker, Timeout, and Fallback Chain.
    """
    def __init__(self, api_base: Optional[str] = None, api_key: Optional[str] = None):
        self.api_base = api_base or os.environ.get("NANOBOT_9ROUTER_BASE", "http://127.0.0.1:20128/v1")
        self.api_key = api_key or os.environ.get("NANOBOT_9ROUTER_KEY", "sk-9router-local")
        self.timeout_seconds = 10
        self.max_retries = 2
        self.circuit_state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.failure_threshold = 3
        self.last_failure_time = 0.0
        self.recovery_timeout = 30.0

    def _check_circuit(self) -> bool:
        if self.circuit_state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.circuit_state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def generate_chat_completion(self, prompt: str, system_prompt: Optional[str] = None, model: str = "orfree") -> Dict[str, Any]:
        if not self._check_circuit():
            return {
                "status": "degraded",
                "provider": "LocalFallbackEngine",
                "model": "rule-based-safety",
                "content": f"[Circuit OPEN - 9Router Offline]: Yêu cầu '{prompt}' đã được chuyển tiếp vào hàng đợi xử lý.",
                "error": "CIRCUIT_BREAKER_OPEN"
            }

        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        body = {"model": model, "messages": messages, "temperature": 0.1, "max_tokens": 1024}
        data = json.dumps(body).encode("utf-8")

        for attempt in range(self.max_retries + 1):
            try:
                t0 = time.perf_counter()
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                    latency = (time.perf_counter() - t0) * 1000
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    content = resp_data["choices"][0]["message"]["content"]
                    
                    self.circuit_state = CircuitState.CLOSED
                    self.consecutive_failures = 0
                    return {
                        "status": "success",
                        "provider": "9Router",
                        "model": model,
                        "content": content,
                        "latency_ms": latency
                    }
            except Exception as e:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.failure_threshold:
                    self.circuit_state = CircuitState.OPEN
                    self.last_failure_time = time.time()

                if attempt == self.max_retries:
                    return {
                        "status": "degraded",
                        "provider": "LocalFallbackEngine",
                        "model": "rule-based-safety",
                        "content": f"[9Router Fallback]: Hệ thống ghi nhận yêu cầu: '{prompt}'.",
                        "error": str(e)
                    }
                time.sleep(0.5 * (attempt + 1))
