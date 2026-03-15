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


class LeadTriageAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="lead_triage_agent")

    def run(self, task: AgentTask) -> AgentResult:
        message = task.payload.get("message", "").lower()

        if "pricing" in message or "enterprise" in message or "demo" in message:
            category = "Hot Lead"
            score = 0.9
            priority = "High"
            next_action = "engagement_request"
        elif "just browsing" in message or "curious" in message:
            category = "Cold Lead"
            score = 0.3
            priority = "Low"
            next_action = None
        else:
            category = "General Inquiry"
            score = 0.5
            priority = "Medium"
            next_action = None

        return AgentResult(
            task_id=task.task_id,
            agent_name=self.name,
            status="success",
            output={
                "category": category,
                "score": score,
                "priority": priority,
                "reasoning_summary": "Mock keyword-based triage result."
            },
            next_action=next_action
        )