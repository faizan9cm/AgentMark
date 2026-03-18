import json
from pathlib import Path
from orchestrator.agent_runtime import AgentRuntime
from orchestrator.contracts import AgentTask
from evaluation.metrics import accuracy_score, safe_equal, contains_all_keywords
from evaluation.llm_judge import EngagementLLMJudge


class BenchmarkEvaluator:
    def __init__(self, dataset_path: str = "evaluation/benchmark_dataset.json"):
        self.dataset_path = Path(dataset_path)
        self.runtime = AgentRuntime(enable_reflection = False, enable_consolidation = False)
        self.engagement_judge = EngagementLLMJudge()
        self.use_llm_judge = False

    def load_dataset(self):
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_lead_triage(self, examples: list[dict]) -> dict:
        total = 0
        category_correct = 0
        priority_correct = 0
        next_action_correct = 0

        details = []

        for example in examples:
            print(f"Running lead triage benchmark: {example['id']}")
            task = AgentTask(
                task_id=f"eval_{example['id']}",
                task_type=example["task_type"],
                payload=example["input"],
                context={},
                session_id=f"eval_session_{example['id']}",
                lead_id=example["input"].get("lead_id"),
            )

            try:
                result = self.runtime.execute_task(task)
            except Exception as e:
                details.append({
                "id": example["id"],
                "status": "error",
                "error": str(e),
                "expected": example["expected"],
                })
                total += 1
                continue

            expected = example["expected"]
            output = result.output

            total += 1

            category_ok = safe_equal(output.get("category"), expected.get("category"))
            priority_ok = safe_equal(output.get("priority"), expected.get("priority"))
            next_action_ok = safe_equal(result.next_action, expected.get("next_action"))

            category_correct += int(category_ok)
            priority_correct += int(priority_ok)
            next_action_correct += int(next_action_ok)

            details.append({
                "id": example["id"],
                "status": result.status,
                "output": output,
                "next_action": result.next_action,
                "expected": expected,
                "category_correct": category_ok,
                "priority_correct": priority_ok,
                "next_action_correct": next_action_ok,
            })

        return {
            "task": "lead_triage",
            "total": total,
            "category_accuracy": accuracy_score(category_correct, total),
            "priority_accuracy": accuracy_score(priority_correct, total),
            "next_action_accuracy": accuracy_score(next_action_correct, total),
            "details": details,
        }

    def evaluate_campaign_optimizer(self, examples: list[dict]) -> dict:
        total = 0
        escalation_correct = 0
        details = []

        for example in examples:
            print(f"Running campaign benchmark: {example['id']}")
            task = AgentTask(
                task_id=f"eval_{example['id']}",
                task_type=example["task_type"],
                payload=example["input"],
                context={},
                session_id=f"eval_session_{example['id']}",
            )

            try:
                result = self.runtime.execute_task(task)
            except Exception as e:
                details.append({
                "id": example["id"],
                "status": "error",
                "error": str(e),
                "expected": example["expected"],
                })
                total += 1
                continue

            expected = example["expected"]
            output = result.output

            total += 1

            escalation_ok = safe_equal(
                output.get("escalation_flag"),
                expected.get("escalation_flag")
            )

            escalation_correct += int(escalation_ok)

            details.append({
                "id": example["id"],
                "status": result.status,
                "output": output,
                "expected": expected,
                "escalation_correct": escalation_ok,
            })

        return {
            "task": "campaign_optimizer",
            "total": total,
            "escalation_accuracy": accuracy_score(escalation_correct, total),
            "details": details,
        }

    def evaluate_engagement_quality(self, lead_examples: list[dict]) -> dict:
        total = 0
        judge_total = 0.0
        keyword_pass = 0
        details = []

        for example in lead_examples:
            print(f"Running engagement benchmark: {example['id']}")
            chain_task = AgentTask(
                task_id=f"eval_chain_{example['id']}",
                task_type=example["task_type"],
                payload=example["input"],
                context={},
                session_id=f"eval_chain_session_{example['id']}",
                lead_id=example["input"].get("lead_id"),
            )

            try:
                results = self.runtime.execute_task_chain(chain_task)
            except Exception as e:
                details.append({
                "id": example["id"],
                "status": "error",
                "error": str(e),
                })
                continue

            engagement_result = None
            for result in results:
                if result.agent_name == "engagement_agent":
                    engagement_result = result
                    break

            if not engagement_result:
                continue

            total += 1

            response_message = engagement_result.output.get("response_message", "")
            keywords = ["demo", "pricing"]

            keyword_ok = contains_all_keywords(response_message, keywords)
            keyword_pass += int(keyword_ok)

            judge_scores = None
            if self.use_llm_judge:
                judge_scores = self.engagement_judge.score_response(
                lead_message=example["input"]["message"],
                response_message=response_message,
                )
                judge_total += float(judge_scores.get("overall_score", 0.0))

            details.append({
                "id": example["id"],
                "response_message": response_message,
                "engagement_summary": engagement_result.output.get("engagement_summary"),
                "keyword_check_passed": keyword_ok,
                "required_keywords": keywords,
                "llm_judge": judge_scores,
            })

        return {
            "task": "engagement_quality",
            "total": total,
            "keyword_quality_score": accuracy_score(keyword_pass, total),
            "avg_llm_judge_score": (judge_total / total) if (total and self.use_llm_judge) else None,
            "details": details,
        }

    def run_all(self) -> dict:
        dataset = self.load_dataset()

        lead_examples = [x for x in dataset if x["task_type"] == "new_lead"]
        campaign_examples = [x for x in dataset if x["task_type"] == "campaign_review"]

        return {
            "lead_triage": self.evaluate_lead_triage(lead_examples),
            "campaign_optimizer": self.evaluate_campaign_optimizer(campaign_examples),
            "engagement_quality": {
                "task": "engagement_quality",
                "skipped": True,
                "reason": "Temporarily disabled to avoid rate-limit stalls during initial benchmark validation."
            },
        }   