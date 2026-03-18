from evaluation.evaluator import BenchmarkEvaluator
from evaluation.reporting import save_report
import json


def main():
    evaluator = BenchmarkEvaluator()
    report = evaluator.run_all()

    print("\n--- Benchmark Report ---")
    print(json.dumps(report, indent=2))

    output_path = save_report(report)
    print(f"\nSaved report to: {output_path}")


if __name__ == "__main__":
    main()