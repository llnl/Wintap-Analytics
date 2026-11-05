#!/usr/bin/env python3
"""Supplement live evidence with actual Python writer edge cases, never a fake live oracle."""

import argparse
from dataclasses import fields, replace
import importlib.util
import os
from pathlib import Path
import sys
import time

import evidence


def check(binary, output):
    output.mkdir(mode=0o700, exist_ok=False)
    source = Path(__file__).resolve().parents[3] / "Lintap/pidstat-collector.py"
    spec = importlib.util.spec_from_file_location("spike_fixture_reference", source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    os.environ["TZ"] = "America/Phoenix"
    time.tzset()
    values = {field.name: 0 for field in fields(module.SampleRow)}
    values.update(date_col="2026-10-30", sample_time="23:59:59", uid=0, pid=123,
                  usr_percent=12.345, cpu_percent=250.125, vsz_kb=814169220,
                  rss_kb=1892724, kb_read_per_sec=-1.0,
                  command='worker "quoted" café\tname\nnext', hostname="fixture",
                  cgroup_path="/", pid_ns_inode=None, container_runtime=None, container_id=None)
    first = module.SampleRow(**values)
    rows = [first, first,
            replace(first, pid=2147483647, cgroup_path="/docker/" + "a" * 64,
                    pid_ns_inode=9007199254740993, container_runtime="docker", container_id="a" * 64),
            replace(first, pid=124, date_col="2026-10-31", sample_time="00:00:00", command=""),
            replace(first, pid=125, date_col="2026-10-31", sample_time="00:00:01",
                    cpu_percent=0.0, container_runtime="", container_id="")]
    tsv = output / "fixture.tsv"
    tsv.write_text("".join(row.to_tsv() + "\n" for row in rows))
    config = module.Config(output, 5, 300, 300, output / "python", output / "runtime", "ZSTD", 1, 0, 0, "fixture")
    collector = module.Collector(config, sampler=object())
    try:
        for row in rows:
            epoch = int(time.mktime(time.strptime(row.date_col + " " + row.sample_time, "%Y-%m-%d %H:%M:%S")))
            collector.rotate_current_window_if_needed(epoch)
            collector.append_rows([row])
        collector.seal_current_spool()
        collector.process_pending_spools()
    finally:
        collector.close()
    record = evidence.Recorder(output).run([str(binary.resolve()), "--input", str(tsv.resolve()),
               "--output", str((output / "go").resolve()), "--timezone", "America/Phoenix"])
    if record["returncode"] != 0:
        raise RuntimeError("Go fixture encoding failed; inspect recorded command logs")
    python_rows, python_schema, _ = evidence.read_dataset(output / "python")
    go_rows, go_schema, _ = evidence.read_dataset(output / "go")
    report = evidence.compare_rows(python_rows, go_rows)
    report["schemas_equal"] = all(s["columns"] == python_schema[0]["columns"] and
        s["physical"] == python_schema[0]["physical"] for s in python_schema + go_schema)
    report.update(kind="controlled-source-writer-fixture-not-live-proc", source_sha256=evidence.sha(source),
                  input_sha256=evidence.sha(tsv), binary_sha256=evidence.sha(binary),
                  python_schema=python_schema, go_schema=go_schema)
    evidence.write(output / "python-rows.json", python_rows)
    evidence.write(output / "go-rows.json", go_rows)
    evidence.write(output / "comparison.json", report)
    passed = report["equal"] and report["schemas_equal"] and len(python_rows) == len(rows)
    evidence.write(output / "result.json", {"status": "PASS" if passed else "FAIL", "scope": report["kind"]})
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.exit(check(args.binary, args.output))
