#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


def parse_duckdb_json_stream(text: str) -> list:
    decoder = json.JSONDecoder()
    pos = 0
    values = []
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            break
        value, pos = decoder.raw_decode(text, pos)
        values.append(value)
    return values


def run_duckdb_json(db: Path, sql: str) -> list:
    proc = subprocess.run(
        ["sudo", "duckdb", "-json", str(db), "-c", sql],
        check=True,
        text=True,
        capture_output=True,
    )
    return parse_duckdb_json_stream(proc.stdout)


def load_live_snapshot(snapshot_path: Path | None) -> dict[str, Any] | None:
    if snapshot_path is None:
        return None
    return json.loads(snapshot_path.read_text())


def get_linux_live_process_start_utc(pid: int) -> dt.datetime | None:
    stat_path = Path(f"/proc/{pid}/stat")
    uptime_path = Path("/proc/uptime")
    if not stat_path.exists() or not uptime_path.exists():
        return None

    try:
        stat = stat_path.read_text()
        end_comm = stat.rfind(")")
        if end_comm < 0:
            return None
        parts = stat[end_comm + 1 :].strip().split()
        if len(parts) <= 19:
            return None
        start_ticks = int(parts[19])
        uptime_seconds = float(uptime_path.read_text().split()[0])
        clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        if clock_ticks <= 0:
            clock_ticks = 100
        now_unix = time.time()
        process_start_unix = (now_unix - uptime_seconds) + (start_ticks / clock_ticks)
        return dt.datetime.fromtimestamp(process_start_unix, tz=dt.timezone.utc)
    except Exception:
        return None


def count_live_linux_processes() -> int | None:
    proc_dir = Path("/proc")
    if not proc_dir.exists():
        return None
    return sum(1 for child in proc_dir.iterdir() if child.is_dir() and child.name.isdigit())


def classify_open_rows(open_rows: list[dict[str, Any]], live_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    if live_snapshot is not None:
        live_processes = live_snapshot["processes"]
        snapshot_by_pid: dict[int, list[dict[str, Any]]] = {}
        for row in live_processes:
            snapshot_by_pid.setdefault(int(row["process_id"]), []).append(row)

        live_open_rows = 0
        stale_open_rows = 0
        unknown_open_rows = 0
        sample_stale_open_rows: list[dict[str, Any]] = []

        for row in open_rows:
            create_time = dt.datetime.fromisoformat(str(row["create_time"]).replace(" ", "T")).replace(tzinfo=dt.timezone.utc)
            candidates = snapshot_by_pid.get(int(row["process_id"]), [])
            matched = False
            for candidate in candidates:
                live_start_utc = dt.datetime.fromisoformat(candidate["live_start_utc"].replace("Z", "+00:00"))
                if abs((live_start_utc - create_time).total_seconds()) <= 2:
                    matched = True
                    break

            if matched:
                live_open_rows += 1
            else:
                stale_open_rows += 1
                if len(sample_stale_open_rows) < 10:
                    sample_stale_open_rows.append(row)

        return {
            "tracked_open_rows": len(open_rows),
            "tracked_open_distinct_pids": len({row["process_id"] for row in open_rows}),
            "live_system_processes": len(live_processes),
            "live_open_rows": live_open_rows,
            "stale_open_rows": stale_open_rows,
            "unknown_open_rows": unknown_open_rows,
            "sample_stale_open_rows": sample_stale_open_rows,
        }

    if os.name != "posix" or not Path("/proc").exists():
        return {
            "tracked_open_rows": len(open_rows),
            "tracked_open_distinct_pids": len({row["process_id"] for row in open_rows}),
            "live_system_processes": None,
            "live_open_rows": None,
            "stale_open_rows": None,
            "unknown_open_rows": len(open_rows),
            "sample_stale_open_rows": [],
        }

    live_open_rows = 0
    stale_open_rows = 0
    unknown_open_rows = 0
    sample_stale_open_rows: list[dict[str, Any]] = []

    for row in open_rows:
        live_start_utc = get_linux_live_process_start_utc(int(row["process_id"]))
        if live_start_utc is None:
            stale_open_rows += 1
            if len(sample_stale_open_rows) < 10:
                sample_stale_open_rows.append(row)
            continue

        create_time = dt.datetime.fromisoformat(str(row["create_time"]).replace(" ", "T")).replace(tzinfo=dt.timezone.utc)
        if abs((live_start_utc - create_time).total_seconds()) <= 2:
            live_open_rows += 1
        else:
            unknown_open_rows += 1

    return {
        "tracked_open_rows": len(open_rows),
        "tracked_open_distinct_pids": len({row["process_id"] for row in open_rows}),
        "live_system_processes": count_live_linux_processes(),
        "live_open_rows": live_open_rows,
        "stale_open_rows": stale_open_rows,
        "unknown_open_rows": unknown_open_rows,
        "sample_stale_open_rows": sample_stale_open_rows,
    }


def summarize_live_process_coverage(
    open_rows: list[dict[str, Any]],
    all_rows: list[dict[str, Any]],
    live_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if live_snapshot is not None:
        snapshot_time = dt.datetime.fromisoformat(live_snapshot["captured_at_utc"].replace("Z", "+00:00"))
        live_processes = live_snapshot["processes"]
        open_rows_by_pid: dict[int, list[dict[str, Any]]] = {}
        for row in open_rows:
            open_rows_by_pid.setdefault(int(row["process_id"]), []).append(row)

        all_rows_by_pid: dict[int, list[dict[str, Any]]] = {}
        for row in all_rows:
            all_rows_by_pid.setdefault(int(row["process_id"]), []).append(row)

        live_pids_with_matching_open_row = 0
        live_pids_missing_open_row = 0
        live_pids_with_closed_row_after_snapshot = 0
        sample_missing_live_pids: list[dict[str, Any]] = []

        for live_row in live_processes:
            pid = int(live_row["process_id"])
            live_start_utc = dt.datetime.fromisoformat(live_row["live_start_utc"].replace("Z", "+00:00"))
            candidate_rows = open_rows_by_pid.get(pid, [])
            matched = False
            for row in candidate_rows:
                create_time = dt.datetime.fromisoformat(str(row["create_time"]).replace(" ", "T")).replace(tzinfo=dt.timezone.utc)
                if abs((live_start_utc - create_time).total_seconds()) <= 2:
                    matched = True
                    break

            if matched:
                live_pids_with_matching_open_row += 1
                continue

            candidate_rows = all_rows_by_pid.get(pid, [])
            matched_closed_after_snapshot = False
            for row in candidate_rows:
                create_time = dt.datetime.fromisoformat(str(row["create_time"]).replace(" ", "T")).replace(tzinfo=dt.timezone.utc)
                if abs((live_start_utc - create_time).total_seconds()) > 2:
                    continue

                exit_time_text = row.get("exit_time")
                if not exit_time_text:
                    continue

                exit_time = dt.datetime.fromisoformat(str(exit_time_text).replace(" ", "T")).replace(tzinfo=dt.timezone.utc)
                if exit_time >= snapshot_time:
                    matched_closed_after_snapshot = True
                    break

            if matched_closed_after_snapshot:
                live_pids_with_closed_row_after_snapshot += 1
            else:
                live_pids_missing_open_row += 1
                if len(sample_missing_live_pids) < 20:
                    sample_missing_live_pids.append(live_row)

        return {
            "live_system_processes": len(live_processes),
            "live_pids_with_matching_open_row": live_pids_with_matching_open_row,
            "live_pids_with_closed_row_after_snapshot": live_pids_with_closed_row_after_snapshot,
            "live_pids_missing_open_row": live_pids_missing_open_row,
            "sample_missing_live_pids": sample_missing_live_pids,
        }

    if os.name != "posix" or not Path("/proc").exists():
        return {
            "live_system_processes": None,
            "live_pids_with_matching_open_row": None,
            "live_pids_missing_open_row": None,
            "sample_missing_live_pids": [],
        }

    open_rows_by_pid: dict[int, list[dict[str, Any]]] = {}
    for row in open_rows:
        open_rows_by_pid.setdefault(int(row["process_id"]), []).append(row)

    live_pids_with_matching_open_row = 0
    live_pids_missing_open_row = 0
    sample_missing_live_pids: list[dict[str, Any]] = []

    for proc_dir in sorted(Path("/proc").iterdir(), key=lambda path: int(path.name) if path.name.isdigit() else -1):
        if not proc_dir.is_dir() or not proc_dir.name.isdigit():
            continue

        pid = int(proc_dir.name)
        live_start_utc = get_linux_live_process_start_utc(pid)
        if live_start_utc is None:
            continue

        candidate_rows = open_rows_by_pid.get(pid, [])
        matched = False
        for row in candidate_rows:
            create_time = dt.datetime.fromisoformat(str(row["create_time"]).replace(" ", "T")).replace(tzinfo=dt.timezone.utc)
            if abs((live_start_utc - create_time).total_seconds()) <= 2:
                matched = True
                break

        if matched:
            live_pids_with_matching_open_row += 1
        else:
            live_pids_missing_open_row += 1
            if len(sample_missing_live_pids) < 20:
                sample_missing_live_pids.append(
                    {
                        "process_id": pid,
                        "live_start_utc": live_start_utc.isoformat().replace("+00:00", "Z"),
                    }
                )

    return {
        "live_system_processes": live_pids_with_matching_open_row + live_pids_missing_open_row,
        "live_pids_with_matching_open_row": live_pids_with_matching_open_row,
        "live_pids_missing_open_row": live_pids_missing_open_row,
        "sample_missing_live_pids": sample_missing_live_pids,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--live-snapshot", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    live_snapshot = load_live_snapshot(args.live_snapshot)

    telemetry_exists_result = run_duckdb_json(
        args.db,
        "SELECT COUNT(*) AS has_telemetry FROM information_schema.tables WHERE table_name = 'process_retention_telemetry';",
    )
    telemetry_exists = bool(telemetry_exists_result[0][0]["has_telemetry"])

    sql_parts = [
        """
SELECT 'table_totals' AS section,
  COUNT(*) AS rows,
  COUNT(DISTINCT pid_hash) AS distinct_pid_hashes,
  COUNT(DISTINCT process_id) AS distinct_pids,
  COUNT(*) FILTER (WHERE exit_time IS NULL) AS open_rows,
  COUNT(*) FILTER (WHERE exit_time IS NOT NULL) AS closed_rows
FROM process;
""",
        """
SELECT 'by_name' AS section, process_name, COUNT(*) AS rows,
  COUNT(*) FILTER (WHERE exit_time IS NULL) AS open_rows,
  COUNT(*) FILTER (WHERE exit_time IS NOT NULL) AS closed_rows
FROM process
GROUP BY process_name
ORDER BY rows DESC
LIMIT 25;
""",
        """
SELECT 'duplicate_pid' AS section, process_id, COUNT(*) AS rows,
  COUNT(DISTINCT pid_hash) AS identities,
  COUNT(*) FILTER (WHERE exit_time IS NULL) AS open_rows
FROM process
GROUP BY process_id
HAVING COUNT(*) > 1
ORDER BY rows DESC
LIMIT 25;
""",
        """
SELECT 'stop_only_like' AS section,
  COUNT(*) AS rows
FROM process
WHERE create_time = exit_time AND exit_time IS NOT NULL;
        """,
        """
SELECT 'all_rows_detail' AS section,
  pid_hash,
  process_id,
  process_name,
  create_time,
  exit_time
FROM process
ORDER BY process_id, create_time;
        """,
        """
SELECT 'open_rows_detail' AS section,
  pid_hash,
  process_id,
  process_name,
  create_time
FROM process
WHERE exit_time IS NULL
ORDER BY process_id, create_time;
        """,
    ]

    if telemetry_exists:
        sql_parts.extend(
            [
                """
SELECT 'telemetry_totals' AS section,
  metric_name,
  SUM(metric_value) AS metric_value,
  MAX(observed_at) AS last_observed_at
FROM process_retention_telemetry
GROUP BY metric_name
ORDER BY metric_name;
""",
                """
SELECT 'telemetry_by_name' AS section,
  metric_name,
  process_name,
  SUM(metric_value) AS metric_value
FROM process_retention_telemetry
GROUP BY metric_name, process_name
ORDER BY metric_name, metric_value DESC
LIMIT 100;
""",
            ]
        )

    manifest_info = None
    manifest_csv = None
    if args.manifest:
        manifest = json.loads(args.manifest.read_text())
        pids = sorted({int(proc["observed_pid"]) for proc in manifest.get("processes", [])})
        manifest_info = {
            "manifest_processes": len(manifest.get("processes", [])),
            "manifest_cases": len(manifest.get("cases", [])),
            "manifest_distinct_pids": len(pids),
        }
        manifest_csv = args.manifest.parent / "manifest-pids.csv"
        with manifest_csv.open("w", encoding="utf-8") as handle:
            handle.write("pid\n")
            for pid in pids:
                handle.write(f"{pid}\n")
        path_sql = str(manifest_csv).replace("'", "''")
        sql_parts.extend(
            [
                f"""
WITH m AS (SELECT pid::INTEGER AS pid FROM read_csv_auto('{path_sql}')),
p AS (SELECT * FROM process)
SELECT
  COUNT(*) AS manifest_pids,
  COUNT(p.process_id) AS joined_rows,
  COUNT(DISTINCT p.process_id) AS observed_manifest_pids,
  COUNT(*) - COUNT(DISTINCT p.process_id) AS missing_manifest_pids,
  COUNT(p.process_id) FILTER (WHERE p.exit_time IS NULL) AS open_rows_for_manifest_pids,
  COUNT(p.process_id) FILTER (WHERE p.exit_time IS NOT NULL) AS closed_rows_for_manifest_pids,
  COUNT(DISTINCT p.process_id) FILTER (WHERE p.exit_time IS NULL) AS open_manifest_pids,
  COUNT(DISTINCT p.process_id) FILTER (WHERE p.exit_time IS NOT NULL) AS closed_manifest_pids
FROM m LEFT JOIN p ON p.process_id = m.pid;
""",
                f"""
WITH m AS (SELECT pid::INTEGER AS pid FROM read_csv_auto('{path_sql}'))
SELECT p.process_name, COUNT(*) AS rows,
  COUNT(*) FILTER (WHERE p.exit_time IS NULL) AS open_rows,
  COUNT(*) FILTER (WHERE p.exit_time IS NOT NULL) AS closed_rows
FROM m JOIN process p ON p.process_id = m.pid
GROUP BY p.process_name
ORDER BY rows DESC;
""",
            ]
        )

    sql = "\n".join(sql_parts)
    result_sets = run_duckdb_json(args.db, sql)
    summary = {
        "db": str(args.db),
        "manifest": str(args.manifest) if args.manifest else None,
        "live_snapshot": str(args.live_snapshot) if args.live_snapshot else None,
        "manifest_info": manifest_info,
        "telemetry_table_present": telemetry_exists,
        "table_totals": result_sets[0],
        "by_name": result_sets[1],
        "duplicate_pid": result_sets[2],
        "stop_only_like": result_sets[3],
        "all_rows_detail": result_sets[4],
        "open_rows_detail": result_sets[5],
    }

    summary["open_row_liveness"] = classify_open_rows(summary["open_rows_detail"], live_snapshot)
    summary["live_process_coverage"] = summarize_live_process_coverage(summary["open_rows_detail"], summary["all_rows_detail"], live_snapshot)

    next_result_index = 6
    if telemetry_exists:
        summary["telemetry_totals"] = result_sets[next_result_index]
        summary["telemetry_by_name"] = result_sets[next_result_index + 1]
        next_result_index += 2

    if args.manifest:
        summary["manifest_pid_summary"] = result_sets[next_result_index]
        summary["manifest_by_name"] = result_sets[next_result_index + 1]

    text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
