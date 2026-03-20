import uuid

from interaction.models import UserMessage, InteractionResult
from interaction.session_manager import SessionManager
from interaction.lead_manager import LeadManager
from interaction.intent_router import IntentRouter
from interaction.general_responder import GeneralResponder

from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask


class InteractionController:
    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.session_manager = SessionManager()
        self.lead_manager = LeadManager()
        self.intent_router = IntentRouter()
        self.general_responder = GeneralResponder()

    def _build_payload(self, user_message: UserMessage, task_type: str, lead_id: str | None) -> dict:
        base_payload = {
            "lead_id": lead_id,
            "lead_name": user_message.user_name,
            "message": user_message.message,
            "source": user_message.metadata.get("source", "chat_interface"),
        }

        if task_type == "campaign_review":
            return {
                "channel": user_message.metadata.get("channel", "unknown"),
                "ctr": user_message.metadata.get("ctr", 0.0),
                "conversion_rate": user_message.metadata.get("conversion_rate", 0.0),
            }

        return base_payload

    def handle_message(self, user_message: UserMessage) -> InteractionResult:
        session_id = self.session_manager.get_or_create_session_id(user_message.session_id)

        routing = self.intent_router.detect_task_type(user_message.message)
        task_type = routing["task_type"]
        is_lead_related = routing["is_lead_related"]

        if task_type == "general_inquiry":
            self.runtime.memory.short_term.create_or_get(
                session_id=session_id,
                lead_id=None,
            )

            self.runtime.memory.short_term.add_message(
                session_id=session_id,
                role="user",
                content=user_message.message,
                agent_name="user",
                summary="General user message.",
            )

            short_term = self.runtime.memory.short_term.get(session_id)
            recent_messages = short_term.messages if short_term else []

            reply = self.general_responder.respond(
                message=user_message.message,
                user_name=user_message.user_name,
                session_id=session_id,
                recent_messages=recent_messages,
            )

            self.runtime.memory.short_term.add_message(
                session_id=session_id,
                role="assistant",
                content=reply["response_message"],
                agent_name="general_responder",
                summary="General responder reply.",
            )

            return InteractionResult(
                session_id=session_id,
                lead_id=None,
                detected_task_type=task_type,
                runtime_results=[
                    {
                        "task_id": f"interaction_general_{uuid.uuid4().hex[:10]}",
                        "agent_name": "general_responder",
                        "status": "success",
                        "output": {
                            "response_message": reply["response_message"],
                            "response_type": reply["response_type"],
                            "routing_reason": routing["reason"],
                        },
                        "next_action": None,
                    }
                ],
                trace_run_id=None,
            )

        lead_id = self.lead_manager.get_or_create_lead_id(
            lead_id=user_message.lead_id,
            is_lead_related=is_lead_related,
        )

        task = AgentTask(
            task_id=f"interaction_{uuid.uuid4().hex[:10]}",
            task_type=task_type,
            payload=self._build_payload(user_message, task_type, lead_id),
            context={"interaction_router": routing},
            session_id=session_id,
            lead_id=lead_id,
        )

        results = self.runtime.execute_task_chain(task, run_post_processing=False)
        trace_run_id = task.context.get("trace_run_id")

        return InteractionResult(
            session_id=session_id,
            lead_id=lead_id,
            detected_task_type=task_type,
            runtime_results=[result.model_dump() for result in results],
            trace_run_id=trace_run_id,
        )