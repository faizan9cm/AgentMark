from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from orchestrator.event_types import NEW_LEAD


def run_memory_aware_lead_flow():
    runtime = AgentRuntime()

    first_task = AgentTask(
        task_id="lead_chain_101",
        task_type=NEW_LEAD,
        payload={
            "lead_id": "lead_faizan_memory",
            "lead_name": "Faizan",
            "message": "Hi, I am interested in enterprise pricing and would like a demo for my team.",
            "source": "website"
        },
        context={},
        session_id="session_faizan_memory",
        lead_id="lead_faizan_memory",
    )

    first_results = runtime.execute_task_chain(first_task)

    print("\n--- First Lead Flow ---")
    for idx, result in enumerate(first_results, start=1):
        print(f"\nStep {idx}")
        print(result.model_dump())

    second_task = AgentTask(
        task_id="lead_chain_102",
        task_type=NEW_LEAD,
        payload={
            "lead_id": "lead_faizan_memory",
            "lead_name": "Faizan",
            "message": "Following up — we are mainly evaluating pricing, onboarding, and support options for a 20-person team.",
            "source": "website"
        },
        context={},
        session_id="session_faizan_memory",
        lead_id="lead_faizan_memory",
    )

    second_results = runtime.execute_task_chain(second_task)

    print("\n--- Second Lead Flow (Memory-Aware) ---")
    for idx, result in enumerate(second_results, start=1):
        print(f"\nStep {idx}")
        print(result.model_dump())

    print("\n--- Long-Term Memory ---")
    ltm = runtime.memory.long_term.get("lead_faizan_memory")
    print(ltm.model_dump() if ltm else None)

    print("\n--- Short-Term Memory ---")
    stm = runtime.memory.short_term.get("session_faizan_memory")
    print(stm.model_dump() if stm else None)


if __name__ == "__main__":
    run_memory_aware_lead_flow()