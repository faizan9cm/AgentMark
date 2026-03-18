from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response


class EngagementLLMJudge:
    def __init__(self):
        self.llm = LLMClient()

    def score_response(self, lead_message: str, response_message: str) -> dict:
        system_prompt = """
You are an evaluation judge for marketing engagement responses.

Evaluate the response on:
- relevance
- personalization
- actionability

Rules:
- Return only valid JSON
- Do not include markdown or code fences

Return JSON:
{
  "relevance": float,
  "personalization": float,
  "actionability": float,
  "overall_score": float,
  "reasoning": "string"
}
"""

        user_prompt = f"""
Lead message:
{lead_message}

Agent response:
{response_message}
"""

        raw_output = self.llm.chat(system_prompt, user_prompt)
        return parse_json_response(raw_output)