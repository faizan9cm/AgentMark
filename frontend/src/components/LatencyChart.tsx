import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function LatencyChart({
  metrics,
}: {
  metrics: Record<string, { avg_latency_ms: number; count: number }>;
}) {
  const data = Object.entries(metrics).map(([agent, value]) => ({
    agent,
    avg_latency_ms: value.avg_latency_ms,
    count: value.count,
  }));

  return (
    <div className="card" style={{ padding: 18, height: 380 }}>
      <h3 className="card-title">Latency per Agent</h3>
      <div className="muted" style={{ marginBottom: 12 }}>
        Average agent execution latency from persisted trace spans
      </div>

      <ResponsiveContainer width="100%" height="88%">
        <BarChart data={data}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="agent" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip
            contentStyle={{
              background: "#111827",
              border: "1px solid #374151",
              borderRadius: 12,
              color: "#e5e7eb",
            }}
          />
          <Bar dataKey="avg_latency_ms" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}