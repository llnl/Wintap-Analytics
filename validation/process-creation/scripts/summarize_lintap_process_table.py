#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

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
    ]

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
    proc = subprocess.run(["sudo", "duckdb", "-json", str(args.db), "-c", sql], check=True, text=True, capture_output=True)
    result_sets = parse_duckdb_json_stream(proc.stdout)
    summary = {
        "db": str(args.db),
        "manifest": str(args.manifest) if args.manifest else None,
        "manifest_info": manifest_info,
        "table_totals": result_sets[0],
        "by_name": result_sets[1],
        "duplicate_pid": result_sets[2],
        "stop_only_like": result_sets[3],
    }
    if args.manifest:
        summary["manifest_pid_summary"] = result_sets[4]
        summary["manifest_by_name"] = result_sets[5]

    text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
