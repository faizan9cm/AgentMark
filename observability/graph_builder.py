from observability.trace_models import TraceGraph
from observability.trace_store import TraceStore


class GraphBuilder:
    def __init__(self, store: TraceStore):
        self.store = store

    def build_run_graph(self, run_id: str) -> dict:
        spans = self.store.get_spans(run_id)
        edges = self.store.get_edges(run_id)

        nodes = []
        for span in spans:
            nodes.append({
                "id": span.span_id,
                "label": span.agent_name or span.event_type,
                "event_type": span.event_type,
                "agent_name": span.agent_name,
                "task_id": span.task_id,
                "status": span.status,
                "latency_ms": span.latency_ms,
                "estimated_cost_usd": span.estimated_cost_usd,
            })

        graph = TraceGraph(
            run_id=run_id,
            nodes=nodes,
            edges=[edge.model_dump() for edge in edges],
        )
        return graph.model_dump()