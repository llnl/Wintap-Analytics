#!/usr/bin/env python3
"""Guest-side reference capture; imports the real Python collector, never its port."""

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import tarfile
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(source, output, samples, interval):
    source = source.resolve()
    source_hash = sha(source)
    spec = importlib.util.spec_from_file_location("pidstat_reference", source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.duckdb is None:
        raise RuntimeError("reference Python requires its existing DuckDB environment")
    if platform.system() != "Linux" or platform.machine() not in ("aarch64", "arm64"):
        raise RuntimeError("first reference target must be Linux arm64")
    if "ubuntu" not in Path("/etc/os-release").read_text().lower():
        raise RuntimeError("first reference target must be Ubuntu")
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    hostname = module.short_hostname()
    reads, links, enumerations = {}, {}, []
    original_read = module.read_optional_text
    original_link = os.readlink
    original_scandir = os.scandir

    def observed_scandir(path):
        if str(path) == "/proc":
            with original_scandir(path) as scan:
                entries = list(scan)
            enumerations.append([entry.name for entry in entries if entry.name.isdigit()])
            return iter(entries)
        return original_scandir(path)

    def observed_read(path):
        value = original_read(path)
        reads[str(path)] = value  # Includes unavailable reads; never invent zero values.
        return value

    def observed_link(path, *args, **kwargs):
        try:
            value = original_link(path, *args, **kwargs)
        except OSError:
            links[str(path)] = None
            raise
        links[str(path)] = value
        return value

    module.read_optional_text = observed_read
    os.readlink = observed_link
    os.scandir = observed_scandir
    collector = None
    captures, golden = [], []
    try:
        sampler = module.ProcSampler(hostname)
        initial_reads = dict(reads)
        config = module.Config(
            data_root=output / "data", interval_sec=interval,
            rotate_interval_sec=300, min_rotate_interval_sec=300,
            parquet_root=output / "data", spool_dir=output / "runtime",
            parquet_compression="ZSTD", duckdb_threads=1,
            max_unshipped_bytes=0, max_unshipped_age_sec=0, hostname=hostname)
        collector = module.Collector(config, sampler=sampler)
        for index in range(samples):
            reads.clear()
            links.clear()
            enumerations.clear()
            started = time.time()
            rows = sampler.sample(started)
            captures.append({"captured_at": started, "reads": dict(reads),
                             "proc_pid_enumerations": list(enumerations),
                             "pid_ns_links": dict(links),
                             "snapshots": [asdict(s) for s in sampler.previous.values()],
                             "output_rows": len(rows)})
            if rows:
                collector.rotate_current_window_if_needed(int(started))
                collector.append_rows(rows)
                golden.extend(row.to_tsv() for row in rows)
            if index + 1 < samples:
                time.sleep(max(interval - (time.time() - started), 0))
        collector.seal_current_spool()
        collector.process_pending_spools()
    finally:
        module.read_optional_text = original_read
        os.readlink = original_link
        os.scandir = original_scandir
        if collector is not None:
            collector.close()
    if not golden or list(config.spool_dir.glob("pending-*.tsv")):
        raise RuntimeError("reference emitted no rows or failed to convert a pending spool")
    if sha(source) != source_hash:
        raise RuntimeError("reference source changed during capture")
    inputs = {"initial_reads": initial_reads, "samples": captures,
              "hostname": hostname, "clock_ticks": sampler.clock_ticks,
              "page_size_bytes": os.sysconf("SC_PAGE_SIZE"),
              "mem_total_kb": sampler.mem_total_kb, "timezone": list(time.tzname)}
    (output / "capture.json").write_text(json.dumps(inputs) + "\n")
    (output / "golden.tsv").write_text("\n".join(golden) + "\n")
    files = [output / "capture.json", output / "golden.tsv"] + sorted(
        (output / "data").rglob("*.parquet"))
    manifest = {"kind": "actual-python-proc-reference", "source": str(source),
                "source_sha256": source_hash, "python": sys.version,
                "duckdb": module.duckdb.__version__, "platform": platform.platform(),
                "architecture": platform.machine(), "interval_sec": interval,
                "sample_count": samples, "rows": len(golden),
                "files": {str(p.relative_to(output)): sha(p) for p in files}}
    (output / "reference.json").write_text(json.dumps(manifest, indent=2) + "\n")
    archive = output / "reference.tar"
    with tarfile.open(archive, "w") as tar:
        for path in files + [output / "reference.json"]:
            tar.add(path, arcname=str(path.relative_to(output)), recursive=False)
    archive.chmod(0o600)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("samples", type=int)
    parser.add_argument("interval", type=int)
    args = parser.parse_args()
    if not 2 <= args.samples <= 12 or not 1 <= args.interval <= 30:
        parser.error("samples must be 2..12 and interval 1..30 seconds")
    print(json.dumps(capture(args.source, args.output, args.samples, args.interval)))
