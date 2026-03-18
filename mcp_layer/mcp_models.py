from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class MCPRequest(BaseModel):
    request_id: str
    kind: str  # "resource" or "tool"
    name: str
    params: Dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    request_id: str
    status: str
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None