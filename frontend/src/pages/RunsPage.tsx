import { useEffect, useState } from "react";
import { getRuns } from "../api/client";
import type { TraceRun } from "../types";
import { Link } from "react-router-dom";

export default function RunsPage() {
  const [runs, setRuns] = useState<TraceRun[]>([]);

  useEffect(() => {
    const load = async () => {
      const data = await getRuns();
      setRuns(data.runs || []);
    };
    load();
  }, []);

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div>
        <h1 className="page-title">Trace Runs</h1>
        <p className="page-subtitle">
          Persisted execution history for the multi-agent runtime.
        </p>
      </div>

      <div className="card" style={{ padding: 18 }}>
        <div style={{ display: "grid", gap: 12 }}>
          {runs.length === 0 ? (
            <div className="muted">No trace runs found yet.</div>
          ) : (
            runs.map((run) => (
              <Link
                key={run.run_id}
                to={`/trace/${run.run_id}`}
                style={{
                  display: "block",
                  textDecoration: "none",
                  color: "#e5e7eb",
                  background: "#1f2937",
                  padding: 18,
                  borderRadius: 16,
                  border: "1px solid #374151",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                  <div style={{ fontWeight: 800 }}>{run.run_id}</div>
                  <span className="badge">{run.status}</span>
                </div>

                <div style={{ marginTop: 10, display: "grid", gap: 4, fontSize: 14, color: "#cbd5e1" }}>
                  <div>session: {run.session_id || "-"}</div>
                  <div>lead: {run.lead_id || "-"}</div>
                  <div>latency: {run.total_latency_ms ?? 0} ms</div>
                  <div>cost: ${run.total_estimated_cost_usd}</div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}