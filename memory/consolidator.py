from memory.memory_manager import MemoryManager
from orchestrator.llm_client import LLMClient
from orchestrator.json_utils import parse_json_response
from datetime import datetime
from memory.schemas import EpisodicMemoryRecord


class MemoryConsolidator:
    def __init__(self, memory: MemoryManager):
        self.memory = memory
        self.llm = LLMClient()

    def consolidate_lead_history(self, lead_id: str) -> None:
        record = self.memory.long_term.get(lead_id)
        if not record or not record.history:
            return

        recent_history = record.history[-10:]

        system_prompt = """
You are consolidating lead history for a marketing multi-agent system.

Your job:
- summarize the lead's current state
- identify the latest status
- compress repeated interaction history into a short useful summary

Rules:
- Return only JSON
- Do not include markdown or code fences
- Keep summary concise but informative
- latest_status should be one short phrase

Return JSON:
{
  "summary": "string",
  "latest_status": "string"
}
"""

        user_prompt = f"""
Lead name: {record.lead_name}
Lead source: {record.source}

Recent history:
{recent_history}
"""

        try:
            raw_output = self.llm.chat(system_prompt, user_prompt)
            parsed = parse_json_response(raw_output)
        except Exception:
            return

        self.memory.long_term.update_summary(
            lead_id=lead_id,
            summary=parsed["summary"],
            latest_status=parsed.get("latest_status"),
        )
    

    def consolidate_episodic_memory(self) -> None:
        episodes = self.memory.episodic.list_all()
        if not episodes:
            return

        top_episodes = sorted(
            episodes,
            key=lambda x: x.success_score,
            reverse=True
        )[:20]

        system_prompt = """
You are consolidating episodic lessons for an autonomous agent system.

Your job:
- remove redundant lessons
- merge highly similar lessons
- keep only reusable, concrete, high-signal lessons

Rules:
- Return only JSON
- Do not include markdown or code fences
- Preserve concrete lessons
- Remove generic or repeated lessons

Return JSON:
{
  "episodes": [
    {
      "episode_id": "string",
      "situation": "string",
      "action_taken": "string",
      "outcome": "string",
      "success_score": float,
      "tags": ["string"]
    }
  ]
}
"""

        serialized = [episode.model_dump() for episode in top_episodes]

        try:
            raw_output = self.llm.chat(system_prompt, f"Episodes:\n{serialized}")
            parsed = parse_json_response(raw_output)
        except Exception:
            return

        consolidated = []
        seen_ids = set()

        for item in parsed.get("episodes", []):
            episode_id = item.get("episode_id")
            if not episode_id or episode_id in seen_ids:
                continue
            seen_ids.add(episode_id)

            outcome = item.get("outcome", "").strip()
            if len(outcome) < 20:
                continue
            try:
                consolidated.append(EpisodicMemoryRecord(**item))
            except Exception:
                continue

        if consolidated:
            self.memory.episodic.replace_all(consolidated)
    

    def consolidate_session(self, session_id: str) -> None:
        record = self.memory.short_term.get(session_id)
        if not record or not record.messages:
            return

        recent_messages = record.messages[-12:]

        system_prompt = """
You are consolidating short-term session memory.

Your job:
- summarize the current session state in one concise paragraph
- capture the latest important context for future continuation

Rules:
- Return only JSON
- Do not include markdown or code fences

Return JSON:
{
  "summary": "string"
}
"""

        user_prompt = f"""
Recent messages:
{recent_messages}
"""

        try:
            raw_output = self.llm.chat(system_prompt, user_prompt)
            parsed = parse_json_response(raw_output)
        except Exception:
            return

        self.memory.short_term.summarize_and_trim(
            session_id=session_id,
            summary=parsed["summary"],
            keep_last=8,
        )