from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os
import platform
import shutil
import subprocess
import sys
import time

from .schema import CaseSpec, Manifest, ProcessSpec, utc_now_iso


def _iso(ts: float | None = None) -> str:
    dt = datetime.fromtimestamp(ts if ts is not None else time.time(), tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_pid_lines(stdout: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    for line in stdout.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        try:
            parsed[key.strip()] = int(value.strip())
        except ValueError:
            continue
    return parsed


def _which(name: str, fallback: str) -> str:
    return shutil.which(name) or fallback


def _python_parent_child_script(child_count: int = 1, child_sleep_seconds: float = 0.0) -> str:
    return (
        "import os, subprocess, sys; "
        "print(f'PARENT_PID={os.getpid()}', flush=True); "
        "children=[]; "
        f"child_count={child_count}; child_sleep={child_sleep_seconds!r}; "
        "\nfor idx in range(child_count):\n"
        "    child = subprocess.Popen([sys.executable, '-c', f'import time; time.sleep({child_sleep!r})'])\n"
        "    children.append(child)\n"
        "    print(f'CHILD_PID_{idx}={child.pid}', flush=True)\n"
        "\nfor child in children:\n"
        "    child.wait()\n"
    )


class WorkloadBuilder:
    def __init__(self, run_id: str, profile: str = "process-baseline-v1") -> None:
        self.run_id = run_id
        self.profile = profile
        self.cases: list[CaseSpec] = []
        self.processes: list[ProcessSpec] = []
        self.notes: list[str] = []

    def add_simple_exec(self) -> None:
        started = time.time()
        if os.name == "nt":
            command = [sys.executable, "-c", "import os; print(f'CHILD_PID={os.getpid()}')"]
            proc = subprocess.run(command, check=True, text=True, capture_output=True)
            ended = time.time()
            pids = _parse_pid_lines(proc.stdout)
            pid = pids.get("CHILD_PID")
            expected_name = Path(sys.executable).name
        else:
            sh = _which("sh", "/bin/sh")
            true = _which("true", "/usr/bin/true")
            command = [sh, "-c", f"echo CHILD_PID=$$; {true}"]
            proc = subprocess.run(command, check=True, text=True, capture_output=True)
            ended = time.time()
            pids = _parse_pid_lines(proc.stdout)
            pid = pids.get("CHILD_PID")
            expected_name = "sh"
        if pid is None:
            raise RuntimeError(f"simple_exec did not report child pid: {proc.stdout!r}")
        case_id = "simple_exec_001"
        ref = "simple_exec_child_001"
        self.cases.append(
            CaseSpec(
                case_id=case_id,
                case_type="simple_exec",
                started_utc=_iso(started),
                ended_utc=_iso(ended),
                expected_events=["exec_attempt", "exec_success", "process_exit"],
                tags=["process", "exec"],
                process_refs=[ref],
            )
        )
        self.processes.append(
            ProcessSpec(
                process_ref=ref,
                case_id=case_id,
                role="child",
                observed_pid=pid,
                observed_ppid=os.getpid(),
                command=command,
                expected_name=expected_name,
                started_by_workload_utc=_iso(started),
                ended_by_workload_utc=_iso(ended),
                provenance_markers=[f"run_id={self.run_id}", f"case_id={case_id}"],
            )
        )

    def add_fork_exec(self) -> None:
        started = time.time()
        if os.name == "nt":
            command = [sys.executable, "-c", _python_parent_child_script(child_count=1, child_sleep_seconds=1)]
            child_command = [sys.executable, "-c", "import time; time.sleep(1)"]
            expected_parent_name = Path(sys.executable).name
            expected_child_name = Path(sys.executable).name
        else:
            bash = _which("bash", "/bin/bash")
            sleep = _which("sleep", "/bin/sleep")
            command = [bash, "-c", f"echo PARENT_PID=$$; {sleep} 1 & echo CHILD_PID_0=$!; wait"]
            child_command = [sleep, "1"]
            expected_parent_name = "bash"
            expected_child_name = "sleep"
        proc = subprocess.run(command, check=True, text=True, capture_output=True)
        ended = time.time()
        pids = _parse_pid_lines(proc.stdout)
        parent = pids.get("PARENT_PID")
        child = pids.get("CHILD_PID_0")
        if parent is None or child is None:
            raise RuntimeError(f"fork_exec did not report pids: {proc.stdout!r}")
        case_id = "fork_exec_001"
        parent_ref = "fork_exec_parent_001"
        child_ref = "fork_exec_child_001"
        self.cases.append(
            CaseSpec(
                case_id=case_id,
                case_type="fork_exec",
                started_utc=_iso(started),
                ended_utc=_iso(ended),
                expected_events=["process_fork", "exec_success", "process_exit"],
                tags=["process", "parent-child", "exec_success"],
                process_refs=[parent_ref, child_ref],
            )
        )
        self.processes.extend(
            [
                ProcessSpec(
                    process_ref=parent_ref,
                    case_id=case_id,
                    role="parent",
                    observed_pid=parent,
                    command=command,
                    expected_name=expected_parent_name,
                    started_by_workload_utc=_iso(started),
                    ended_by_workload_utc=_iso(ended),
                    provenance_markers=[f"run_id={self.run_id}", f"case_id={case_id}"],
                ),
                ProcessSpec(
                    process_ref=child_ref,
                    case_id=case_id,
                    role="child",
                    observed_pid=child,
                    observed_ppid=parent,
                    command=child_command,
                    expected_name=expected_child_name,
                    parent_ref=parent_ref,
                    started_by_workload_utc=_iso(started),
                    ended_by_workload_utc=_iso(ended),
                    provenance_markers=[f"run_id={self.run_id}", f"case_id={case_id}"],
                ),
            ]
        )

    def add_short_lived_burst(self, count: int = 6) -> None:
        started = time.time()
        count = max(1, count)
        if os.name == "nt":
            command = [sys.executable, "-c", _python_parent_child_script(child_count=count, child_sleep_seconds=0)]
            child_command = [sys.executable, "-c", "import time; time.sleep(0)"]
            expected_parent_name = Path(sys.executable).name
            expected_child_name = Path(sys.executable).name
        else:
            bash = _which("bash", "/bin/bash")
            true = _which("true", "/usr/bin/true")
            children = "".join(f"{true} & echo CHILD_PID_{idx}=$!; " for idx in range(count))
            command = [bash, "-c", f"echo PARENT_PID=$$; {children} wait"]
            child_command = [true]
            expected_parent_name = "bash"
            expected_child_name = "true"
        proc = subprocess.run(command, check=True, text=True, capture_output=True)
        ended = time.time()
        pids = _parse_pid_lines(proc.stdout)
        parent = pids.get("PARENT_PID")
        if parent is None:
            raise RuntimeError(f"short_lived did not report parent pid: {proc.stdout!r}")
        case_id = "short_lived_burst_001"
        refs = ["short_lived_parent_001"]
        self.processes.append(
            ProcessSpec(
                process_ref="short_lived_parent_001",
                case_id=case_id,
                role="parent",
                observed_pid=parent,
                command=command,
                expected_name=expected_parent_name,
                started_by_workload_utc=_iso(started),
                ended_by_workload_utc=_iso(ended),
                provenance_markers=[f"run_id={self.run_id}", f"case_id={case_id}"],
            )
        )
        for idx in range(count):
            pid = pids.get(f"CHILD_PID_{idx}")
            if pid is None:
                continue
            ref = f"short_lived_child_{idx:03d}"
            refs.append(ref)
            self.processes.append(
                ProcessSpec(
                    process_ref=ref,
                    case_id=case_id,
                    role="child",
                    observed_pid=pid,
                    observed_ppid=parent,
                    command=child_command,
                    expected_name=expected_child_name,
                    parent_ref="short_lived_parent_001",
                    started_by_workload_utc=_iso(started),
                    ended_by_workload_utc=_iso(ended),
                    provenance_markers=[f"run_id={self.run_id}", f"case_id={case_id}", f"seq={idx}"],
                )
            )
        self.cases.append(
            CaseSpec(
                case_id=case_id,
                case_type="short_lived_burst",
                started_utc=_iso(started),
                ended_utc=_iso(ended),
                expected_events=["process_fork", "exec_attempt", "exec_success", "process_exit"],
                required=False,
                tags=["process", "burst", "short-lived"],
                process_refs=refs,
                notes=["Recall distribution matters more than binary pass/fail for this case."],
            )
        )

    def add_execveat_if_supported(self) -> None:
        if platform.system().lower() != "linux" or not hasattr(os, "execveat"):
            self.notes.append("execveat_fexecve skipped: os.execveat is unavailable on this platform")
            return
        started = time.time()
        py = sys.executable.replace("'", "'\\''")
        bash = _which("bash", "/bin/bash")
        sleep = _which("sleep", "/bin/sleep")
        proc = subprocess.run(
            [
                bash,
                "-c",
                "echo PARENT_PID=$$; "
                f"'{py}' -c 'import os; fd=os.open(\"{sleep}\", os.O_RDONLY); "
                f"os.execveat(fd, \"\", [\"{sleep}\",\"1\"], os.environ, os.AT_EMPTY_PATH)' & "
                "echo CHILD_PID=$!; wait",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        ended = time.time()
        pids = _parse_pid_lines(proc.stdout)
        parent = pids.get("PARENT_PID")
        child = pids.get("CHILD_PID")
        if parent is None or child is None:
            raise RuntimeError(f"execveat did not report pids: {proc.stdout!r}")
        case_id = "execveat_fexecve_001"
        parent_ref = "execveat_parent_001"
        child_ref = "execveat_child_001"
        self.cases.append(
            CaseSpec(
                case_id=case_id,
                case_type="execveat_fexecve",
                started_utc=_iso(started),
                ended_utc=_iso(ended),
                expected_events=["exec_attempt", "exec_success", "process_exit"],
                tags=["process", "execveat", "at_empty_path"],
                process_refs=[parent_ref, child_ref],
            )
        )
        self.processes.extend(
            [
                ProcessSpec(parent_ref, case_id, "parent", parent, command=[bash], expected_name="bash"),
                ProcessSpec(
                    child_ref,
                    case_id,
                    "child",
                    child,
                    observed_ppid=parent,
                    command=[sleep, "1"],
                    expected_name="sleep",
                    parent_ref=parent_ref,
                    provenance_markers=["execveat_flags=0x00001000"],
                ),
            ]
        )

    def manifest(self) -> Manifest:
        return Manifest(
            schema_version="process-validation-manifest/v1",
            run_id=self.run_id,
            created_utc=utc_now_iso(),
            workload_profile=self.profile,
            cases=self.cases,
            processes=self.processes,
            notes=self.notes,
        )


def generate_process_baseline(run_id: str, short_lived_children: int = 6) -> Manifest:
    builder = WorkloadBuilder(run_id)
    builder.add_simple_exec()
    builder.add_fork_exec()
    builder.add_execveat_if_supported()
    builder.add_short_lived_burst(short_lived_children)
    return builder.manifest()
