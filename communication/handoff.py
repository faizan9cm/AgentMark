from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AgentHandoff(BaseModel):
    handoff_id: str
    from_agent: str
    to_agent: str
    task_id: str
    task_type: str
    session_id: Optional[str] = None
    lead_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None