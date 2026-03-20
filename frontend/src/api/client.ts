import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 20000,
});

export async function interact(payload: {
  message: string;
  session_id?: string;
  lead_id?: string;
  user_name?: string;
  metadata?: Record<string, unknown>;
}) {
  const res = await api.post("/interact", payload);
  return res.data;
}

export async function getRuns() {
  const res = await api.get("/traces");
  return res.data;
}

export async function getRun(runId: string) {
  const res = await api.get(`/traces/${runId}`);
  return res.data;
}

export async function getRunGraph(runId: string) {
  const res = await api.get(`/traces/${runId}/graph`);
  return res.data;
}

export async function getLatencyMetrics() {
  const res = await api.get("/metrics/latency");
  return res.data;
}

export async function getCostMetrics() {
  const res = await api.get("/metrics/cost");
  return res.data;
}