from abc import ABC, abstractmethod
from orchestrator.contracts import AgentTask, AgentResult


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, task: AgentTask) -> AgentResult:
        pass