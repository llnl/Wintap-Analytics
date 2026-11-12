#!/usr/bin/env python3
"""Actual Python sampler/config differential fixtures; supplemental to real proc replay."""

import argparse
from dataclasses import asdict, fields
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

import evidence


def stat(pid=123, start=10, user=100, system=20, guest=0, **values):
    columns = ["0"] * 41
    columns[0] = "S"
    mapping = {7: 20, 9: 3, 11: user, 12: system, 19: start,
               20: 8192, 21: 10, 36: 3, 39: 7, 40: guest}
    for index, value in mapping.items():
        columns[index] = str(values.get(str(index), value))
    return f"{pid} (worker (nested) café\tname) " + " ".join(columns) + "\n"


def fixtures(module, output, binary, ticks=100, page_bytes=4096):
    initial = {"/proc/meminfo": "MemTotal: 1000 kB\n"}
    id_text = "a" * 64
    base = {"/proc/123/stat": stat(), "/proc/123/status": "Uid: 1000 1000\nvoluntary_ctxt_switches: 5\nnonvoluntary_ctxt_switches: 2\n",
            "/proc/123/io": "read_bytes: 1024\nwrite_bytes: 2048\n",
            "/proc/123/schedstat": "0 1000000000 2\n", "/proc/123/cgroup": "2:cpu:/system.slice/docker-" + id_text + ".scope"}
    second = dict(base)
    second.update({"/proc/123/stat": stat(user=320, system=50, guest=20),
                   "/proc/123/status": "Uid: 1001\nvoluntary_ctxt_switches: 15\nnonvoluntary_ctxt_switches: 8\n",
                   "/proc/123/io": "read_bytes: 3072\nwrite_bytes: 6144\ncancelled_write_bytes: 1024\n",
                   "/proc/123/schedstat": "0 1500000000 2\n"})
    reset = dict(second)
    reset.update({"/proc/123/stat": stat(user=10, system=2, guest=1), "/proc/123/io": None,
                  "/proc/123/schedstat": "0 malformed 2", "/proc/123/cgroup": "0::/changed-live-cgroup"})
    reused = dict(base)
    reused.update({"/proc/123/stat": stat(start=11, user=0, system=0), "/proc/123/cgroup": "0::/libpod-" + id_text + ".scope"})
    reused_next = dict(reused)
    reused_next["/proc/123/stat"] = stat(start=11, user=50, system=10)
    malformed = dict(reused_next)
    malformed["/proc/123/stat"] = "123 (short) S 0\n"
    exited = dict(base)
    exited["/proc/123/status"] = None
    pairs = [dict(values) for values in [base, second, reset, reused, reused_next, malformed, exited, base, second]]
    start = 1793429998.0  # Emitted Phoenix 23:59:59/midnight, then zero-elapsed clamp.
    offsets = [0, 1.9999998, 2, 3, 4, 5, 6, 7, 6]
    source = dict(initial)
    links = {"/proc/123/ns/pid": "pid:[4026531836]"}
    # Additional independent processes exercise actual Python cgroup v1/v2/hybrid
    # parsing and null/malformed namespace links, not only Go hand expectations.
    extra = [(124, "0::/cri-containerd-" + id_text + ".scope", "pid:[9007199254740993]"),
             (125, "2:cpu:/crio-" + id_text + ".scope", "pid:[4026531836]"),
             (126, "0::/containerd/" + id_text, "pid:[4026531836]"),
             (127, "0::/\n2:cpu:/long/path\n3:memory:/short", "invalid"),
             (128, None, None), (129, "0::/docker/INVALID", None)]
    for index, values in enumerate(pairs):
        for pid, cgroup, link in extra:
            values.update({f"/proc/{pid}/stat": stat(pid=pid, user=100 + index * 20),
                           f"/proc/{pid}/status": "Uid: 0\n", f"/proc/{pid}/io": None,
                           f"/proc/{pid}/schedstat": None, f"/proc/{pid}/cgroup": cgroup})
            links[f"/proc/{pid}/ns/pid"] = link
    names = ["123", *[str(pid) for pid, _, _ in extra]]
    captures, rows, row_epochs = [], [], []

    def read(path):
        return source.get(str(path))

    with patch.object(module, "read_optional_text", side_effect=read), \
         patch.object(os, "sysconf", side_effect=lambda key: {"SC_CLK_TCK": ticks, "SC_PAGE_SIZE": page_bytes}[key]), \
         patch.object(os, "scandir", side_effect=lambda path: iter([SimpleNamespace(name=name) for name in names])), \
         patch.object(os, "readlink", side_effect=lambda path: links[str(path)]):
        sampler = module.ProcSampler("fixture")
        for values, offset in zip(pairs, offsets):
            source.clear()
            source.update(values)
            stamp = start + offset
            sampled = sampler.sample(stamp)
            rows.extend(sampled)
            row_epochs.extend([int(stamp)] * len(sampled))
            captures.append({"captured_at": stamp, "reads": dict(values), "pid_ns_links": dict(links),
                             "proc_pid_enumerations": [names]})
    raw = {"kind": "controlled-source-sampler-fixture-not-live-proc", "initial_reads": initial,
           "clock_ticks": ticks, "page_size_bytes": page_bytes, "hostname": "fixture", "samples": captures}
    evidence.write(output / "capture.json", raw)
    (output / "python.tsv").write_text("".join(row.to_tsv() + "\n" for row in rows))
    config = module.Config(output / "python", 1, 300, 300, output / "python", output / "runtime", "ZSTD", 1, 0, 0, "fixture")
    collector = module.Collector(config, sampler=object())
    try:
        for row, epoch in zip(rows, row_epochs):
            collector.rotate_current_window_if_needed(epoch)
            collector.append_rows([row])
        collector.seal_current_spool()
        collector.process_pending_spools()
    finally:
        collector.close()
    record = evidence.Recorder(output).run([str(binary.resolve()), "--replay", str((output / "capture.json").resolve()),
        "--output", str((output / "go").resolve()), "--timezone", "America/Phoenix"])
    assert record["returncode"] == 0, record
    python_rows, python_schema, _ = evidence.read_dataset(output / "python")
    go_rows, go_schema, _ = evidence.read_dataset(output / "go")
    report = evidence.compare_rows(python_rows, go_rows)
    report["schemas_equal"] = all(s["columns"] == python_schema[0]["columns"] and s["physical"] == python_schema[0]["physical"] for s in python_schema + go_schema)
    report["tsv_equal"] = (output / "python.tsv").read_bytes() == (output / "go/golden.tsv").read_bytes()
    evidence.write(output / "python-rows.json", python_rows)
    evidence.write(output / "go-rows.json", go_rows)
    evidence.write(output / "comparison.json", report)
    assert report["equal"] and report["schemas_equal"] and report["tsv_equal"], report

    # Explicitly document the planned malformed-counter resilience delta rather
    # than treating a Python exception as a successful differential comparison.
    bad = dict(base)
    bad["/proc/123/io"] = "read_bytes: not-a-number\n"
    source.clear()
    source.update({**initial, **bad})
    python_error = None
    with patch.object(module, "read_optional_text", side_effect=read), \
         patch.object(os, "sysconf", side_effect=lambda key: {"SC_CLK_TCK": ticks, "SC_PAGE_SIZE": page_bytes}[key]), \
         patch.object(os, "readlink", side_effect=lambda path: links[str(path)]):
        try:
            module.ProcSampler("fixture")._read_snapshot(123, start)
        except ValueError as error:
            python_error = str(error)
    assert python_error is not None
    evidence.write(output / "malformed-counter-delta.json", {"python_behavior": "ValueError", "python_error": python_error,
        "go_behavior": "skip-malformed-process (Go regression)", "reason": "fpc-02 malformed-record fault handling; no valid-input parity waiver"})


def config_checks(module, output, binary):
    scenarios = [{}, {"WINTAP_ETL_UPLOAD_INTERVAL_SEC": "600"},
                 {"WINTAP_ETL_UPLOAD_INTERVAL_SEC": "600", "PIDSTAT_ROTATE_INTERVAL_SEC": "20"},
                 {"PIDSTAT_ROTATE_INTERVAL_SEC": "20", "PIDSTAT_MIN_ROTATE_INTERVAL_SEC": "10"},
                 {"WINTAP_DATA_ROOT": "/isolated/data", "WINTAP_RUNTIME_ROOT": "/isolated/runtime", "PIDSTAT_HOSTNAME": "override"},
                 {"PIDSTAT_PARQUET_ROOT": "relative/parquet", "PIDSTAT_SPOOL_DIR": "relative/runtime", "PIDSTAT_MAX_UNSHIPPED_BYTES": "0", "PIDSTAT_MAX_UNSHIPPED_AGE_SEC": "60"},
                 {"PIDSTAT_INTERVAL_SEC": "0"}, {"PIDSTAT_ROTATE_INTERVAL_SEC": ""},
                 {"PIDSTAT_MAX_UNSHIPPED_BYTES": "-1"}, {"PIDSTAT_DUCKDB_THREADS": "0"},
                 {"PIDSTAT_INTERVAL_SEC": "  +5 "}, {"PIDSTAT_MAX_UNSHIPPED_BYTES": "1_024"},
                 {"WINTAP_DATA_ROOT": "/isolated/a/../data"},
                 {"PIDSTAT_MAX_UNSHIPPED_BYTES": "１２３"}, {"PIDSTAT_MAX_UNSHIPPED_BYTES": "١٢٣"},
                 {"PIDSTAT_MAX_UNSHIPPED_BYTES": "1__2"}, {"PIDSTAT_SPOOL_DIR": "//root///runtime/./"}]
    reports = []
    recorder = evidence.Recorder(output)
    for index, env in enumerate(scenarios):
        actual_env = {"PIDSTAT_HOSTNAME": "fixture", **env}
        try:
            with patch.dict(os.environ, actual_env, clear=True), \
                 patch.object(module.Config, "default_data_root", return_value=Path("/var/log/lintap/data")), \
                 patch.object(module.Config, "default_runtime_root", return_value=Path("/var/log/lintap/runtime")), \
                 patch.object(Path, "mkdir"):
                expected = asdict(module.Config.from_env())
            expected = {key: str(value) if isinstance(value, Path) else value for key, value in expected.items()}
            python_valid = True
        except ValueError:
            expected, python_valid = None, False
        record = recorder.run(["/usr/bin/env", "-i", *[key + "=" + value for key, value in actual_env.items()], str(binary.resolve()), "--show-config"])
        actual = json.loads(Path(record["stdout"]).read_text()) if record["returncode"] == 0 else None
        equal = (actual == expected) if python_valid else record["returncode"] != 0
        reports.append({"case": index, "env": actual_env, "python": expected, "go": actual, "equal": equal, "record": record})
    evidence.write(output / "config-comparison.json", reports)
    assert all(report["equal"] for report in reports), [r for r in reports if not r["equal"]]


def check(binary, output):
    output.mkdir(mode=0o700, exist_ok=False)
    source = Path(__file__).resolve().parents[3] / "Lintap/pidstat-collector.py"
    spec = importlib.util.spec_from_file_location("sampler_fixture_reference", source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    os.environ["TZ"] = "America/Phoenix"
    time.tzset()
    fixtures(module, output, binary)
    alternate = output / "alternate-kernel-fixtures"
    alternate.mkdir(mode=0o700)
    fixtures(module, alternate, binary, ticks=250, page_bytes=16384)
    config_checks(module, output, binary)
    evidence.write(output / "result.json", {"status": "PASS", "kind": "controlled-source-sampler-config-fixture-not-live-proc",
        "source_sha256": evidence.sha(source), "binary_sha256": evidence.sha(binary)})
    print("PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    check(args.binary, args.output)
