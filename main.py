from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from orchestrator.event_types import NEW_LEAD, CAMPAIGN_REVIEW


def run_lead_chain():
    runtime = AgentRuntime()

    task = AgentTask(
        task_id="lead_chain_001",
        task_type=NEW_LEAD,
        payload={
            "lead_name": "Faizan",
            "message": "Hi, I am interested in enterprise pricing and would like a demo for my team.",
            "source": "website"
        },
        context={}
    )

    results = runtime.execute_task_chain(task)

    print("\n--- Lead Chain Execution ---")
    for idx, result in enumerate(results, start=1):
        print(f"\nStep {idx}")
        print(result.model_dump())


def run_campaign_chain():
    runtime = AgentRuntime()

    task = AgentTask(
        task_id="campaign_001",
        task_type=CAMPAIGN_REVIEW,
        payload={
            "channel": "LinkedIn Ads",
            "ctr": 0.011,
            "conversion_rate": 0.018
        },
        context={}
    )

    results = runtime.execute_task_chain(task)

    print("\n--- Campaign Chain Execution ---")
    for idx, result in enumerate(results, start=1):
        print(f"\nStep {idx}")
        print(result.model_dump())


if __name__ == "__main__":
    run_lead_chain()
    run_campaign_chain()