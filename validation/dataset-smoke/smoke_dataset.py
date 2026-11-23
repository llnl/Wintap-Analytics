#!/usr/bin/env python3
"""Bounded, opt-in readiness smoke for one local Wintap dataset snapshot."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import queue
import re
import sys
import threading
import time
from typing import Any

import duckdb


REMOTE_PATH = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
FAMILIES = ("process", "file", "network")


class BudgetExceeded(RuntimeError):
    """A fixed smoke-check budget was exceeded."""


class InputRefused(RuntimeError):
    """A path was not an acceptable local input."""


@dataclass(frozen=True)
class Budgets:
    command_seconds: float = 120.0
    query_seconds: float = 15.0
    memory_limit: str = "256MB"
    catalog_objects: int = 32
    parquet_files: int = 3
    parquet_file_bytes: int = 32 * 1024 * 1024
    sampled_rows: int = 128
    discovery_entries: int = 128


def _status(state: str, reason: str, **counts: Any) -> dict[str, Any]:
    return {"status": state, "reason": reason, **counts}


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _local_path(value: str) -> Path:
    if REMOTE_PATH.match(value):
        raise InputRefused("remote_path")
    return Path(value)


def _resolve_root(value: str) -> Path:
    path = _local_path(value)
    try:
        resolved = path.resolve(strict=True)
    except (FileNotFoundError, OSError) as error:
        raise InputRefused("dataset_root_unavailable") from error
    if not resolved.is_dir():
        raise InputRefused("dataset_root_not_directory")
    return resolved


def _resolve_under_root(root: Path, value: str) -> Path:
    supplied = _local_path(value)
    candidate = supplied if supplied.is_absolute() else root / supplied
    try:
        resolved = candidate.resolve(strict=False)
    except OSError as error:
        raise InputRefused("path_unavailable") from error
    if not _is_within(resolved, root):
        raise InputRefused("path_escapes_dataset_root")
    try:
        resolved = candidate.resolve(strict=True)
    except (FileNotFoundError, OSError) as error:
        raise InputRefused("path_missing") from error
    if not _is_within(resolved, root):
        raise InputRefused("path_escapes_dataset_root")
    return resolved


def _snapshot(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def _remaining_query_time(deadline: float, budgets: Budgets) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise BudgetExceeded("command_time")
    return min(budgets.query_seconds, remaining)


def _run_query(connection: Any, sql: str, parameters: list[Any] | None,
               timeout: float) -> list[tuple[Any, ...]]:
    """Execute and fetch in a worker so DuckDB can be interrupted at the budget."""
    result: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)

    def execute() -> None:
        try:
            rows = connection.execute(sql, parameters or []).fetchall()
            result.put(("rows", rows))
        except BaseException as error:  # Propagated without printing its contents.
            result.put(("error", error))

    worker = threading.Thread(target=execute, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        connection.interrupt()
        worker.join(1.0)
        raise BudgetExceeded("query_time")
    kind, value = result.get_nowait()
    if kind == "error":
        raise value
    return value


def _hour_key(path: Path) -> tuple[str, str] | None:
    day = hour = None
    for part in path.parts:
        lowered = part.lower()
        if lowered.startswith("daypk="):
            day = lowered
        elif lowered.startswith("hourpk="):
            hour = lowered
    return (day, hour) if day is not None and hour is not None else None


def _family(path: Path) -> str | None:
    for part in path.parts:
        tokens = set(re.findall(r"[a-z]+", part.lower()))
        for family in FAMILIES:
            if family in tokens or part.lower().startswith(family):
                return family
    return None


def _discover_parquet(raw_root: Path, dataset_root: Path,
                      budgets: Budgets) -> list[tuple[Path, Path]]:
    candidates: list[tuple[Path, Path]] = []
    pending = [raw_root]
    visited: set[Path] = set()
    entries_seen = 0

    while pending:
        directory = pending.pop()
        resolved_directory = directory.resolve(strict=True)
        if resolved_directory in visited:
            continue
        visited.add(resolved_directory)
        entries = []
        try:
            with os.scandir(directory) as iterator:
                for entry in iterator:
                    entries_seen += 1
                    if entries_seen > budgets.discovery_entries:
                        raise BudgetExceeded("discovery_entries")
                    entries.append(entry)
            entries.sort(key=lambda item: item.name)
        except OSError as error:
            raise InputRefused("raw_discovery_failed") from error
        for entry in entries:
            logical = Path(entry.path)
            try:
                resolved = logical.resolve(strict=True)
            except (FileNotFoundError, OSError) as error:
                raise InputRefused("raw_path_unavailable") from error
            if not _is_within(resolved, dataset_root):
                raise InputRefused("raw_path_escapes_dataset_root")
            if entry.is_dir(follow_symlinks=True):
                pending.append(logical)
            elif (entry.is_file(follow_symlinks=True)
                  and logical.name.lower().endswith(".parquet")
                  and ".active" not in logical.name.lower()):
                candidates.append((logical.relative_to(raw_root), resolved))

    partitioned = [item for item in candidates if _hour_key(item[0]) is not None]
    if candidates and not partitioned:
        raise InputRefused("raw_hour_partition_missing")
    selected_hour = max((_hour_key(item[0]) for item in partitioned), default=None)
    candidates = [item for item in partitioned if _hour_key(item[0]) == selected_hour]

    candidates.sort(key=lambda item: item[0].as_posix())
    selected: list[tuple[Path, Path]] = []
    for family in FAMILIES:
        match = next((item for item in candidates
                      if _family(item[0]) == family and item not in selected), None)
        if match is not None:
            selected.append(match)
    for item in candidates:
        if len(selected) >= budgets.parquet_files:
            break
        if item not in selected:
            selected.append(item)
    return selected[:budgets.parquet_files]


def smoke_raw(dataset_root: Path, budgets: Budgets = Budgets(),
              deadline: float | None = None) -> dict[str, Any]:
    base = dict(files_selected=0, schema_columns=0, sampled_rows=0,
                families={family: "missing" for family in FAMILIES})
    deadline = deadline if deadline is not None else time.monotonic() + budgets.command_seconds
    raw_candidate = dataset_root / "raw_sensor"
    if not raw_candidate.exists():
        return _status("unavailable", "raw_root_missing", **base)
    try:
        _remaining_query_time(deadline, budgets)
        raw_root = raw_candidate.resolve(strict=True)
        if not _is_within(raw_root, dataset_root):
            raise InputRefused("raw_root_escapes_dataset_root")
        if not raw_root.is_dir():
            raise InputRefused("raw_root_not_directory")
        selected = _discover_parquet(raw_root, dataset_root, budgets)
        if not selected:
            return _status("empty", "no_finalized_parquet", **base)
        for _, path in selected:
            if path.stat().st_size > budgets.parquet_file_bytes:
                raise BudgetExceeded("parquet_file_bytes")

        snapshots = {path: _snapshot(path) for _, path in selected}
        family_state = {family: "missing" for family in FAMILIES}
        for logical, _ in selected:
            family = _family(logical)
            if family is not None:
                family_state[family] = "present"

        connection = duckdb.connect(":memory:", config={
            "autoinstall_known_extensions": "false",
            "autoload_known_extensions": "false",
            "allow_unsigned_extensions": "false",
            "threads": "1",
            "memory_limit": budgets.memory_limit,
            "max_temp_directory_size": "0B",
        })
        sampled = 0
        schema_columns = 0
        try:
            for _, path in selected:
                schema_columns += _run_query(
                    connection,
                    "SELECT count(*) FROM parquet_schema(?) WHERE num_children IS NULL",
                    [str(path)], _remaining_query_time(deadline, budgets))[0][0]
                sampled += len(_run_query(
                    connection,
                    f"SELECT 1 FROM read_parquet(?) LIMIT {budgets.sampled_rows}",
                    [str(path)], _remaining_query_time(deadline, budgets)))
        finally:
            connection.close()
        if any(_snapshot(path) != before for path, before in snapshots.items()):
            raise InputRefused("raw_input_changed")
        state = "readable" if sampled else "empty"
        reason = "sample_readable" if sampled else "selected_files_empty"
        return _status(state, reason, files_selected=len(selected),
                       schema_columns=schema_columns, sampled_rows=sampled,
                       families=family_state)
    except BudgetExceeded:
        return _status("budget_exceeded", "raw_budget", **base)
    except (InputRefused, OSError, duckdb.Error):
        return _status("unavailable", "raw_error", **base)


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def smoke_database(dataset_root: Path, database_value: str,
                   budgets: Budgets = Budgets(),
                   deadline: float | None = None) -> dict[str, Any]:
    base = dict(catalog_objects=0, base_tables=0, columns_inspected=0,
                sampled_rows=0)
    deadline = deadline if deadline is not None else time.monotonic() + budgets.command_seconds
    try:
        _remaining_query_time(deadline, budgets)
        database = _resolve_under_root(dataset_root, database_value)
        if not database.is_file():
            raise InputRefused("database_not_file")
        wal_paths = {Path(str(database) + ".wal")}
        supplied = _local_path(database_value)
        supplied = supplied if supplied.is_absolute() else dataset_root / supplied
        wal_paths.add(Path(str(supplied) + ".wal"))
        if any(path.exists() for path in wal_paths):
            return _status("unavailable", "wal_present", **base)
        before = _snapshot(database)
    except BudgetExceeded:
        return _status("budget_exceeded", "database_budget", **base)
    except InputRefused as error:
        return _status("unavailable", str(error), **base)
    except OSError:
        return _status("unavailable", "database_stat_failed", **base)

    connection = None
    try:
        connection = duckdb.connect(str(database), read_only=True, config={
            "enable_external_access": "false",
            "autoinstall_known_extensions": "false",
            "autoload_known_extensions": "false",
            "allow_unsigned_extensions": "false",
            "threads": "1",
            "memory_limit": budgets.memory_limit,
            "max_temp_directory_size": "0B",
            "lock_configuration": "true",
        })
        catalog = _run_query(connection, f"""
            SELECT schema_name, table_name, 'table'
              FROM duckdb_tables()
             WHERE database_name = current_database() AND internal = false
            UNION ALL
            SELECT schema_name, view_name, 'view'
              FROM duckdb_views()
             WHERE database_name = current_database() AND internal = false
            UNION ALL
            SELECT DISTINCT schema_name, function_name, 'macro'
              FROM duckdb_functions()
             WHERE database_name = current_database()
               AND internal = false AND function_type = 'macro'
            ORDER BY 1, 2, 3
            LIMIT {budgets.catalog_objects + 1}
        """, None, _remaining_query_time(deadline, budgets))
        if len(catalog) > budgets.catalog_objects:
            raise BudgetExceeded("catalog_objects")
        tables = [row for row in catalog if row[2] == "table"]
        if not tables:
            if _snapshot(database) != before:
                raise InputRefused("database_changed")
            return _status("empty", "no_base_table", catalog_objects=len(catalog),
                           base_tables=0, columns_inspected=0, sampled_rows=0)

        schema, table, _ = tables[0]
        columns = _run_query(connection, """
            SELECT count(*) FROM duckdb_columns()
             WHERE database_name = current_database()
               AND schema_name = ? AND table_name = ?
        """, [schema, table], _remaining_query_time(deadline, budgets))[0][0]
        qualified = f"{_quote_identifier(schema)}.{_quote_identifier(table)}"
        rows = _run_query(connection,
                          f"SELECT 1 FROM {qualified} LIMIT {budgets.sampled_rows}",
                          None, _remaining_query_time(deadline, budgets))
        if _snapshot(database) != before:
            raise InputRefused("database_changed")
        state = "readable" if rows else "empty"
        reason = "sample_readable" if rows else "sampled_table_empty"
        return _status(state, reason, catalog_objects=len(catalog),
                       base_tables=len(tables), columns_inspected=columns,
                       sampled_rows=len(rows))
    except BudgetExceeded:
        return _status("budget_exceeded", "database_budget", **base)
    except (InputRefused, OSError, duckdb.Error):
        return _status("unavailable", "database_error", **base)
    finally:
        if connection is not None:
            connection.close()


def run_smoke(dataset_value: str, database_value: str,
              budgets: Budgets = Budgets()) -> dict[str, Any]:
    try:
        root = _resolve_root(dataset_value)
    except InputRefused as error:
        unavailable = _status("unavailable", str(error))
        return {"raw": dict(unavailable), "database": dict(unavailable)}
    deadline = time.monotonic() + budgets.command_seconds
    return {
        "raw": smoke_raw(root, budgets, deadline),
        "database": smoke_database(root, database_value, budgets, deadline),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only, bounded readiness smoke for an explicit local dataset")
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--database", required=True,
                        help="Database path relative to dataset root (or contained absolute path)")
    args = parser.parse_args(argv)
    result = run_smoke(args.dataset_root, args.database)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    failed = {"unavailable", "budget_exceeded"}
    return 2 if any(section["status"] in failed for section in result.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
