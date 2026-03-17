import json
from typing import List
from neo4j import GraphDatabase
from memory.schemas import SemanticMemoryRecord
from memory.storage_config import StorageConfig


class Neo4jSemanticMemory:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            StorageConfig.NEO4J_URI,
            auth=(StorageConfig.NEO4J_USERNAME, StorageConfig.NEO4J_PASSWORD),
        )

    def add_triplet(self, subject: str, relation: str, object_: str, metadata: dict | None = None) -> None:
        metadata_json = json.dumps(metadata or {})

        query = """
        MERGE (s:Entity {name: $subject})
        MERGE (o:Entity {name: $object})
        MERGE (s)-[r:RELATION {type: $relation}]->(o)
        SET r.metadata_json = $metadata_json
        """

        with self.driver.session() as session:
            session.run(
                query,
                subject=subject,
                relation=relation,
                object=object_,
                metadata_json=metadata_json,
            )

    def query_by_subject(self, subject: str) -> List[SemanticMemoryRecord]:
        query = """
        MATCH (s:Entity {name: $subject})-[r:RELATION]->(o:Entity)
        RETURN s.name AS subject, r.type AS relation, o.name AS object, coalesce(r.metadata_json, "{}") AS metadata_json
        """

        with self.driver.session() as session:
            result = session.run(query, subject=subject)
            records = []
            for record in result:
                metadata_json = record.get("metadata_json")
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except Exception:
                    metadata = {}

                records.append(
                    SemanticMemoryRecord(
                        subject=record["subject"],
                        relation=record["relation"],
                        object=record["object"],
                        metadata=metadata,
                    )
                )
            return records

    def list_all(self) -> List[SemanticMemoryRecord]:
        query = """
        MATCH (s:Entity)-[r:RELATION]->(o:Entity)
        RETURN s.name AS subject, r.type AS relation, o.name AS object, coalesce(r.metadata_json, "{}") AS metadata_json
        """

        with self.driver.session() as session:
            result = session.run(query)
            records = []
            for record in result:
                metadata_json = record.get("metadata_json")
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except Exception:
                    metadata = {}

                records.append(
                    SemanticMemoryRecord(
                        subject=record["subject"],
                        relation=record["relation"],
                        object=record["object"],
                        metadata=metadata,
                    )
                )
            return records