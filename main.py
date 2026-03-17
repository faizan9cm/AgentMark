from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from orchestrator.event_types import NEW_LEAD


def run_consolidation_demo():
    runtime = AgentRuntime()

    task1 = AgentTask(
        task_id="lead_cons_001",
        task_type=NEW_LEAD,
        payload={
            "lead_id": "lead_cons_faizan",
            "lead_name": "Faizan",
            "message": "Hi, I want enterprise pricing and a demo for my 20-person team.",
            "source": "website"
        },
        context={},
        session_id="session_cons_faizan",
        lead_id="lead_cons_faizan",
    )

    task2 = AgentTask(
        task_id="lead_cons_002",
        task_type=NEW_LEAD,
        payload={
            "lead_id": "lead_cons_faizan",
            "lead_name": "Faizan",
            "message": "Following up — we are also evaluating onboarding and support options.",
            "source": "website"
        },
        context={},
        session_id="session_cons_faizan",
        lead_id="lead_cons_faizan",
    )

    runtime.execute_task_chain(task1)
    runtime.execute_task_chain(task2)

    print("\n--- Long-Term Memory ---")
    ltm = runtime.memory.long_term.get("lead_cons_faizan")
    print(ltm.model_dump() if ltm else None)

    print("\n--- Short-Term Memory ---")
    stm = runtime.memory.short_term.get("session_cons_faizan")
    print(stm.model_dump() if stm else None)

    print("\n--- Episodic Memory ---")
    for episode in runtime.memory.episodic.list_all():
        print(episode.model_dump())


if __name__ == "__main__":
    run_consolidation_demo()