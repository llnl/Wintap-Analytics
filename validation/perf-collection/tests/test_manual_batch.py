from pathlib import Path
import json
import subprocess
import sys

import duckdb

from wintap_perf_collection.cli.manual_batch import parse_dotnet_collect_csv, parse_dotnet_collect_json


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_manual_batch_writes_partitioned_parquet(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    pid = 4321
    proc_dir = proc_root / str(pid)
    write(proc_dir / "comm", "Lintap\n")
    write(
        proc_dir / "smaps_rollup",
        "Rss: 1234 kB\nPss: 456 kB\nPrivate_Clean: 11 kB\nPrivate_Dirty: 22 kB\nRssAnon: 333 kB\nRssFile: 444 kB\nSwap: 0 kB\n",
    )
    write(
        proc_dir / "status",
        "Name:\tLintap\nState:\tS (sleeping)\nTgid:\t4321\nPid:\t4321\nPPid:\t1\nThreads:\t4\nFDSize:\t64\nVmRSS:\t2048 kB\nRssAnon:\t1024 kB\nRssFile:\t512 kB\nVmSwap:\t0 kB\nvoluntary_ctxt_switches:\t88\nnonvoluntary_ctxt_switches:\t5\n",
    )
    write(
        proc_dir / "maps",
        "00400000-00452000 r-xp 00000000 08:02 12345 /usr/bin/foo\n00652000-00653000 rw-p 00052000 08:02 12345 /usr/bin/foo\n",
    )
    (proc_dir / "fd").mkdir(parents=True)
    (proc_dir / "fd" / "0").symlink_to("/dev/null")
    (proc_dir / "fd" / "1").symlink_to("/dev/null")

    project_dir = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        "-m",
        "wintap_perf_collection.cli.manual_batch",
        "--data-root",
        str(tmp_path / "data"),
        "--proc-root",
        str(proc_root),
        "--pid",
        str(pid),
        "--duration-seconds",
        "1",
        "--interval-seconds",
        "0.1",
        "--run-id",
        "test-run",
    ]
    proc = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, env={**dict(), "PYTHONPATH": str(project_dir / "src")}, check=True)
    summary = json.loads(proc.stdout)
    assert "perf_smaps_rollup" in summary["outputs"]
    assert "perf_proc_status" in summary["outputs"]
    assert "perf_fd_map" in summary["outputs"]

    con = duckdb.connect()
    try:
        smaps_rows = con.execute("select count(*) from read_parquet(?)", [summary["outputs"]["perf_smaps_rollup"]]).fetchone()[0]
        status_rows = con.execute("select count(*) from read_parquet(?)", [summary["outputs"]["perf_proc_status"]]).fetchone()[0]
        fd_rows = con.execute("select count(*) from read_parquet(?)", [summary["outputs"]["perf_fd_map"]]).fetchone()[0]
    finally:
        con.close()

    assert smaps_rows > 0
    assert status_rows > 0
    assert fd_rows > 0


def test_parse_dotnet_collect_json() -> None:
    text = json.dumps(
        {
            "TargetProcess": "dotnet",
            "StartTime": "2026-08-29T13:17:56.8436947-07:00",
            "Events": [
                {
                    "timestamp": "2026-08-29T13:18:01.0980844-07:00",
                    "provider": "System.Runtime",
                    "name": "dotnet.process.memory.working_set (By)",
                    "tags": "",
                    "counterType": "Metric",
                    "meterTags": "",
                    "instrumentTags": "",
                    "value": 196182016,
                },
                {
                    "timestamp": "2026-08-29T13:18:01.1018023-07:00",
                    "provider": "System.Runtime",
                    "name": "dotnet.gc.last_collection.heap.fragmentation.size (By)",
                    "tags": "gc.heap.generation=gen2",
                    "counterType": "Metric",
                    "meterTags": "",
                    "instrumentTags": "",
                    "value": 30904,
                },
            ],
        }
    )

    parsed = parse_dotnet_collect_json(
        text,
        hostname="spk16.llnl.gov",
        pid=743557,
        process_name="Lintap",
        run_id="lintap-perf-5m",
        command="dotnet-counters collect --format json",
    )

    assert [row["counter_key"] for row in parsed] == [
        "system_runtime_dotnet_process_memory_working_set_by",
        "system_runtime_dotnet_gc_last_collection_heap_fragmentation_size_by_gc_heap_generation_gen2",
    ]
    assert [row["value"] for row in parsed] == [196182016.0, 30904.0]
    assert parsed[0]["time"] == "2026-08-29T20:18:01Z"


def test_parse_dotnet_collect_csv() -> None:
    text = """Timestamp,Provider,Counter Name,Counter Type,Mean/Increment
08/29/2026 13:18:50,System.Runtime,dotnet.process.memory.working_set (By),Metric,175312896
08/29/2026 13:18:50,System.Runtime,dotnet.process.cpu.time (s / 2 sec)[cpu.mode=user],Rate,1.7813419999999995
"""

    parsed = parse_dotnet_collect_csv(
        text,
        hostname="spk16.llnl.gov",
        pid=743557,
        process_name="Lintap",
        run_id="lintap-perf-5m",
        command="dotnet-counters collect --format csv",
    )

    assert [row["counter_key"] for row in parsed] == [
        "system_runtime_dotnet_process_memory_working_set_by",
        "system_runtime_dotnet_process_cpu_time_s_2_sec_cpu_mode_user",
    ]
    assert [row["value"] for row in parsed] == [175312896.0, 1.7813419999999995]


def test_manual_batch_writes_dotnet_collect_parquet(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    pid = 4321
    proc_dir = proc_root / str(pid)
    write(proc_dir / "comm", "Lintap\n")
    write(proc_dir / "smaps_rollup", "Rss: 1234 kB\nAnonymous: 333 kB\n")
    write(proc_dir / "status", "Name:\tLintap\nState:\tS (sleeping)\nTgid:\t4321\nPid:\t4321\nPPid:\t1\nThreads:\t4\nFDSize:\t64\nVmRSS:\t2048 kB\nRssAnon:\t1024 kB\nRssFile:\t512 kB\nVmSwap:\t0 kB\nvoluntary_ctxt_switches:\t88\nnonvoluntary_ctxt_switches:\t5\n")
    write(proc_dir / "maps", "00400000-00452000 r-xp 00000000 08:02 12345 /usr/bin/foo\n")
    (proc_dir / "fd").mkdir(parents=True)
    (proc_dir / "fd" / "0").symlink_to("/dev/null")

    fake_dotnet_counters = tmp_path / "fake-dotnet-counters.py"
    write(
        fake_dotnet_counters,
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import pathlib\n"
        "import sys\n"
        "args = sys.argv[1:]\n"
        "output = pathlib.Path(args[args.index('--output') + 1]).with_suffix('.json')\n"
        "output.write_text(json.dumps({'TargetProcess': 'dotnet', 'StartTime': '2026-08-29T13:17:56.8436947-07:00', 'Events': [{'timestamp': '2026-08-29T13:18:01.0980844-07:00', 'provider': 'System.Runtime', 'name': 'dotnet.process.memory.working_set (By)', 'tags': '', 'counterType': 'Metric', 'meterTags': '', 'instrumentTags': '', 'value': 196182016}]}), encoding='utf-8')\n"
        "print('Starting a counter session. Press Q to quit.')\n",
    )
    fake_dotnet_counters.chmod(0o755)

    project_dir = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        "-m",
        "wintap_perf_collection.cli.manual_batch",
        "--data-root",
        str(tmp_path / "data"),
        "--proc-root",
        str(proc_root),
        "--pid",
        str(pid),
        "--duration-seconds",
        "1",
        "--interval-seconds",
        "0.1",
        "--run-id",
        "dotnet-collect-test",
        "--dotnet-counters-format",
        "json",
        "--dotnet-counters-binary",
        str(fake_dotnet_counters),
        "--dotnet-counters-refresh-interval",
        "1",
    ]
    proc = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, env={**dict(), "PYTHONPATH": str(project_dir / "src")}, check=True)
    summary = json.loads(proc.stdout)
    assert "perf_dotnet_counters" in summary["outputs"]

    con = duckdb.connect()
    try:
        parsed_rows = con.execute("select count(*) from read_parquet(?)", [summary["outputs"]["perf_dotnet_counters"]]).fetchone()[0]
    finally:
        con.close()

    assert parsed_rows == 1
