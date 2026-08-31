from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import socket


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_kb_value(raw: str) -> int:
    token = raw.strip().split()[0]
    return int(token)


def parse_smaps_rollup(text: str) -> dict[str, int]:
    metrics: dict[str, int] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value or not value.endswith("kB"):
            continue
        metrics[key] = parse_kb_value(value)
    return metrics


def parse_status(text: str) -> dict[str, int | str]:
    wanted_kb = {
        "VmPeak",
        "VmSize",
        "VmLck",
        "VmPin",
        "VmHWM",
        "VmRSS",
        "RssAnon",
        "RssFile",
        "RssShmem",
        "VmData",
        "VmStk",
        "VmExe",
        "VmLib",
        "VmPTE",
        "VmSwap",
    }
    wanted_int = {"Tgid", "Pid", "PPid", "Threads", "FDSize", "voluntary_ctxt_switches", "nonvoluntary_ctxt_switches"}
    wanted_text = {"Name", "State"}

    parsed: dict[str, int | str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in wanted_kb and value:
            parsed[key] = parse_kb_value(value)
        elif key in wanted_int and value:
            parsed[key] = int(value.split()[0])
        elif key in wanted_text:
            parsed[key] = value
    return parsed


def count_fds(fd_dir: Path) -> int:
    return sum(1 for _ in fd_dir.iterdir())


def summarize_maps(text: str) -> dict[str, int]:
    mapped_regions = 0
    mapped_bytes_total = 0
    executable_regions = 0
    writable_private_regions = 0

    for line in text.splitlines():
        if not line:
            continue
        fields = line.split()
        if len(fields) < 2:
            continue
        address_range = fields[0]
        perms = fields[1]
        if "-" not in address_range:
            continue
        start_raw, end_raw = address_range.split("-", 1)
        start = int(start_raw, 16)
        end = int(end_raw, 16)
        mapped_regions += 1
        mapped_bytes_total += max(0, end - start)
        if "x" in perms:
            executable_regions += 1
        if perms.startswith("rw") and "p" in perms:
            writable_private_regions += 1

    return {
        "mapped_regions": mapped_regions,
        "mapped_bytes_total": mapped_bytes_total,
        "executable_regions": executable_regions,
        "writable_private_regions": writable_private_regions,
    }


@dataclass
class ProcSnapshotPaths:
    proc_root: Path
    pid: int

    @property
    def proc_dir(self) -> Path:
        return self.proc_root / str(self.pid)

    @property
    def smaps_rollup(self) -> Path:
        return self.proc_dir / "smaps_rollup"

    @property
    def status(self) -> Path:
        return self.proc_dir / "status"

    @property
    def maps(self) -> Path:
        return self.proc_dir / "maps"

    @property
    def fd_dir(self) -> Path:
        return self.proc_dir / "fd"

    @property
    def comm(self) -> Path:
        return self.proc_dir / "comm"


def read_process_name(paths: ProcSnapshotPaths) -> str:
    return read_text(paths.comm).strip()


def collect_smaps_rollup_row(paths: ProcSnapshotPaths, run_id: str, hostname: str | None = None) -> dict[str, int | str]:
    row: dict[str, int | str] = {
        "time": iso_now(),
        "hostname": hostname or socket.gethostname(),
        "pid": paths.pid,
        "process_name": read_process_name(paths),
        "run_id": run_id,
    }
    row.update(parse_smaps_rollup(read_text(paths.smaps_rollup)))
    return row


def collect_proc_status_row(paths: ProcSnapshotPaths, run_id: str, hostname: str | None = None) -> dict[str, int | str]:
    row: dict[str, int | str] = {
        "time": iso_now(),
        "hostname": hostname or socket.gethostname(),
        "pid": paths.pid,
        "process_name": read_process_name(paths),
        "run_id": run_id,
    }
    row.update(parse_status(read_text(paths.status)))
    return row


def collect_fd_map_row(paths: ProcSnapshotPaths, run_id: str, hostname: str | None = None) -> dict[str, int | str]:
    row: dict[str, int | str] = {
        "time": iso_now(),
        "hostname": hostname or socket.gethostname(),
        "pid": paths.pid,
        "process_name": read_process_name(paths),
        "run_id": run_id,
        "open_fd_count": count_fds(paths.fd_dir),
    }
    row.update(summarize_maps(read_text(paths.maps)))
    return row
