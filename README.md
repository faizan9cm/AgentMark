# 🚀 AgentMark — Autonomous Multi-Agent Marketing System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Redis](https://img.shields.io/badge/Redis-Memory-red)
![Postgres](https://img.shields.io/badge/Postgres-Storage-blue)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph-orange)
![Status](https://img.shields.io/badge/Status-Complete-success)

---

## 🧠 Overview

AgentMark is a **production-style multi-agent AI system** built to simulate real-world autonomous marketing workflows.

Unlike typical LLM projects, this system demonstrates:

* 🧩 Multi-agent orchestration (manager + worker agents)
* 🧠 Adaptive multi-layer memory (short-term, long-term, episodic, semantic)
* 🔗 JSON-RPC 2.0 inter-agent communication
* 🌐 HTTP + WebSocket transport layers
* 🧱 MCP-style structured data access
* 🔁 Self-reflection and learning loops
* 📊 Benchmark & evaluation pipeline

> This project is designed to resemble how **real agent systems are engineered**, not just prompt-based apps.

---

## 🎯 Why This Project Matters

Most AI projects:

* use a single agent
* lack memory
* lack evaluation
* lack real system design

AgentMark demonstrates:

✔ Agent collaboration
✔ Persistent learning
✔ Real-time execution
✔ Structured protocols
✔ Measurable performance

---

## 🏗️ System Architecture

See full diagram:

📄 `diagrams/system_architecture.md`

---

## 🤖 Agent Hierarchy

### 🧭 Strategy Agent

* handles escalation
* makes high-level decisions

### 🔍 Lead Triage Agent

* classifies leads (Hot / Cold / Inquiry)
* assigns priority

### 💬 Engagement Agent

* generates personalized responses
* schedules demos

### 📈 Campaign Optimizer Agent

* analyzes performance
* suggests improvements or escalation

---

## 🔗 Communication Layer

### Protocol

* JSON-RPC 2.0 for structured agent execution

### Transport

* HTTP → request/response execution
* WebSocket → real-time event streaming

### Handoff System

Each agent handoff preserves:

* session_id
* lead_id
* compact memory context
* previous outputs
* reasoning for transition

---

## 🧠 Memory Architecture

| Memory Type | Storage  | Purpose                              |
| ----------- | -------- | ------------------------------------ |
| Short-Term  | Redis    | session context, live events         |
| Long-Term   | Postgres | lead history, summaries              |
| Episodic    | Postgres | reusable lessons                     |
| Semantic    | Neo4j    | relationships & structured knowledge |

### Key Capabilities

* selective retrieval
* deduplication
* summarization
* consolidation

---

## 📊 Observability

AgentMark includes a full observability system:

🔍 Trace Runs

Each interaction generates a trace run

⚡ Latency Tracking

Per-agent execution latency

💰 Cost Estimation

Token-based cost tracking per agent

🔗 Execution Graph

Visual graph of agent flow

Example:

{
  "run_id": "run_xyz",
  "nodes": ["lead_triage_agent", "engagement_agent"],
  "edges": ["handoff"]
}


---

## 💬 Frontend (React UI)

AgentMark includes a production-style UI dashboard

- Features

* Chat-based interaction
* Live event stream (WebSocket)

- Dashboard:

* cost metrics
* latency metrics


- Runs page:

* history of executions


- Trace page:

* execution timeline
* graph visualization

---

## 📡 Real-Time Execution (WebSocket)

Example event stream:

```json
{
  "event_type": "agent_result",
  "agent_name": "lead_triage_agent",
  "output": {
    "category": "Hot Lead",
    "priority": "High"
  }
}
```

Run:

```bash
python -m evaluation.run_benchmarks
```

---

## 📈 Benchmark Results

| Task               |               Metric |                         Score |
| ------------------ | -------------------: | ----------------------------: |
| Lead Triage        |    Category Accuracy |                          1.00 |
| Lead Triage        |    Priority Accuracy |                          1.00 |
| Lead Triage        | Next Action Accuracy |                          1.00 |
| Campaign Optimizer |  Escalation Accuracy |                          1.00 |
| Engagement         |               Status | Skipped (rate-limit safe run) |

> Note: dataset is intentionally small for validation under free-tier limits.

---


## 🧱 MCP Layer (Model Context Protocol)

AgentMark includes an MCP-style layer for structured data access.

### Resources

* lead history
* episodic lessons
* semantic relations
* campaign analytics

### Tools

* update lead preferences

Agents consume MCP data instead of directly querying databases.

---

## 🖥️ Running the Full System

### 1. Start storage

```bash
docker compose -f deployment/docker-compose.storage.yml up -d
```

### 2. Activate env

```bash
venv\Scripts\activate
```

### 3. Start server

```bash
uvicorn api.server:app --reload
```

### 4. Start UI

```bash
cd frontend
npm install
npm run dev
```
- Frontend runs on:
```
http://localhost:5173
```

### 5. Test WebSocket (Optional)

```bash
python ws_test.py
```

### 6. Run benchmarks (Optional)

```bash
python -m evaluation.run_benchmarks
```

---

## 🔌 API

### Core

* `GET /health`
* `POST /tasks/execute`
* `POST /tasks/execute-chain`

### JSON-RPC

* `GET /rpc/methods`
* `POST /rpc`

### WebSocket

* `/ws/{session_id}`

### MCP

* `GET /mcp/resources`
* `GET /mcp/tools`
* `POST /mcp`

---

## 🔁 Example Workflow

1. Lead enters system
2. Triage agent classifies
3. Engagement agent responds
4. Memory updates across layers
5. Campaign optimizer evaluates
6. Real-time events streamed

---

## 📂 Repository Structure

```text
AgentMark/
├── agents/
├── api/
├── communication/
├── deployment/
├── diagrams/
├── evaluation/
├── experiments/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── index.html
├── interaction/
├── managers/
├── mcp_layer/
├── memory/
├── observability/
├── orchestrator/
├── reflection/
├── main.py
├── ws_test.py
└── README.md
```

---

## 🧪 Experiments

* memory vs no memory
* reflection vs no reflection
* multi-agent chain behavior

See `/experiments`

---

## 🚧 Future Improvements

* CRM integrations
* live dashboard UI
* embedding-based retrieval
* distributed agent workers
* richer semantic graph
* full MCP interoperability

---

## 👤 Author

**Faizan Habib**

---

## 📌 Final Note

This project focuses on **system design depth** rather than surface-level features.

It demonstrates how autonomous AI systems can be built with:

* structure
* memory
* communication protocols
* evaluation

---

## ⭐ If you found this useful

Give it a star — or better, try extending it.
