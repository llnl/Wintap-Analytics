#!/usr/bin/env python3
"""Actual Python legacy spool production/recovery vs Go; real captures are required."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

import evidence


def load_reference():
    source = Path(__file__).resolve().parents[3] / "Lintap/pidstat-collector.py"
    spec = importlib.util.spec_from_file_location("spool_python_reference", source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.duckdb is None:
        raise RuntimeError("actual Python/DuckDB reference required")
    return module, source


def env_for(root, hostname, compression="ZSTD"):
    return {"PIDSTAT_PARQUET_ROOT": str((root / "data").resolve()),
            "PIDSTAT_SPOOL_DIR": str((root / "spool").resolve()),
            "PIDSTAT_HOSTNAME": hostname, "PIDSTAT_INTERVAL_SEC": "1",
            "PIDSTAT_ROTATE_INTERVAL_SEC": "300", "PIDSTAT_MIN_ROTATE_INTERVAL_SEC": "1",
            "PIDSTAT_MAX_UNSHIPPED_BYTES": "0", "PIDSTAT_MAX_UNSHIPPED_AGE_SEC": "0",
            "PIDSTAT_PARQUET_COMPRESSION": compression}


def config(module, root, hostname, codec="ZSTD"):
    (root / "spool").mkdir(parents=True, mode=0o700)
    return module.Config(root / "data", 1, 300, 1, root / "data", root / "spool", codec, 1, 0, 0, hostname)


def compare(reference, candidate, output):
    expected, expected_schema, _ = evidence.read_dataset(reference)
    actual, actual_schema, _ = evidence.read_dataset(candidate)
    report = evidence.compare_rows(expected, actual)
    report["schemas_equal"] = all(s["columns"] == expected_schema[0]["columns"] and
        s["physical"] == expected_schema[0]["physical"] for s in expected_schema + actual_schema)
    evidence.write(output / "python-rows.json", expected)
    evidence.write(output / "go-rows.json", actual)
    evidence.write(output / "comparison.json", report)
    assert report["equal"] and report["schemas_equal"], report
    return report


def record_go(recorder, binary, root, hostname, codec="ZSTD", args=None):
    return recorder.run(["/usr/bin/env", *[key + "=" + value for key, value in env_for(root, hostname, codec).items()],
                         str(binary.resolve()), *(args or ["--recover"]), "--timezone", "America/Phoenix"], timeout=300)


def check(binary, reference, output):
    output.mkdir(mode=0o700, exist_ok=False)
    module, source = load_reference()
    evidence.validate_reference(reference)
    capture = json.loads((reference / "capture.json").read_text())
    rows = (reference / "golden.tsv").read_text().splitlines()
    assert len(rows) == sum(sample["output_rows"] for sample in capture["samples"])
    os.environ["TZ"] = "America/Phoenix"
    time.tzset()
    recorder = evidence.Recorder(output)
    reports = {}
    hostname = capture["hostname"]

    for case in ["current", "current-missing-meta", "pending-multiple", "pending-invalid-meta"]:
        root = output / case
        collector = module.Collector(config(module, root / "python", hostname), sampler=object())
        index = 0
        # Drive the unchanged producer methods on ACTUAL live Python rows, using
        # the captured sample epoch, never timestamps inferred from rounded TSV.
        try:
            for sample in capture["samples"]:
                count = sample["output_rows"]
                if not count:
                    continue
                collector.rotate_current_window_if_needed(int(sample["captured_at"]))
                collector.append_rows([SimpleNamespace(to_tsv=lambda text=text: text) for text in rows[index:index+count]])
                index += count
            assert index == len(rows)
            if case.startswith("pending"):
                collector.seal_current_spool()
                if case == "pending-multiple":
                    pending = next(collector.config.spool_dir.glob("pending-*.tsv"))
                    contents = pending.read_text().splitlines(keepends=True)
                    split = len(contents) // 2
                    pending.write_text("".join(contents[:split]))
                    second = pending.with_name("pending-second.tsv")
                    second.write_text("".join(contents[split:]))
                    shutil.copyfile(pending.with_suffix(".meta"), second.with_suffix(".meta"))
                else:
                    for meta in collector.config.spool_dir.glob("*.meta"):
                        meta.write_text("window_start_epoch=not-an-integer\n")
            elif case == "current-missing-meta":
                collector.current_meta_path().unlink()
            go = root / "go"
            (go / "spool").mkdir(parents=True, mode=0o700)
            for path in collector.config.spool_dir.iterdir():
                shutil.copyfile(path, go / "spool" / path.name)
            evidence.write(root / "legacy-spool-manifest.json", {p.name: evidence.sha(p) for p in (go / "spool").iterdir()})
            collector.salvage_spool_files()
        finally:
            collector.close()
        record = record_go(recorder, binary, go, hostname)
        assert record["returncode"] == 0, record
        report = compare(root / "python/data", go / "data", root)
        assert report["python_rows"] == len(rows)
        assert not list((go / "spool").glob("*.tsv"))
        assert not list((go / "spool").glob("*.meta"))
        reports[case] = report

    # Same captured RAW reads through sampler -> durable Go spool -> writer.
    root = output / "raw-durable-replay"
    record = record_go(recorder, binary, root, hostname, args=["--spool-replay", str((reference / "capture.json").resolve())])
    assert record["returncode"] == 0, record
    reports["raw-durable-replay"] = compare(reference, root / "data", root)

    # Actual reference compression and metadata semantics. This is supplemental,
    # with already captured real rows, not an invented sampler or synthetic oracle.
    for index, codec in enumerate(["ZSTD", "zstd", "SNAPPY", "GZIP", "LZ4_RAW", "UNCOMPRESSED", "LZ4", "BROTLI", "invalid"]):
        root = output / (f"codec-{index}-" + codec)
        cfg = config(module, root / "python", hostname, codec)
        collector = module.Collector(cfg, sampler=object())
        spool = cfg.spool_dir / "pending-codec.tsv"
        spool.write_text(rows[0] + "\n")
        collector.write_meta_file(spool.with_suffix(".meta"), module.window_start_for_epoch(int(capture["samples"][1]["captured_at"]), 300))
        go = root / "go"
        (go / "spool").mkdir(parents=True, mode=0o700)
        shutil.copyfile(spool, go / "spool" / spool.name)
        shutil.copyfile(spool.with_suffix(".meta"), go / "spool" / spool.with_suffix(".meta").name)
        try:
            python_success = collector.convert_spool_to_parquet(spool, spool.with_suffix(".meta"))
        finally:
            collector.close()
        record = record_go(recorder, binary, go, hostname, codec)
        go_success = record["returncode"] == 0
        reports["codec-" + codec] = {"python_success": python_success, "go_success": go_success}
        evidence.write(root / "acceptance.json", reports["codec-" + codec])
        assert python_success == go_success, (codec, python_success, go_success)
        if python_success:
            reports["codec-" + codec] = compare(root / "python/data", go / "data", root)
        else:
            assert (go / "spool" / spool.name).exists()

    evidence.write(output / "result.json", {"status": "PASS", "kind": "actual-Python-legacy-spool-and-real-raw-durable-replay",
        "source_sha256": evidence.sha(source), "binary_sha256": evidence.sha(binary),
        "capture_sha256": evidence.sha(reference / "capture.json"), "reports": reports})
    print("PASS: actual Python legacy spools, raw durable replay and compression")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    check(args.binary, args.reference, args.output)
