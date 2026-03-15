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


class EngagementAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="engagement_agent")

    def run(self, task: AgentTask) -> AgentResult:
        lead_name = task.payload.get("lead_name", "there")
        category = task.payload.get("category", "Unknown")

        response_message = (
            f"Hello {lead_name}, thanks for your interest. "
            f"We noticed you may be a {category}. "
            f"Our team can help you with the next steps."
        )

        return AgentResult(
            task_id=task.task_id,
            agent_name=self.name,
            status="success",
            output={
                "response_message": response_message,
                "follow_up_action": "Send email within 24 hours",
                "engagement_summary": "Mock engagement response generated."
            },
            next_action=None
        )