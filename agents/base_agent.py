from abc import ABC, abstractmethod
from orchestrator.contracts import AgentTask, AgentResult


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, task: AgentTask) -> AgentResult:
        """Execute the task and return a structured result."""
        pass