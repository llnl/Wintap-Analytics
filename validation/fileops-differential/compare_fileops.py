#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import PurePosixPath

try:
    import duckdb
except ImportError as exc:  # pragma: no cover - runtime preflight
    raise SystemExit(f"duckdb Python package is required: {exc}")


NOISE_PREFIXES = ("/proc", "/sys", "/dev")
NON_REGULAR_RE = re.compile(r"^(socket|pipe|anon_inode|eventfd|inotify|memfd):\[")


def quote(value: str) -> str:
    return value.replace("'", "''")


def list_columns(connection: duckdb.DuckDBPyConnection, parquet_glob: str) -> set[str]:
    rows = connection.execute(f"DESCRIBE SELECT * FROM read_parquet('{quote(parquet_glob)}')").fetchall()
    return {row[0] for row in rows}


def pick_column(columns: set[str], candidates: tuple[str, ...]) -> str:
    lowered = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    raise SystemExit(f"could not find any of columns {candidates}; available={sorted(columns)}")


def normalize_path(path: str) -> str:
    path = (path or "").strip().lower()
    if path.endswith(" (deleted)"):
        path = path[: -len(" (deleted)")]
    return str(PurePosixPath(path)) if path.startswith("/") else path


def is_regular_candidate(path: str) -> bool:
    path = normalize_path(path)
    if not path:
        return False
    if path.startswith(NOISE_PREFIXES):
        return False
    if NON_REGULAR_RE.match(path):
        return False
    return path.startswith("/")


def load_tuples(parquet_glob: str) -> tuple[Counter[tuple[int, str, str]], Counter[str]]:
    connection = duckdb.connect()
    try:
        columns = list_columns(connection, parquet_glob)
        path_col = pick_column(columns, ("Path", "path", "File_Path", "file_path", "file", "File"))
        pid_col = pick_column(columns, ("PID", "pid", "ProcessId", "process_id"))
        op_col = pick_column(columns, ("ActivityType", "activity_type", "op", "operation", "EventType", "event_type"))
        rows = connection.execute(
            f"SELECT {pid_col}, {path_col}, {op_col} FROM read_parquet('{quote(parquet_glob)}')"
        ).fetchall()
    finally:
        connection.close()

    regular: Counter[tuple[int, str, str]] = Counter()
    noise: Counter[str] = Counter()
    for pid, raw_path, raw_op in rows:
        path = normalize_path(str(raw_path or ""))
        op = str(raw_op or "").lower()
        if is_regular_candidate(path):
            regular[(int(pid), path, op)] += 1
        else:
            if not path:
                noise["empty"] += 1
            elif path.startswith(NOISE_PREFIXES):
                noise[path.split("/", 2)[1] if path.startswith("/") else path] += 1
            elif NON_REGULAR_RE.match(path):
                noise[path.split(":", 1)[0]] += 1
            else:
                noise["other"] += 1
    return regular, noise


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline/candidate FileOps parquet outputs")
    parser.add_argument("--baseline", required=True, help="Baseline raw_process_file parquet glob")
    parser.add_argument("--candidate", required=True, help="Candidate raw_process_file parquet glob")
    parser.add_argument("--json-out", help="Optional summary JSON path")
    args = parser.parse_args()

    baseline, baseline_noise = load_tuples(args.baseline)
    candidate, candidate_noise = load_tuples(args.candidate)
    missing = baseline - candidate
    added = candidate - baseline
    summary = {
        "baseline_regular_tuples": sum(baseline.values()),
        "candidate_regular_tuples": sum(candidate.values()),
        "missing_regular_tuples": sum(missing.values()),
        "added_regular_tuples": sum(added.values()),
        "baseline_noise": dict(baseline_noise),
        "candidate_noise": dict(candidate_noise),
        "missing_samples": [
            {"pid": pid, "path": path, "op": op, "count": count}
            for (pid, path, op), count in missing.most_common(25)
        ],
        "added_samples": [
            {"pid": pid, "path": path, "op": op, "count": count}
            for (pid, path, op), count in added.most_common(25)
        ],
    }

    text = json.dumps(summary, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.write("\n")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
