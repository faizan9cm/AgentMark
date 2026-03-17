from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    Float,
    DateTime,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from memory.storage_config import StorageConfig

Base = declarative_base()


class LongTermMemoryDB(Base):
    __tablename__ = "long_term_memory"

    lead_id = Column(String, primary_key=True)
    lead_name = Column(String, nullable=True)
    source = Column(String, nullable=True)
    preferences_json = Column(Text, nullable=False, default="{}")
    history_json = Column(Text, nullable=False, default="[]")
    summary = Column(Text, nullable=True)
    latest_status = Column(String, nullable=True)
    consolidated_at = Column(DateTime, nullable=True)


class EpisodicMemoryDB(Base):
    __tablename__ = "episodic_memory"

    episode_id = Column(String, primary_key=True)
    situation = Column(Text, nullable=False)
    action_taken = Column(Text, nullable=False)
    outcome = Column(Text, nullable=False)
    success_score = Column(Float, nullable=False)
    tags_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


engine = create_engine(StorageConfig.POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)


def init_postgres_tables():
    Base.metadata.create_all(bind=engine)