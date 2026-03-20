from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response


class IntentRouter:
    def __init__(self):
        self.llm = LLMClient()

    def detect_task_type(self, message: str) -> dict:
        text = (message or "").strip().lower()

        # Fast rule-based routing first
        if text in {"hi", "hello", "hey", "hi there", "hello there"}:
            return {
                "task_type": "general_inquiry",
                "is_lead_related": False,
                "reason": "Simple greeting detected."
            }

        if any(word in text for word in ["pricing", "demo", "enterprise", "onboarding", "support"]):
            return {
                "task_type": "new_lead",
                "is_lead_related": True,
                "reason": "Lead-like buying intent detected from keywords."
            }

        if any(word in text for word in ["ctr", "conversion", "campaign", "ads"]):
            return {
                "task_type": "campaign_review",
                "is_lead_related": False,
                "reason": "Campaign analytics intent detected from keywords."
            }

        # LLM fallback only if rules did not match
        system_prompt = """
You are an intent router for a multi-agent marketing system.

Your job:
- infer the best task type for the user message
- decide whether this message is lead-related
- provide a short reason

Allowed task types:
- new_lead
- engagement_request
- campaign_review
- strategy_review
- general_inquiry

Rules:
- Return only JSON
- Do not include markdown or code fences

Return JSON:
{
  "task_type": "new_lead" | "engagement_request" | "campaign_review" | "strategy_review" | "general_inquiry",
  "is_lead_related": true | false,
  "reason": "string"
}
"""

        user_prompt = f"""
User message:
{message}
"""

        raw_output = self.llm.chat(system_prompt, user_prompt)
        return parse_json_response(raw_output)