import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getRun, getRunGraph } from "../api/client";
import TraceTimeline from "../components/TraceTimeline";
import ExecutionGraph from "../components/ExecutionGraph";
import type { TraceDetail } from "../types";

export default function TracePage() {
  const { runId } = useParams();
  const [trace, setTrace] = useState<TraceDetail | null>(null);
  const [graph, setGraph] = useState<any>(null);

  useEffect(() => {
    if (!runId) return;

    const load = async () => {
      const traceData = await getRun(runId);
      const graphData = await getRunGraph(runId);
      setTrace(traceData);
      setGraph(graphData);
    };

    load();
  }, [runId]);

  if (!trace) return <div className="muted">Loading trace...</div>;

  return (
    <div style={{ display: "grid", gap: 24 }}>
      <div>
        <h1 className="page-title">Trace Detail</h1>
        <p className="page-subtitle">
          Span-level execution, latency, cost, and handoff graph for a single run.
        </p>
      </div>

      <div className="grid-3">
        <div className="card" style={{ padding: 18 }}>
          <div className="muted">Run ID</div>
          <div style={{ fontWeight: 800, marginTop: 8 }}>{trace.run.run_id}</div>
        </div>

        <div className="card" style={{ padding: 18 }}>
          <div className="muted">Total Latency</div>
          <div className="metric-value" style={{ fontSize: "1.5rem", marginTop: 8 }}>
            {trace.run.total_latency_ms} ms
          </div>
        </div>

        <div className="card" style={{ padding: 18 }}>
          <div className="muted">Estimated Cost</div>
          <div className="metric-value" style={{ fontSize: "1.5rem", marginTop: 8 }}>
            ${trace.run.total_estimated_cost_usd}
          </div>
        </div>
      </div>

      <TraceTimeline spans={trace.spans} />
      {graph && <ExecutionGraph graph={graph} />}
    </div>
  );
}