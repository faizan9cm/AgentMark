import json
from datetime import datetime
from pathlib import Path


def save_report(report: dict, output_dir: str = "evaluation/results") -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = output_path / f"benchmark_report_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return str(file_path)