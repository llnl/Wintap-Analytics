from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
from tempfile import TemporaryDirectory
import threading
import time
import re

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


@dataclass
class DotnetCollectCapture:
    hostname: str
    pid: int
    process_name: str
    run_id: str
    fmt: str
    command: str
    output_path: Path
    temp_dir: TemporaryDirectory[str]
    process: subprocess.Popen[str]


def normalize_counter_name(counter_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", counter_name.lower()).strip("_")


def normalize_dotnet_timestamp(raw: str) -> str:
    raw = raw.strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        parsed = datetime.strptime(raw, "%m/%d/%Y %H:%M:%S").astimezone()
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def split_counter_name_and_tags(raw: str) -> tuple[str, str]:
    match = re.match(r"^(?P<name>.+?)(?:\[(?P<tags>.+)\])?$", raw.strip())
    if match is None:
        return raw.strip(), ""
    return match.group("name").strip(), (match.group("tags") or "").strip()


def build_counter_key(provider: str, counter_name: str, tags: str) -> str:
    parts = [normalize_counter_name(provider), normalize_counter_name(counter_name)]
    if tags:
        for tag in tags.split(","):
            parts.append(normalize_counter_name(tag))
    return "_".join(part for part in parts if part)


def parse_dotnet_collect_json(
    text: str,
    *,
    hostname: str,
    pid: int,
    process_name: str,
    run_id: str,
    command: str,
) -> list[dict[str, str | int | float]]:
    payload = json.loads(text)
    parsed_rows: list[dict[str, str | int | float]] = []

    for event in payload.get("Events", []):
        value = event.get("value")
        if not isinstance(value, int | float):
            continue

        provider = str(event.get("provider", "")).strip()
        counter_name = str(event.get("name", "")).strip()
        tags = str(event.get("tags", "")).strip()
        if not provider or not counter_name:
            continue

        parsed_rows.append(
            {
                "time": normalize_dotnet_timestamp(str(event.get("timestamp", ""))),
                "hostname": hostname,
                "pid": pid,
                "process_name": process_name,
                "run_id": run_id,
                "command": command,
                "counter_provider": provider,
                "counter_name": counter_name,
                "counter_key": build_counter_key(provider, counter_name, tags),
                "counter_type": str(event.get("counterType", "")).strip(),
                "counter_tags": tags,
                "meter_tags": str(event.get("meterTags", "")).strip(),
                "instrument_tags": str(event.get("instrumentTags", "")).strip(),
                "value": float(value),
            }
        )

    return parsed_rows


def parse_dotnet_collect_csv(
    text: str,
    *,
    hostname: str,
    pid: int,
    process_name: str,
    run_id: str,
    command: str,
) -> list[dict[str, str | int | float]]:
    parsed_rows: list[dict[str, str | int | float]] = []
    reader = csv.DictReader(io.StringIO(text))

    for row in reader:
        provider = str(row.get("Provider", "")).strip()
        raw_counter_name = str(row.get("Counter Name", "")).strip()
        counter_type = str(row.get("Counter Type", "")).strip()
        value_text = str(row.get("Mean/Increment", "")).strip()
        if not provider or not raw_counter_name or not value_text:
            continue

        counter_name, tags = split_counter_name_and_tags(raw_counter_name)

        try:
            value = float(value_text.replace(",", ""))
        except ValueError:
            continue

        parsed_rows.append(
            {
                "time": normalize_dotnet_timestamp(str(row.get("Timestamp", ""))),
                "hostname": hostname,
                "pid": pid,
                "process_name": process_name,
                "run_id": run_id,
                "command": command,
                "counter_provider": provider,
                "counter_name": counter_name,
                "counter_key": build_counter_key(provider, counter_name, tags),
                "counter_type": counter_type,
                "counter_tags": tags,
                "meter_tags": "",
                "instrument_tags": "",
                "value": value,
            }
        )

    return parsed_rows


def format_duration_for_dotnet(seconds: int) -> str:
    days, remainder = divmod(max(0, seconds), 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, secs = divmod(remainder, 60)
    return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"


def start_dotnet_counters_collect(
    *,
    dotnet_counters_binary: str,
    fmt: str,
    refresh_interval: int,
    duration_seconds: int,
    hostname: str,
    pid: int,
    process_name: str,
    run_id: str,
) -> DotnetCollectCapture:
    temp_dir = TemporaryDirectory(prefix="wpc-dotnet-counters-")
    output_path = Path(temp_dir.name) / f"dotnet-counters.{fmt}"
    output_stem = output_path.with_suffix("")
    command_parts = [
        dotnet_counters_binary,
        "collect",
        "--process-id",
        str(pid),
        "--refresh-interval",
        str(refresh_interval),
        "--format",
        fmt,
        "--output",
        str(output_stem),
        "--duration",
        format_duration_for_dotnet(duration_seconds),
        "--counters",
        "System.Runtime",
    ]
    process = subprocess.Popen(command_parts, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return DotnetCollectCapture(
        hostname=hostname,
        pid=pid,
        process_name=process_name,
        run_id=run_id,
        fmt=fmt,
        command=" ".join(shlex.quote(part) for part in command_parts),
        output_path=output_path,
        temp_dir=temp_dir,
        process=process,
    )


def finish_dotnet_counters_collect(capture: DotnetCollectCapture) -> list[dict[str, str | int | float]]:
    try:
        try:
            stdout, _ = capture.process.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            capture.process.kill()
            stdout, _ = capture.process.communicate(timeout=5)
            raise RuntimeError(f"dotnet-counters collect timed out: {stdout.strip()}")

        if capture.process.returncode != 0:
            raise RuntimeError(f"dotnet-counters collect failed: {stdout.strip()}")
        if not capture.output_path.exists():
            raise RuntimeError(f"dotnet-counters collect did not produce {capture.output_path}")

        text = capture.output_path.read_text(encoding="utf-8")
        if capture.fmt == "json":
            rows = parse_dotnet_collect_json(
                text,
                hostname=capture.hostname,
                pid=capture.pid,
                process_name=capture.process_name,
                run_id=capture.run_id,
                command=capture.command,
            )
        else:
            rows = parse_dotnet_collect_csv(
                text,
                hostname=capture.hostname,
                pid=capture.pid,
                process_name=capture.process_name,
                run_id=capture.run_id,
                command=capture.command,
            )
        if not rows:
            raise RuntimeError(f"dotnet-counters collect produced no parseable rows from {capture.output_path}")
        return rows
    finally:
        capture.temp_dir.cleanup()


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
    parser.add_argument("--dotnet-counters-format", choices=("json", "csv"), default="")
    parser.add_argument("--dotnet-counters-binary", default="dotnet-counters")
    parser.add_argument("--dotnet-counters-refresh-interval", type=int, default=5)
    parser.add_argument("--lintap-diag-command", default="")
    args = parser.parse_args()

    pid = args.pid or discover_pid_by_substring(args.proc_root, args.process_name_substring)
    paths = ProcSnapshotPaths(proc_root=args.proc_root, pid=pid)
    process_name = paths.comm.read_text(encoding="utf-8").strip()

    captures: list[LineCapture] = []
    dotnet_capture: DotnetCollectCapture | None = None
    collector_errors: dict[str, str] = {}
    if args.dotnet_counters_format:
        dotnet_capture = start_dotnet_counters_collect(
            dotnet_counters_binary=args.dotnet_counters_binary,
            fmt=args.dotnet_counters_format,
            refresh_interval=args.dotnet_counters_refresh_interval,
            duration_seconds=args.duration_seconds,
            hostname=args.hostname,
            pid=pid,
            process_name=process_name,
            run_id=args.run_id,
        )
    if args.lintap_diag_command:
        captures.append(start_line_capture("perf_lintap_diag_raw", args.lintap_diag_command, args.hostname, pid, process_name, args.run_id))

    rows_by_event: dict[str, list[dict]] = defaultdict(list)
    started = time.time()
    try:
        while time.time() - started < args.duration_seconds:
            for event_type, collector in (
                ("perf_smaps_rollup", collect_smaps_rollup_row),
                ("perf_proc_status", collect_proc_status_row),
                ("perf_fd_map", collect_fd_map_row),
            ):
                try:
                    rows_by_event[event_type].append(collector(paths, args.run_id, hostname=args.hostname))
                except PermissionError as exc:
                    collector_errors.setdefault(event_type, f"permission denied: {exc}")
                except FileNotFoundError as exc:
                    collector_errors.setdefault(event_type, f"missing procfs path: {exc}")
            time.sleep(args.interval_seconds)
    finally:
        for capture in captures:
            stop_line_capture(capture)
            rows_by_event[capture.event_type].extend(capture.rows)
        if dotnet_capture is not None:
            try:
                rows_by_event["perf_dotnet_counters"].extend(finish_dotnet_counters_collect(dotnet_capture))
            except RuntimeError as exc:
                collector_errors.setdefault("perf_dotnet_counters", str(exc))

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
        "collector_errors": collector_errors,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
