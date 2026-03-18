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
from orchestrator.prompt_utils import format_memory_for_prompt
from orchestrator.prompt_utils import format_memory_for_prompt, format_mcp_for_prompt



class LeadTriageAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="lead_triage_agent")
        self.llm = LLMClient()

    def run(self, task: AgentTask) -> AgentResult:
        message = task.payload.get("message", "")
        source = task.payload.get("source", "unknown")
        lead_name = task.payload.get("lead_name", "unknown")
        memory_context = format_memory_for_prompt(task.context.get("memory", {}))
        mcp_context = format_mcp_for_prompt(task.context.get("mcp", {}))

        system_prompt = """
You are a Lead Triage Agent for a marketing automation system.

Your job:
- classify the lead
- estimate score from 0.0 to 1.0
- assign priority
- provide a short reasoning summary
- decide the next action

Use relevant memory if it helps, especially:
- prior lead history
- recent session context
- known lead source or prior classification patterns

Rules:
- Return only JSON
- Do not include markdown
- Do not include code fences
- Keep reasoning_summary concise
- If the lead shows strong buying intent, use engagement_request as next_action
- If a known lead continues to show strong buying intent, follow-up intent, pricing interest, demo interest, onboarding questions, support questions, or team evaluation details, set next_action to "engagement_request".

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

Relevant memory:
{memory_context}
MCP context:
{mcp_context}
"""

        try:
            raw_output = self.llm.chat(system_prompt, user_prompt)
            parsed = parse_json_response(raw_output)
            message_lower = message.lower()
            strong_intent_terms = [
                "pricing", "demo", "onboarding", "support", "team",
                "enterprise", "evaluation", "evaluate"
            ]

            if (
                parsed["category"] == "Hot Lead"
                and any(term in message_lower for term in strong_intent_terms)
            ):
                parsed["next_action"] = "engagement_request"
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