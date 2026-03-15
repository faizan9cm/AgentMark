from orchestrator.event_types import (
    NEW_LEAD,
    QUALIFIED_LEAD,
    ENGAGEMENT_REQUEST,
    CAMPAIGN_REVIEW,
    STRATEGY_REVIEW,
)


class AgentRuntime:
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