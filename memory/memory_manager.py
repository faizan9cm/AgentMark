from memory.short_term_memory_redis import RedisShortTermMemory
from memory.long_term_memory_postgres import PostgresLongTermMemory
from memory.episodic_memory_postgres import PostgresEpisodicMemory
from memory.semantic_memory_neo4j import Neo4jSemanticMemory
from memory.db_models import init_postgres_tables


class MemoryManager:
    def __init__(self):
        init_postgres_tables()

        self.short_term = RedisShortTermMemory()
        self.long_term = PostgresLongTermMemory()
        self.episodic = PostgresEpisodicMemory()
        self.semantic = Neo4jSemanticMemory()