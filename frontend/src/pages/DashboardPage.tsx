import { useEffect, useState } from "react";
import { getCostMetrics, getLatencyMetrics } from "../api/client";
import CostCard from "../components/CostCard";
import LatencyChart from "../components/LatencyChart";

export default function DashboardPage() {
  const [cost, setCost] = useState<{ total_estimated_cost_usd: number; by_agent: Record<string, number> } | null>(null);
  const [latency, setLatency] = useState<Record<string, { avg_latency_ms: number; count: number }> | null>(null);

  useEffect(() => {
    const load = async () => {
      const costData = await getCostMetrics();
      const latencyData = await getLatencyMetrics();
      setCost(costData);
      setLatency(latencyData);
    };
    load();
  }, []);

  return (
    <div style={{ display: "grid", gap: 24 }}>
      <div>
        <h1 className="page-title">Observability Dashboard</h1>
        <p className="page-subtitle">
          Monitor cost, latency, and execution health across persisted runs.
        </p>
      </div>

      <div className="grid-2">
        {cost && (
          <CostCard
            total={cost.total_estimated_cost_usd}
            byAgent={cost.by_agent}
          />
        )}

        <div className="card" style={{ padding: 18 }}>
          <h3 className="card-title">Summary</h3>
          <div className="grid-3">
            <div style={{ background: "#1f2937", padding: 14, borderRadius: 14, border: "1px solid #374151" }}>
              <div className="muted">Tracked Agents</div>
              <div className="metric-value" style={{ fontSize: "1.5rem" }}>
                {latency ? Object.keys(latency).length : 0}
              </div>
            </div>
            <div style={{ background: "#1f2937", padding: 14, borderRadius: 14, border: "1px solid #374151" }}>
              <div className="muted">Cost Tracked</div>
              <div className="metric-value" style={{ fontSize: "1.5rem" }}>
                {cost ? "Yes" : "No"}
              </div>
            </div>
            <div style={{ background: "#1f2937", padding: 14, borderRadius: 14, border: "1px solid #374151" }}>
              <div className="muted">Latency Tracked</div>
              <div className="metric-value" style={{ fontSize: "1.5rem" }}>
                {latency ? "Yes" : "No"}
              </div>
            </div>
          </div>
        </div>
      </div>

      {latency && <LatencyChart metrics={latency} />}
    </div>
  );
}