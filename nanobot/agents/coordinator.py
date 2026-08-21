from typing import Dict, Any
from nanobot.core.security import SecurityPolicyEngine, Permission, ActionRiskLevel
from nanobot.core.hybrid_router import CactusHybridRouter
from nanobot.core.needle_adapter import NeedleToolAdapter
from nanobot.providers.nine_router import NineRouterClient
from nanobot.core.observability import ObservabilityTracer, RequestTelemetry
from nanobot.core.trust_model import TrustLevel
from .base_agent import NOOABaseAgent

class NanobotCoordinator(NOOABaseAgent):
    """
    Central NOOA Coordinator Agent.
    Implements Cactus Hybrid Edge-Cloud Routing, Needle 2 Tool Invocation & 9Router Cloud Escalation.
    """
    def __init__(self):
        super().__init__(required_permissions={Permission.READ_ONLY, Permission.EXECUTE_TOOL})
        self.security = SecurityPolicyEngine()
        self.router = CactusHybridRouter()
        self.needle_adapter = NeedleToolAdapter()
        self.cloud_client = NineRouterClient()
        self.tracer = ObservabilityTracer()

    def process_message(self, text: str, user_id: int = 1449852069) -> Dict[str, Any]:
        # 1. Security check
        if not self.security.is_user_authorized(user_id):
            return {"status": "error", "message": "Unauthorized user access."}

        # 2. Hybrid Routing Evaluation
        decision = self.router.evaluate_query(text)

        # 3. Route execution
        if decision.route == "LOCAL_EDGE":
            if decision.tool:
                # Execute tool via Needle Adapter
                tool_res = self.needle_adapter.execute_tool_call(decision.tool, {"query": text})
                telemetry = RequestTelemetry(
                    user_id=user_id,
                    intent=decision.intent,
                    route="LOCAL_EDGE",
                    confidence=decision.confidence,
                    confidence_source=decision.confidence_source.value,
                    agent=decision.agent,
                    tool=decision.tool,
                    tool_success=tool_res.get("status") == "success",
                    trust_level=tool_res.get("trust_level", TrustLevel.UNKNOWN).value if hasattr(tool_res.get("trust_level"), "value") else str(tool_res.get("trust_level", "UNKNOWN")),
                    escalated=False
                )
                self.tracer.log_event(telemetry)
                return {
                    "status": "success",
                    "routing": decision.model_dump(),
                    "telemetry": telemetry.model_dump(),
                    "result": tool_res
                }
            else:
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
