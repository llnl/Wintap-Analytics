"""Bounded consumer of service.status_page v1; no ledger, SDK, lock or data I/O.

Deployment pins the complete canonical binding hash and ledger identity. This
checks an advisory export's identity/shape, NOT its authoritative correctness.
Unsupported/missing facts remain None. Only allowlisted fields reach the UI.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path

MAX_BYTES = 1024 * 1024
PAGE_SIZE = 100
STALE_SECONDS = 180  # Presentation only; never a timeout, expiry or death test.
UTC = dt.timezone.utc
FIELDS = {
    "version",
    "advisory",
    "observed_at",
    "ledger_id",
    "binding",
    "state",
    "authority_high_water",
    "jobs",
    "runs",
    "maintenance",
    "next_job",
    "next_run",
    "next_maintenance",
    "scope",
}


class InvalidSnapshot(ValueError):
    pass


@dataclass(frozen=True)
class Snapshot:
    availability: str
    retrieved_at: dt.datetime
    reason: str = ""
    observed_at: dt.datetime | None = None
    age_seconds: float | None = None
    state: dict | None = None
    jobs: tuple | None = None
    runs: tuple | None = None
    maintenance: tuple | None = None
    has_more: dict | None = None
    sequence: None = None
    grant_delivery: None = None
    entity_runs: None = None
    partition_catalog: None = None


def _require(condition):
    if not condition:
        raise InvalidSnapshot("Unsupported or malformed advisory snapshot")


def _identity(value):
    _require(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{32}", value) is not None)


def _timestamp(value, *, hour=False):
    _require(isinstance(value, str))
    try:
        result = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        raise InvalidSnapshot("Invalid observation timestamp") from None
    _require(result.strftime("%Y-%m-%dT%H:%M:%SZ") == value)
    _require(not hour or result.minute == result.second == 0)
    return result


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        _require(key not in value)
        value[key] = item
    return value


def _constant(_value):
    raise InvalidSnapshot("Nonfinite snapshot value")


def _finite_float(value):
    result = float(value)
    _require(math.isfinite(result))
    return result


def _read(path):
    # A wrongly configured DB, symlink, pipe or device must not be read/block UI.
    _require(path.is_absolute() and path.name == "status.json")
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    try:
        _require(stat.S_ISREG(os.fstat(fd).st_mode))
        with os.fdopen(fd, "rb", closefd=False) as stream:
            payload = stream.read(MAX_BYTES + 1)
        _require(len(payload) <= MAX_BYTES)
    finally:
        os.close(fd)
    return json.loads(
        payload, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_finite_float
    )


def _page(value, key, fields, identity, states, timestamp_key):
    rows = value[key]
    _require(isinstance(rows, list) and len(rows) <= PAGE_SIZE)
    previous = ""
    for row in rows:
        _require(isinstance(row, dict) and set(row) == fields)
        _identity(row[identity])
        _require(row[identity] > previous)
        previous = row[identity]
        _require(isinstance(row["state"], str) and row["state"] in states)
        _timestamp(row[timestamp_key])
    cursor_key = {"jobs": "next_job", "runs": "next_run", "maintenance": "next_maintenance"}[key]
    cursor = value[cursor_key]
    if cursor is not None:
        _identity(cursor)
        _require(bool(rows) and cursor == previous)
    return rows


def _validate(value, binding_sha256, ledger_id):
    _require(isinstance(value, dict) and set(value) == FIELDS)
    _require(type(value["version"]) is int and value["version"] == 1 and value["advisory"] is True)
    _identity(value["ledger_id"])
    _require(value["ledger_id"] == ledger_id)
    binding = value["binding"]
    _require(isinstance(binding, dict) and set(binding) == {"dataset_id", "roots", "entity"})
    # Pin the WHOLE binding, including entity policy and ALL active roots. Do not
    # implement a second active-root resolver or reduce it to the visible raw root.
    digest = hashlib.sha256(
        json.dumps(binding, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    _require(digest == binding_sha256)
    _require(isinstance(value["scope"], str) and len(value["scope"]) <= 4096)
    _require(
        value["authority_high_water"] is None or isinstance(value["authority_high_water"], dict)
    )
    observed = _timestamp(value["observed_at"])
    state = value["state"]
    _require(
        isinstance(state, dict)
        and set(state)
        == {"mode", "next_hour", "active_run_id", "block_reason", "readers", "waiting"}
    )
    _require(
        isinstance(state["mode"], str)
        and state["mode"] in {"OPEN", "DRAINING", "WRITING", "BLOCKED"}
    )
    _timestamp(state["next_hour"], hour=True)
    if state["active_run_id"] is not None:
        _identity(state["active_run_id"])
    for key in ("readers", "waiting"):
        _require(type(state[key]) is int and 0 <= state[key] <= 10_000)
    _require(isinstance(state["block_reason"], str) and len(state["block_reason"]) <= 4096)
    jobs = _page(
        value,
        "jobs",
        {"job_id", "state", "first_seen", "grant_id"},
        "job_id",
        {"WAITING", "GRANTED", "RELEASED", "CANCELLED"},
        "first_seen",
    )
    for row in jobs:
        if row["grant_id"] is not None:
            _identity(row["grant_id"])
    runs = _page(
        value,
        "runs",
        {"run_id", "cli_run_id", "hour_start", "hour_end", "state", "started_at"},
        "run_id",
        {"INTENT", "BLOCKED", "COMPLETED"},
        "started_at",
    )
    for row in runs:
        _identity(row["cli_run_id"])
        start, end = (_timestamp(row[key], hour=True) for key in ("hour_start", "hour_end"))
        _require(end - start == dt.timedelta(hours=1))
    maintenance = _page(
        value,
        "maintenance",
        {"maintenance_id", "run_id", "operation", "created_at", "state"},
        "maintenance_id",
        {"FINISHED", "ABANDONED", "PENDING"},
        "created_at",
    )
    for row in maintenance:
        _identity(row["run_id"])
        _require(
            isinstance(row["operation"], str)
            and row["operation"] in {"checkpoints-repair", "deletions-repair"}
        )
    return observed, state, jobs, runs, maintenance


def read_snapshot(env=None, *, now=None, high_water=None):
    """Read exactly the configured local export, returning sanitized unavailable.

    high_water is the session's latest accepted producer observation time for the
    same deployment pins. v1 has no monotonic sequence or sub-second clock; same-
    second changes cannot establish rollback or absence of intervening writes.
    """
    env = os.environ if env is None else env
    now = dt.datetime.now(UTC) if now is None else now
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Retrieval time must be timezone-aware")
    now = now.astimezone(UTC)
    try:
        path = Path(env.get("WINTAP_STATUS_EXPORT", ""))
        binding_sha256 = env.get("WINTAP_STATUS_BINDING_SHA256", "")
        ledger_id = env.get("WINTAP_STATUS_LEDGER_ID", "")
        _require(
            isinstance(binding_sha256, str)
            and re.fullmatch(r"[a-f0-9]{64}", binding_sha256) is not None
        )
        _identity(ledger_id)
        value = _read(path)
        observed, state, jobs, runs, maintenance = _validate(value, binding_sha256, ledger_id)
        _require(observed <= now and (high_water is None or observed >= high_water))
        age = (now - observed).total_seconds()
        # Do not retain/render binding roots, free-form diagnostic, scope or
        # authority payloads. These may contain private identifiers or secrets.
        safe_state = {
            key: state[key] for key in ("mode", "next_hour", "active_run_id", "readers", "waiting")
        }
        safe_state["block_reason_present"] = bool(state["block_reason"])
        safe_runs = tuple(
            {
                "run_id": row["run_id"],
                "cli_run_id": row["cli_run_id"],
                "hour_start": row["hour_start"],
                "hour_end": row["hour_end"],
                "intent_at": row["started_at"],
                "reported_state": row["state"],
                "launched_at": None,
                "finished_at": None,
                "completion": "Reported only; certificate unavailable",
            }
            for row in sorted(runs, key=lambda item: (item["started_at"], item["run_id"]))
        )
        return Snapshot(
            "stale" if age > STALE_SECONDS else "available",
            now,
            observed_at=observed,
            age_seconds=age,
            state=safe_state,
            jobs=tuple(dict(row) for row in jobs),
            runs=safe_runs,
            maintenance=tuple(dict(row) for row in maintenance),
            has_more={
                key: value[cursor] is not None
                for key, cursor in (
                    ("jobs", "next_job"),
                    ("runs", "next_run"),
                    ("maintenance", "next_maintenance"),
                )
            },
        )
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        return Snapshot(
            "unavailable",
            now,
            "Missing, unpinned, unreadable or unsupported advisory export; writer activity is unknown.",
        )
