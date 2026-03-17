import json
from typing import Optional
import redis
from memory.schemas import ShortTermMemoryRecord
from memory.storage_config import StorageConfig


class RedisShortTermMemory:
    def __init__(self):
        self.client = redis.Redis.from_url(StorageConfig.REDIS_URL, decode_responses=True)

    def _key(self, session_id: str) -> str:
        return f"short_term:{session_id}"

    def get(self, session_id: str) -> Optional[ShortTermMemoryRecord]:
        raw = self.client.get(self._key(session_id))
        if not raw:
            return None
        return ShortTermMemoryRecord(**json.loads(raw))

    def create_or_get(self, session_id: str, lead_id: str | None = None) -> ShortTermMemoryRecord:
        record = self.get(session_id)
        if record:
            return record

        record = ShortTermMemoryRecord(session_id=session_id, lead_id=lead_id)
        self.client.set(self._key(session_id), record.model_dump_json())
        return record

    def save(self, record: ShortTermMemoryRecord) -> None:
        self.client.set(self._key(record.session_id), record.model_dump_json())

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent_name: str | None = None,
        summary: str | None = None,
    ) -> ShortTermMemoryRecord:
        from datetime import datetime

        record = self.create_or_get(session_id=session_id)
        record.messages.append({
            "role": role,
            "content": content,
            "agent_name": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
        })

        if agent_name:
            record.latest_agent = agent_name
        if summary:
            record.latest_summary = summary

        self.save(record)
        return record

    def update_summary(self, session_id: str, summary: str) -> None:
        record = self.create_or_get(session_id=session_id)
        record.latest_summary = summary
        self.save(record)

    def trim(self, session_id: str, keep_last: int = 12) -> None:
        record = self.get(session_id)
        if not record:
            return
        if len(record.messages) > keep_last:
            record.messages = record.messages[-keep_last:]
            self.save(record)

    def summarize_and_trim(self, session_id: str, summary: str, keep_last: int = 8) -> None:
        record = self.get(session_id)
        if not record:
            return
        record.latest_summary = summary
        if len(record.messages) > keep_last:
            record.messages = record.messages[-keep_last:]
        self.save(record)

    def clear(self, session_id: str) -> None:
        self.client.delete(self._key(session_id))