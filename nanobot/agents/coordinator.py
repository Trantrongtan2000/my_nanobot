import re
from typing import Dict, Any, Optional
from nanobot.core.security import SecurityPolicyEngine, Permission, ActionRiskLevel
from nanobot.core.hybrid_router import CactusHybridRouter
from nanobot.core.needle_adapter import NeedleAgentAdapter
from nanobot.providers.nine_router import NineRouterClient
from nanobot.core.observability import ObservabilityTracer, RequestTelemetry
from nanobot.core.trust_model import TrustLevel
from nanobot.core.confidence_policy import ConfidencePolicy, ConfidenceSource
from .base_agent import NOOABaseAgent

class NanobotCoordinator(NOOABaseAgent):
    """
    Production NOOA Coordinator Agent.
    Implements Security Policy Enforcement, Cactus Hybrid Semantic Routing,
    Needle 2 Tool Calling, and 9Router Cloud Escalation.
    """
    def __init__(self):
        super().__init__(required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL})
        self.security = SecurityPolicyEngine()
        self.confidence_policy = ConfidencePolicy()
        self.router = CactusHybridRouter(policy=self.confidence_policy)
        self.needle_adapter = NeedleAgentAdapter()
        self.cloud_client = NineRouterClient()
        self.tracer = ObservabilityTracer()

    def _extract_tool_arguments(self, tool_name: str, text: str) -> Dict[str, Any]:
        """Extract typed arguments from user query for specific tool."""
        q = text.strip()
        if tool_name == "lookup_device_by_serial":
            # Extract serial pattern
            sn_match = re.search(r"(T\d{8}|N\d{6}|\d{5})", q, re.IGNORECASE)
            serial = sn_match.group(1) if sn_match else q
            return {"serial_no": serial}
        elif tool_name == "get_calibration_status":
            return {"days_ahead": 60}
        elif tool_name == "create_notion_note":
            return {"title": "Ghi chú từ Telegram", "content": q}
        elif tool_name == "get_device_location":
            return {"device_name": q}
        elif tool_name == "search_service_record":
            sn_match = re.search(r"(T\d{8}|N\d{6}|\d{5})", q, re.IGNORECASE)
            serial = sn_match.group(1) if sn_match else q
            return {"device_serial": serial}
        else: # lookup_device
            return {"query": q}

    def process_message(self, text: str, user_id: int = 1449852069) -> Dict[str, Any]:
        # 1. Security check
        if not self.security.is_user_authorized(user_id):
            return {"status": "error", "message": "Unauthorized user access."}

        # 2. Hybrid Routing Evaluation
        decision = self.router.evaluate_query(text)

        # 3. Route Execution: Local Edge (Needle 2)
        if decision.route == "LOCAL_EDGE":
            if decision.tool:
                # Check confidence threshold for action
                tool_def = self.needle_adapter.registry.get_tool(decision.tool)
                min_conf = tool_def.min_confidence_required if tool_def else 0.80
                
                if decision.confidence < min_conf:
                    # Low confidence -> trigger escalation
                    decision.route = "CLOUD_FRONTIER"
                else:
                    # Resolve typed arguments and execute
                    tool_args = self._extract_tool_arguments(decision.tool, text)
                    tool_res = self.needle_adapter.execute_tool(decision.tool, tool_args)
                    
                    trust_val = tool_res.get("trust_level", TrustLevel.UNKNOWN)
                    trust_str = trust_val.value if hasattr(trust_val, "value") else str(trust_val)

                    telemetry = RequestTelemetry(
                        user_id=user_id,
                        intent=decision.intent,
                        route="LOCAL_EDGE",
                        confidence=decision.confidence,
                        confidence_source=decision.confidence_source.value,
                        agent=decision.agent,
                        tool=decision.tool,
                        tool_success=tool_res.get("status") == "success",
                        trust_level=trust_str,
                        escalated=False
                    )
                    self.tracer.log_event(telemetry)
                    return {
                        "status": "success",
                        "routing": decision.model_dump(),
                        "telemetry": telemetry.model_dump(),
                        "result": tool_res
                    }

            if not decision.tool:
                return {
                    "status": "success",
                    "routing": decision.model_dump(),
                    "response": "🐈 Nanobot sẵn sàng hỗ trợ bạn."
                }

        # 4. Cloud Escalation (9Router)
        cloud_res = self.cloud_client.generate_chat_completion(prompt=text)
        telemetry = RequestTelemetry(
            user_id=user_id,
            intent=decision.intent,
            route="CLOUD_FRONTIER",
            confidence=decision.confidence,
            confidence_source=decision.confidence_source.value,
            agent=decision.agent,
            tool=None,
            tool_success=cloud_res.get("status") == "success",
            trust_level=TrustLevel.INFERRED.value,
            escalated=True,
            cloud_provider=cloud_res.get("provider")
        )
        self.tracer.log_event(telemetry)
        return {
            "status": "success",
            "routing": decision.model_dump(),
            "telemetry": telemetry.model_dump(),
            "result": cloud_res
        }
