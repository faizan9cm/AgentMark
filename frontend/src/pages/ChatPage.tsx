import { useMemo, useRef, useState } from "react";
import { interact } from "../api/client";
import EventStream from "../components/EventStream";
import type { InteractionResponse, StreamEvent } from "../types";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [sessionId, setSessionId] = useState<string>("");
  const [result, setResult] = useState<InteractionResponse | null>(null);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  const currentSessionId = useMemo(() => sessionId || "", [sessionId]);

  const connectSocket = (sid: string) => {
    if (wsRef.current) wsRef.current.close();

    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${sid}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as StreamEvent;
      setEvents((prev) => [...prev, data]);
    };

    ws.onerror = () => {
      setError("WebSocket connection error");
    };

    wsRef.current = ws;
  };

  const handleSend = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setError("");
    setEvents([]);
    setResult(null);

    const sid = currentSessionId || `session_ui_${Math.random().toString(16).slice(2, 10)}`;
    setSessionId(sid);
    connectSocket(sid);

    try {
      const response = await interact({
        message,
        session_id: sid,
        user_name: "Faizan",
        metadata: { source: "ui_web_app" },
      });
      setResult(response);
    } catch (err: any) {
      setError(err?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid-2">
      <div className="card" style={{ padding: 22 }}>
        <div style={{ marginBottom: 18 }}>
          <h1 className="page-title">Chat Control Panel</h1>
          <p className="page-subtitle">
            Send natural language instructions into the agent system and watch execution live.
          </p>
        </div>

        <div style={{ display: "grid", gap: 14 }}>
          <div>
            <label className="label">Session ID</label>
            <input
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              placeholder="auto-generated if empty"
              className="field"
            />
          </div>

          <div>
            <label className="label">Message</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={8}
              className="field"
              placeholder="We need enterprise pricing, onboarding support, and a demo for our team."
            />
          </div>

          <div style={{ display: "flex", gap: 12 }}>
            <button onClick={handleSend} disabled={loading} className="btn btn-primary">
              {loading ? "Running..." : "Send to Agent System"}
            </button>
            <button
              onClick={() => {
                setMessage("We need enterprise pricing, onboarding support, and a demo for our team.");
              }}
              className="btn btn-secondary"
            >
              Fill Example
            </button>
          </div>
        </div>

        {error && (
          <div
            style={{
              marginTop: 14,
              color: "#fecaca",
              background: "rgba(127,29,29,0.25)",
              border: "1px solid rgba(248,113,113,0.3)",
              padding: 12,
              borderRadius: 12,
            }}
          >
            {error}
          </div>
        )}

        {result && (
          <div
            style={{
              marginTop: 22,
              background: "#1f2937",
              padding: 18,
              borderRadius: 16,
              border: "1px solid #374151",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
              <h3 className="card-title" style={{ margin: 0 }}>
                Interaction Result
              </h3>
              <span className="badge">{result.detected_task_type}</span>
            </div>

            <div style={{ marginTop: 12, display: "grid", gap: 6, fontSize: 14 }}>
              <div><strong>session_id:</strong> {result.session_id}</div>
              <div><strong>lead_id:</strong> {result.lead_id || "-"}</div>
              <div><strong>trace_run_id:</strong> {result.trace_run_id || "-"}</div>
            </div>

            <pre className="pre-block">{JSON.stringify(result.runtime_results, null, 2)}</pre>
          </div>
        )}
      </div>

      <EventStream events={events} />
    </div>
  );
}