import uuid


class LeadManager:
    def get_or_create_lead_id(self, lead_id: str | None = None, is_lead_related: bool = True) -> str | None:
        if not is_lead_related:
            return None
        if lead_id:
            return lead_id
        return f"lead_{uuid.uuid4().hex[:10]}"