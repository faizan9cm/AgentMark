import uuid


class SessionManager:
    def get_or_create_session_id(self, session_id: str | None = None) -> str:
        if session_id:
            return session_id
        return f"session_{uuid.uuid4().hex[:10]}"