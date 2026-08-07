from __future__ import annotations

from pathlib import Path

from .schema import Manifest, write_jsonl


def write_mock_normalized_events(manifest: Manifest, normalized_dir: Path, *, inject_duplicate: bool = True) -> None:
    """Write normalized mock events for local evaluator development.

    The mock intentionally models ideal capture for required events and can inject
    one duplicate exec_success row to validate duplicate detection.
    """

    identity_rows = []
    identity_by_ref: dict[str, str] = {}
    for proc in manifest.processes:
        identity = f"mock:{proc.observed_pid}:{proc.process_ref}"
        identity_by_ref[proc.process_ref] = identity
        identity_rows.append(
            {
                "sensor": "mock",
                "run_id": manifest.run_id,
                "tool_process_id": identity,
                "pid": proc.observed_pid,
                "start_time_utc": proc.started_by_workload_utc,
                "identity_confidence": "high",
                "identity_source": "mock",
                "pid_reuse_safe": True,
                "process_ref": proc.process_ref,
                "case_id": proc.case_id,
            }
        )

    fork_rows = []
    attempt_rows = []
    success_rows = []
    exit_rows = []

    for case in manifest.cases:
        case_procs = [proc for proc in manifest.processes if proc.case_id == case.case_id]
        children = [proc for proc in case_procs if proc.parent_ref]
        target = children[0] if children else (case_procs[0] if case_procs else None)
        if "process_fork" in case.expected_events:
            for child in children:
                fork_rows.append(
                    {
                        "sensor": "mock",
                        "run_id": manifest.run_id,
                        "case_id": case.case_id,
                        "parent_pid": child.observed_ppid,
                        "child_pid": child.observed_pid,
                        "parent_identity": identity_by_ref.get(child.parent_ref or ""),
                        "child_identity": identity_by_ref[child.process_ref],
                        "fork_kind": "unknown",
                        "source_hook": "mock_fork",
                    }
                )
        if target and "exec_attempt" in case.expected_events:
            attempt_rows.append(
                {
                    "sensor": "mock",
                    "run_id": manifest.run_id,
                    "case_id": case.case_id,
                    "pid": target.observed_pid,
                    "identity": identity_by_ref[target.process_ref],
                    "syscall": "execveat" if "execveat" in case.case_type else "execve",
                    "flags": "0x00001000" if "execveat" in case.case_type else "0x00000000",
                    "source_hook": "mock_exec_attempt",
                }
            )
        if target and "exec_success" in case.expected_events:
            row = {
                "sensor": "mock",
                "run_id": manifest.run_id,
                "case_id": case.case_id,
                "pid": target.observed_pid,
                "identity": identity_by_ref[target.process_ref],
                "executable": target.expected_executable,
                "command_line": " ".join(target.command),
                "parent_pid": target.observed_ppid,
                "parent_identity": identity_by_ref.get(target.parent_ref or ""),
                "source_hook": "sched_process_exec",
            }
            success_rows.append(row)
            if inject_duplicate and case.case_type == "fork_exec":
                success_rows.append(dict(row))
        if "process_exit" in case.expected_events:
            for proc in case_procs:
                exit_rows.append(
                    {
                        "sensor": "mock",
                        "run_id": manifest.run_id,
                        "case_id": case.case_id,
                        "pid": proc.observed_pid,
                        "identity": identity_by_ref[proc.process_ref],
                    }
                )

    write_jsonl(normalized_dir / "process_identity.jsonl", identity_rows)
    write_jsonl(normalized_dir / "process_fork.jsonl", fork_rows)
    write_jsonl(normalized_dir / "exec_attempt.jsonl", attempt_rows)
    write_jsonl(normalized_dir / "exec_success.jsonl", success_rows)
    write_jsonl(normalized_dir / "process_exit.jsonl", exit_rows)
    write_jsonl(normalized_dir / "sensor_loss.jsonl", [])
