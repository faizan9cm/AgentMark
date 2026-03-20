import type { StreamEvent } from "../types";

function colorForEvent(eventType: string) {
  if (eventType.includes("error")) return "#f87171";
  if (eventType.includes("handoff")) return "#fbbf24";
  if (eventType.includes("complete")) return "#22c55e";
  return "#60a5fa";
}

export default function EventStream({ events }: { events: StreamEvent[] }) {
  return (
    <div className="card" style={{ padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h3 className="card-title" style={{ margin: 0 }}>
          Live Event Stream
        </h3>
        <span className="badge">{events.length} events</span>
      </div>

      <div style={{ maxHeight: 620, overflowY: "auto", display: "grid", gap: 12 }}>
        {events.length === 0 ? (
          <div
            style={{
              padding: 18,
              borderRadius: 14,
              border: "1px dashed #334155",
              background: "#0b1222",
              color: "#94a3b8",
            }}
          >
            No live events yet.
          </div>
        ) : (
          events.map((event, idx) => (
            <div
              key={`${event.event_type}-${idx}`}
              style={{
                background: "#1f2937",
                padding: 14,
                borderRadius: 14,
                border: "1px solid #374151",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                <div style={{ fontWeight: 800, color: colorForEvent(event.event_type) }}>{event.event_type}</div>
                <div className="muted" style={{ fontSize: 12 }}>
                  {event.agent_name || "-"}
                </div>
              </div>

              <div style={{ fontSize: 13, color: "#9ca3af", marginTop: 6 }}>
                task: {event.task_id || "-"} | session: {event.session_id || "-"}
              </div>

              <pre className="pre-block" style={{ marginTop: 10 }}>
                {JSON.stringify(event.payload, null, 2)}
              </pre>
            </div>
          ))
        )}
      </div>
    </div>
  );
}