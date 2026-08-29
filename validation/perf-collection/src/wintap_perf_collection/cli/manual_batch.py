from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import threading
import time

from wintap_perf_collection.parquet import write_partitioned_parquet
from wintap_perf_collection.procfs import (
    ProcSnapshotPaths,
    collect_fd_map_row,
    collect_proc_status_row,
    collect_smaps_rollup_row,
)


@dataclass
class LineCapture:
    event_type: str
    command: str
    hostname: str
    pid: int
    process_name: str
    run_id: str
    rows: list[dict[str, str | int]] = field(default_factory=list)
    process: subprocess.Popen[str] | None = None
    thread: threading.Thread | None = None


def discover_pid_by_substring(proc_root: Path, process_name_substring: str) -> int:
    needle = process_name_substring.lower()
    candidates: list[int] = []
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        comm = entry / "comm"
        if not comm.exists():
            continue
        try:
            name = comm.read_text(encoding="utf-8").strip().lower()
        except OSError:
            continue
        if needle in name:
            candidates.append(int(entry.name))
    if not candidates:
        raise SystemExit(f"No process under {proc_root} matched substring: {process_name_substring!r}")
    return max(candidates)


def start_line_capture(event_type: str, command: str, hostname: str, pid: int, process_name: str, run_id: str) -> LineCapture:
    capture = LineCapture(
        event_type=event_type,
        command=command,
        hostname=hostname,
        pid=pid,
        process_name=process_name,
        run_id=run_id,
    )
    proc = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    capture.process = proc

    def reader() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            capture.rows.append(
                {
                    "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "hostname": hostname,
                    "pid": pid,
                    "process_name": process_name,
                    "run_id": run_id,
                    "command": command,
                    "line": line.rstrip("\n"),
                }
            )

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    capture.thread = thread
    return capture


def stop_line_capture(capture: LineCapture) -> None:
    if capture.process is None:
        return
    capture.process.terminate()
    try:
        capture.process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        capture.process.kill()
        capture.process.wait(timeout=5)
    if capture.thread is not None:
        capture.thread.join(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual-batch Lintap performance collectors")
    parser.add_argument("--data-root", type=Path, default=Path(os.environ.get("WINTAP_DATA_ROOT", "/tmp/lintap-perf")))
    parser.add_argument("--proc-root", type=Path, default=Path("/proc"))
    parser.add_argument("--pid", type=int)
    parser.add_argument("--process-name-substring", default="Lintap")
    parser.add_argument("--hostname", default=socket.gethostname())
    parser.add_argument("--run-id", default=f"perf-{int(time.time())}")
    parser.add_argument("--duration-seconds", type=int, default=300)
    parser.add_argument("--interval-seconds", type=float, default=5.0)
    parser.add_argument("--dotnet-counters-command", default="")
    parser.add_argument("--lintap-diag-command", default="")
    args = parser.parse_args()

    pid = args.pid or discover_pid_by_substring(args.proc_root, args.process_name_substring)
    paths = ProcSnapshotPaths(proc_root=args.proc_root, pid=pid)
    process_name = paths.comm.read_text(encoding="utf-8").strip()

    captures: list[LineCapture] = []
    if args.dotnet_counters_command:
        captures.append(start_line_capture("perf_dotnet_counters_raw", args.dotnet_counters_command, args.hostname, pid, process_name, args.run_id))
    if args.lintap_diag_command:
        captures.append(start_line_capture("perf_lintap_diag_raw", args.lintap_diag_command, args.hostname, pid, process_name, args.run_id))

    rows_by_event: dict[str, list[dict]] = defaultdict(list)
    started = time.time()
    try:
        while time.time() - started < args.duration_seconds:
            rows_by_event["perf_smaps_rollup"].append(collect_smaps_rollup_row(paths, args.run_id, hostname=args.hostname))
            rows_by_event["perf_proc_status"].append(collect_proc_status_row(paths, args.run_id, hostname=args.hostname))
            rows_by_event["perf_fd_map"].append(collect_fd_map_row(paths, args.run_id, hostname=args.hostname))
            time.sleep(args.interval_seconds)
    finally:
        for capture in captures:
            stop_line_capture(capture)
            rows_by_event[capture.event_type].extend(capture.rows)

    outputs: dict[str, str] = {}
    for event_type, rows in rows_by_event.items():
        out = write_partitioned_parquet(rows, args.data_root, event_type, args.run_id)
        if out is not None:
            outputs[event_type] = str(out)

    summary = {
        "run_id": args.run_id,
        "data_root": str(args.data_root),
        "proc_root": str(args.proc_root),
        "hostname": args.hostname,
        "pid": pid,
        "process_name": process_name,
        "duration_seconds": args.duration_seconds,
        "interval_seconds": args.interval_seconds,
        "outputs": outputs,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
