import json
from pathlib import Path
from typing import Dict, Optional
from memory.schemas import LongTermMemoryRecord
from datetime import datetime


class LongTermMemory:
    def __init__(self, file_path: str = "memory/data/long_term_memory.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save({})

    def _load(self) -> Dict[str, dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, dict]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get(self, lead_id: str) -> Optional[LongTermMemoryRecord]:
        data = self._load()
        record = data.get(lead_id)
        return LongTermMemoryRecord(**record) if record else None

    def create_or_get(
        self,
        lead_id: str,
        lead_name: str | None = None,
        source: str | None = None,
    ) -> LongTermMemoryRecord:
        data = self._load()
        if lead_id not in data:
            data[lead_id] = LongTermMemoryRecord(
                lead_id=lead_id,
                lead_name=lead_name,
                source=source,
            ).model_dump()
            self._save(data)
        return LongTermMemoryRecord(**data[lead_id])

    def append_history(self, lead_id: str, event: dict) -> LongTermMemoryRecord:
        data = self._load()
        if lead_id not in data:
            data[lead_id] = LongTermMemoryRecord(lead_id=lead_id).model_dump()

        event_signature = {
            "task_type": event.get("task_type"),
            "agent_name": event.get("agent_name"),
            "status": event.get("status"),
            "output": event.get("output"),
        }

        existing_history = data[lead_id]["history"]
        for existing in existing_history[-3:]:
            existing_signature = {
                "task_type": existing.get("task_type"),
                "agent_name": existing.get("agent_name"),
                "status": existing.get("status"),
                "output": existing.get("output"),
            }
            if existing_signature == event_signature:
                return LongTermMemoryRecord(**data[lead_id])

        event["timestamp"] = datetime.utcnow().isoformat()
        data[lead_id]["history"].append(event)
        self._save(data)
        return LongTermMemoryRecord(**data[lead_id])

    def update_preferences(self, lead_id: str, preferences: dict) -> LongTermMemoryRecord:
        data = self._load()
        if lead_id not in data:
            data[lead_id] = LongTermMemoryRecord(lead_id=lead_id).model_dump()

        data[lead_id]["preferences"].update(preferences)
        self._save(data)
        return LongTermMemoryRecord(**data[lead_id])
    
    def update_summary(
        self,
        lead_id: str,
        summary: str,
        latest_status: str | None = None,
    ) -> LongTermMemoryRecord:
        data = self._load()
        if lead_id not in data:
            data[lead_id] = LongTermMemoryRecord(lead_id=lead_id).model_dump()

        data[lead_id]["summary"] = summary
        data[lead_id]["latest_status"] = latest_status
        data[lead_id]["consolidated_at"] = datetime.utcnow().isoformat()
        self._save(data)
        return LongTermMemoryRecord(**data[lead_id])