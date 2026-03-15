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


class CampaignOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="campaign_optimizer_agent")

    def run(self, task: AgentTask) -> AgentResult:
        ctr = task.payload.get("ctr", 0.0)
        conversion_rate = task.payload.get("conversion_rate", 0.0)

        if ctr < 0.02:
            recommendation = "Improve ad creatives and re-test subject lines."
            escalation_flag = True
        elif conversion_rate < 0.05:
            recommendation = "Improve landing page and lead qualification flow."
            escalation_flag = False
        else:
            recommendation = "Campaign is performing well. Continue monitoring."
            escalation_flag = False

        return AgentResult(
            task_id=task.task_id,
            agent_name=self.name,
            status="success",
            output={
                "optimization_recommendation": recommendation,
                "confidence": 0.75,
                "escalation_flag": escalation_flag
            },
            next_action="strategy_review" if escalation_flag else None
        )