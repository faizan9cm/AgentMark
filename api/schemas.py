from pydantic import BaseModel
from typing import Any, Dict, Optional


class HttpRpcEnvelope(BaseModel):
    jsonrpc: str
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class StreamEvent(BaseModel):
    event_type: str
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_name: Optional[str] = None
    payload: Dict[str, Any]