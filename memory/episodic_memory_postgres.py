import json
from typing import List
from memory.schemas import EpisodicMemoryRecord
from memory.db_models import SessionLocal, EpisodicMemoryDB


class PostgresEpisodicMemory:
    def add_episode(self, episode: EpisodicMemoryRecord) -> None:
        with SessionLocal() as db:
            existing = db.query(EpisodicMemoryDB).filter_by(episode_id=episode.episode_id).first()
            if existing:
                return

            row = EpisodicMemoryDB(
                episode_id=episode.episode_id,
                situation=episode.situation,
                action_taken=episode.action_taken,
                outcome=episode.outcome,
                success_score=episode.success_score,
                tags_json=json.dumps(episode.tags),
            )
            db.add(row)
            db.commit()

    def list_all(self) -> List[EpisodicMemoryRecord]:
        with SessionLocal() as db:
            rows = db.query(EpisodicMemoryDB).all()
            return [
                EpisodicMemoryRecord(
                    episode_id=row.episode_id,
                    situation=row.situation,
                    action_taken=row.action_taken,
                    outcome=row.outcome,
                    success_score=row.success_score,
                    tags=json.loads(row.tags_json),
                )
                for row in rows
            ]

    def search_by_tag(self, tag: str) -> List[EpisodicMemoryRecord]:
        results = []
        for episode in self.list_all():
            if tag in episode.tags:
                results.append(episode)
        return results

    def search_by_tags(self, tags: list[str], limit: int = 5) -> List[EpisodicMemoryRecord]:
        matches = []
        for episode in self.list_all():
            if any(tag in episode.tags for tag in tags):
                matches.append(episode)
        matches = sorted(matches, key=lambda x: x.success_score, reverse=True)
        return matches[:limit]

    def top_k(self, k: int = 3) -> List[EpisodicMemoryRecord]:
        episodes = self.list_all()
        episodes = sorted(episodes, key=lambda x: x.success_score, reverse=True)
        return episodes[:k]

    def replace_all(self, episodes: List[EpisodicMemoryRecord]) -> None:
        with SessionLocal() as db:
            db.query(EpisodicMemoryDB).delete()
            for episode in episodes:
                db.add(EpisodicMemoryDB(
                    episode_id=episode.episode_id,
                    situation=episode.situation,
                    action_taken=episode.action_taken,
                    outcome=episode.outcome,
                    success_score=episode.success_score,
                    tags_json=json.dumps(episode.tags),
                ))
            db.commit()