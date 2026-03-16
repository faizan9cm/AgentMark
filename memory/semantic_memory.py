from typing import List
from memory.schemas import SemanticMemoryRecord


class SemanticMemory:
    def __init__(self):
        self.triplets: List[SemanticMemoryRecord] = []

    def add_triplet(self, subject: str, relation: str, object_: str, metadata: dict | None = None) -> None:
        for triplet in self.triplets:
            if (
                triplet.subject == subject
                and triplet.relation == relation
                and triplet.object == object_
            ):
                return

        self.triplets.append(
            SemanticMemoryRecord(
                subject=subject,
                relation=relation,
                object=object_,
                metadata=metadata or {},
            )
        )

    def query_by_subject(self, subject: str) -> List[SemanticMemoryRecord]:
        return [t for t in self.triplets if t.subject == subject]

    def list_all(self) -> List[SemanticMemoryRecord]:
        return self.triplets