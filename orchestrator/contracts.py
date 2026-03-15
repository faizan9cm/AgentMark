from pydantic import BaseModel
from typing import Any, Dict, Optional


class AgentTask(BaseModel):
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    context: Dict[str, Any] = {}
    assigned_by: Optional[str] = None


class AgentResult(BaseModel):
    task_id: str
    agent_name: str
    status: str
    output: Dict[str, Any]
    next_action: Optional[str] = None