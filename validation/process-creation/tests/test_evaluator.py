from pathlib import Path

from wintap_process_validation.evaluator import evaluate
from wintap_process_validation.mock import write_mock_normalized_events
from wintap_process_validation.schema import CaseSpec, Manifest, ProcessSpec


def make_manifest() -> Manifest:
    return Manifest(
        schema_version="process-validation-manifest/v1",
        run_id="mock-run",
        created_utc="2026-07-31T00:00:00Z",
        workload_profile="unit",
        cases=[
            CaseSpec(
                case_id="fork_exec_001",
                case_type="fork_exec",
                started_utc="2026-07-31T00:00:00Z",
                ended_utc="2026-07-31T00:00:01Z",
                expected_events=["process_fork", "exec_attempt", "exec_success", "process_exit"],
                process_refs=["parent", "child"],
            )
        ],
        processes=[
            ProcessSpec(process_ref="parent", case_id="fork_exec_001", role="parent", observed_pid=100),
            ProcessSpec(process_ref="child", case_id="fork_exec_001", role="child", observed_pid=101, observed_ppid=100, parent_ref="parent"),
        ],
    )


def test_evaluator_detects_duplicate_exec_success(tmp_path: Path) -> None:
    manifest = make_manifest()
    normalized = tmp_path / "normalized"
    write_mock_normalized_events(manifest, normalized, inject_duplicate=True)
    report = evaluate(manifest, normalized)
    assert report.metrics["fork_recall"].rate == 1.0
    assert report.metrics["exec_attempt_recall"].rate == 1.0
    assert report.metrics["exec_success_recall"].rate == 1.0
    assert report.metrics["exit_recall"].rate == 1.0
    assert report.metrics["parent_join_rate"].rate == 1.0
    assert report.metrics["duplicate_exec_success"] == 1
    assert report.metrics["identity_cross_case_collisions"] == 0
    assert report.warnings


def test_evaluator_clean_mock_has_no_duplicate_warning(tmp_path: Path) -> None:
    manifest = make_manifest()
    normalized = tmp_path / "normalized"
    write_mock_normalized_events(manifest, normalized, inject_duplicate=False)
    report = evaluate(manifest, normalized)
    assert report.metrics["duplicate_exec_success"] == 0
    assert "duplicate exec_success rows detected for one or more case/identity pairs" not in report.warnings
