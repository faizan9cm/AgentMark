from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from orchestrator.event_types import NEW_LEAD


def test_json_rpc_lead_triage():
    runtime = AgentRuntime()

    request = {
        "jsonrpc": "2.0",
        "id": "rpc_001",
        "method": "lead_triage.run",
        "params": {
            "task_id": "rpc_task_001",
            "task_type": "new_lead",
            "payload": {
                "lead_id": "lead_rpc_faizan",
                "lead_name": "Faizan",
                "message": "Hi, I want enterprise pricing and a demo for my team.",
                "source": "website"
            },
            "context": {},
            "session_id": "session_rpc_faizan",
            "lead_id": "lead_rpc_faizan"
        }
    }

    response = runtime.handle_json_rpc(request)

    print("\n--- JSON-RPC Response ---")
    print(response)


def test_json_rpc_invalid_method():
    runtime = AgentRuntime()

    request = {
        "jsonrpc": "2.0",
        "id": "rpc_002",
        "method": "unknown.method",
        "params": {}
    }

    response = runtime.handle_json_rpc(request)

    print("\n--- JSON-RPC Invalid Method Response ---")
    print(response)


def test_handoff_chain():
    runtime = AgentRuntime()

    task = AgentTask(
        task_id="handoff_task_001",
        task_type=NEW_LEAD,
        payload={
            "lead_id": "lead_handoff_faizan",
            "lead_name": "Faizan",
            "message": "We want enterprise pricing, onboarding details, and a demo for our team.",
            "source": "website",
        },
        context={},
        session_id="session_handoff_faizan",
        lead_id="lead_handoff_faizan",
    )

    results = runtime.execute_task_chain(task)

    print("\n--- Handoff Chain Results ---")
    for idx, result in enumerate(results, start=1):
        print(f"\nStep {idx}")
        print(result.model_dump())

    print("\n--- Short-Term Memory ---")
    stm = runtime.memory.short_term.get("session_handoff_faizan")
    print(stm.model_dump() if stm else None)


if __name__ == "__main__":
    test_json_rpc_lead_triage()
    test_json_rpc_invalid_method()
    test_handoff_chain()