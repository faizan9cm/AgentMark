import json
from pathlib import Path
from memory.memory_manager import MemoryManager
from memory.schemas import EpisodicMemoryRecord


def migrate():
    memory = MemoryManager()

    long_term_path = Path("memory/data/long_term_memory.json")
    episodic_path = Path("memory/data/episodic_memory.json")

    if long_term_path.exists():
        with open(long_term_path, "r", encoding="utf-8") as f:
            long_term_data = json.load(f)

        for lead_id, record in long_term_data.items():
            memory.long_term.create_or_get(
                lead_id=lead_id,
                lead_name=record.get("lead_name"),
                source=record.get("source"),
            )

            preferences = record.get("preferences", {})
            if preferences:
                memory.long_term.update_preferences(lead_id, preferences)

            for event in record.get("history", []):
                memory.long_term.append_history(lead_id, event)

            if record.get("summary"):
                memory.long_term.update_summary(
                    lead_id=lead_id,
                    summary=record["summary"],
                    latest_status=record.get("latest_status"),
                )

    if episodic_path.exists():
        with open(episodic_path, "r", encoding="utf-8") as f:
            episodic_data = json.load(f)

        for item in episodic_data:
            try:
                episode = EpisodicMemoryRecord(**item)
                memory.episodic.add_episode(episode)
            except Exception:
                continue

    print("Migration completed.")


if __name__ == "__main__":
    migrate()