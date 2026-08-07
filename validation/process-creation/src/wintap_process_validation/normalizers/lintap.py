from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import glob

from ..schema import NormalizedEvent, write_jsonl


def normalize_lintap_process_rows(rows: Iterable[dict[str, Any]], run_id: str) -> dict[str, list[NormalizedEvent]]:
    tables: dict[str, list[NormalizedEvent]] = {
        "process_identity": [],
        "process_fork": [],
        "exec_attempt": [],
        "exec_success": [],
        "process_exit": [],
        "process_rundown": [],
        "sensor_loss": [],
    }

    seen_identities: set[str] = set()
    for row in rows:
        pid = _to_int(_pick(row, "PID", "pid"))
        if pid is None:
            continue
        pid_hash = _to_str(_pick(row, "PidHash", "pid_hash")) or f"lintap:pid:{pid}:unknown"
        activity = (_to_str(_pick(row, "ActivityType", "activity_type")) or "").lower()
        message_type = (_to_str(_pick(row, "MessageType", "message_type")) or "").lower()
        if message_type and "process" not in message_type:
            continue

        case_id = _extract_marker(row, "case_id") or _to_str(_pick(row, "case_id", "CaseId"))
        arguments = _to_str(_pick(row, "Process_Arguments", "Arguments", "process_arguments")) or ""
        command_line = _to_str(_pick(row, "Process_CommandLine", "CommandLine", "process_command_line"))
        parent_pid = _to_int(_pick(row, "Process_ParentPID", "ParentPid", "parent_pid"))
        parent_hash = _to_str(_pick(row, "Process_ParentPidHash", "ParentPidHash", "parent_pid_hash"))
        event_time = _to_str(_pick(row, "EventTime", "CapturedUtc", "captured_utc", "event_time"))
        process_name = _to_str(_pick(row, "ProcessName", "Process_Name", "Name", "process_name"))
        process_path = _to_str(_pick(row, "ProcessPath", "Process_Path", "Path", "process_path"))

        if pid_hash not in seen_identities:
            tables["process_identity"].append(
                {
                    "sensor": "lintap",
                    "run_id": run_id,
                    "tool_process_id": pid_hash,
                    "pid": pid,
                    "start_time_utc": event_time,
                    "identity_confidence": "high" if pid_hash else "low",
                    "identity_source": "pid_hash",
                    "pid_reuse_safe": True,
                    "case_id": case_id,
                    "raw": _compact_raw(row),
                }
            )
            seen_identities.add(pid_hash)

        base = {
            "sensor": "lintap",
            "run_id": run_id,
            "case_id": case_id,
            "event_time_utc": event_time,
            "pid": pid,
            "identity": pid_hash,
            "parent_pid": parent_pid,
            "parent_identity": parent_hash,
            "executable": process_path,
            "process_name": process_name,
            "command_line": command_line,
            "raw": _compact_raw(row),
        }

        if activity == "refresh":
            tables["process_rundown"].append({**base, "source_hook": "proc_rundown"})
            continue
        if activity == "stop":
            tables["process_exit"].append(base)
            continue
        if activity != "start":
            continue

        if "PROC_START_SRC=sched_exec" in arguments:
            tables["exec_success"].append({**base, "source_hook": "sched_process_exec"})
        elif "PROC_START_SRC=execve_or_execveat" in arguments:
            syscall = "execveat" if "FLAGS=0x00001000" in arguments else "execve_or_execveat"
            tables["exec_attempt"].append(
                {
                    **base,
                    "syscall": syscall,
                    "flags": _extract_flags(arguments),
                    "source_hook": "sys_enter_execve_or_execveat",
                }
            )
        else:
            # Older/alternate schemas may not preserve breadcrumbs. Keep the row
            # as exec_success because Wintap Process Start historically meant a
            # process start-like event, but mark provenance as inferred.
            tables["exec_success"].append({**base, "source_hook": "lintap_process_start_inferred"})

    return tables


def write_lintap_normalized(rows: Iterable[dict[str, Any]], run_id: str, out_dir: Path) -> None:
    tables = normalize_lintap_process_rows(rows, run_id)
    for table, table_rows in tables.items():
        write_jsonl(out_dir / f"{table}.jsonl", table_rows)


def read_lintap_process_parquet(parquet_root: Path) -> list[dict[str, Any]]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("duckdb is required for Parquet normalization. Run with `uv run --extra parquet ...`.") from exc

    files = [Path(path) for path in glob.glob(str(parquet_root / "**" / "*.parquet*"), recursive=True)]
    process_files = [path for path in files if "process" in str(path).lower()]
    selected = process_files or files
    if not selected:
        return []
    file_list = ", ".join("'" + str(path).replace("'", "''") + "'" for path in selected)
    sql = f"SELECT * FROM read_parquet([{file_list}], union_by_name=true)"
    con = duckdb.connect(database=":memory:")
    try:
        result = con.execute(sql)
        cols = [desc[0] for desc in result.description]
        return [dict(zip(cols, row)) for row in result.fetchall()]
    finally:
        con.close()


def _pick(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row:
            return row[name]
    return None


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _extract_marker(row: dict[str, Any], key: str) -> str | None:
    text = _to_str(_pick(row, "Process_Arguments", "Arguments", "process_arguments")) or ""
    prefix = key + "="
    for token in text.split():
        if token.startswith(prefix):
            return token[len(prefix) :]
    return None


def _extract_flags(arguments: str) -> str | None:
    for token in arguments.split():
        if token.startswith("FLAGS="):
            return token.split("=", 1)[1]
    return None


def _compact_raw(row: dict[str, Any]) -> dict[str, Any]:
    keep = [
        "PID",
        "MessageType",
        "ActivityType",
        "PidHash",
        "Process_ParentPID",
        "Process_ParentPidHash",
        "ParentPid",
        "ParentPidHash",
        "Process_Arguments",
        "Arguments",
    ]
    return {key: row[key] for key in keep if key in row}
