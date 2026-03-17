import json
from pathlib import Path
from typing import List
from memory.schemas import EpisodicMemoryRecord


class EpisodicMemory:
    def __init__(self, file_path: str = "memory/data/episodic_memory.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save([])

    def _load(self) -> List[dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: List[dict]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_episode(self, episode: EpisodicMemoryRecord) -> None:
        data = self._load()

        for item in data:
            if item.get("episode_id") == episode.episode_id:
                return

        data.append(episode.model_dump())
        self._save(data)

    def list_all(self) -> List[EpisodicMemoryRecord]:
        return [EpisodicMemoryRecord(**item) for item in self._load()]

    def search_by_tag(self, tag: str) -> List[EpisodicMemoryRecord]:
        results = []
        for item in self._load():
            if tag in item.get("tags", []):
                results.append(EpisodicMemoryRecord(**item))
        return results
    
    def top_k(self, k: int = 3) -> List[EpisodicMemoryRecord]:
        episodes = self.list_all()
        episodes = sorted(episodes, key=lambda x: x.success_score, reverse=True)
        return episodes[:k]