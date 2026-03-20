import json
import uuid
from datetime import datetime
from typing import List, Optional

from observability.trace_models import TraceRun, TraceSpan, TraceEdge
from memory.db_models import SessionLocal, TraceRunDB, TraceSpanDB, TraceEdgeDB


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


class TraceStore:
    def add_run(self, run: TraceRun) -> None:
        with SessionLocal() as db:
            existing = db.query(TraceRunDB).filter_by(run_id=run.run_id).first()
            if existing:
                return

            row = TraceRunDB(
                run_id=run.run_id,
                session_id=run.session_id,
                lead_id=run.lead_id,
                entrypoint=run.entrypoint,
                status=run.status,
                started_at=_parse_dt(run.started_at),
                ended_at=_parse_dt(run.ended_at),
                total_latency_ms=run.total_latency_ms,
                total_estimated_cost_usd=run.total_estimated_cost_usd,
            )
            db.add(row)
            db.commit()

    def update_run(self, run_id: str, **updates) -> Optional[TraceRun]:
        with SessionLocal() as db:
            row = db.query(TraceRunDB).filter_by(run_id=run_id).first()
            if not row:
                return None

            for key, value in updates.items():
                if key in {"started_at", "ended_at"} and isinstance(value, str):
                    value = _parse_dt(value)
                setattr(row, key, value)

            db.commit()
            db.refresh(row)
            return self.get_run(run_id)

    def get_run(self, run_id: str) -> Optional[TraceRun]:
        with SessionLocal() as db:
            row = db.query(TraceRunDB).filter_by(run_id=run_id).first()
            if not row:
                return None

            return TraceRun(
                run_id=row.run_id,
                session_id=row.session_id,
                lead_id=row.lead_id,
                entrypoint=row.entrypoint,
                status=row.status,
                started_at=row.started_at.isoformat(),
                ended_at=row.ended_at.isoformat() if row.ended_at else None,
                total_latency_ms=row.total_latency_ms,
                total_estimated_cost_usd=row.total_estimated_cost_usd,
            )

    def list_runs(self) -> List[TraceRun]:
        with SessionLocal() as db:
            rows = db.query(TraceRunDB).order_by(TraceRunDB.started_at.desc()).all()
            return [
                TraceRun(
                    run_id=row.run_id,
                    session_id=row.session_id,
                    lead_id=row.lead_id,
                    entrypoint=row.entrypoint,
                    status=row.status,
                    started_at=row.started_at.isoformat(),
                    ended_at=row.ended_at.isoformat() if row.ended_at else None,
                    total_latency_ms=row.total_latency_ms,
                    total_estimated_cost_usd=row.total_estimated_cost_usd,
                )
                for row in rows
            ]

    def add_span(self, span: TraceSpan) -> None:
        with SessionLocal() as db:
            existing = db.query(TraceSpanDB).filter_by(span_id=span.span_id).first()
            if existing:
                return

            row = TraceSpanDB(
                span_id=span.span_id,
                run_id=span.run_id,
                parent_span_id=span.parent_span_id,
                session_id=span.session_id,
                task_id=span.task_id,
                agent_name=span.agent_name,
                event_type=span.event_type,
                status=span.status,
                started_at=_parse_dt(span.started_at),
                ended_at=_parse_dt(span.ended_at),
                latency_ms=span.latency_ms,
                model_name=span.model_name,
                estimated_input_tokens=span.estimated_input_tokens,
                estimated_output_tokens=span.estimated_output_tokens,
                estimated_cost_usd=span.estimated_cost_usd,
                payload_json=json.dumps(span.payload),
            )
            db.add(row)
            db.commit()

    def get_spans(self, run_id: str) -> List[TraceSpan]:
        with SessionLocal() as db:
            rows = db.query(TraceSpanDB).filter_by(run_id=run_id).order_by(TraceSpanDB.started_at.asc()).all()
            return [
                TraceSpan(
                    span_id=row.span_id,
                    run_id=row.run_id,
                    parent_span_id=row.parent_span_id,
                    session_id=row.session_id,
                    task_id=row.task_id,
                    agent_name=row.agent_name,
                    event_type=row.event_type,
                    status=row.status,
                    started_at=row.started_at.isoformat(),
                    ended_at=row.ended_at.isoformat() if row.ended_at else None,
                    latency_ms=row.latency_ms,
                    model_name=row.model_name,
                    estimated_input_tokens=int(row.estimated_input_tokens) if row.estimated_input_tokens is not None else None,
                    estimated_output_tokens=int(row.estimated_output_tokens) if row.estimated_output_tokens is not None else None,
                    estimated_cost_usd=row.estimated_cost_usd,
                    payload=json.loads(row.payload_json or "{}"),
                )
                for row in rows
            ]

    def update_span(self, run_id: str, span_id: str, **updates) -> None:
        with SessionLocal() as db:
            row = db.query(TraceSpanDB).filter_by(run_id=run_id, span_id=span_id).first()
            if not row:
                return

            for key, value in updates.items():
                if key in {"started_at", "ended_at"} and isinstance(value, str):
                    value = _parse_dt(value)
                elif key == "payload" and isinstance(value, dict):
                    key = "payload_json"
                    value = json.dumps(value)
                setattr(row, key, value)

            db.commit()

    def add_edge(self, edge: TraceEdge) -> None:
        with SessionLocal() as db:
            row = TraceEdgeDB(
                id=f"edge_{uuid.uuid4().hex[:12]}",
                run_id=edge.run_id,
                from_node=edge.from_node,
                to_node=edge.to_node,
                edge_type=edge.edge_type,
                reason=edge.reason,
            )
            db.add(row)
            db.commit()

    def get_edges(self, run_id: str) -> List[TraceEdge]:
        with SessionLocal() as db:
            rows = db.query(TraceEdgeDB).filter_by(run_id=run_id).all()
            return [
                TraceEdge(
                    run_id=row.run_id,
                    from_node=row.from_node,
                    to_node=row.to_node,
                    edge_type=row.edge_type,
                    reason=row.reason,
                )
                for row in rows
            ]