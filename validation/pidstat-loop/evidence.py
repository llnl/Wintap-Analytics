#!/usr/bin/env python3
"""One deterministic pidstat experiment. The OpenCode skill owns repair iteration."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import struct
import subprocess
import sys
import tarfile
import time
import uuid


HERE = Path(__file__).resolve().parent
COLUMNS = ["time", "uid", "pid", "usr_percent", "system_percent", "guest_percent",
           "wait_percent", "cpu_percent", "cpu_core", "minflt_per_sec", "majflt_per_sec",
           "vsz_kb", "rss_kb", "mem_percent", "kb_read_per_sec", "kb_write_per_sec",
           "kb_cancelled_write_per_sec", "iodelay_ticks", "context_switch_per_sec",
           "nonvoluntary_context_switch_per_sec", "command", "hostname", "cgroup_path",
           "pid_ns_inode", "container_runtime", "container_id"]
KEY = ["time", "uid", "pid", "hostname", "partition", "window_start_epoch"]


def sha(path):
    with Path(path).open("rb") as stream:
        result = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


class Recorder:
    def __init__(self, output):
        self.output, self.number = output, 0

    def run(self, argv, timeout=300, stdin=None):
        self.number += 1
        prefix = self.output / f"{self.number:02d}-command"
        started = time.monotonic()
        with prefix.with_suffix(".stdout").open("wb") as out, prefix.with_suffix(".stderr").open("wb") as err:
            try:
                process = subprocess.Popen(argv, stdout=out, stderr=err,
                                           stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                           start_new_session=True)
                try:
                    process.communicate(input=stdin, timeout=timeout)
                    rc = process.returncode
                except (subprocess.TimeoutExpired, KeyboardInterrupt):
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    err.write(b"Local client interrupted; guest work may still be running.\n")
                    rc = -1
            except OSError as error:
                err.write(str(error).encode())
                rc = -1
        result = {"argv": argv, "returncode": rc,
                  "elapsed_seconds": time.monotonic() - started,
                  "stdout": str(prefix.with_suffix(".stdout")),
                  "stderr": str(prefix.with_suffix(".stderr"))}
        write(prefix.with_suffix(".json"), result)
        return result


def extract_reference(archive, target):
    """Do not trust guest archive paths, links or special files."""
    target.mkdir(mode=0o700, exist_ok=False)
    with tarfile.open(archive) as tar:
        total, seen = 0, set()
        for member in tar:
            name = Path(member.name)
            if (name.is_absolute() or ".." in name.parts or not member.isfile()
                    or str(name) in seen):
                raise ValueError("unsafe or duplicate reference archive entry")
            seen.add(str(name))
            total += member.size
            if total > 256 * 1024 * 1024:
                raise ValueError("reference archive exceeds 256 MiB limit")
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as out, tar.extractfile(member) as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    out.write(block)


def validate_reference(root):
    manifest = json.loads((root / "reference.json").read_text())
    if (manifest.get("kind") != "actual-python-proc-reference" or manifest.get("rows", 0) <= 0
            or manifest.get("sample_count", 0) < 2
            or not re.fullmatch(r"[0-9a-f]{64}", manifest.get("source_sha256", ""))):
        raise ValueError("missing actual Python reference provenance/rows")
    files = manifest.get("files", {})
    if not {"capture.json", "golden.tsv"} <= set(files):
        raise ValueError("reference must include raw captures and actual Python TSV")
    for name, expected in files.items():
        path = Path(name)
        if (path.is_absolute() or ".." in path.parts
                or not (root / path).resolve().is_relative_to(root.resolve())
                or sha(root / path) != expected):
            raise ValueError(f"reference input/output hash mismatch: {name}")
    actual = {str(p.relative_to(root)) for p in (root / "data").rglob("*.parquet")}
    if not actual or actual != {name for name in files if name.endswith(".parquet")}:
        raise ValueError("reference Parquet file set differs from manifest")
    return manifest


def inspect_elf(path, machine):
    data = Path(path).read_bytes()
    if len(data) < 64 or data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("requires a little-endian 64-bit ELF binary")
    header = struct.unpack_from("<16sHHIQQQIHHHHHH", data)
    _, kind, actual, version, entry, offset, _, _, _, size, count, _, _, _ = header
    if kind not in (2, 3) or actual != machine or version != 1 or not entry or not count:
        raise ValueError("not an executable ELF for the requested architecture")
    if size < 56 or offset + size * count > len(data):
        raise ValueError("invalid/truncated ELF program headers")
    for index in range(count):
        segment = struct.unpack_from("<IIQQQQQQ", data, offset + index * size)
        tag, _, file_offset, _, _, file_size, _, _ = segment
        if tag == 3:
            raise ValueError("ELF requests a dynamic interpreter (PT_INTERP)")
        if file_offset + file_size > len(data):
            raise ValueError("truncated ELF segment")
        if tag == 2:
            if file_size % 16:
                raise ValueError("malformed dynamic segment")
            for pos in range(file_offset, file_offset + file_size, 16):
                dynamic_tag, _ = struct.unpack_from("<qQ", data, pos)
                if dynamic_tag == 0:
                    break
                if dynamic_tag == 1:
                    raise ValueError("ELF requires a shared library (DT_NEEDED)")
    return {"path": str(path), "sha256": sha(path), "machine": actual,
            "interpreter": None, "needed_libraries": []}


def value_json(value):
    if isinstance(value, datetime):
        return value.isoformat(timespec="microseconds")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite metric value")
    return value


def read_dataset(root):
    import duckdb  # Development/test dependency only; never used by the installed Go collector.
    files = sorted(root.rglob("*.parquet")) if root.is_dir() else [root]
    if not files or any(not path.is_file() for path in files):
        raise ValueError("missing Parquet dataset")
    rows, schemas = [], []
    with duckdb.connect() as db:
        for path in files:
            query = db.execute("SELECT * FROM read_parquet(?, hive_partitioning=false)", [str(path)])
            columns = [(field[0], str(field[1])) for field in query.description]
            partition = [part for part in path.parts if part.startswith(("dayPK=", "hourPK="))]
            window = re.fullmatch(r".+\+pidstat\+(\d+)(?:-\d+-\d+)?\.parquet", path.name)
            if (len(partition) != 2 or not re.fullmatch(r"dayPK=\d{8}", partition[0])
                    or not re.fullmatch(r"hourPK=\d{2}", partition[1]) or window is None):
                raise ValueError(f"missing/invalid pidstat partition or window filename: {path}")
            for record in query.fetchall():
                row = {name: value_json(value) for (name, _), value in zip(columns, record)}
                row["partition"] = partition
                row["window_start_epoch"] = int(window[1])
                rows.append(row)
            physical = db.execute(
                "SELECT name, type, repetition_type, converted_type, logical_type "
                "FROM parquet_schema(?) WHERE type IS NOT NULL", [str(path)]).fetchall()
            schemas.append({"file": str(path), "sha256": sha(path), "columns": columns,
                            "physical": [list(field) for field in physical]})
    return rows, schemas, duckdb.__version__


def compare_rows(reference, candidate):
    """Exact keyed multiset comparison: duplicates and unmatched rows cannot disappear."""
    def token(row):
        return json.dumps(row, sort_keys=True, allow_nan=False)

    def grouped(rows):
        result = defaultdict(list)
        for row in rows:
            key = token({name: row.get(name) for name in KEY})
            result[key].append(row)
        return result

    a, b = grouped(reference), grouped(candidate)
    unmatched_a, unmatched_b = [], []
    differences = {name: {"mismatches": 0, "max_absolute_error": 0} for name in COLUMNS}
    for key in sorted(set(a) | set(b)):
        left, right = sorted(a[key], key=token), sorted(b[key], key=token)
        # Pair identical rows first, then inspect remaining mismatches. This preserves
        # duplicate accounting without sorting differences inventing extra mismatches.
        right_tokens = Counter(token(row) for row in right)
        remaining_left = []
        for row in left:
            if right_tokens[token(row)]:
                right_tokens[token(row)] -= 1
            else:
                remaining_left.append(row)
        remaining_right = []
        for row in right:
            if right_tokens[token(row)]:
                remaining_right.append(row)
                right_tokens[token(row)] -= 1
        unmatched_a.extend(remaining_left[len(remaining_right):])
        unmatched_b.extend(remaining_right[len(remaining_left):])
        for old, new in zip(remaining_left, remaining_right):
            for name in COLUMNS:
                if old.get(name) != new.get(name):
                    differences[name]["mismatches"] += 1
                    x, y = old.get(name), new.get(name)
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        differences[name]["max_absolute_error"] = max(
                            differences[name]["max_absolute_error"], abs(x - y))
    equal = Counter(map(token, reference)) == Counter(map(token, candidate))
    return {"equal": equal, "python_rows": len(reference), "candidate_rows": len(candidate),
            "unmatched_python": unmatched_a, "unmatched_candidate": unmatched_b,
            "columns": differences}


def compare(reference, candidate, output):
    manifest = validate_reference(reference)
    a, schema_a, version = read_dataset(reference / "data")
    b, schema_b, _ = read_dataset(candidate)
    if len(a) != manifest["rows"]:
        raise ValueError("Python manifest row count differs from actual Parquet")
    expected = schema_a[0]
    if [name for name, _ in expected["columns"]] != COLUMNS:
        raise ValueError("Python reference no longer matches the agreed 26-column contract")
    schemas_equal = all(row["columns"] == expected["columns"] and
                        row["physical"] == expected["physical"] for row in schema_a + schema_b)
    report = compare_rows(a, b)
    report.update(schemas_equal=schemas_equal, duckdb=version,
                  reference_source_sha256=manifest["source_sha256"],
                  replay_input_sha256=manifest["files"]["capture.json"],
                  python_schema=schema_a, candidate_schema=schema_b)
    write(output / "python-rows.json", a)
    write(output / "candidate-rows.json", b)
    write(output / "comparison.json", report)
    return report["equal"] and schemas_equal, report


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, help="new private evidence directory")
    commands = cli.add_subparsers(dest="mode", required=True)
    capture = commands.add_parser("capture-python", help="one isolated real reference run in lintap-dev")
    capture.add_argument("--collector", required=True, help="absolute guest Python collector path")
    capture.add_argument("--python", required=True, help="absolute guest interpreter with DuckDB")
    capture.add_argument("--samples", type=int, default=3)
    capture.add_argument("--interval", type=int, default=5)
    exact = commands.add_parser("compare", help="exact replay parity, not paired-live tolerance")
    exact.add_argument("--reference", type=Path, required=True)
    exact.add_argument("--candidate", type=Path, required=True)
    static = commands.add_parser("static", help="inspect both actual ELF binaries without executing them")
    static.add_argument("--arm64", type=Path, required=True)
    static.add_argument("--amd64", type=Path, required=True)
    smoke = commands.add_parser("smoke", help="hash-matched root restricted-PATH --help startup only")
    smoke.add_argument("--host-binary", type=Path, required=True)
    smoke.add_argument("--guest-binary", required=True)
    record = commands.add_parser("record", help="record exactly one supplied test/build command")
    record.add_argument("--timeout", type=int, default=300)
    record.add_argument("argv", nargs=argparse.REMAINDER)
    return cli


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    if args.mode == "capture-python" and (not 2 <= args.samples <= 12 or not 1 <= args.interval <= 30):
        cli.error("samples must be 2..12 and interval 1..30 seconds")
    if args.mode == "record" and not 1 <= args.timeout <= 7200:
        cli.error("timeout must be 1..7200 seconds")
    output = (args.output or HERE / "evidence" /
              (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])).resolve()
    try:
        output.mkdir(mode=0o700, parents=True, exist_ok=False)
    except OSError as error:
        cli.error(str(error))
    print("Evidence: " + str(output), flush=True)
    write(output / "manifest.json", {"mode": args.mode, "utility_sha256": sha(Path(__file__)),
          "capture_helper_sha256": sha(HERE / "capture_python.py"), "python": sys.version,
          "arguments": vars(args), "started_at": datetime.now(timezone.utc).isoformat()})
    recorder = Recorder(output)
    status, detail = "INCOMPLETE", {}
    try:
        if args.mode == "record":
            command = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
            if not command:
                raise ValueError("record requires a command after --")
            detail = recorder.run(command, args.timeout)
            status = "PASS" if detail["returncode"] == 0 else "FAIL"
        elif args.mode == "static":
            detail = {"arm64": inspect_elf(args.arm64, 183), "amd64": inspect_elf(args.amd64, 62)}
            status = "PASS"
        elif args.mode == "compare":
            passed, detail = compare(args.reference.resolve(), args.candidate.resolve(), output)
            status = "PASS" if passed else "FAIL"
        elif args.mode == "capture-python":
            if not all(Path(p).is_absolute() for p in (args.collector, args.python)):
                raise ValueError("guest collector/interpreter paths must be absolute")
            guest = "/var/tmp/pidstat-reference-" + uuid.uuid4().hex
            capture = recorder.run(["multipass", "exec", "lintap-dev", "--", "sudo",
                                   args.python, "-", args.collector, guest,
                                   str(args.samples), str(args.interval)],
                                  600 + args.samples * args.interval,
                                  (HERE / "capture_python.py").read_bytes())
            detail = {"capture": capture, "guest_directory": guest}
            if capture["returncode"] != 0:
                status = "FAIL"
            else:
                transfer = recorder.run(["multipass", "exec", "lintap-dev", "--", "sudo",
                                         "cat", guest + "/reference.tar"], 300)
                detail["transfer"] = transfer
                if transfer["returncode"] != 0:
                    status = "FAIL"
                else:
                    extract_reference(Path(transfer["stdout"]), output / "reference")
                    detail["reference"] = validate_reference(output / "reference")
                    status = "PASS"
        else:
            if not Path(args.guest_binary).is_absolute():
                raise ValueError("guest binary path must be absolute")
            host = inspect_elf(args.host_binary, 183)
            hashed = recorder.run(["multipass", "exec", "lintap-dev", "--", "sudo",
                                   "sha256sum", "--", args.guest_binary])
            words = Path(hashed["stdout"]).read_text().split()
            detail = {"host": host, "guest_hash": hashed}
            if hashed["returncode"] != 0 or not words or words[0] != host["sha256"]:
                status = "FAIL"
            else:
                startup = recorder.run(["multipass", "exec", "lintap-dev", "--", "sudo", "env",
                                        "PATH=/usr/sbin:/usr/bin:/sbin:/bin", args.guest_binary, "--help"])
                detail["startup"] = startup
                status = "PASS" if startup["returncode"] == 0 else "FAIL"
    except Exception as error:
        detail = {"error": f"{type(error).__name__}: {error}", "partial": detail}
    result = {"status": status, "scope": args.mode, "detail": detail}
    write(output / "result.json", result)
    print(status + " — " + str(output / "result.json"))
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[status]


if __name__ == "__main__":
    sys.exit(main())
