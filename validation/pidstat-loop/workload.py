#!/usr/bin/env python3
"""Bounded fpc-01 reference stimulus, NOT a collector or parity oracle."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time


def run(output, duration):
    output.mkdir(mode=0o700, exist_ok=False)
    started = time.time()
    deadline = time.monotonic() + duration
    payload = b"x" * (4 * 1024 * 1024)
    memory = bytearray(32 * 1024 * 1024)
    results = {"pid": os.getpid(), "started_at": started, "duration_seconds": duration,
               "cpu_threads": 2, "memory_bytes": len(memory), "children": [],
               "io_bytes_written": 0, "hash_iterations": [0, 0]}

    def cpu(index):
        # Large hashlib inputs release Python's GIL: two threads in one process.
        while time.monotonic() < deadline:
            hashlib.sha256(payload).digest()
            results["hash_iterations"][index] += 1

    def io():
        # At most 64 MiB total writes, 4 MiB retained, with fsync and actual reads.
        for _ in range(16):
            if time.monotonic() >= deadline:
                break
            with (output / "io.bin").open("wb", buffering=0) as stream:
                stream.write(payload)
                os.fsync(stream.fileno())
                results["io_bytes_written"] += len(payload)
            with (output / "io.bin").open("rb", buffering=0) as stream:
                stream.read()
            time.sleep(duration / 10)

    threads = [threading.Thread(target=cpu, args=(i,)) for i in range(2)]
    threads.append(threading.Thread(target=io))
    for thread in threads:
        thread.start()
    children = []
    try:
        for _ in range(10):
            if time.monotonic() >= deadline:
                break
            child = subprocess.Popen(["/bin/sleep", "2"])
            children.append(child)
            results["children"].append(child.pid)
            time.sleep(duration / 10)
    finally:
        for child in children:
            child.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=duration + 5)
    results["finished_at"] = time.time()
    (output / "workload.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=20)
    args = parser.parse_args()
    if not 5 <= args.duration <= 30:
        parser.error("duration must be 5..30 seconds")
    run(args.output, args.duration)
