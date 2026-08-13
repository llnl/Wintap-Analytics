#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_summary(run_dir: Path | None, summary_path: Path | None) -> tuple[dict, Path]:
    if summary_path is None:
        if run_dir is None:
            raise SystemExit("Provide --run-dir or --summary")
        summary_path = run_dir / "process-table-summary.json"

    return json.loads(summary_path.read_text()), summary_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--show-missing", action="store_true")
    args = parser.parse_args()

    summary, summary_path = load_summary(args.run_dir, args.summary)

    coverage = summary.get("live_process_coverage", {})
    liveness = summary.get("open_row_liveness", {})
    totals = summary.get("table_totals", [{}])[0]
    telemetry_rows = summary.get("telemetry_totals", [])
    telemetry = {row["metric_name"]: int(row["metric_value"]) for row in telemetry_rows}

    result = {
        "summary": str(summary_path),
        "run_id": summary_path.parent.name,
        "live_system_processes": coverage.get("live_system_processes", liveness.get("live_system_processes")),
        "live_pids_with_matching_open_row": coverage.get("live_pids_with_matching_open_row"),
        "live_pids_with_closed_row_after_snapshot": coverage.get("live_pids_with_closed_row_after_snapshot", 0),
        "live_pids_missing_open_row": coverage.get("live_pids_missing_open_row"),
        "tracked_open_rows": liveness.get("tracked_open_rows"),
        "stale_open_rows": liveness.get("stale_open_rows"),
        "open_rows": totals.get("open_rows"),
        "closed_rows": totals.get("closed_rows"),
        "table_rows": totals.get("rows"),
        "telemetry": telemetry,
    }

    if args.show_missing:
        result["sample_missing_live_pids"] = coverage.get("sample_missing_live_pids", [])
        result["sample_stale_open_rows"] = liveness.get("sample_stale_open_rows", [])

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
