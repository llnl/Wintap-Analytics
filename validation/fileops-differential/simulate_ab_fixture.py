#!/usr/bin/env python3
"""Fixture generator for run_fop11_ab.sh --simulate: writes synthetic File
parquet into the simulated data root, timestamped 'now' so the script's live
harvest windows capture them. The OFF phase writes per-event rows; the ON
phase writes the aggregated equivalent (first-emit + summary) so the
comparator's count conservation is exercised end to end."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import duckdb


def filetime_now() -> int:
    return (int(time.time()) + 11644473600) * 10_000_000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=["off", "on"])
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--work-dir", required=True)
    args = parser.parse_args()

    ft = filetime_now()
    w = args.work_dir.rstrip("/")
    if args.phase == "off":
        # Raw per-event rows: 3 opens + 2 reads of f1, 1 open of f2.
        rows = [
            (111, f"{w}/f1.dat", "Open", 1, ft),
            (111, f"{w}/f1.dat", "Open", 1, ft),
            (111, f"{w}/f1.dat", "Open", 1, ft),
            (111, f"{w}/f1.dat", "Read", 1, ft),
            (111, f"{w}/f1.dat", "Read", 1, ft),
            (111, f"{w}/f2.dat", "Open", 1, ft),
        ]
    else:
        # Aggregated equivalent: first emits (count 1) + summaries (repeats).
        rows = [
            (222, f"{w}/f1.dat", "Open", 1, ft),
            (222, f"{w}/f1.dat", "Open", 2, ft),  # summary: 2 repeats
            (222, f"{w}/f1.dat", "Read", 1, ft),
            (222, f"{w}/f1.dat", "Read", 1, ft),
            (222, f"{w}/f2.dat", "Open", 1, ft),
        ]
    # Background noise outside the prefix, both phases.
    rows.append((999, "/var/unrelated/background.log", "Write", 1, ft))

    out_dir = Path(args.data_root) / "raw_sensor" / "raw_process_file"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"raw-File-sim-{args.phase}-{ft}.parquet"

    con = duckdb.connect()
    con.execute(
        "CREATE TABLE t (PID INTEGER, path VARCHAR, activityType VARCHAR, "
        "eventCount INTEGER, firstSeen BIGINT)"
    )
    con.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?)", rows)
    con.execute(f"COPY t TO '{out}' (FORMAT PARQUET)")
    con.close()
    print(f"fixture written: {out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
