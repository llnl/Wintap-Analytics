"""Synthetic-only controls for the opt-in local dataset smoke helper."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import duckdb


SOURCE = Path(__file__).with_name("smoke_dataset.py")
SPEC = importlib.util.spec_from_file_location("dataset_smoke", SOURCE)
smoke = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = smoke
SPEC.loader.exec_module(smoke)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DatasetSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dataset-smoke-")
        self.root = Path(self.temp.name) / "dataset"
        (self.root / "raw_sensor").mkdir(parents=True)
        (self.root / "duckdb").mkdir()
        self.database = self.root / "duckdb/wintap.duckdb"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_parquet(self, relative: str =
                      "process/dayPK=20261122/hourPK=12/process.parquet",
                      rows: int = 2) -> Path:
        path = self.root / "raw_sensor" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = duckdb.connect(":memory:")
        try:
            connection.execute(
                f"COPY (SELECT range AS event_id, 'private-value' AS payload "
                f"FROM range({rows})) TO ? (FORMAT PARQUET)", [str(path)])
        finally:
            connection.close()
        return path

    def write_database(self, rows: int = 2) -> None:
        connection = duckdb.connect(str(self.database))
        try:
            connection.execute("CREATE TABLE events AS SELECT range AS id FROM range(?)",
                               [rows])
        finally:
            connection.close()

    def test_tiny_inputs_are_read_without_values_or_changes(self) -> None:
        parquet = self.write_parquet()
        self.write_database()
        before = {path: (digest(path), path.stat().st_mtime_ns)
                  for path in (parquet, self.database)}
        result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual(result["raw"]["status"], "readable")
        self.assertEqual(result["raw"]["sampled_rows"], 2)
        self.assertEqual(result["database"]["status"], "readable")
        self.assertEqual(result["database"]["sampled_rows"], 2)
        self.assertNotIn("private-value", json.dumps(result))
        self.assertEqual(before, {path: (digest(path), path.stat().st_mtime_ns)
                                  for path in before})

    def test_missing_database_is_not_created_and_raw_is_independent(self) -> None:
        self.write_parquet()
        result = smoke.run_smoke(str(self.root), "duckdb/missing.duckdb")
        self.assertEqual(result["raw"]["status"], "readable")
        self.assertEqual(result["database"]["status"], "unavailable")
        self.assertEqual(result["database"]["reason"], "path_missing")
        self.assertFalse((self.root / "duckdb/missing.duckdb").exists())

    def test_missing_and_empty_raw_roots_are_distinct(self) -> None:
        self.write_database()
        empty = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual((empty["raw"]["status"], empty["raw"]["reason"]),
                         ("empty", "no_finalized_parquet"))
        (self.root / "raw_sensor").rmdir()
        missing = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual((missing["raw"]["status"], missing["raw"]["reason"]),
                         ("unavailable", "raw_root_missing"))
        self.assertEqual(missing["database"]["status"], "readable")

    def test_empty_base_table_is_not_positive_evidence(self) -> None:
        self.write_database(rows=0)
        result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual(result["database"]["status"], "empty")
        self.assertEqual(result["database"]["reason"], "sampled_table_empty")
        self.assertEqual(result["database"]["sampled_rows"], 0)

    def test_corrupt_parquet_is_unavailable(self) -> None:
        path = self.root / "raw_sensor/process/dayPK=20261122/hourPK=12/bad.parquet"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"not parquet")
        self.write_database()
        result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual(result["raw"]["status"], "unavailable")
        self.assertEqual(result["database"]["status"], "readable")

    def test_unpartitioned_parquet_is_not_claimed_as_one_hour(self) -> None:
        self.write_parquet("process/unpartitioned.parquet")
        self.write_database()
        result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual(result["raw"]["status"], "unavailable")
        self.assertEqual(result["raw"]["reason"], "raw_error")
        self.assertEqual(result["database"]["status"], "readable")

    def test_external_view_and_macro_are_catalogued_but_never_executed(self) -> None:
        external = self.write_parquet("external/source.parquet")
        connection = duckdb.connect(str(self.database))
        try:
            quoted = str(external).replace("'", "''")
            connection.execute(
                f"CREATE VIEW external_only AS SELECT * FROM read_parquet('{quoted}')")
            connection.execute(
                f"CREATE MACRO external_count() AS "
                f"(SELECT count(*) FROM read_parquet('{quoted}'))")
        finally:
            connection.close()
        external.unlink()
        result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual(result["database"]["status"], "empty")
        self.assertEqual(result["database"]["reason"], "no_base_table")
        self.assertEqual(result["database"]["catalog_objects"], 2)

    def test_wal_is_refused_without_repair(self) -> None:
        self.write_database()
        wal = Path(str(self.database) + ".wal")
        wal.write_bytes(b"synthetic wal marker")
        before = wal.read_bytes()
        result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual((result["database"]["status"],
                          result["database"]["reason"]),
                         ("unavailable", "wal_present"))
        self.assertEqual(wal.read_bytes(), before)

    def test_remote_and_escaping_paths_are_refused(self) -> None:
        self.write_database()
        outside = Path(self.temp.name) / "outside.duckdb"
        outside.write_bytes(b"outside")
        (self.root / "duckdb/link.duckdb").symlink_to(outside)
        escaped = smoke.run_smoke(str(self.root), "duckdb/link.duckdb")
        self.assertEqual(escaped["database"]["reason"],
                         "path_escapes_dataset_root")
        remote = smoke.run_smoke("s3://private-bucket/data", "db.duckdb")
        self.assertEqual(remote["raw"]["status"], "unavailable")
        self.assertFalse(Path("s3:").exists())

    def test_escaping_raw_symlink_is_refused(self) -> None:
        self.write_database()
        outside = Path(self.temp.name) / "outside.parquet"
        outside.write_bytes(b"not read")
        link = self.root / "raw_sensor/process.parquet"
        link.symlink_to(outside)
        result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual(result["raw"]["status"], "unavailable")
        self.assertEqual(outside.read_bytes(), b"not read")

    def test_file_catalog_and_discovery_budgets_fail_visibly(self) -> None:
        parquet = self.write_parquet()
        self.write_database()
        tiny_file = smoke.run_smoke(
            str(self.root), "duckdb/wintap.duckdb",
            smoke.Budgets(parquet_file_bytes=1))
        self.assertEqual(tiny_file["raw"]["status"], "budget_exceeded")

        tiny_catalog = smoke.run_smoke(
            str(self.root), "duckdb/wintap.duckdb",
            smoke.Budgets(catalog_objects=0))
        self.assertEqual(tiny_catalog["database"]["status"], "budget_exceeded")

        parquet.unlink()
        for number in range(3):
            (self.root / "raw_sensor" / f"entry-{number}").write_text("x")
        tiny_discovery = smoke.run_smoke(
            str(self.root), "duckdb/wintap.duckdb",
            smoke.Budgets(discovery_entries=2))
        self.assertEqual(tiny_discovery["raw"]["status"], "budget_exceeded")

    def test_row_limit_and_family_selection_are_bounded(self) -> None:
        for family in ("process", "file", "network", "registry"):
            self.write_parquet(
                f"{family}/dayPK=20261122/hourPK=12/{family}.parquet", rows=4)
        self.write_database(rows=4)
        result = smoke.run_smoke(
            str(self.root), "duckdb/wintap.duckdb",
            smoke.Budgets(sampled_rows=1))
        self.assertEqual(result["raw"]["files_selected"], 3)
        self.assertEqual(result["raw"]["sampled_rows"], 3)
        self.assertEqual(result["raw"]["families"], {
            "process": "present", "file": "present", "network": "present"})
        self.assertEqual(result["database"]["sampled_rows"], 1)

    def test_query_timeout_interrupts_blocking_connection(self) -> None:
        class BlockingConnection:
            def __init__(self) -> None:
                self.released = threading.Event()
                self.interrupted = False

            def execute(self, _sql, _parameters):
                self.released.wait(2)
                return self

            def fetchall(self):
                return []

            def interrupt(self):
                self.interrupted = True
                self.released.set()

        connection = BlockingConnection()
        with self.assertRaises(smoke.BudgetExceeded):
            smoke._run_query(connection, "SELECT 1", None, 0.01)
        self.assertTrue(connection.interrupted)

    def test_query_budget_failure_is_reported_not_accepted(self) -> None:
        self.write_parquet()
        self.write_database()
        with patch.object(smoke, "_run_query",
                          side_effect=smoke.BudgetExceeded("query_time")):
            result = smoke.run_smoke(str(self.root), "duckdb/wintap.duckdb")
        self.assertEqual(result["raw"]["status"], "budget_exceeded")
        self.assertEqual(result["database"]["status"], "budget_exceeded")

    def test_command_budget_is_shared_by_both_checks(self) -> None:
        self.write_parquet()
        self.write_database()
        result = smoke.run_smoke(
            str(self.root), "duckdb/wintap.duckdb",
            smoke.Budgets(command_seconds=0))
        self.assertEqual(result["raw"]["status"], "budget_exceeded")
        self.assertEqual(result["database"]["status"], "budget_exceeded")

    def test_cli_is_sanitized_and_requires_explicit_paths(self) -> None:
        self.write_parquet()
        self.write_database()
        output = io.StringIO()
        with redirect_stdout(output):
            code = smoke.main(["--dataset-root", str(self.root),
                               "--database", "duckdb/wintap.duckdb"])
        self.assertEqual(code, 0)
        rendered = output.getvalue()
        self.assertNotIn(str(self.root), rendered)
        self.assertNotIn("events", rendered)
        self.assertNotIn("private-value", rendered)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            smoke.main([])

    def test_database_open_errors_are_sanitized(self) -> None:
        self.database.write_bytes(b"not a database")
        output = io.StringIO()
        with redirect_stdout(output):
            code = smoke.main(["--dataset-root", str(self.root),
                               "--database", "duckdb/wintap.duckdb"])
        self.assertEqual(code, 2)
        rendered = output.getvalue()
        self.assertIn('"reason":"database_error"', rendered)
        self.assertNotIn(str(self.database), rendered)
        self.assertNotIn("not a database", rendered)

    def test_source_has_no_write_or_extension_sql(self) -> None:
        source = SOURCE.read_text()
        for forbidden in ("COPY TO", "CREATE TABLE", "CREATE VIEW",
                          "INSTALL ", "LOAD ", "CHECKPOINT", "ATTACH "):
            self.assertNotIn(forbidden, source.upper())
        self.assertNotIn('"temp_directory"', source)


if __name__ == "__main__":
    unittest.main()
