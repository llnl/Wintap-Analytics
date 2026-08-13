from wintap_process_validation.normalizers.lintap import normalize_lintap_process_rows


def test_lintap_normalizer_splits_exec_provenance() -> None:
    rows = [
        {
            "PID": 100,
            "MessageType": "Process",
            "ActivityType": "Start",
            "PidHash": "h100",
            "Process_ParentPID": 1,
            "Process_ParentPidHash": "h1",
            "Process_Arguments": "case_id=sched PROC_START_SRC=sched_exec PARENT_HASH_SRC=ebpf",
            "Process_CommandLine": "sleep 1",
            "CapturedUtc": "2026-07-31T00:00:00Z",
        },
        {
            "PID": 101,
            "MessageType": "Process",
            "ActivityType": "Start",
            "PidHash": "h101",
            "Process_Arguments": "case_id=attempt PROC_START_SRC=execve_or_execveat FLAGS=0x00001000",
            "CapturedUtc": "2026-07-31T00:00:01Z",
        },
        {
            "PID": 102,
            "MessageType": "Process",
            "ActivityType": "Refresh",
            "PidHash": "h102",
            "CapturedUtc": "2026-07-31T00:00:02Z",
        },
        {
            "PID": 103,
            "MessageType": "Process",
            "ActivityType": "Stop",
            "PidHash": "h103",
            "CapturedUtc": "2026-07-31T00:00:03Z",
        },
    ]
    tables = normalize_lintap_process_rows(rows, "run1")
    assert len(tables["process_identity"]) == 4
    assert len(tables["exec_success"]) == 1
    assert tables["exec_success"][0]["source_hook"] == "sched_process_exec"
    assert len(tables["exec_attempt"]) == 1
    assert tables["exec_attempt"][0]["syscall"] == "execveat"
    assert tables["exec_attempt"][0]["flags"] == "0x00001000"
    assert len(tables["process_rundown"]) == 1
    assert len(tables["process_exit"]) == 1
