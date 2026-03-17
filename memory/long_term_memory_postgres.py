import json
from datetime import datetime
from typing import Optional
from memory.schemas import LongTermMemoryRecord
from memory.db_models import SessionLocal, LongTermMemoryDB


class PostgresLongTermMemory:
    def get(self, lead_id: str) -> Optional[LongTermMemoryRecord]:
        with SessionLocal() as db:
            row = db.query(LongTermMemoryDB).filter_by(lead_id=lead_id).first()
            if not row:
                return None

            return LongTermMemoryRecord(
                lead_id=row.lead_id,
                lead_name=row.lead_name,
                source=row.source,
                preferences=json.loads(row.preferences_json),
                history=json.loads(row.history_json),
                summary=row.summary,
                latest_status=row.latest_status,
                consolidated_at=row.consolidated_at.isoformat() if row.consolidated_at else None,
            )

    def create_or_get(
        self,
        lead_id: str,
        lead_name: str | None = None,
        source: str | None = None,
    ) -> LongTermMemoryRecord:
        with SessionLocal() as db:
            row = db.query(LongTermMemoryDB).filter_by(lead_id=lead_id).first()
            if not row:
                row = LongTermMemoryDB(
                    lead_id=lead_id,
                    lead_name=lead_name,
                    source=source,
                    preferences_json="{}",
                    history_json="[]",
                )
                db.add(row)
                db.commit()
                db.refresh(row)

        return self.get(lead_id)

    def append_history(self, lead_id: str, event: dict) -> LongTermMemoryRecord:
        with SessionLocal() as db:
            row = db.query(LongTermMemoryDB).filter_by(lead_id=lead_id).first()
            if not row:
                row = LongTermMemoryDB(
                    lead_id=lead_id,
                    preferences_json="{}",
                    history_json="[]",
                )
                db.add(row)
                db.commit()
                db.refresh(row)

            history = json.loads(row.history_json)

            event_signature = {
                "task_type": event.get("task_type"),
                "agent_name": event.get("agent_name"),
                "status": event.get("status"),
                "output": event.get("output"),
            }

            for existing in history[-3:]:
                existing_signature = {
                    "task_type": existing.get("task_type"),
                    "agent_name": existing.get("agent_name"),
                    "status": existing.get("status"),
                    "output": existing.get("output"),
                }
                if existing_signature == event_signature:
                    return self.get(lead_id)

            event["timestamp"] = datetime.utcnow().isoformat()
            history.append(event)
            row.history_json = json.dumps(history)
            db.commit()

        return self.get(lead_id)

    def update_preferences(self, lead_id: str, preferences: dict) -> LongTermMemoryRecord:
        with SessionLocal() as db:
            row = db.query(LongTermMemoryDB).filter_by(lead_id=lead_id).first()
            if not row:
                row = LongTermMemoryDB(
                    lead_id=lead_id,
                    preferences_json="{}",
                    history_json="[]",
                )
                db.add(row)
                db.commit()
                db.refresh(row)

            current = json.loads(row.preferences_json)
            current.update(preferences)
            row.preferences_json = json.dumps(current)
            db.commit()

        return self.get(lead_id)

    def update_summary(self, lead_id: str, summary: str, latest_status: str | None = None) -> LongTermMemoryRecord:
        with SessionLocal() as db:
            row = db.query(LongTermMemoryDB).filter_by(lead_id=lead_id).first()
            if not row:
                row = LongTermMemoryDB(
                    lead_id=lead_id,
                    preferences_json="{}",
                    history_json="[]",
                )
                db.add(row)
                db.commit()
                db.refresh(row)

            row.summary = summary
            row.latest_status = latest_status
            row.consolidated_at = datetime.utcnow()
            db.commit()

        return self.get(lead_id)