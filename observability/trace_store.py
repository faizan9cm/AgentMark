from typing import Dict, List, Optional
from observability.trace_models import TraceRun, TraceSpan, TraceEdge


class TraceStore:
    def __init__(self):
        self.runs: Dict[str, TraceRun] = {}
        self.spans: Dict[str, List[TraceSpan]] = {}
        self.edges: Dict[str, List[TraceEdge]] = {}

    def add_run(self, run: TraceRun) -> None:
        self.runs[run.run_id] = run
        self.spans.setdefault(run.run_id, [])
        self.edges.setdefault(run.run_id, [])

    def update_run(self, run_id: str, **updates) -> Optional[TraceRun]:
        run = self.runs.get(run_id)
        if not run:
            return None

        updated = run.model_copy(update=updates)
        self.runs[run_id] = updated
        return updated

    def get_run(self, run_id: str) -> Optional[TraceRun]:
        return self.runs.get(run_id)

    def list_runs(self) -> List[TraceRun]:
        return list(self.runs.values())

    def add_span(self, span: TraceSpan) -> None:
        self.spans.setdefault(span.run_id, []).append(span)

    def get_spans(self, run_id: str) -> List[TraceSpan]:
        return self.spans.get(run_id, [])

    def add_edge(self, edge: TraceEdge) -> None:
        self.edges.setdefault(edge.run_id, []).append(edge)

    def get_edges(self, run_id: str) -> List[TraceEdge]:
        return self.edges.get(run_id, [])