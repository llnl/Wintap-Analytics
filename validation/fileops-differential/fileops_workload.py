#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mmap
import os
import socket
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic FileOps workload")
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--files", type=int, default=16)
    parser.add_argument("--rounds", type=int, default=4)
    args = parser.parse_args()

    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"work_dir": str(work_dir), "files": [], "noise": []}

    payload = b"wintap-fileops-differential\n" * 32
    for round_index in range(args.rounds):
        for file_index in range(args.files):
            path = work_dir / f"fileops-{round_index:02d}-{file_index:03d}.dat"
            with path.open("wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            with path.open("rb") as handle:
                handle.read(64)
            with path.open("r+b") as handle:
                with mmap.mmap(handle.fileno(), 0) as mapped:
                    mapped[:1]
            path.unlink()
            manifest["files"].append(str(path))

    # fop-13 scenario: dirfd-relative opens through an explicit O_DIRECTORY
    # handle. The DIR_OPEN record teaches the sensor's dir-identity index and
    # the relative opens must resolve to absolute paths under work_dir.
    rel_dir = work_dir / "relbase"
    rel_dir.mkdir(exist_ok=True)
    rel_target = rel_dir / "relative-target.dat"
    rel_target.write_bytes(payload)
    dir_fd = os.open(str(rel_dir), os.O_RDONLY | os.O_DIRECTORY)
    try:
        for _ in range(args.rounds):
            fd = os.open("relative-target.dat", os.O_RDONLY, dir_fd=dir_fd)
            try:
                os.read(fd, 64)
            finally:
                os.close(fd)
        manifest["files"].append(str(rel_target))
        manifest["dirfd_relative"] = {
            "base_dir": str(rel_dir),
            "relative_name": "relative-target.dat",
            "expected_absolute": str(rel_target),
        }
    finally:
        os.close(dir_fd)
        rel_target.unlink()
        rel_dir.rmdir()

    # Negative/noise cases: these should not be required in regular-file parity.
    try:
        Path("/proc/self/stat").read_text(encoding="utf-8")
        manifest["noise"].append("/proc/self/stat")
    except OSError:
        pass

    try:
        with open("/dev/null", "wb") as handle:
            handle.write(b"noise")
        manifest["noise"].append("/dev/null")
    except OSError:
        pass

    try:
        left, right = socket.socketpair()
        try:
            left.sendall(b"socket-noise")
            right.recv(64)
            manifest["noise"].append("socketpair")
        finally:
            left.close()
            right.close()
    except OSError:
        pass

    Path(args.manifest).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
