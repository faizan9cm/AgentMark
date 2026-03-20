import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";

const nav = [
  { to: "/", label: "Chat" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/runs", label: "Runs" },
];

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation();

  return (
    <div style={{ minHeight: "100vh", display: "grid", gridTemplateColumns: "260px 1fr" }}>
      <aside
        style={{
          borderRight: "1px solid #253046",
          background: "rgba(8, 13, 26, 0.92)",
          backdropFilter: "blur(10px)",
          padding: 24,
        }}
      >
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.03em" }}>AgentMark</div>
          <div className="muted" style={{ marginTop: 6 }}>
            Multi-agent observability console
          </div>
        </div>

        <div style={{ display: "grid", gap: 10 }}>
          {nav.map((item) => {
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                style={{
                  textDecoration: "none",
                  padding: "12px 14px",
                  borderRadius: 12,
                  border: `1px solid ${active ? "rgba(96,165,250,0.4)" : "#253046"}`,
                  background: active ? "rgba(37,99,235,0.18)" : "#111827",
                  color: active ? "#dbeafe" : "#cbd5e1",
                  fontWeight: 700,
                }}
              >
                {item.label}
              </Link>
            );
          })}
        </div>

        <div
          className="card"
          style={{
            marginTop: 24,
            padding: 14,
            borderRadius: 14,
          }}
        >
          <div className="badge">UI Phase 16</div>
          <div style={{ marginTop: 10, fontWeight: 700 }}>Production-style control panel</div>
          <div className="muted" style={{ fontSize: 13, marginTop: 6 }}>
            Chat, traces, latency, cost, and run history in one interface.
          </div>
        </div>
      </aside>

      <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
        <header
          style={{
            height: 72,
            borderBottom: "1px solid #253046",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 24px",
            background: "rgba(11, 16, 32, 0.72)",
            backdropFilter: "blur(8px)",
          }}
        >
          <div>
            <div style={{ fontSize: 15, fontWeight: 700 }}>Agent Operations Console</div>
            <div className="muted" style={{ fontSize: 13 }}>
              Real-time orchestration and observability
            </div>
          </div>

          <div className="badge">Backend Connected</div>
        </header>

        <main style={{ padding: 24, minWidth: 0 }}>{children}</main>
      </div>
    </div>
  );
}