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


class TraceRunDB(Base):
    __tablename__ = "trace_runs"

    run_id = Column(String, primary_key=True)
    session_id = Column(String, nullable=True)
    lead_id = Column(String, nullable=True)
    entrypoint = Column(String, nullable=False)
    status = Column(String, nullable=False, default="running")
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    total_latency_ms = Column(Float, nullable=True)
    total_estimated_cost_usd = Column(Float, nullable=False, default=0.0)


class TraceSpanDB(Base):
    __tablename__ = "trace_spans"

    span_id = Column(String, primary_key=True)
    run_id = Column(String, nullable=False)
    parent_span_id = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    task_id = Column(String, nullable=True)
    agent_name = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="success")
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    latency_ms = Column(Float, nullable=True)
    model_name = Column(String, nullable=True)
    estimated_input_tokens = Column(Float, nullable=True)
    estimated_output_tokens = Column(Float, nullable=True)
    estimated_cost_usd = Column(Float, nullable=False, default=0.0)
    payload_json = Column(Text, nullable=False, default="{}")


class TraceEdgeDB(Base):
    __tablename__ = "trace_edges"

    id = Column(String, primary_key=True)
    run_id = Column(String, nullable=False)
    from_node = Column(String, nullable=False)
    to_node = Column(String, nullable=False)
    edge_type = Column(String, nullable=False)
    reason = Column(Text, nullable=True)


engine = create_engine(StorageConfig.POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)


def init_postgres_tables():
    Base.metadata.create_all(bind=engine)