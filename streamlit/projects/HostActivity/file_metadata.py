"""Filename-based collection time and S3 object-metadata aggregation."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import PurePosixPath

from queries import MAX_CHART_POINTS, choose_bucket_minutes
from s3_source import S3ObjectMetadata


UTC = dt.timezone.utc
FILETIME_EPOCH = dt.datetime(1601, 1, 1, tzinfo=UTC)
FILETIME_TICKS_PER_SECOND = 10_000_000


@dataclass(frozen=True)
class ParsedFileMetadata:
    hostname: str
    event_type: str
    collect_time: dt.datetime
    size_bytes: int


@dataclass(frozen=True)
class FileMetadataResult:
    listed_files: int
    files_in_window: int
    total_size_bytes: int
    unparsed_files: int
    unparsed_size_bytes: int
    outside_window_files: int
    outside_window_size_bytes: int
    bucket_minutes: int
    host_count: int
    host_summary: tuple[dict, ...]
    points: tuple[dict, ...]


def _filetime_datetime(value: str) -> dt.datetime:
    if not value.isascii() or not value.isdecimal():
        raise ValueError("Filename collect time must be a nonnegative Win32 FILETIME integer")
    ticks = int(value)
    seconds, remaining_ticks = divmod(ticks, FILETIME_TICKS_PER_SECOND)
    try:
        return FILETIME_EPOCH + dt.timedelta(seconds=seconds, microseconds=remaining_ticks // 10)
    except OverflowError:
        raise ValueError("Filename collect time is outside the supported datetime range") from None


def _canonical_event_type(value: str) -> str:
    normalized = value.strip().lower()
    if "tcp" in normalized or "udp" in normalized:
        return "raw_process_conn_incr"
    aliases = {
        "raw_host_sensor": "raw_host",
        "raw_macip_sensor": "raw_macip",
        "raw_file": "raw_process_file",
        "raw_processstop": "raw_process",
        "raw_registry": "raw_process_registry",
    }
    return aliases.get(normalized, normalized)


def parse_file_metadata(obj: S3ObjectMetadata) -> ParsedFileMetadata | None:
    """Parse ``hostname+event_type+filetime.parquet`` without opening the object."""
    filename = PurePosixPath(obj.key).name
    if not filename.lower().endswith(".parquet"):
        return None
    stem = filename[:-len(".parquet")]
    parts = stem.split("+")
    if len(parts) != 3:
        return None
    hostname, filename_event_type, filetime = parts
    if not hostname.strip() or not filename_event_type.strip():
        return None
    if _canonical_event_type(filename_event_type) != obj.event_type:
        return None
    try:
        collect_time = _filetime_datetime(filetime)
    except ValueError:
        return None
    return ParsedFileMetadata(
        hostname=hostname.strip(),
        event_type=obj.event_type,
        collect_time=collect_time,
        size_bytes=obj.size_bytes,
    )


def aggregate_file_metadata(
    objects,
    start: dt.datetime,
    end: dt.datetime,
    *,
    point_budget: int = MAX_CHART_POINTS,
) -> FileMetadataResult:
    """Aggregate valid filename timestamps and S3 sizes in the exact UTC window."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Metadata window bounds must include a timezone")
    start_utc = start.astimezone(UTC)
    end_utc = end.astimezone(UTC)
    if end_utc <= start_utc:
        raise ValueError("Metadata window end must be after its start")

    listed_files = 0
    unparsed_files = 0
    unparsed_size_bytes = 0
    outside_window_files = 0
    outside_window_size_bytes = 0
    accepted = []
    for obj in objects:
        listed_files += 1
        parsed = parse_file_metadata(obj)
        if parsed is None:
            unparsed_files += 1
            unparsed_size_bytes += obj.size_bytes
        elif not start_utc <= parsed.collect_time < end_utc:
            outside_window_files += 1
            outside_window_size_bytes += parsed.size_bytes
        else:
            accepted.append(parsed)

    host_stats = {}
    for file in accepted:
        stats = host_stats.setdefault(
            file.hostname,
            {"hostname": file.hostname, "file_count": 0, "size_bytes": 0, "latest_collect": file.collect_time},
        )
        stats["file_count"] += 1
        stats["size_bytes"] += file.size_bytes
        stats["latest_collect"] = max(stats["latest_collect"], file.collect_time)

    host_count = len(host_stats)
    bucket_minutes = choose_bucket_minutes(host_count, point_budget)
    grouped = {}
    for file in accepted:
        elapsed_minutes = (file.collect_time - start_utc).total_seconds() / 60
        offset_minutes = int(elapsed_minutes // bucket_minutes) * bucket_minutes
        bucket = start_utc + dt.timedelta(minutes=offset_minutes)
        stats = grouped.setdefault(
            (bucket, file.hostname),
            {"bucket_utc": bucket, "hostname": file.hostname, "file_count": 0, "size_bytes": 0},
        )
        stats["file_count"] += 1
        stats["size_bytes"] += file.size_bytes

    if len(grouped) > point_budget:
        raise ValueError(f"Chart point budget exceeded ({point_budget:,} points); no chart was produced")

    host_summary = tuple(
        sorted(host_stats.values(), key=lambda item: (-item["file_count"], item["hostname"]))
    )
    points = tuple(
        grouped[key]
        for key in sorted(grouped)
    )
    return FileMetadataResult(
        listed_files=listed_files,
        files_in_window=len(accepted),
        total_size_bytes=sum(file.size_bytes for file in accepted),
        unparsed_files=unparsed_files,
        unparsed_size_bytes=unparsed_size_bytes,
        outside_window_files=outside_window_files,
        outside_window_size_bytes=outside_window_size_bytes,
        bucket_minutes=bucket_minutes,
        host_count=host_count,
        host_summary=host_summary,
        points=points,
    )
