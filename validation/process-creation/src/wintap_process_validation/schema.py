from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal
import json


EventName = Literal[
    "process_fork",
    "exec_attempt",
    "exec_success",
    "process_exit",
    "process_rundown",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ProcessSpec:
    process_ref: str
    case_id: str
    role: str
    observed_pid: int
    observed_ppid: int | None = None
    command: list[str] = field(default_factory=list)
    expected_executable: str | None = None
    expected_name: str | None = None
    started_by_workload_utc: str | None = None
    ended_by_workload_utc: str | None = None
    parent_ref: str | None = None
    identity_expectation: str = "pid_plus_start_time"
    provenance_markers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FileSpec:
    file_ref: str
    case_id: str
    path: str
    expected_activities: list[str]
    owner_process_ref: str | None = None


@dataclass(frozen=True)
class NetworkSpec:
    network_ref: str
    case_id: str
    protocol: str
    direction: str
    remote_host: str
    remote_port: int
    owner_process_ref: str | None = None
    payload_marker: str | None = None


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    case_type: str
    started_utc: str
    ended_utc: str | None
    expected_events: list[EventName]
    required: bool = True
    tags: list[str] = field(default_factory=list)
    process_refs: list[str] = field(default_factory=list)
    file_refs: list[str] = field(default_factory=list)
    network_refs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Manifest:
    schema_version: str
    run_id: str
    created_utc: str
    workload_profile: str
    cases: list[CaseSpec] = field(default_factory=list)
    processes: list[ProcessSpec] = field(default_factory=list)
    files: list[FileSpec] = field(default_factory=list)
    network: list[NetworkSpec] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n")

    @staticmethod
    def read(path: Path) -> "Manifest":
        data = json.loads(path.read_text())
        return Manifest(
            schema_version=data["schema_version"],
            run_id=data["run_id"],
            created_utc=data["created_utc"],
            workload_profile=data["workload_profile"],
            cases=[CaseSpec(**item) for item in data.get("cases", [])],
            processes=[ProcessSpec(**item) for item in data.get("processes", [])],
            files=[FileSpec(**item) for item in data.get("files", [])],
            network=[NetworkSpec(**item) for item in data.get("network", [])],
            notes=list(data.get("notes", [])),
        )


NormalizedEvent = dict[str, Any]


def write_jsonl(path: Path, rows: Iterable[NormalizedEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[NormalizedEvent]:
    if not path.exists():
        return []
    rows: list[NormalizedEvent] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows
