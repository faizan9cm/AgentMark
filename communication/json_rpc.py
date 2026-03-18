from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: str
    method: str
    params: Dict[str, Any]


class JsonRpcSuccessResponse(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: str
    result: Dict[str, Any]


class JsonRpcErrorObject(BaseModel):
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class JsonRpcErrorResponse(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: str
    error: JsonRpcErrorObject