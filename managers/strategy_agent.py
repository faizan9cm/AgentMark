"""
Strategy Agent

Purpose:
- Monitor overall system behavior
- Review campaign optimization suggestions
- Update higher-level strategy
- Trigger policy or prompt changes
- Analyze performance trends across agents
"""

from agents.base_agent import BaseAgent
from orchestrator.contracts import AgentTask, AgentResult
from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response
from orchestrator.prompt_utils import format_memory_for_prompt


class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="strategy_agent")
        self.llm = LLMClient()

    def run(self, task: AgentTask) -> AgentResult:
        memory_context = format_memory_for_prompt(task.context.get("memory", {}))

        system_prompt = """
You are a Strategy Agent for a marketing system.

Your role:
- review escalated campaign issues
- use relevant memory and prior patterns if available
- provide a higher-level strategic recommendation
- summarize the strategic shift

Rules:
- Return only JSON
- Do not include markdown
- Do not include code fences

Return ONLY valid JSON with this schema:
{
  "strategy_decision": "string",
  "summary": "string"
}
"""

        user_prompt = f"""
Escalated campaign context:
{task.payload}

Relevant memory:
{memory_context}
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
                "strategy_decision": parsed["strategy_decision"],
                "summary": parsed["summary"],
            },
            next_action=None,
        )