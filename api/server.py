import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from api.websocket_manager import WebSocketManager
from starlette.concurrency import run_in_threadpool

app = FastAPI(title="AgentMark Transport Layer")
app.state.main_loop = None

@app.on_event("startup")
async def startup_event():
    app.state.main_loop = asyncio.get_running_loop()

runtime = AgentRuntime()
ws_manager = WebSocketManager()


def runtime_event_callback(event: dict):
    session_id = event.get("session_id")
    if not session_id:
        return

    loop = app.state.main_loop
    if loop is None:
        return

    loop.call_soon_threadsafe(
        asyncio.create_task,
        ws_manager.broadcast_to_session(session_id, event)
    )


runtime.set_event_callback(runtime_event_callback)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/rpc/methods")
def list_rpc_methods():
    return {"methods": runtime.list_rpc_methods()}


@app.post("/rpc")
def handle_rpc(request_data: dict):
    return runtime.handle_json_rpc(request_data)


@app.post("/tasks/execute")
async def execute_task(task_data: dict):
    task = AgentTask(**task_data)
    result = await run_in_threadpool(runtime.execute_task, task)
    return result.model_dump()


@app.post("/tasks/execute-chain")
async def execute_task_chain(task_data: dict):
    task = AgentTask(**task_data)
    results = await run_in_threadpool(runtime.execute_task_chain, task)
    return {"results": [result.model_dump() for result in results]}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await ws_manager.connect(session_id, websocket)
    
    try:
        await websocket.send_json({
            "event_type": "connection_open",
            "session_id": session_id,
            "task_id": None,
            "agent_name": "transport",
            "payload": {"message": "WebSocket connected"},
        })

        while True:
            incoming = await websocket.receive_json()
            
            if incoming.get("type") == "rpc":
                response = runtime.handle_json_rpc(incoming["data"])
                await websocket.send_json({
                    "event_type": "rpc_response",
                    "session_id": session_id,
                    "task_id": None,
                    "agent_name": "transport",
                    "payload": response,
                })

            elif incoming.get("type") == "execute_chain":
                try:
                    task = AgentTask(**incoming["data"])

                    results = await run_in_threadpool(runtime.execute_task_chain, task)

                    await websocket.send_json({
                        "event_type": "chain_complete",
                        "session_id": session_id,
                        "task_id": task.task_id,
                        "agent_name": "runtime",
                        "payload": {"results": [r.model_dump() for r in results]},
                    })
                except Exception as e:
                    await websocket.send_json({
                        "event_type": "transport_error",
                        "session_id": session_id,
                        "task_id": incoming.get("data", {}).get("task_id"),
                        "agent_name": "transport",
                        "payload": {"message": str(e)},
                    })

            else:
                await websocket.send_json({
                    "event_type": "transport_error",
                    "session_id": session_id,
                    "task_id": None,
                    "agent_name": "transport",
                    "payload": {"message": "Unsupported WebSocket message type"},
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)