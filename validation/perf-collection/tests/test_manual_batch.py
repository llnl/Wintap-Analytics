from pathlib import Path
import json
import subprocess
import sys

import duckdb


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
