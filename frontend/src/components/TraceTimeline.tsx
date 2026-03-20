import type { TraceSpan } from "../types";

export default function TraceTimeline({ spans }: { spans: TraceSpan[] }) {
  return (
    <div className="card" style={{ padding: 18 }}>
      <h3 className="card-title">Trace Timeline</h3>

      <div style={{ display: "grid", gap: 14 }}>
        {spans.map((span) => (
          <div
            key={span.span_id}
            style={{
              background: "#1f2937",
              padding: 16,
              borderRadius: 16,
              border: "1px solid #374151",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <div style={{ fontWeight: 800 }}>{span.agent_name}</div>
              <span className="badge">{span.status}</span>
            </div>

            <div style={{ marginTop: 10, fontSize: 14, color: "#cbd5e1", display: "grid", gap: 4 }}>
              <div>task: {span.task_id}</div>
              <div>latency: {span.latency_ms} ms</div>
              <div>model: {span.model_name}</div>
              <div>
                tokens: in {span.estimated_input_tokens} / out {span.estimated_output_tokens}
              </div>
              <div>cost: ${span.estimated_cost_usd}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}