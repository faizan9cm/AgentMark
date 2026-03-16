"""
Engagement Agent

Purpose:
- Generate personalized outreach
- Continue lead conversation
- Suggest follow-up actions
- Use customer context from memory

Input:
- lead profile
- triage result
- previous interaction history

Output:
- response message
- follow_up_action
- engagement summary
"""

from agents.base_agent import BaseAgent
from orchestrator.contracts import AgentTask, AgentResult
from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response


class EngagementAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="engagement_agent")
        self.llm = LLMClient()

    def run(self, task: AgentTask) -> AgentResult:
        lead_name = task.payload.get("lead_name", "there")
        category = task.payload.get("category", "General Inquiry")
        lead_message = task.payload.get("message", "")

        system_prompt = """
You are an Engagement Agent in a marketing system.

Your job:
- write a personalized response to the lead
- suggest a follow-up action
- summarize the engagement intent

Return ONLY valid JSON in this schema:
{
  "response_message": "string",
  "follow_up_action": "string",
  "engagement_summary": "string"
}
"""

        user_prompt = f"""
Lead name: {lead_name}
Lead category: {category}
Lead message: {lead_message}
"""

        try:
            raw_output = self.llm.chat(system_prompt, user_prompt)
            parsed = parse_json_response(raw_output)
        except Exception as e:
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                status="error",
                output={
                    "error": str(e),
                    "raw_output": raw_output if "raw_output" in locals() else None,
                },
                next_action=None,
            )

        return AgentResult(
            task_id=task.task_id,
            agent_name=self.name,
            status="success",
            output={
                "response_message": parsed["response_message"],
                "follow_up_action": parsed["follow_up_action"],
                "engagement_summary": parsed["engagement_summary"],
            },
            next_action=None,
        )