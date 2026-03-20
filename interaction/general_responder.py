from orchestrator.llm_client import LLMClient


class GeneralResponder:
    def __init__(self):
        self.llm = LLMClient()

    def respond(
        self,
        message: str,
        user_name: str | None = None,
        session_id: str | None = None,
        recent_messages: list[dict] | None = None,
    ) -> dict:
        display_name = user_name if user_name else None
        recent_messages = recent_messages or []

        history_text_parts = []
        for msg in recent_messages[-8:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            history_text_parts.append(f"{role}: {content}")

        history_text = "\n".join(history_text_parts) if history_text_parts else "No prior conversation."

        system_prompt = f"""
You are the conversational responder for AgentMark.

Your job:
- answer naturally and contextually
- maintain continuity with the ongoing session
- remember facts explicitly stated earlier in the session when they appear in the conversation history
- be concise, warm, and helpful
- do NOT behave like a sales bot unless the user clearly asks about business topics
- do NOT invent facts not present in the session history
- if the user asks about their name, only answer from the provided session context
- if no name was provided or mentioned earlier, say you do not know
- return plain text only
- do not use markdown
- do not use code fences

Session context:
- User name provided in current request: {display_name}
- Session id: {session_id or "unknown"}

Recent conversation:
{history_text}
"""

        user_prompt = message
        text = self.llm.chat(system_prompt, user_prompt).strip()

        return {
            "response_message": text,
            "response_type": "general_inquiry_reply",
        }