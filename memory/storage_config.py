import os
from dotenv import load_dotenv

load_dotenv()


class StorageConfig:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/agentmark")
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")