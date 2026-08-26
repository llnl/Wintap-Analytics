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
    path = (path or "").strip()
    if path.endswith(" (deleted)"):
        path = path[: -len(" (deleted)")]
    if sys.platform.startswith("win"):
        path = path.lower()
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


def is_relative_candidate(path: str) -> bool:
    """A workload-relevant relative path: non-empty, not pseudo/non-regular noise,
    and not absolute. These are invisible to the strict absolute-tuple gate, so
    they get their own relative->absolute upgrade matching (fop-12/fop-13)."""
    path = normalize_path(path)
    if not path or path.startswith("/"):
        return False
    if NON_REGULAR_RE.match(path):
        return False
    return True


def normalize_relative(path: str) -> str:
    path = normalize_path(path)
    while path.startswith("./"):
        path = path[2:]
    return str(PurePosixPath(path)) if path else path


def match_relative_upgrades(
    relative: Counter[tuple[int, str, str]],
    other_relative: Counter[tuple[int, str, str]],
    absolute: Counter[tuple[int, str, str]],
) -> tuple[Counter[tuple[int, str, str]], Counter[tuple[int, str, str]]]:
    """Split relative tuples into matched (still present as relative, or present
    as an absolute path ending in /<relative>) vs unmatched."""
    by_pid_op: dict[tuple[int, str], list[str]] = {}
    for (pid, path, op) in absolute:
        by_pid_op.setdefault((pid, op), []).append(path)

    matched: Counter[tuple[int, str, str]] = Counter()
    unmatched: Counter[tuple[int, str, str]] = Counter()
    for (pid, rel_path, op), count in relative.items():
        if (pid, rel_path, op) in other_relative:
            matched[(pid, rel_path, op)] += count
            continue
        suffix = "/" + normalize_relative(rel_path)
        if any(candidate.endswith(suffix) for candidate in by_pid_op.get((pid, op), ())):
            matched[(pid, rel_path, op)] += count
        else:
            unmatched[(pid, rel_path, op)] += count
    return matched, unmatched


def load_tuples(parquet_glob: str) -> tuple[Counter[tuple[int, str, str]], Counter[tuple[int, str, str]], Counter[str]]:
    connection = duckdb.connect()
    try:
        columns = list_columns(connection, parquet_glob)
        path_col = pick_column(columns, ("Path", "path", "File_Path", "file_path", "file", "File"))
        pid_col = pick_column(columns, ("PID", "pid", "ProcessId", "process_id"))
        op_col = pick_column(columns, ("ActivityType", "activity_type", "op", "operation", "EventType", "event_type"))
        # fop-11 count conservation: rows may be aggregates carrying an
        # eventCount for the raw events they represent. Weight tuple counts by
        # it when present so pre- and post-aggregation streams compare on raw
        # event cardinality; absent column -> every row weighs 1.
        count_expr = "1"
        for candidate in ("eventCount", "event_count", "EventCount"):
            if candidate in columns or candidate.lower() in {c.lower() for c in columns}:
                actual = next(c for c in columns if c.lower() == candidate.lower())
                count_expr = f"COALESCE({actual}, 1)"
                break
        rows = connection.execute(
            f"SELECT {pid_col}, {path_col}, {op_col}, {count_expr} FROM read_parquet('{quote(parquet_glob)}')"
        ).fetchall()
    finally:
        connection.close()

    regular: Counter[tuple[int, str, str]] = Counter()
    relative: Counter[tuple[int, str, str]] = Counter()
    noise: Counter[str] = Counter()
    for pid, raw_path, raw_op, raw_count in rows:
        path = normalize_path(str(raw_path or ""))
        op = str(raw_op or "").lower()
        weight = max(int(raw_count or 1), 1)
        if is_regular_candidate(path):
            regular[(int(pid), path, op)] += weight
        elif is_relative_candidate(path):
            relative[(int(pid), path, op)] += weight
        else:
            if not path:
                noise["empty"] += 1
            elif path.startswith(NOISE_PREFIXES):
                noise[path.split("/", 2)[1] if path.startswith("/") else path] += 1
            elif NON_REGULAR_RE.match(path):
                noise[path.split(":", 1)[0]] += 1
            else:
                noise["other"] += 1
    return regular, relative, noise


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline/candidate FileOps parquet outputs")
    parser.add_argument("--baseline", required=True, help="Baseline raw_process_file parquet glob")
    parser.add_argument("--candidate", required=True, help="Candidate raw_process_file parquet glob")
    parser.add_argument("--json-out", help="Optional summary JSON path")
    parser.add_argument(
        "--fail-on-unmatched-relative",
        action="store_true",
        help="Also fail when a baseline relative-path tuple has no candidate "
        "counterpart, either relative or as an absolute path ending in "
        "/<relative> (fop-12/fop-13 upgrade matching). Default: report only.",
    )
    args = parser.parse_args()

    baseline, baseline_relative, baseline_noise = load_tuples(args.baseline)
    candidate, candidate_relative, candidate_noise = load_tuples(args.candidate)
    missing = baseline - candidate
    added = candidate - baseline
    upgraded_relative, unmatched_relative = match_relative_upgrades(
        baseline_relative, candidate_relative, candidate
    )
    summary = {
        "baseline_regular_tuples": sum(baseline.values()),
        "candidate_regular_tuples": sum(candidate.values()),
        "missing_regular_tuples": sum(missing.values()),
        "added_regular_tuples": sum(added.values()),
        "baseline_relative_tuples": sum(baseline_relative.values()),
        "candidate_relative_tuples": sum(candidate_relative.values()),
        "matched_relative_tuples": sum(upgraded_relative.values()),
        "unmatched_relative_tuples": sum(unmatched_relative.values()),
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
        "unmatched_relative_samples": [
            {"pid": pid, "path": path, "op": op, "count": count}
            for (pid, path, op), count in unmatched_relative.most_common(25)
        ],
    }

    text = json.dumps(summary, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.write("\n")

    if missing:
        return 1
    if args.fail_on_unmatched_relative and unmatched_relative:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
