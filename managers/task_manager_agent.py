"""
Task Manager Agent

Purpose:
- Receive incoming task/event
- Decide which worker agent should handle it
- Manage handoff between agents
- Maintain execution flow

Examples:
- new lead -> Lead Triage Agent
- qualified lead -> Engagement Agent
- campaign review request -> Campaign Optimization Agent
"""

from agents.base_agent import BaseAgent
from orchestrator.contracts import AgentTask, AgentResult


class TaskManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="task_manager_agent")

    def run(self, task: AgentTask) -> AgentResult:
        return AgentResult(
            task_id=task.task_id,
            agent_name=self.name,
            status="success",
            output={
                "message": "Task manager received the task.",
                "task_type": task.task_type
            },
            next_action=None
        )