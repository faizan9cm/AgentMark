from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from orchestrator.event_types import NEW_LEAD


def run_lead_chain():
    runtime = AgentRuntime()

    task = AgentTask(
        task_id="task_chain_001",
        task_type=NEW_LEAD,
        payload={
            "lead_name": "Faizan",
            "message": "I want enterprise pricing and a demo",
            "source": "website"
        },
        context={}
    )

    results = runtime.execute_task_chain(task)

    print("\n--- Chained Execution ---")
    for idx, result in enumerate(results, start=1):
        print(f"\nStep {idx}")
        print(result.model_dump())


if __name__ == "__main__":
    run_lead_chain()