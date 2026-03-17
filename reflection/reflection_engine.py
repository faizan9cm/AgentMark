from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response
from reflection.reflection_schemas import ReflectionResult


class ReflectionEngine:
    def __init__(self):
        self.llm = LLMClient()

    def reflect(
        self,
        agent_name: str,
        task_type: str,
        input_payload: dict,
        agent_output: dict,
        memory_context: dict | None = None,
    ) -> ReflectionResult:
        system_prompt = """
You are a reflection engine for an autonomous multi-agent system.

Your job:
- evaluate whether the agent output produced a useful reusable lesson
- extract one lesson if appropriate
- suggest one improvement hint
- assign a success score from 0.0 to 1.0
- choose one short tag

Rules:
- Store only lessons that are reusable and non-trivial
- Do not store generic lessons like "be helpful"
- If the result is too ordinary or not reusable, set should_store to false
- Return only valid JSON
- Do not include markdown or code fences

Return JSON in this schema:
{
  "should_store": true | false,
  "lesson": "string",
  "improvement_hint": "string",
  "success_score": float,
  "tag": "string",
  "reasoning": "string"
}
"""

        user_prompt = f"""
Agent name: {agent_name}
Task type: {task_type}

Input payload:
{input_payload}

Agent output:
{agent_output}

Memory context:
{memory_context}
"""

        raw_output = self.llm.chat(system_prompt, user_prompt)
        parsed = parse_json_response(raw_output)
        return ReflectionResult(**parsed)