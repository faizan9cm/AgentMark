from typing import Dict, Optional
from memory.schemas import ShortTermMemoryRecord


class ShortTermMemory:
    def __init__(self):
        self.store: Dict[str, ShortTermMemoryRecord] = {}

    def get(self, session_id: str) -> Optional[ShortTermMemoryRecord]:
        return self.store.get(session_id)

    def create_or_get(self, session_id: str, lead_id: str | None = None) -> ShortTermMemoryRecord:
        if session_id not in self.store:
            self.store[session_id] = ShortTermMemoryRecord(
                session_id=session_id,
                lead_id=lead_id,
            )
        return self.store[session_id]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent_name: str | None = None,
        summary: str | None = None,
    ) -> ShortTermMemoryRecord:
        record = self.create_or_get(session_id=session_id)
        record.messages.append({
            "role": role,
            "content": content,
            "agent_name": agent_name,
        })
        if agent_name:
            record.latest_agent = agent_name
        if summary:
            record.latest_summary = summary
        return record

    def update_summary(self, session_id: str, summary: str) -> None:
        record = self.create_or_get(session_id=session_id)
        record.latest_summary = summary

    def clear(self, session_id: str) -> None:
        if session_id in self.store:
            del self.store[session_id]