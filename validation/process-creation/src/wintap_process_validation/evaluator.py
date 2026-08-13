from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from collections import defaultdict
import json

from .schema import Manifest, NormalizedEvent, read_jsonl


@dataclass(frozen=True)
class RecallMetric:
    observed: int
    expected: int

    @property
    def rate(self) -> float | None:
        if self.expected == 0:
            return None
        return self.observed / self.expected

    def to_dict(self) -> dict[str, Any]:
        return {"observed": self.observed, "expected": self.expected, "rate": self.rate}


@dataclass
class EvaluationReport:
    run_id: str
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        def convert(value: Any) -> Any:
            if isinstance(value, RecallMetric):
                return value.to_dict()
            return value

        return {
            "run_id": self.run_id,
            "metrics": {key: convert(value) for key, value in self.metrics.items()},
            "warnings": self.warnings,
        }

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n")


def load_normalized(normalized_dir: Path) -> dict[str, list[NormalizedEvent]]:
    tables = {}
    for name in [
        "process_identity",
        "process_fork",
        "exec_attempt",
        "exec_success",
        "process_exit",
        "process_rundown",
        "file_activity",
        "network_activity",
        "sensor_loss",
    ]:
        tables[name] = read_jsonl(normalized_dir / f"{name}.jsonl")
    return tables


def evaluate(manifest: Manifest, normalized_dir: Path) -> EvaluationReport:
    tables = load_normalized(normalized_dir)
    report = EvaluationReport(run_id=manifest.run_id)

    report.metrics["fork_recall"] = _recall(manifest, "process_fork", tables["process_fork"])
    report.metrics["exec_attempt_recall"] = _recall(manifest, "exec_attempt", tables["exec_attempt"])
    report.metrics["exec_success_recall"] = _recall(manifest, "exec_success", tables["exec_success"])
    report.metrics["exit_recall"] = _recall(manifest, "process_exit", tables["process_exit"])
    report.metrics["rundown_recall"] = _recall(manifest, "process_rundown", tables["process_rundown"])

    parent_observed, parent_expected = _parent_join_counts(manifest, tables)
    report.metrics["parent_join_rate"] = RecallMetric(parent_observed, parent_expected)
    report.metrics["duplicate_exec_success"] = _duplicate_count(tables["exec_success"], key_fields=("case_id", "identity"))
    report.metrics["identity_cross_case_collisions"] = _identity_cross_case_collisions(tables["process_identity"])
    report.metrics["sensor_loss_total"] = _sensor_loss_total(tables["sensor_loss"])

    if report.metrics["duplicate_exec_success"]:
        report.warnings.append("duplicate exec_success rows detected for one or more case/identity pairs")
    if report.metrics["sensor_loss_total"]:
        report.warnings.append("sensor loss metrics are non-zero")
    return report


def _recall(manifest: Manifest, event_name: str, observed_rows: list[NormalizedEvent]) -> RecallMetric:
    expected = {case.case_id for case in manifest.cases if event_name in case.expected_events and case.required}
    observed = {str(row.get("case_id")) for row in observed_rows if row.get("case_id") in expected}
    return RecallMetric(observed=len(observed), expected=len(expected))


def _parent_join_counts(manifest: Manifest, tables: dict[str, list[NormalizedEvent]]) -> tuple[int, int]:
    identity_by_ref = {
        str(row.get("process_ref")): str(row.get("tool_process_id"))
        for row in tables["process_identity"]
        if row.get("process_ref") and row.get("tool_process_id")
    }
    expected = [proc for proc in manifest.processes if proc.parent_ref]
    observed = 0
    for proc in expected:
        child_identity = identity_by_ref.get(proc.process_ref)
        parent_identity = identity_by_ref.get(proc.parent_ref or "")
        if not child_identity or not parent_identity:
            continue
        if any(
            row.get("child_identity") == child_identity and row.get("parent_identity") == parent_identity
            for row in tables["process_fork"]
        ):
            observed += 1
    return observed, len(expected)


def _duplicate_count(rows: list[NormalizedEvent], key_fields: tuple[str, ...]) -> int:
    counts: dict[tuple[Any, ...], int] = defaultdict(int)
    for row in rows:
        key = tuple(row.get(field) for field in key_fields)
        counts[key] += 1
    return sum(count - 1 for count in counts.values() if count > 1)


def _identity_cross_case_collisions(identity_rows: list[NormalizedEvent]) -> int:
    cases_by_identity: dict[str, set[str]] = defaultdict(set)
    for row in identity_rows:
        identity = row.get("tool_process_id")
        case_id = row.get("case_id")
        if identity and case_id:
            cases_by_identity[str(identity)].add(str(case_id))
    return sum(1 for cases in cases_by_identity.values() if len(cases) > 1)


def _sensor_loss_total(loss_rows: list[NormalizedEvent]) -> int | float:
    total: int | float = 0
    for row in loss_rows:
        value = row.get("metric_value", 0)
        if isinstance(value, (int, float)):
            total += value
    return total
