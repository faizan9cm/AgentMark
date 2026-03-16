from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ShortTermMemoryRecord(BaseModel):
    session_id: str
    lead_id: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    latest_agent: Optional[str] = None
    latest_summary: Optional[str] = None


class LongTermMemoryRecord(BaseModel):
    lead_id: str
    lead_name: Optional[str] = None
    source: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)


class EpisodicMemoryRecord(BaseModel):
    episode_id: str
    situation: str
    action_taken: str
    outcome: str
    success_score: float
    tags: List[str] = Field(default_factory=list)


class SemanticMemoryRecord(BaseModel):
    subject: str
    relation: str
    object: str
    metadata: Dict[str, Any] = Field(default_factory=dict)