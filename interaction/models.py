from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class UserMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    lead_id: Optional[str] = None
    user_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InteractionResult(BaseModel):
    session_id: str
    lead_id: Optional[str] = None
    detected_task_type: str
    runtime_results: list[dict]
    trace_run_id: Optional[str] = None