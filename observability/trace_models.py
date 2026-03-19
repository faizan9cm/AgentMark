from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class TraceRun(BaseModel):
    run_id: str
    session_id: Optional[str] = None
    lead_id: Optional[str] = None
    entrypoint: str
    status: str = "running"
    started_at: str
    ended_at: Optional[str] = None
    total_latency_ms: Optional[float] = None
    total_estimated_cost_usd: float = 0.0


class TraceSpan(BaseModel):
    span_id: str
    run_id: str
    parent_span_id: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_name: Optional[str] = None
    event_type: str
    status: str = "success"
    started_at: str
    ended_at: Optional[str] = None
    latency_ms: Optional[float] = None
    model_name: Optional[str] = None
    estimated_input_tokens: Optional[int] = None
    estimated_output_tokens: Optional[int] = None
    estimated_cost_usd: float = 0.0
    payload: Dict[str, Any] = Field(default_factory=dict)


class TraceEdge(BaseModel):
    run_id: str
    from_node: str
    to_node: str
    edge_type: str
    reason: Optional[str] = None


class TraceGraph(BaseModel):
    run_id: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]