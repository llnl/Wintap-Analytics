from wintap_process_validation.workload import generate_process_baseline


def test_generate_process_baseline_runs_on_current_platform() -> None:
    manifest = generate_process_baseline("unit-run", short_lived_children=2)
    assert manifest.run_id == "unit-run"
    assert any(case.case_type == "simple_exec" for case in manifest.cases)
    assert any(case.case_type == "fork_exec" for case in manifest.cases)
    assert any(case.case_type == "short_lived_burst" for case in manifest.cases)
    assert manifest.processes
    for process in manifest.processes:
        assert process.observed_pid > 0
