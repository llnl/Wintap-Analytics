from __future__ import annotations

import argparse
from pathlib import Path
import json

from wintap_process_validation.evaluator import evaluate
from wintap_process_validation.mock import write_mock_normalized_events
from wintap_process_validation.schema import Manifest
from wintap_process_validation.workload import generate_process_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and evaluate a mock process validation run")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--run-id", default="mock-run-001")
    parser.add_argument("--no-duplicate", action="store_true", help="do not inject duplicate exec_success row")
    args = parser.parse_args()

    args.run_dir.mkdir(parents=True, exist_ok=True)
    manifest = generate_process_baseline(args.run_id, short_lived_children=3)
    manifest_path = args.run_dir / "manifest.json"
    manifest.write(manifest_path)
    normalized_dir = args.run_dir / "normalized"
    write_mock_normalized_events(manifest, normalized_dir, inject_duplicate=not args.no_duplicate)
    report = evaluate(Manifest.read(manifest_path), normalized_dir)
    report_path = args.run_dir / "reports" / "report.json"
    report.write(report_path)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    print(f"wrote {manifest_path}")
    print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
