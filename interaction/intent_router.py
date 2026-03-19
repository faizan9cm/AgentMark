from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response


class IntentRouter:
    def __init__(self):
        self.llm = LLMClient()

    def detect_task_type(self, message: str) -> dict:
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