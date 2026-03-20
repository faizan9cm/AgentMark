export type RuntimeResult = {
    task_id: string;
    agent_name: string;
    status: string;
    output: Record<string, unknown>;
    next_action: string | null;
};

export type InteractionResponse = {
    session_id: string;
    lead_id?: string;
    detected_task_type: string;
    runtime_results: RuntimeResult[];
    trace_run_id?: string;
};

export type StreamEvent = {
    event_type: string;
    session_id?: string | null;
    task_id?: string | null;
    agent_name?: string | null;
    payload: Record<string, unknown>;
};

export type TraceRun = {
    run_id: string;
    session_id?: string | null;
    lead_id?: string | null;
    entrypoint: string;
    status: string;
    started_at: string;
    ended_at?: string | null;
    total_latency_ms?: number | null;
    total_estimated_cost_usd: number;
};

export type TraceSpan = {
    span_id: string;
    run_id: string;
    task_id?: string | null;
    agent_name?: string | null;
    event_type: string;
    status: string;
    started_at: string;
    ended_at?: string | null;
    latency_ms?: number | null;
    model_name?: string | null;
    estimated_input_tokens?: number | null;
    estimated_output_tokens?: number | null;
    estimated_cost_usd: number;
    payload: Record<string, unknown>;
};

export type TraceEdge = {
    run_id: string;
    from_node: string;
    to_node: string;
    edge_type: string;
    reason?: string | null;
};

export type TraceDetail = {
    run: TraceRun;
    spans: TraceSpan[];
    edges: TraceEdge[];
};