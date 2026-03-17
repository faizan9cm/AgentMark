from pydantic import BaseModel
from typing import Optional


class ReflectionResult(BaseModel):
    should_store: bool
    lesson: str
    improvement_hint: str
    success_score: float
    tag: str
    reasoning: Optional[str] = None