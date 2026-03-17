from typing import Any, Dict, List, Optional
from memory.memory_manager import MemoryManager


class MemoryRetriever:
    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def get_short_term_context(self, session_id: Optional[str]) -> Dict[str, Any]:
        if not session_id:
            return {}

        record = self.memory.short_term.get(session_id)
        if not record:
            return {}

        messages = record.messages[-6:]  # only recent context
        return {
            "session_id": record.session_id,
            "lead_id": record.lead_id,
            "latest_agent": record.latest_agent,
            "latest_summary": record.latest_summary,
            "recent_messages": messages,
        }

    def get_long_term_context(self, lead_id: Optional[str]) -> Dict[str, Any]:
        if not lead_id:
            return {}

        record = self.memory.long_term.get(lead_id)
        if not record:
            return {}

        history = record.history[-6:]  # recent persistent history
        return {
            "lead_id": record.lead_id,
            "lead_name": record.lead_name,
            "source": record.source,
            "preferences": record.preferences,
            "recent_history": history,
        }

    def get_episodic_context(self, tags: Optional[List[str]] = None, limit: int = 3) -> List[Dict[str, Any]]:
        episodes = self.memory.episodic.list_all()

        if tags:
            filtered = []
            for episode in episodes:
                if any(tag in episode.tags for tag in tags):
                    filtered.append(episode)
            episodes = filtered

        episodes = sorted(episodes, key=lambda x: x.success_score, reverse=True)
        return [episode.model_dump() for episode in episodes[:limit]]

    def get_semantic_context(self, lead_id: Optional[str]) -> List[Dict[str, Any]]:
        if not lead_id:
            return []

        triplets = self.memory.semantic.query_by_subject(lead_id)
        return [triplet.model_dump() for triplet in triplets]

    def build_agent_memory_context(
        self,
        session_id: Optional[str],
        lead_id: Optional[str],
        episodic_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "short_term": self.get_short_term_context(session_id),
            "long_term": self.get_long_term_context(lead_id),
            "episodic": self.get_episodic_context(tags=episodic_tags),
            "semantic": self.get_semantic_context(lead_id),
        }