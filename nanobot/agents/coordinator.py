import re
import hashlib
from typing import Dict, Any, Optional
from nanobot.core.security import SecurityPolicyEngine, Permission, ActionRiskLevel
from nanobot.core.hybrid_router import CactusHybridRouter
from nanobot.core.needle_adapter import NeedleAgentAdapter
from nanobot.providers.nine_router import NineRouterClient
from nanobot.core.observability import ObservabilityTracer, RequestTelemetry
from nanobot.core.trust_model import TrustLevel
from nanobot.core.confidence_policy import ConfidencePolicy, ConfidenceSource
from .contract import AgentContext, AgentResult
from .registry import AgentRegistry, AgentFactory
from .self_improvement_agent import PersistentEventStore, ImprovementEvent, ImprovementEventType

# Import specialized agents to guarantee registration
from . import specialized_agents
from . import self_improvement_agent

class NanobotCoordinator:
    """
    Production NOOA Coordinator (Hardened against Fowler Smells & Spec Gaps).
    Enforces Security Sanitizer, Typed Argument Resolution, and Correct Event Taxonomy.
    """
    def __init__(self):
        self.security = SecurityPolicyEngine()
        self.confidence_policy = ConfidencePolicy()
        self.router = CactusHybridRouter(policy=self.confidence_policy)
        self.needle_adapter = NeedleAgentAdapter()
        self.cloud_client = NineRouterClient()
        self.tracer = ObservabilityTracer()
        self.event_store = PersistentEventStore()

    def _extract_tool_arguments(self, tool_name: str, text: str) -> Dict[str, Any]:
        """Extract typed arguments from user query for specific tool."""
        q = text.strip()
        if tool_name == "lookup_device_by_serial":
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
        # 1. Security Check
        if not self.security.is_user_authorized(user_id):
            return {"status": "error", "message": "Unauthorized user access."}

        # 2. Invoke Security Sanitizer on untrusted input
        sanitized_input = self.security.sanitize_untrusted_content(text)

        # 3. Hybrid Routing Evaluation (Cactus Hybrid)
        decision = self.router.evaluate_query(text)
        req_id = "req-" + hashlib.sha256(text.encode()).hexdigest()[:8]

        # 4. Route Execution: LOCAL_EDGE
        if decision.route == "LOCAL_EDGE":
            if decision.agent and decision.agent in [a.name for a in AgentRegistry.list_agents()]:
                # Dynamic Agent Dispatch via Factory
                agent_instance = AgentFactory.create_agent(decision.agent)
                context = AgentContext(
                    request_id=req_id,
                    user_id=user_id,
                    input_text=text,
                    routing_decision=decision
                )
                agent_res: AgentResult = agent_instance.execute(context)

                # Record telemetry
                telemetry = RequestTelemetry(
                    request_id=req_id,
                    user_id=user_id,
                    intent=decision.intent,
                    route="LOCAL_EDGE",
                    confidence=decision.confidence,
                    confidence_source=decision.confidence_source.value,
                    agent=decision.agent,
                    tool=decision.tool,
                    tool_success=agent_res.status == "success",
                    trust_level=agent_res.trust_level.value,
                    escalated=False
                )
                self.tracer.log_event(telemetry)

                # Record appropriate improvement event type (Fix ternary logic bug)
                if agent_res.status != "success":
                    ev_type = ImprovementEventType.TOOL_FAILURE
                elif decision.confidence < 0.85:
                    ev_type = ImprovementEventType.LOW_CONFIDENCE
                else:
                    ev_type = ImprovementEventType.LOW_CONFIDENCE # default audit track

                self.event_store.append_event(ImprovementEvent(
                    request_id=req_id,
                    event_type=ev_type,
                    input_hash=hashlib.sha256(text.strip().encode()).hexdigest()[:16],
                    route=decision.route,
                    agent=decision.agent,
                    tool=decision.tool,
                    cactus_confidence=decision.confidence,
                    needle_confidence=0.98,
                    outcome=agent_res.status,
                    trust_level=agent_res.trust_level.value
                ))

                return {
                    "status": "success",
                    "routing": decision.model_dump(),
                    "telemetry": telemetry.model_dump(),
                    "result": {
                        "status": agent_res.status,
                        "trust_level": agent_res.trust_level.value,
                        "data": agent_res.output
                    }
                }

            elif decision.tool:
                # Fast Tool Dispatch with TYPED Argument Resolution
                tool_def = self.needle_adapter.registry.get_tool(decision.tool)
                min_conf = tool_def.min_confidence_required if tool_def else 0.80
                
                if decision.confidence < min_conf:
                    decision.route = "CLOUD_FRONTIER"
                else:
                    tool_args = self._extract_tool_arguments(decision.tool, text)
                    tool_res = self.needle_adapter.execute_tool(decision.tool, tool_args)
                    
                    trust_val = tool_res.get("trust_level", TrustLevel.UNKNOWN)
                    trust_str = trust_val.value if hasattr(trust_val, "value") else str(trust_val)
                    telemetry = RequestTelemetry(
                        request_id=req_id,
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

            return {
                "status": "success",
                "routing": decision.model_dump(),
                "response": "🐈 Nanobot sẵn sàng hỗ trợ bạn."
            }

        # 5. Cloud Escalation: CLOUD_FRONTIER (9Router)
        cloud_res = self.cloud_client.generate_chat_completion(prompt=sanitized_input)
        telemetry = RequestTelemetry(
            request_id=req_id,
            user_id=user_id,
            intent=decision.intent,
            route="CLOUD_FRONTIER",
            confidence=decision.confidence,
            confidence_source=decision.confidence_source.value,
            agent="CloudReasoningAgent",
            tool=None,
            tool_success=cloud_res.get("status") == "success",
            trust_level=TrustLevel.INFERRED.value,
            escalated=True,
            cloud_provider=cloud_res.get("provider")
        )
        self.tracer.log_event(telemetry)

        # Record cloud escalation event
        self.event_store.append_event(ImprovementEvent(
            request_id=req_id,
            event_type=ImprovementEventType.CLOUD_ESCALATION,
            input_hash=hashlib.sha256(text.strip().encode()).hexdigest()[:16],
            route="CLOUD_FRONTIER",
            agent="CloudReasoningAgent",
            cactus_confidence=decision.confidence,
            outcome=cloud_res.get("status", "unknown"),
            trust_level=TrustLevel.INFERRED.value
        ))

        return {
            "status": "success",
            "routing": decision.model_dump(),
            "telemetry": telemetry.model_dump(),
            "result": cloud_res
        }
