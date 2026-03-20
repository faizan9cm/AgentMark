from typing import Callable, Optional
import json
import time

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
from memory.retriever import MemoryRetriever
from memory.consolidator import MemoryConsolidator

from reflection.reflection_engine import ReflectionEngine

from communication.json_rpc import (
    JsonRpcRequest,
    JsonRpcSuccessResponse,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
)
from communication.registry import AgentMethodRegistry
from communication.errors import METHOD_NOT_FOUND, INTERNAL_ERROR, INVALID_PARAMS
from communication.handoff import AgentHandoff

from mcp_layer.mcp_server import MCPServer
from mcp_layer.mcp_client import MCPClient

from observability.trace_store import TraceStore
from observability.tracer import Tracer
from observability.cost_estimator import CostEstimator
from observability.graph_builder import GraphBuilder


class AgentRuntime:
    def __init__(self, enable_reflection: bool = True, enable_consolidation: bool = True):
        self.enable_reflection = enable_reflection
        self.enable_consolidation = enable_consolidation

        self.memory = MemoryManager()
        self.agents = {
            "lead_triage_agent": LeadTriageAgent(),
            "engagement_agent": EngagementAgent(),
            "campaign_optimizer_agent": CampaignOptimizerAgent(),
            "strategy_agent": StrategyAgent(),
        }

        self.retriever = MemoryRetriever(self.memory)
        self.reflection = ReflectionEngine()
        self.consolidator = MemoryConsolidator(self.memory)

        self.registry = AgentMethodRegistry()
        self._register_agent_methods()

        self.event_callback = None

        self.mcp_server = MCPServer()
        self.mcp_client = MCPClient(self.mcp_server)
        self._register_mcp_targets()

        self.trace_store = TraceStore()
        self.tracer = Tracer(self.trace_store)
        self.cost_estimator = CostEstimator()
        self.graph_builder = GraphBuilder(self.trace_store)

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

    def execute_task(self, task: AgentTask, run_reflection: bool = True) -> AgentResult:
        session_id = task.session_id or task.task_id
        lead_id = task.lead_id or task.payload.get("lead_id")

        run_id = task.context.get("trace_run_id")
        span_start = time.perf_counter()
        span_id = None

        agent_name = self.route_task(task.task_type)

        if run_id:
            span_id = self.tracer.start_span(
                run_id=run_id,
                event_type="agent_execution",
                session_id=session_id,
                task_id=task.task_id,
                agent_name=agent_name,
                payload={"task_type": task.task_type},
            )

        task.context["trace_span_id"] = span_id

        self.emit_event(
            event_type="task_received",
            session_id=session_id,
            task_id=task.task_id,
            agent_name="runtime",
            payload={
                "task_type": task.task_type,
                "assigned_by": task.assigned_by,
            },
        )

        self.memory.short_term.create_or_get(session_id=session_id, lead_id=lead_id)

        self.memory.short_term.add_message(
            session_id=session_id,
            role="system_event",
            content=f"Received task: {task.task_type}",
            agent_name="runtime",
            summary="Task entered runtime.",
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

        task.context = {
            **task.context,
            "memory": self.retriever.build_agent_memory_context(
                session_id=session_id,
                lead_id=lead_id,
                episodic_tags=episodic_tags,
            ),
        }

        task.context["mcp"] = {
            "lead_history": self.mcp_client.get_resource(
                request_id=f"mcp_lead_history_{task.task_id}",
                name="lead_history",
                params={"lead_id": lead_id} if lead_id else {},
            ),
            "episodic_lessons": self.mcp_client.get_resource(
                request_id=f"mcp_episodic_{task.task_id}",
                name="episodic_lessons",
                params={"tags": episodic_tags},
            ),
        }

        if task.task_type == "campaign_review":
            task.context["mcp"]["campaign_analytics"] = self.mcp_client.get_resource(
                request_id=f"mcp_campaign_{task.task_id}",
                name="campaign_analytics",
                params=task.payload,
            )

        agent = self.agents[agent_name]
        result = agent.run(task)

        latency_ms = round((time.perf_counter() - span_start) * 1000, 2)

        if run_id and span_id:
            output_text = str(result.output)
            input_text = str(task.payload)
            cost_info = self.cost_estimator.estimate_cost(
                model_name=getattr(getattr(agent, "llm", None), "model", "default"),
                input_text=input_text,
                output_text=output_text,
            )

            self.tracer.finish_span(
                run_id=run_id,
                span_id=span_id,
                status=result.status,
                latency_ms=latency_ms,
                model_name=getattr(getattr(agent, "llm", None), "model", None),
                estimated_input_tokens=cost_info["estimated_input_tokens"],
                estimated_output_tokens=cost_info["estimated_output_tokens"],
                estimated_cost_usd=cost_info["estimated_cost_usd"],
                payload_update={
                    "result_status": result.status,
                    "next_action": result.next_action,
                },
            )

        if task.task_type == "campaign_review":
            self.emit_event(
                event_type="campaign_update",
                session_id=session_id,
                task_id=task.task_id,
                agent_name=result.agent_name,
                payload=result.output,
            )

        self.emit_event(
            event_type="agent_result",
            session_id=session_id,
            task_id=task.task_id,
            agent_name=result.agent_name,
            payload=result.model_dump(),
        )

        self.memory.short_term.add_message(
            session_id=session_id,
            role="agent_result",
            content=json.dumps(result.output),
            agent_name=result.agent_name,
            summary=result.output.get("reasoning_summary")
            or result.output.get("engagement_summary")
            or result.output.get("summary")
            or "Agent completed task.",
        )

        if lead_id and result.status == "success":
            self.memory.long_term.create_or_get(
                lead_id=lead_id,
                lead_name=task.payload.get("lead_name"),
                source=task.payload.get("source"),
            )

            self.memory.long_term.append_history(
                lead_id=lead_id,
                event={
                    "task_type": task.task_type,
                    "agent_name": result.agent_name,
                    "status": result.status,
                    "output": result.output,
                },
            )

        if lead_id and task.payload.get("source"):
            try:
                self.memory.semantic.add_triplet(
                    subject=lead_id,
                    relation="came_from",
                    object_=task.payload["source"],
                    metadata={"task_id": task.task_id},
                )
            except Exception:
                pass

        if lead_id and result.output.get("category"):
            try:
                self.memory.semantic.add_triplet(
                    subject=lead_id,
                    relation="classified_as",
                    object_=result.output["category"],
                    metadata={"agent": result.agent_name},
                )
            except Exception:
                pass

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
                    tags=["lead_triage", "hot_lead"],
                )
            )

        if run_reflection and self.enable_reflection:
            self.reflect_on_result(task, result)

        return result

    def execute_task_chain(self, task: AgentTask, run_post_processing: bool = True) -> list[AgentResult]:
        results = []
        run_start = time.perf_counter()

        run_id = self.tracer.start_run(
            entrypoint="execute_task_chain",
            session_id=task.session_id,
            lead_id=task.lead_id,
        )

        current_task = task
        current_task.context["trace_run_id"] = run_id

        try:
            while current_task is not None:
                result = self.execute_task(current_task, run_reflection=run_post_processing)
                results.append(result)

                current_span_id = current_task.context.get("trace_span_id")
                source_span_id = current_task.context.get("source_span_id")

                if run_id and source_span_id and current_span_id:
                    self.tracer.add_edge(
                        run_id=run_id,
                        from_node=source_span_id,
                        to_node=current_span_id,
                        edge_type="handoff",
                        reason=current_task.context.get("handoff", {}).get("reason"),
                    )

                if result.next_action == "engagement_request":
                    handoff = self.build_handoff(
                        from_agent=result.agent_name,
                        to_agent="engagement_agent",
                        current_task=current_task,
                        next_task_type="engagement_request",
                        payload={
                            "lead_id": current_task.payload.get("lead_id"),
                            "lead_name": current_task.payload.get("lead_name", "there"),
                            "category": result.output.get("category", "General Inquiry"),
                            "message": current_task.payload.get("message", ""),
                            "source": current_task.payload.get("source", "unknown"),
                        },
                        reason="Lead triage determined that engagement follow-up is required.",
                    )

                    self.emit_event(
                        event_type="handoff_created",
                        session_id=current_task.session_id,
                        task_id=handoff.task_id,
                        agent_name=result.agent_name,
                        payload=handoff.model_dump(),
                    )

                    if current_task.session_id:
                        self.memory.short_term.add_message(
                            session_id=current_task.session_id,
                            role="handoff",
                            content=handoff.model_dump_json(),
                            agent_name=result.agent_name,
                            summary=handoff.reason,
                        )

                    current_task = AgentTask(
                        task_id=handoff.task_id,
                        task_type=handoff.task_type,
                        payload=handoff.payload,
                        context={
                            **handoff.context,
                            "handoff": handoff.model_dump(),
                            "previous_result": result.output,
                            "trace_run_id": run_id,
                            "source_span_id": current_span_id,
                        },
                        assigned_by=result.agent_name,
                        session_id=handoff.session_id,
                        lead_id=handoff.lead_id,
                    )

                elif result.next_action == "strategy_review":
                    handoff = self.build_handoff(
                        from_agent=result.agent_name,
                        to_agent="strategy_agent",
                        current_task=current_task,
                        next_task_type="strategy_review",
                        payload=result.output,
                        reason="Campaign optimizer escalated the issue for strategic review.",
                    )

                    self.emit_event(
                        event_type="handoff_created",
                        session_id=current_task.session_id,
                        task_id=handoff.task_id,
                        agent_name=result.agent_name,
                        payload=handoff.model_dump(),
                    )

                    if current_task.session_id:
                        self.memory.short_term.add_message(
                            session_id=current_task.session_id,
                            role="handoff",
                            content=handoff.model_dump_json(),
                            agent_name=result.agent_name,
                            summary=handoff.reason,
                        )

                    current_task = AgentTask(
                        task_id=handoff.task_id,
                        task_type=handoff.task_type,
                        payload=handoff.payload,
                        context={
                            **handoff.context,
                            "handoff": handoff.model_dump(),
                            "previous_result": result.output,
                            "trace_run_id": run_id,
                            "source_span_id": current_span_id,
                        },
                        assigned_by=result.agent_name,
                        session_id=handoff.session_id,
                        lead_id=handoff.lead_id,
                    )
                else:
                    current_task = None

            session_id = task.session_id
            lead_id = task.lead_id

            if run_post_processing and self.enable_consolidation:
                self.consolidate_after_chain(session_id=session_id, lead_id=lead_id)

            total_latency_ms = round((time.perf_counter() - run_start) * 1000, 2)
            self.tracer.finish_run(
                run_id=run_id,
                status="success",
                total_latency_ms=total_latency_ms,
            )

            return results

        except Exception:
            total_latency_ms = round((time.perf_counter() - run_start) * 1000, 2)
            self.tracer.finish_run(
                run_id=run_id,
                status="error",
                total_latency_ms=total_latency_ms,
            )
            raise

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

    def consolidate_after_chain(self, session_id: str | None, lead_id: str | None) -> None:
        if session_id:
            try:
                self.consolidator.consolidate_session(session_id)
            except Exception:
                pass

        if lead_id:
            try:
                self.consolidator.consolidate_lead_history(lead_id)
            except Exception:
                pass

        try:
            self.consolidator.consolidate_episodic_memory()
        except Exception:
            pass

    def _register_agent_methods(self) -> None:
        self.registry.register("lead_triage.run", self._rpc_lead_triage_run)
        self.registry.register("engagement.run", self._rpc_engagement_run)
        self.registry.register("campaign_optimizer.run", self._rpc_campaign_optimizer_run)
        self.registry.register("strategy.run", self._rpc_strategy_run)

    def _rpc_lead_triage_run(self, params: dict) -> dict:
        task = AgentTask(**params)
        result = self.execute_task(task)
        return result.model_dump()

    def _rpc_engagement_run(self, params: dict) -> dict:
        task = AgentTask(**params)
        result = self.execute_task(task)
        return result.model_dump()

    def _rpc_campaign_optimizer_run(self, params: dict) -> dict:
        task = AgentTask(**params)
        result = self.execute_task(task)
        return result.model_dump()

    def _rpc_strategy_run(self, params: dict) -> dict:
        task = AgentTask(**params)
        result = self.execute_task(task)
        return result.model_dump()

    def handle_json_rpc(self, request_data: dict) -> dict:
        try:
            request = JsonRpcRequest(**request_data)
        except Exception as e:
            return JsonRpcErrorResponse(
                id=request_data.get("id", "unknown"),
                error=JsonRpcErrorObject(
                    code=INVALID_PARAMS,
                    message="Invalid JSON-RPC request",
                    data={"details": str(e)},
                ),
            ).model_dump()

        handler = self.registry.get(request.method)
        if not handler:
            return JsonRpcErrorResponse(
                id=request.id,
                error=JsonRpcErrorObject(
                    code=METHOD_NOT_FOUND,
                    message=f"Method not found: {request.method}",
                ),
            ).model_dump()

        try:
            result = handler(request.params)
            return JsonRpcSuccessResponse(
                id=request.id,
                result=result,
            ).model_dump()
        except Exception as e:
            return JsonRpcErrorResponse(
                id=request.id,
                error=JsonRpcErrorObject(
                    code=INTERNAL_ERROR,
                    message="Internal server error",
                    data={"details": str(e)},
                ),
            ).model_dump()

    def list_rpc_methods(self):
        return self.registry.list_methods()

    def build_handoff(
        self,
        from_agent: str,
        to_agent: str,
        current_task: AgentTask,
        next_task_type: str,
        payload: dict,
        reason: str,
    ) -> AgentHandoff:
        return AgentHandoff(
            handoff_id=f"handoff_{current_task.task_id}_{to_agent}",
            from_agent=from_agent,
            to_agent=to_agent,
            task_id=f"{current_task.task_id}_{to_agent}",
            task_type=next_task_type,
            session_id=current_task.session_id,
            lead_id=current_task.lead_id,
            payload=payload,
            context=self.compact_context_for_handoff(current_task.context),
            reason=reason,
        )

    def set_event_callback(self, callback: Optional[Callable[[dict], None]]):
        self.event_callback = callback

    def emit_event(
        self,
        event_type: str,
        session_id: str | None,
        task_id: str | None,
        agent_name: str | None,
        payload: dict,
    ) -> None:
        if self.event_callback:
            try:
                self.event_callback({
                    "event_type": event_type,
                    "session_id": session_id,
                    "task_id": task_id,
                    "agent_name": agent_name,
                    "payload": payload,
                })
            except Exception:
                pass

    def compact_context_for_handoff(self, context: dict) -> dict:
        memory = context.get("memory", {})
        mcp = context.get("mcp", {})

        compact_memory = {
            "short_term": {
                "latest_summary": memory.get("short_term", {}).get("latest_summary"),
                "latest_agent": memory.get("short_term", {}).get("latest_agent"),
            },
            "long_term": {
                "summary": memory.get("long_term", {}).get("summary"),
                "latest_status": memory.get("long_term", {}).get("latest_status"),
            },
            "episodic": [
                {
                    "outcome": e.get("outcome"),
                    "success_score": e.get("success_score"),
                    "tags": e.get("tags"),
                }
                for e in memory.get("episodic", [])[:2]
            ],
            "semantic": [
                {
                    "subject": s.get("subject"),
                    "relation": s.get("relation"),
                    "object": s.get("object"),
                }
                for s in memory.get("semantic", [])[:3]
            ],
        }

        compact_mcp = {
            "lead_history": {
                "status": mcp.get("lead_history", {}).get("status"),
                "data": {
                    "summary": mcp.get("lead_history", {}).get("data", {}).get("summary"),
                    "latest_status": mcp.get("lead_history", {}).get("data", {}).get("latest_status"),
                },
            },
            "episodic_lessons": {
                "status": mcp.get("episodic_lessons", {}).get("status"),
                "data": {
                    "lessons": [
                        {
                            "outcome": lesson.get("outcome"),
                            "success_score": lesson.get("success_score"),
                            "tags": lesson.get("tags"),
                        }
                        for lesson in mcp.get("episodic_lessons", {}).get("data", {}).get("lessons", [])[:2]
                    ]
                },
            },
        }

        new_context = dict(context)
        new_context["memory"] = compact_memory
        new_context["mcp"] = compact_mcp
        return new_context

    def _register_mcp_targets(self) -> None:
        self.mcp_server.registry.register_resource("lead_history", self._mcp_get_lead_history)
        self.mcp_server.registry.register_resource("episodic_lessons", self._mcp_get_episodic_lessons)
        self.mcp_server.registry.register_resource("semantic_relations", self._mcp_get_semantic_relations)
        self.mcp_server.registry.register_resource("campaign_analytics", self._mcp_get_campaign_analytics)
        self.mcp_server.registry.register_tool("update_lead_preferences", self._mcp_update_lead_preferences)

    def _mcp_get_lead_history(self, params: dict) -> dict:
        lead_id = params.get("lead_id")
        if not lead_id:
            return {"history": [], "summary": None}

        record = self.memory.long_term.get(lead_id)
        if not record:
            return {"history": [], "summary": None}

        return {
            "lead_id": record.lead_id,
            "lead_name": record.lead_name,
            "summary": record.summary,
            "latest_status": record.latest_status,
            "recent_history": record.history[-5:],
        }

    def _mcp_get_episodic_lessons(self, params: dict) -> dict:
        tags = params.get("tags", [])
        if tags:
            lessons = self.memory.episodic.search_by_tags(tags, limit=5)
        else:
            lessons = self.memory.episodic.top_k(5)

        return {
            "lessons": [lesson.model_dump() for lesson in lessons]
        }

    def _mcp_get_semantic_relations(self, params: dict) -> dict:
        lead_id = params.get("lead_id")
        if not lead_id:
            return {"relations": []}

        try:
            relations = self.memory.semantic.query_by_subject(lead_id)
        except Exception:
            relations = []

        return {
            "relations": [relation.model_dump() for relation in relations]
        }

    def _mcp_get_campaign_analytics(self, params: dict) -> dict:
        channel = params.get("channel", "unknown")
        ctr = params.get("ctr", 0.0)
        conversion_rate = params.get("conversion_rate", 0.0)

        return {
            "channel": channel,
            "ctr": ctr,
            "conversion_rate": conversion_rate,
            "status": "healthy" if ctr >= 0.02 and conversion_rate >= 0.05 else "needs_attention",
        }

    def _mcp_update_lead_preferences(self, params: dict) -> dict:
        lead_id = params.get("lead_id")
        preferences = params.get("preferences", {})

        if not lead_id:
            return {"updated": False}

        self.memory.long_term.update_preferences(lead_id, preferences)
        return {"updated": True, "lead_id": lead_id}

    def list_trace_runs(self):
        return [run.model_dump() for run in self.trace_store.list_runs()]

    def get_trace_run(self, run_id: str):
        run = self.trace_store.get_run(run_id)
        if not run:
            return None

        return {
            "run": run.model_dump(),
            "spans": [span.model_dump() for span in self.trace_store.get_spans(run_id)],
            "edges": [edge.model_dump() for edge in self.trace_store.get_edges(run_id)],
        }

    def get_trace_graph(self, run_id: str):
        return self.graph_builder.build_run_graph(run_id)

    def get_latency_metrics(self):
        spans = []
        for run in self.trace_store.list_runs():
            spans.extend(self.trace_store.get_spans(run.run_id))

        agent_groups = {}
        for span in spans:
            if not span.agent_name or span.latency_ms is None:
                continue
            agent_groups.setdefault(span.agent_name, []).append(span.latency_ms)

        metrics = {}
        for agent_name, values in agent_groups.items():
            metrics[agent_name] = {
                "count": len(values),
                "avg_latency_ms": round(sum(values) / len(values), 2),
                "max_latency_ms": round(max(values), 2),
                "min_latency_ms": round(min(values), 2),
            }

        return metrics

    def get_cost_metrics(self):
        runs = self.trace_store.list_runs()
        total_cost = round(sum(run.total_estimated_cost_usd for run in runs), 8)

        by_agent = {}
        for run in runs:
            for span in self.trace_store.get_spans(run.run_id):
                if not span.agent_name:
                    continue
                by_agent.setdefault(span.agent_name, 0.0)
                by_agent[span.agent_name] += span.estimated_cost_usd

        by_agent = {
            agent: round(cost, 8)
            for agent, cost in by_agent.items()
        }

        return {
            "total_estimated_cost_usd": total_cost,
            "by_agent": by_agent,
            "run_count": len(runs),
        }