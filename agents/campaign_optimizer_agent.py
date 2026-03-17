"""
Campaign Optimization Agent

Purpose:
- Analyze campaign performance
- Detect weak channels or poor conversion patterns
- Recommend adjustments
- Escalate strategic issues to Strategy Agent

Input:
- campaign metrics
- recent engagement outcomes
- memory summaries

Output:
- optimization recommendation
- confidence
- escalation flag
"""

from agents.base_agent import BaseAgent
from orchestrator.contracts import AgentTask, AgentResult
from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response
from orchestrator.prompt_utils import format_memory_for_prompt


class CampaignOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="campaign_optimizer_agent")
        self.llm = LLMClient()

    def run(self, task: AgentTask) -> AgentResult:
        ctr = task.payload.get("ctr", 0.0)
        conversion_rate = task.payload.get("conversion_rate", 0.0)
        channel = task.payload.get("channel", "unknown")
        memory_context = format_memory_for_prompt(task.context.get("memory", {}))

        system_prompt = """
You are a Campaign Optimization Agent.

Your job:
- analyze campaign performance
- recommend improvements
- use relevant episodic patterns if useful
- estimate confidence
- decide whether the issue should be escalated for strategy review

Rules:
- Return only JSON
- Do not include markdown
- Do not include code fences
- Use memory only when relevant, do not force it

Return ONLY valid JSON in this schema:
{
  "optimization_recommendation": "string",
  "confidence": float,
  "escalation_flag": true | false,
  "summary": "string",
  "next_action": "strategy_review" | null
}
"""

        user_prompt = f"""
Channel: {channel}
CTR: {ctr}
Conversion rate: {conversion_rate}

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
                "optimization_recommendation": parsed["optimization_recommendation"],
                "confidence": parsed["confidence"],
                "escalation_flag": parsed["escalation_flag"],
                "summary": parsed["summary"],
            },
            next_action=parsed.get("next_action"),
        )