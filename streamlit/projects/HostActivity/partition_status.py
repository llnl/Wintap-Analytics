"""Metadata-only inventory of raw and compacted hourly partitions."""
from __future__ import annotations

import datetime as dt
import re
import threading
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from urllib.parse import urlsplit

from s3_source import S3Settings


UTC = dt.timezone.utc
MAX_PARTITION_STATUS_DAYS = 366
MAX_PARTITION_STATUS_EVENTS = 200
MAX_PARTITION_STATUS_LISTINGS = 20_000
MAX_PARTITION_STATUS_WORKERS = 8
HOURS_PER_DAY = 24


@dataclass(frozen=True)
class PartitionCell:
    """One event/day cell, based only on hourly prefix presence."""

    event_type: str
    day: dt.date
    compacted_hours: int
    raw_hours: int
    overlap_hours: int

    @property
    def observed_hours(self) -> int:
        return self.compacted_hours + self.raw_hours - self.overlap_hours

    @property
    def compaction_ratio(self) -> float | None:
        if self.observed_hours == 0:
            return None
        # Full-day denominator intentionally penalizes missing hourly coverage.
        return self.compacted_hours / HOURS_PER_DAY


def _date_range(start: dt.datetime, end: dt.datetime) -> tuple[dt.date, ...]:
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Partition overview bounds must include a timezone")
    first = start.astimezone(UTC).date()
    last_inclusive = (end.astimezone(UTC) - dt.timedelta(microseconds=1)).date()
    if last_inclusive < first:
        raise ValueError("Partition overview end must be after its start")
    days = (last_inclusive - first).days + 1
    if days > MAX_PARTITION_STATUS_DAYS:
        raise ValueError("Partition overview is limited to 366 UTC days")
    return tuple(first + dt.timedelta(days=offset) for offset in range(days))


def _location(uri: str) -> tuple[str, str]:
    parsed = urlsplit(uri)
    bucket = parsed.netloc
    prefix = parsed.path.strip("/")
    if not bucket or not prefix:
        raise ValueError("Configured S3 partition root is invalid")
    return bucket, prefix + "/"


def _list_pages(client, bucket: str, prefix: str, *, delimiter: str | None = None):
    continuation_token = None
    while True:
        request = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if delimiter is not None:
            request["Delimiter"] = delimiter
        if continuation_token is not None:
            request["ContinuationToken"] = continuation_token
        response = client.list_objects_v2(**request)
        yield response
        if not response.get("IsTruncated", False):
            return
        continuation_token = response.get("NextContinuationToken")
        if not continuation_token:
            raise RuntimeError("S3 partition listing returned an incomplete pagination response")


def _event_types(client, root: str) -> tuple[str, ...]:
    bucket, prefix = _location(root)
    result = set()
    for response in _list_pages(client, bucket, prefix, delimiter="/"):
        for entry in response.get("CommonPrefixes", ()):
            child = entry.get("Prefix") if isinstance(entry, dict) else None
            if not isinstance(child, str) or not child.startswith(prefix) or not child.endswith("/"):
                raise RuntimeError("S3 partition listing returned an unexpected event prefix")
            name = child[len(prefix):-1]
            if not name or "/" in name or name in {".", ".."}:
                raise RuntimeError("S3 partition listing returned an unexpected event prefix")
            result.add(name)
            if len(result) > MAX_PARTITION_STATUS_EVENTS:
                raise ValueError("Partition overview event-family limit exceeded")
    return tuple(sorted(result))


def _hours_for_day(client, root: str, event_type: str, day: dt.date) -> set[str]:
    bucket, prefix = _location(root)
    day_prefix = f"{prefix}{event_type}/dayPK={day:%Y%m%d}/"
    hours = set()
    for response in _list_pages(client, bucket, day_prefix, delimiter="/"):
        for entry in response.get("CommonPrefixes", ()):
            child = entry.get("Prefix") if isinstance(entry, dict) else None
            if not isinstance(child, str) or not child.startswith(day_prefix) or not child.endswith("/"):
                raise RuntimeError("S3 partition listing returned an unexpected hour prefix")
            match = re.fullmatch(r"hourPK=(\d{2})/", child[len(day_prefix):])
            if match is None or int(match.group(1)) > 23:
                raise RuntimeError("S3 partition listing returned an invalid hour prefix")
            hours.add(match.group(1))
    return hours


def discover_partition_status(
    client,
    settings: S3Settings,
    start: dt.datetime,
    end: dt.datetime,
) -> tuple[PartitionCell, ...]:
    """Discover raw/compacted hour presence without reading Parquet objects."""
    days = _date_range(start, end)
    raw_events = _event_types(client, settings.raw_sensor_root)
    compacted_events = _event_types(client, settings.compacted_root)
    event_types = tuple(sorted(set(raw_events) | set(compacted_events)))
    request_count = 2 + (len(event_types) * len(days) * 2)
    if request_count > MAX_PARTITION_STATUS_LISTINGS:
        raise ValueError("Partition overview listing budget exceeded; narrow the date range")
    if not event_types:
        return ()

    roots = (("raw", settings.raw_sensor_root), ("compacted", settings.compacted_root))
    presence = {(event, day, kind): set() for event in event_types for day in days for kind, _root in roots}
    lock = threading.Lock()

    def list_one(kind, root, event, day):
        return kind, event, day, _hours_for_day(client, root, event, day)

    requests = (
        (kind, root, event, day)
        for kind, root in roots
        for event in event_types
        for day in days
    )
    with ThreadPoolExecutor(max_workers=MAX_PARTITION_STATUS_WORKERS) as executor:
        pending = set()
        while len(pending) < MAX_PARTITION_STATUS_WORKERS:
            try:
                pending.add(executor.submit(list_one, *next(requests)))
            except StopIteration:
                break
        while pending:
            completed, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in completed:
                kind, event, day, hours = future.result()
                with lock:
                    presence[(event, day, kind)] = hours
                try:
                    pending.add(executor.submit(list_one, *next(requests)))
                except StopIteration:
                    pass

    cells = []
    for event in event_types:
        for day in days:
            raw_hours = presence[(event, day, "raw")]
            compacted_hours = presence[(event, day, "compacted")]
            cells.append(PartitionCell(
                event,
                day,
                len(compacted_hours),
                len(raw_hours),
                len(compacted_hours & raw_hours),
            ))
    return tuple(cells)
