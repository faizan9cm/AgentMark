from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from orchestrator.event_types import NEW_LEAD


def run_reflection_demo():
    runtime = AgentRuntime()

    task = AgentTask(
        task_id="lead_reflect_001",
        task_type=NEW_LEAD,
        payload={
            "lead_id": "lead_reflect_faizan",
            "lead_name": "Faizan",
            "message": "Hi, I want enterprise pricing, onboarding details, and a demo for my 20-person team.",
            "source": "website"
        },
        context={},
        session_id="session_reflect_faizan",
        lead_id="lead_reflect_faizan",
    )

    results = runtime.execute_task_chain(task)

    print("\n--- Execution Results ---")
    for idx, result in enumerate(results, start=1):
        print(f"\nStep {idx}")
        print(result.model_dump())

    print("\n--- Short-Term Memory ---")
    stm = runtime.memory.short_term.get("session_reflect_faizan")
    print(stm.model_dump() if stm else None)

    print("\n--- Episodic Memory ---")
    for episode in runtime.memory.episodic.list_all():
        print(episode.model_dump())


if __name__ == "__main__":
    run_reflection_demo()