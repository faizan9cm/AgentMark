from agents.lead_triage_agent import LeadTriageAgent
from agents.engagement_agent import EngagementAgent
from agents.campaign_optimizer_agent import CampaignOptimizerAgent
from managers.strategy_agent import StrategyAgent
from orchestrator.contracts import AgentTask, AgentResult
from orchestrator.event_types import (
    NEW_LEAD,
    QUALIFIED_LEAD,
    ENGAGEMENT_REQUEST,
    CAMPAIGN_REVIEW,
    STRATEGY_REVIEW,
)


class AgentRuntime:
    def __init__(self):
        self.agents = {
            "lead_triage_agent": LeadTriageAgent(),
            "engagement_agent": EngagementAgent(),
            "campaign_optimizer_agent": CampaignOptimizerAgent(),
            "strategy_agent": StrategyAgent(),
        }

    def route_task(self, task_type: str) -> str:
        if task_type == NEW_LEAD:
            return "lead_triage_agent"
        if task_type in [QUALIFIED_LEAD, ENGAGEMENT_REQUEST]:
            return "engagement_agent"
        if task_type == CAMPAIGN_REVIEW:
            return "campaign_optimizer_agent"
        if task_type == STRATEGY_REVIEW:
            return "strategy_agent"
        raise ValueError(f"Unknown task type: {task_type}")

    def execute_task(self, task: AgentTask) -> AgentResult:
        agent_name = self.route_task(task.task_type)
        agent = self.agents[agent_name]
        return agent.run(task)

    def execute_task_chain(self, task: AgentTask) -> list[AgentResult]:
        results = []

        current_task = task

        while current_task is not None:
            result = self.execute_task(current_task)
            results.append(result)

            if result.next_action == "engagement_request":
                current_task = AgentTask(
                    task_id=current_task.task_id + "_engagement",
                    task_type="engagement_request",
                    payload={
                        "lead_name": current_task.payload.get("lead_name", "there"),
                        "category": result.output.get("category", "General Inquiry"),
                        "message": current_task.payload.get("message", ""),
                        "source": current_task.payload.get("source", "unknown"),
                    },
                    context={"previous_result": result.output},
                    assigned_by=result.agent_name
                )
            elif result.next_action == "strategy_review":
                current_task = AgentTask(
                    task_id=current_task.task_id + "_strategy",
                    task_type="strategy_review",
                    payload=result.output,
                    context={"previous_result": result.output},
                    assigned_by=result.agent_name
                )
            else:
                current_task = None

        return results