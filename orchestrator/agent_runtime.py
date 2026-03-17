from agents.lead_triage_agent import LeadTriageAgent
from agents.engagement_agent import EngagementAgent
from agents.campaign_optimizer_agent import CampaignOptimizerAgent
from managers.strategy_agent import StrategyAgent
from orchestrator.contracts import AgentTask, AgentResult
from orchestrator.event_types import (
    NEW_LEAD,
    QUALIFIED_LEAD,
    ENGAGEMENT_REQUEST,
    CAMPAIGN_REVIEW,
    STRATEGY_REVIEW,
)
from memory.memory_manager import MemoryManager
from memory.schemas import EpisodicMemoryRecord
import json
from memory.retriever import MemoryRetriever
from reflection.reflection_engine import ReflectionEngine


class AgentRuntime:
    def __init__(self):
        self.memory = MemoryManager()
        self.agents = {
            "lead_triage_agent": LeadTriageAgent(),
            "engagement_agent": EngagementAgent(),
            "campaign_optimizer_agent": CampaignOptimizerAgent(),
            "strategy_agent": StrategyAgent(),
        }
        self.retriever = MemoryRetriever(self.memory)
        self.reflection = ReflectionEngine()

    def route_task(self, task_type: str) -> str:
        if task_type == NEW_LEAD:
            return "lead_triage_agent"
        if task_type in [QUALIFIED_LEAD, ENGAGEMENT_REQUEST]:
            return "engagement_agent"
        if task_type == CAMPAIGN_REVIEW:
            return "campaign_optimizer_agent"
        if task_type == STRATEGY_REVIEW:
            return "strategy_agent"
        raise ValueError(f"Unknown task type: {task_type}")

    def execute_task(self, task: AgentTask) -> AgentResult:
        session_id = task.session_id or task.task_id
        lead_id = task.lead_id or task.payload.get("lead_id")

        self.memory.short_term.create_or_get(session_id=session_id, lead_id=lead_id)

        self.memory.short_term.add_message(
            session_id=session_id,
            role="system_event",
            content=f"Received task: {task.task_type}",
            agent_name="runtime",
            summary="Task entered runtime."
        )

        episodic_tags = [task.task_type]

        if task.task_type == "new_lead":
            lead_message = (task.payload.get("message") or "").lower()
            if "pricing" in lead_message or "demo" in lead_message or "enterprise" in lead_message:
                episodic_tags.append("hot_lead")

        if task.task_type == "engagement_request":
            episodic_tags.extend(["engagement", "lead_triage"])

        if task.task_type == "campaign_review":
            episodic_tags.append("campaign_review")

        task.context["memory"] = self.retriever.build_agent_memory_context(
            session_id=session_id,
            lead_id=lead_id,
            episodic_tags=episodic_tags,
        )

        agent_name = self.route_task(task.task_type)
        agent = self.agents[agent_name]
        result = agent.run(task)

        self.memory.short_term.add_message(
            session_id=session_id,
            role="agent_result",
            content = json.dumps(result.output),
            agent_name=result.agent_name,
            summary=result.output.get("reasoning_summary")
                or result.output.get("engagement_summary")
                or result.output.get("summary")
                or "Agent completed task."
        )

        if lead_id:
            self.memory.long_term.create_or_get(
                lead_id=lead_id,
                lead_name=task.payload.get("lead_name"),
                source=task.payload.get("source")
            )

            self.memory.long_term.append_history(
                lead_id=lead_id,
                event={
                    "task_type": task.task_type,
                    "agent_name": result.agent_name,
                    "status": result.status,
                    "output": result.output,
                }
            )
        
        if lead_id and task.payload.get("source"):
            self.memory.semantic.add_triplet(
                subject=lead_id,
                relation="came_from",
                object_=task.payload["source"],
                metadata={"task_id": task.task_id}
            )

        if lead_id and result.output.get("category"):
            self.memory.semantic.add_triplet(
                subject=lead_id,
                relation="classified_as",
                object_=result.output["category"],
                metadata={"agent": result.agent_name}
            )
        
        if (
            result.status == "success"
            and result.agent_name == "lead_triage_agent"
            and result.output.get("category") == "Hot Lead"
        ):
            self.memory.episodic.add_episode(
                EpisodicMemoryRecord(
                    episode_id=f"episode_{task.task_id}",
                    situation=f"Lead message: {task.payload.get('message', '')}",
                    action_taken="Classified as Hot Lead and prepared for engagement.",
                    outcome="High-intent lead detected.",
                    success_score=0.8,
                    tags=["lead_triage", "hot_lead"]
                )
            )

        self.reflect_on_result(task, result)

        return result

    def execute_task_chain(self, task: AgentTask) -> list[AgentResult]:
        results = []

        current_task = task

        while current_task is not None:
            result = self.execute_task(current_task)
            results.append(result)

            if result.next_action == "engagement_request":
                    current_task = AgentTask(
                    task_id=current_task.task_id + "_engagement",
                    task_type="engagement_request",
                    payload={
                        "lead_id": current_task.payload.get("lead_id"),
                        "lead_name": current_task.payload.get("lead_name", "there"),
                        "category": result.output.get("category", "General Inquiry"),
                        "message": current_task.payload.get("message", ""),
                        "source": current_task.payload.get("source", "unknown"),
                    },
                    context={"previous_result": result.output},
                    assigned_by=result.agent_name,
                    session_id=current_task.session_id,
                    lead_id=current_task.lead_id,
                )
            elif result.next_action == "strategy_review":
                    current_task = AgentTask(
                    task_id=current_task.task_id + "_strategy",
                    task_type="strategy_review",
                    payload=result.output,
                    context={"previous_result": result.output},
                    assigned_by=result.agent_name,
                    session_id=current_task.session_id,
                    lead_id=current_task.lead_id,
                )
            else:
                current_task = None

        return results
    
    def reflect_on_result(self, task: AgentTask, result: AgentResult) -> None:
        if result.status != "success":
            return

        try:
            reflection = self.reflection.reflect(
                agent_name=result.agent_name,
                task_type=task.task_type,
                input_payload=task.payload,
                agent_output=result.output,
                memory_context=task.context.get("memory", {}),
            )
        except Exception:
            return

        session_id = task.session_id or task.task_id

        self.memory.short_term.add_message(
            session_id=session_id,
            role="reflection",
            content=reflection.model_dump_json(),
            agent_name="reflection_engine",
            summary=reflection.lesson,
        )

        if not reflection.should_store:
            return

        if reflection.success_score < 0.6:
            return

        if len(reflection.lesson.strip()) < 20:
            return
    
        episode_id = f"reflection_{task.task_id}_{result.agent_name}"

        self.memory.episodic.add_episode(
            EpisodicMemoryRecord(
                episode_id=episode_id,
                situation=f"Task type: {task.task_type}; Input: {task.payload}",
                action_taken=f"Agent output: {result.output}",
                outcome=reflection.lesson,
                success_score=reflection.success_score,
                tags=[result.agent_name, task.task_type, reflection.tag],
            )
        )