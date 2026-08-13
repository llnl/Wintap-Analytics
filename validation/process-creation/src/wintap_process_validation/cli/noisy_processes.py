from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate noisy mixed process creation workload")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--duration-seconds", type=int, default=900)
    parser.add_argument("--interval-seconds", type=float, default=5.0)
    parser.add_argument("--short-per-interval", type=int, default=12)
    parser.add_argument("--long-per-minute", type=int, default=3)
    parser.add_argument("--long-lived-seconds", type=int, default=45)
    args = parser.parse_args()

    run_id = args.run_id or f"noisy-{int(time.time())}"
    args.run_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = args.run_dir / "workload-stdout.log"
    stderr_path = args.run_dir / "workload-stderr.log"

    parameters = vars(args).copy()
    parameters["run_dir"] = str(args.run_dir)
    parameters["run_id"] = run_id

    manifest: dict = {
        "schema_version": "process-validation-manifest/v1",
        "run_id": run_id,
        "created_utc": iso_now(),
        "workload_profile": "noisy-process-mixed-v1",
        "parameters": parameters,
        "cases": [],
        "processes": [],
        "notes": [],
    }

    live: list[subprocess.Popen] = []
    start = time.time()
    next_long = start
    seq = 0

    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        try:
            while time.time() - start < args.duration_seconds:
                now = time.time()
                case_id = f"short_burst_{seq:05d}"
                manifest["cases"].append(
                    {
                        "case_id": case_id,
                        "case_type": "short_burst",
                        "started_utc": iso_now(),
                        "ended_utc": None,
                        "expected_events": ["exec_attempt", "exec_success", "process_exit"],
                        "required": False,
                        "tags": ["short-lived", "burst"],
                        "process_refs": [],
                    }
                )
                for idx in range(args.short_per_interval):
                    ref = f"{case_id}_proc_{idx:03d}"
                    marker = f"run_id={run_id} case_id={case_id} seq={idx}"
                    if os.name == "nt":
                        command = [sys.executable, "-c", "pass", marker]
                        expected_name = Path(sys.executable).name
                    else:
                        command = ["bash", "-c", f": # {marker}"]
                        expected_name = "bash"
                    proc = subprocess.Popen(
                        command,
                        stdout=out,
                        stderr=err,
                        text=True,
                    )
                    manifest["cases"][-1]["process_refs"].append(ref)
                    manifest["processes"].append(
                        {
                            "process_ref": ref,
                            "case_id": case_id,
                            "role": "short_child",
                            "observed_pid": proc.pid,
                            "observed_ppid": os.getpid(),
                            "command": command,
                            "expected_name": expected_name,
                            "started_by_workload_utc": iso_now(),
                            "parent_ref": None,
                            "provenance_markers": [marker],
                        }
                    )
                    proc.wait(timeout=10)

                if now >= next_long:
                    case_id = f"long_lived_{seq:05d}"
                    manifest["cases"].append(
                        {
                            "case_id": case_id,
                            "case_type": "long_lived",
                            "started_utc": iso_now(),
                            "ended_utc": None,
                            "expected_events": ["exec_attempt", "exec_success", "process_exit"],
                            "required": False,
                            "tags": ["long-lived"],
                            "process_refs": [],
                        }
                    )
                    for idx in range(args.long_per_minute):
                        ref = f"{case_id}_proc_{idx:03d}"
                        marker = f"run_id={run_id} case_id={case_id} seq={idx}"
                        proc = subprocess.Popen(
                            [sys.executable, "-c", f"import time; time.sleep({args.long_lived_seconds})", marker],
                            stdout=out,
                            stderr=err,
                            text=True,
                        )
                        live.append(proc)
                        manifest["cases"][-1]["process_refs"].append(ref)
                        manifest["processes"].append(
                            {
                                "process_ref": ref,
                                "case_id": case_id,
                                "role": "long_child",
                                "observed_pid": proc.pid,
                                "observed_ppid": os.getpid(),
                                "command": [sys.executable, "-c", f"import time; time.sleep({args.long_lived_seconds})", marker],
                                "expected_name": Path(sys.executable).name,
                                "started_by_workload_utc": iso_now(),
                                "parent_ref": None,
                                "provenance_markers": [marker],
                            }
                        )
                    next_long = now + 60

                seq += 1
                time.sleep(args.interval_seconds)
        finally:
            for proc in live:
                try:
                    proc.wait(timeout=args.long_lived_seconds + 15)
                except subprocess.TimeoutExpired:
                    proc.send_signal(signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()

    ended = iso_now()
    for case in manifest["cases"]:
        case["ended_utc"] = ended
    by_ref = {p["process_ref"]: p for p in manifest["processes"]}
    for proc in manifest["processes"]:
        proc["ended_by_workload_utc"] = ended

    manifest_path = args.run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"run_id": run_id, "run_dir": str(args.run_dir), "processes": len(manifest["processes"]), "cases": len(manifest["cases"]), "manifest": str(manifest_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
