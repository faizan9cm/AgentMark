import uuid
from datetime import datetime, timezone
from observability.trace_models import TraceRun, TraceSpan, TraceEdge
from observability.trace_store import TraceStore


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Tracer:
    def __init__(self, store: TraceStore):
        self.store = store

    def start_run(self, entrypoint: str, session_id: str | None = None, lead_id: str | None = None) -> str:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        run = TraceRun(
            run_id=run_id,
            session_id=session_id,
            lead_id=lead_id,
            entrypoint=entrypoint,
            started_at=utc_now_iso(),
        )
        self.store.add_run(run)
        return run_id

    def finish_run(self, run_id: str, status: str = "success", total_latency_ms: float | None = None) -> None:
        run = self.store.get_run(run_id)
        if not run:
            return

        spans = self.store.get_spans(run_id)
        total_cost = round(sum(span.estimated_cost_usd for span in spans), 8)

        self.store.update_run(
            run_id,
            status=status,
            ended_at=utc_now_iso(),
            total_latency_ms=total_latency_ms,
            total_estimated_cost_usd=total_cost,
        )

    def start_span(
        self,
        run_id: str,
        event_type: str,
        session_id: str | None = None,
        task_id: str | None = None,
        agent_name: str | None = None,
        parent_span_id: str | None = None,
        payload: dict | None = None,
    ) -> str:
        span_id = f"span_{uuid.uuid4().hex[:12]}"
        span = TraceSpan(
            span_id=span_id,
            run_id=run_id,
            parent_span_id=parent_span_id,
            session_id=session_id,
            task_id=task_id,
            agent_name=agent_name,
            event_type=event_type,
            started_at=utc_now_iso(),
            payload=payload or {},
        )
        self.store.add_span(span)
        return span_id

    def finish_span(
        self,
        run_id: str,
        span_id: str,
        status: str = "success",
        latency_ms: float | None = None,
        model_name: str | None = None,
        estimated_input_tokens: int | None = None,
        estimated_output_tokens: int | None = None,
        estimated_cost_usd: float = 0.0,
        payload_update: dict | None = None,
    ) -> None:
        spans = self.store.get_spans(run_id)
        updated_spans = []

        for span in spans:
            if span.span_id == span_id:
                new_payload = dict(span.payload)
                if payload_update:
                    new_payload.update(payload_update)

                updated_span = span.model_copy(update={
                    "status": status,
                    "ended_at": utc_now_iso(),
                    "latency_ms": latency_ms,
                    "model_name": model_name,
                    "estimated_input_tokens": estimated_input_tokens,
                    "estimated_output_tokens": estimated_output_tokens,
                    "estimated_cost_usd": estimated_cost_usd,
                    "payload": new_payload,
                })
                updated_spans.append(updated_span)
            else:
                updated_spans.append(span)

        self.store.spans[run_id] = updated_spans

    def add_edge(self, run_id: str, from_node: str, to_node: str, edge_type: str, reason: str | None = None) -> None:
        edge = TraceEdge(
            run_id=run_id,
            from_node=from_node,
            to_node=to_node,
            edge_type=edge_type,
            reason=reason,
        )
        self.store.add_edge(edge)