export default function CostCard({
  total,
  byAgent,
}: {
  total: number;
  byAgent: Record<string, number>;
}) {
  return (
    <div className="card" style={{ padding: 18 }}>
      <h3 className="card-title">Estimated Cost</h3>
      <div className="metric-value">${total.toFixed(8)}</div>
      <div className="muted" style={{ marginTop: 6, marginBottom: 16 }}>
        Aggregate estimated model cost across persisted trace runs
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        {Object.entries(byAgent).length === 0 ? (
          <div className="muted">No cost data yet.</div>
        ) : (
          Object.entries(byAgent).map(([agent, cost]) => (
            <div
              key={agent}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                background: "#1f2937",
                padding: "12px 14px",
                borderRadius: 12,
                border: "1px solid #374151",
              }}
            >
              <span style={{ fontWeight: 600 }}>{agent}</span>
              <span style={{ fontWeight: 800 }}>${cost.toFixed(8)}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}