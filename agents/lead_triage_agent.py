"""
Lead Triage Agent

Purpose:
- Classify incoming leads
- Detect user intent
- Score lead quality
- Decide urgency level

Input:
- lead_id
- message
- source
- optional customer metadata

Output:
- category
- score
- priority
- reasoning summary
"""

from agents.base_agent import BaseAgent
from orchestrator.contracts import AgentTask, AgentResult
from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response


class LeadTriageAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="lead_triage_agent")
        self.llm = LLMClient()

    def run(self, task: AgentTask) -> AgentResult:
        message = task.payload.get("message", "")
        source = task.payload.get("source", "unknown")
        lead_name = task.payload.get("lead_name", "unknown")

        system_prompt = """
You are a Lead Triage Agent for a marketing automation system.

Your job:
- classify the lead
- estimate score from 0.0 to 1.0
- assign priority
- provide a short reasoning summary
- decide the next action

Return ONLY valid JSON with this schema:
{
  "category": "Hot Lead" | "Cold Lead" | "General Inquiry",
  "score": float,
  "priority": "High" | "Medium" | "Low",
  "reasoning_summary": "string",
  "next_action": "engagement_request" | null
}
"""

        user_prompt = f"""
Lead name: {lead_name}
Lead source: {source}
Lead message: {message}
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
                "category": parsed["category"],
                "score": parsed["score"],
                "priority": parsed["priority"],
                "reasoning_summary": parsed["reasoning_summary"],
            },
            next_action=parsed.get("next_action"),
        )