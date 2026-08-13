from pathlib import Path

from wintap_process_validation.schema import Manifest, CaseSpec, ProcessSpec


def test_manifest_roundtrip(tmp_path: Path) -> None:
    manifest = Manifest(
        schema_version="process-validation-manifest/v1",
        run_id="test-run",
        created_utc="2026-07-31T00:00:00Z",
        workload_profile="unit",
        cases=[
            CaseSpec(
                case_id="case1",
                case_type="simple_exec",
                started_utc="2026-07-31T00:00:00Z",
                ended_utc="2026-07-31T00:00:01Z",
                expected_events=["exec_attempt", "exec_success"],
                process_refs=["proc1"],
            )
        ],
        processes=[ProcessSpec(process_ref="proc1", case_id="case1", role="child", observed_pid=123)],
    )
    path = tmp_path / "manifest.json"
    manifest.write(path)
    loaded = Manifest.read(path)
    assert loaded == manifest
