#!/usr/bin/env python3
"""Bounded, root-private Ubuntu arm64 recovery/signals; no shared services changed."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

import evidence
from check_spool import config, env_for, load_reference, compare


def check(binary, reference, output):
    assert platform.system() == "Linux" and platform.machine() in ("aarch64", "arm64")
    assert "ubuntu" in Path("/etc/os-release").read_text().lower()
    assert os.geteuid() == 0
    output.mkdir(mode=0o700, exist_ok=False)
    module, source = load_reference()
    source_hash = evidence.sha(source)
    assert source_hash == "3722ef80c87e226a3c0491f9daff34f4cc8bddfba0d1589cf33052aef6e797c5"
    os.environ["TZ"] = "America/Phoenix"
    time.tzset()
    capture = json.loads((reference / "capture.json").read_text())
    rows = (reference / "golden.tsv").read_text().splitlines()
    hostname = capture["hostname"]
    recorder = evidence.Recorder(output)
    reports = {}

    def environment(root, rotation=300):
        return {"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "TZ": "America/Phoenix",
                **env_for(root, hostname), "PIDSTAT_ROTATE_INTERVAL_SEC": str(rotation)}

    def recover(root):
        env = environment(root)
        result = recorder.run(["/usr/bin/env", "-i", *[key + "=" + value for key, value in env.items()],
                               str(binary), "--recover", "--timezone", "America/Phoenix"], timeout=30)
        return result

    def count(root):
        paths = list((root / "data").rglob("*.parquet"))
        if not paths:
            return 0
        records, _, _ = evidence.read_dataset(root / "data")
        return len(records)

    # Execute the unchanged production Python producer natively, then recover its
    # exact leftovers in Go. Keep its input spool copy/hash as evidence.
    root = output / "legacy"
    collector = module.Collector(config(module, root / "python", hostname), sampler=object())
    epoch = module.window_start_for_epoch(int(capture["samples"][1]["captured_at"]), 300)
    collector.initialize_current_window(epoch)
    collector.append_rows([SimpleNamespace(to_tsv=lambda row=row: row) for row in rows])
    go = root / "go"
    (go / "spool").mkdir(parents=True, mode=0o700)
    for path in collector.config.spool_dir.iterdir():
        (go / "spool" / path.name).write_bytes(path.read_bytes())
    collector.salvage_spool_files()
    collector.close()
    result = recover(go)
    assert result["returncode"] == 0, result
    reports["legacy"] = compare(root / "python/data", go / "data", root)

    root = output / "native-raw-replay"
    env = environment(root)
    result = recorder.run(["/usr/bin/env", "-i", *[k + "=" + v for k, v in env.items()],
        str(binary), "--spool-replay", str(reference / "capture.json"), "--timezone", "America/Phoenix"], timeout=30)
    assert result["returncode"] == 0, result
    reports["native-raw-replay"] = compare(reference, root / "data", root)

    for name, stop_signal in [("sigterm", signal.SIGTERM), ("sigint", signal.SIGINT), ("sigkill-restart", signal.SIGKILL)]:
        root = output / name
        root.mkdir(mode=0o700)
        env = environment(root, rotation=300 if stop_signal == signal.SIGKILL else 2)
        if stop_signal == signal.SIGKILL:
            env["PIDSTAT_INTERVAL_SEC"] = "5"
        argv = [str(binary), "--collect", "--timezone", "America/Phoenix"]
        started = time.time()
        with (root / "stdout.log").open("wb") as stdout, (root / "stderr.log").open("wb") as stderr:
            process = subprocess.Popen(argv, env=env, stdout=stdout, stderr=stderr)
            try:
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    current = root / "spool/current.tsv"
                    if current.exists() and current.stat().st_size > 0:
                        break
                    if process.poll() is not None:
                        raise AssertionError(f"collector exited before samples: {process.returncode}")
                    time.sleep(0.05)
                else:
                    raise AssertionError("no live rows before deadline")
                # Another native process must not acquire the same spool.
                locked = recover(root)
                assert locked["returncode"] != 0 and "locked" in Path(locked["stderr"]).read_text(), locked
                if stop_signal != signal.SIGKILL:
                    time.sleep(2.2)
                process.send_signal(stop_signal)
                process.wait(timeout=15)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=15)
        completed_before = count(root)
        if stop_signal == signal.SIGKILL:
            assert process.returncode == -signal.SIGKILL
            current = root / "spool/current.tsv"
            raw = current.read_bytes()
            assert raw and raw.endswith(b"\n")
            (root / "crashed-current.tsv").write_bytes(raw)
            remaining = len(raw.splitlines())
            result = recover(root)
            assert result["returncode"] == 0, result
            assert count(root) == completed_before + remaining
            reports[name] = {"completed_before": completed_before, "recovered_rows": remaining,
                             "total_rows": count(root), "crashed_spool_sha256": hashlib.sha256(raw).hexdigest()}
        else:
            assert process.returncode == 0
            assert completed_before > 0
            assert not (root / "spool/current.tsv").exists()
            assert not list((root / "spool").glob("pending-*.tsv"))
            assert not list((root / "data").rglob("*.active"))
            reports[name] = {"rows": completed_before, "files": len(list((root / "data").rglob("*.parquet"))), "exit": 0}
        evidence.write(root / "run.json", {"argv": argv, "env": env, "pid": process.pid,
            "signal": int(stop_signal), "exit": process.returncode, "elapsed_sec": time.time() - started})

    # A filesystem conversion failure preserves exact input; restoring only the
    # destination permits retry, without modifying data/metadata or thresholds.
    root = output / "conversion-retry"
    cfg = config(module, root, hostname)
    collector = module.Collector(cfg, sampler=object())
    collector.initialize_current_window(epoch)
    collector.append_rows([SimpleNamespace(to_tsv=lambda row=row: row) for row in rows[:20]])
    collector.seal_current_spool()
    collector.close()
    pending = next(cfg.spool_dir.glob("pending-*.tsv"))
    before = evidence.sha(pending)
    dt = module.datetime.fromtimestamp(epoch)
    blocking = cfg.raw_sensor_dir / ("dayPK=" + dt.strftime("%Y%m%d"))
    blocking.parent.mkdir(parents=True, mode=0o700)
    blocking.write_text("private-test-destination-obstruction")
    result = recover(root)
    assert result["returncode"] != 0
    assert evidence.sha(pending) == before
    assert count(root) == 0
    blocking.unlink()  # Only the test-owned obstruction, never shared data.
    result = recover(root)
    assert result["returncode"] == 0 and count(root) == 20
    reports["conversion-retry"] = {"rows": 20, "source_retained_sha256": before}

    assert evidence.sha(source) == source_hash
    evidence.write(output / "result.json", {"status": "PASS", "scope": "isolated-Ubuntu-arm64-recovery-lock-signals-retry",
        "source_sha256": source_hash, "binary_sha256": evidence.sha(binary), "reports": reports,
        "limits": "shortened rotations; not default cadence/paired-live/resource/DBT/package/RHEL proof"})
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    check(args.binary, args.reference, args.output)
