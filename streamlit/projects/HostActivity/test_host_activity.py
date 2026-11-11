"""Offline tests for source configuration, pruning, schemas and raw-row counts."""
import datetime as dt
import importlib
import os
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

import duckdb
import queries
import s3_source

from queries import (
    aggregate_family,
    chart_points,
    choose_bucket_minutes,
    inspect_family,
)
from s3_source import (
    discover_files,
    load_settings,
    partition_globs,
    partition_hours,
    secret_sql,
)


UTC = dt.timezone.utc
START = dt.datetime(2026, 11, 10, 0, 0, tzinfo=UTC)
END = START + dt.timedelta(hours=12)


def filetime(value):
    return int(value.timestamp() * 10_000_000) + 116444736000000000


def copy_values(con, path, sql):
    escaped = str(path).replace("'", "''")
    con.execute(f"COPY ({sql}) TO '{escaped}' (FORMAT PARQUET)")


def sql_literal(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


class FakeConnection:
    def __init__(self, rows):
        self.rows = rows
        self.sql = None
        self.params = None

    def execute(self, sql, params):
        self.sql = sql
        self.params = params
        return self

    def fetchall(self):
        return self.rows


class SourceConfigurationTests(unittest.TestCase):
    def test_dbts_dataset_and_s3_environment_contract(self):
        settings = load_settings({
            "WINTAP_DATA_ROOT": "s3://example-bucket/base/",
            "WINTAP_DBT_RAW_SENSOR_DATASET": "s3://example-bucket/sensor-data/",
            "AWS_PROFILE": "researcher's-profile",
            "AWS_REGION": "us-west-2",
            "AWS_ENDPOINT_URL": "https://s3.example.test/",
            "DUCKDB_USE_SSL": "false",
        })
        self.assertEqual(settings.dataset_root, "s3://example-bucket/sensor-data")
        self.assertEqual(settings.raw_sensor_root, "s3://example-bucket/sensor-data/raw_sensor")
        self.assertEqual(settings.region, "us-west-2")
        self.assertEqual(settings.endpoint_url, "s3.example.test")
        self.assertFalse(settings.use_ssl)
        self.assertIn("PROFILE 'researcher''s-profile'", secret_sql(settings))
        self.assertIn("ENDPOINT 's3.example.test'", secret_sql(settings))
        self.assertIn("USE_SSL false", secret_sql(settings))
        self.assertNotIn("AWS_ACCESS_KEY", secret_sql(settings))

        bare_endpoint = load_settings({
            "WINTAP_DBT_DATASET": "s3://example-bucket/sensor-data",
            "AWS_ENDPOINT_URL": "garage-endpoint.internal:9000",
        })
        self.assertEqual(bare_endpoint.endpoint_url, "garage-endpoint.internal:9000")
        self.assertIn("ENDPOINT 'garage-endpoint.internal:9000'", secret_sql(bare_endpoint))

    def test_dataset_fallbacks_and_invalid_configuration(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        self.assertEqual(settings.raw_sensor_root, "s3://bucket/root/raw_sensor")
        with self.assertRaisesRegex(ValueError, "Set WINTAP_DBT_RAW_SENSOR_DATASET"):
            load_settings({})
        for root in (
            "s3://bucket/root/raw_sensor",
            "s3://bucket/root?token=secret",
            "s3://bucket/root/../other",
            "s3://user:password@bucket/root",
            "s3://bucket/root/*.parquet",
        ):
            with self.subTest(root=root), self.assertRaises(ValueError):
                load_settings({"WINTAP_DBT_DATASET": root})
        with self.assertRaisesRegex(ValueError, "plain s3://"):
            load_settings({"WINTAP_DBT_DATASET": "s3://[malformed"})
        with self.assertRaisesRegex(ValueError, "AWS_ENDPOINT_URL"):
            load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root", "AWS_ENDPOINT_URL": "https://host/path"})
        with self.assertRaisesRegex(ValueError, "AWS_ENDPOINT_URL"):
            load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root", "AWS_ENDPOINT_URL": "https://[malformed"})
        with self.assertRaisesRegex(ValueError, "AWS_ENDPOINT_URL"):
            load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root", "AWS_ENDPOINT_URL": "garage-endpoint.internal:9000/s3"})
        with self.assertRaisesRegex(ValueError, "DUCKDB_USE_SSL"):
            load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root", "DUCKDB_USE_SSL": "maybe"})

    def test_utc_partition_hours_and_partition_scoped_globs(self):
        start = dt.datetime(2026, 11, 10, 23, 30, tzinfo=UTC)
        end = dt.datetime(2026, 11, 11, 0, 30, tzinfo=UTC)
        self.assertEqual(partition_hours(start, end), [("20261110", "23"), ("20261111", "00")])
        exact_end = dt.datetime(2026, 11, 11, 0, 0, tzinfo=UTC)
        self.assertEqual(partition_hours(start, exact_end), [("20261110", "23")])
        plus_two = dt.timezone(dt.timedelta(hours=2))
        self.assertEqual(
            partition_hours(dt.datetime(2026, 11, 11, 1, 30, tzinfo=plus_two), dt.datetime(2026, 11, 11, 2, 30, tzinfo=plus_two)),
            [("20261110", "23"), ("20261111", "00")],
        )
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        with self.assertRaisesRegex(ValueError, "Unsupported raw_sensor event"):
            partition_globs(settings, start, end, event_types=("raw_bad'; SELECT 1",))
        globs = partition_globs(settings, start, end, event_types=("raw_process",))
        self.assertEqual(globs, [
            "s3://bucket/root/raw_sensor/raw_process/dayPK=20261110/hourPK=23/**/*.parquet",
            "s3://bucket/root/raw_sensor/raw_process/dayPK=20261111/hourPK=00/**/*.parquet",
        ])
        with self.assertRaisesRegex(ValueError, "limited to 12 hours"):
            partition_hours(START, END + dt.timedelta(microseconds=1))
        with self.assertRaisesRegex(ValueError, "timezone"):
            partition_hours(dt.datetime(2026, 11, 10), END)

    def test_discovery_deduplicates_and_keeps_nested_network_files(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        path = "s3://bucket/root/raw_sensor/raw_process_conn_incr/dayPK=20261110/hourPK=00/protoPK=tcp/a.parquet"
        # The full range is [00:00, 12:00), so hourPK=12 must not be read.
        connection = FakeConnection([
            (path,), (path,),
            ("s3://bucket/root/raw_sensor/raw_host/dayPK=20261110/hourPK=11/h.parquet",),
        ])
        found = discover_files(connection, settings, START, END, max_files=3)
        self.assertEqual(found["raw_process_conn_incr"], (path,))
        self.assertEqual(len(found["raw_host"]), 1)
        self.assertIn("SELECT file FROM glob(?) LIMIT ?", connection.sql)
        self.assertEqual(connection.params[1], 4)
        self.assertTrue(all("dayPK=" in pattern and "hourPK=" in pattern for pattern in connection.params[0]))
        self.assertTrue(all("hourPK=12" not in pattern for pattern in connection.params[0]))

    def test_discovery_fails_closed_at_file_limit_and_rejects_outside_root(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        files = [(f"s3://bucket/root/raw_sensor/raw_host/dayPK=20261110/hourPK=12/{i}.parquet",) for i in range(3)]
        with self.assertRaisesRegex(ValueError, "file limit exceeded"):
            discover_files(FakeConnection(files), settings, START, END, max_files=2)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            discover_files(FakeConnection([]), settings, START, END, max_files=0)
        with self.assertRaisesRegex(RuntimeError, "outside"):
            discover_files(FakeConnection([("s3://elsewhere/raw_sensor/raw_host/a.parquet",)]), settings, START, END)
        out_of_window = "s3://bucket/root/raw_sensor/raw_host/dayPK=20261110/hourPK=12/h.parquet"
        with self.assertRaisesRegex(RuntimeError, "outside the requested event/day/hour"):
            discover_files(FakeConnection([(out_of_window,)]), settings, START, END)
        unselected_event = "s3://bucket/root/raw_sensor/raw_process/dayPK=20261110/hourPK=00/p.parquet"
        with self.assertRaisesRegex(RuntimeError, "outside the requested event/day/hour"):
            discover_files(
                FakeConnection([(unselected_event,)]), settings, START, END,
                event_types=("raw_host",),
            )

    def test_discovery_can_limit_listing_to_one_selected_family(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        host_path = "s3://bucket/root/raw_sensor/raw_host/dayPK=20261110/hourPK=00/h.parquet"
        found = discover_files(
            FakeConnection([(host_path,)]), settings, START, END,
            event_types=("raw_host",),
        )
        self.assertEqual(found, {"raw_host": (host_path,)})


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "raw.parquet"
        self.con = duckdb.connect(":memory:")

    def tearDown(self):
        self.con.close()
        self.temp.cleanup()

    def test_filetime_exact_window_counts_raw_rows_and_blank_hostnames(self):
        values = [
            ("early", filetime(START - dt.timedelta(seconds=1))),
            ("alpha", filetime(START)),
            ("alpha", filetime(START + dt.timedelta(minutes=1))),
            ("beta", filetime(START + dt.timedelta(minutes=2))),
            (None, filetime(START + dt.timedelta(minutes=2))),
            ("  ", filetime(START + dt.timedelta(minutes=3))),
            ("gamma", filetime(END - dt.timedelta(microseconds=1))),
            ("late", filetime(END)),
        ]
        tuples = ",".join(f"({sql_literal(host)}, {stamp}::BIGINT)" for host, stamp in values)
        copy_values(self.con, self.path, f"SELECT * FROM (VALUES {tuples}) AS t(Hostname, EventTime)")
        projection = inspect_family(self.con, "raw_process", [str(self.path)])
        self.assertEqual(projection.time_mode, "filetime")
        result = aggregate_family(self.con, projection, [str(self.path)], START, END, max_rows=10)
        self.assertEqual(result.rows, 4)
        self.assertEqual(result.rows_without_hostname, 2)
        self.assertEqual(result.host_count, 3)
        counts = {(p["hostname"], p["raw_rows"]) for p in result.points}
        self.assertEqual(counts, {("alpha", 2), ("beta", 1), ("gamma", 1)})
        empty_start = END + dt.timedelta(days=1)
        empty = aggregate_family(
            self.con,
            projection,
            [str(self.path)],
            empty_start,
            empty_start + dt.timedelta(hours=12),
        )
        self.assertEqual(empty.rows, 0)
        self.assertEqual(empty.points, ())

    def test_native_timestamp_and_case_insensitive_host_projection(self):
        copy_values(self.con, self.path, """
            SELECT * FROM (VALUES
                ('host-a', TIMESTAMP '2026-11-10 03:15:00'),
                ('host-a', TIMESTAMP '2026-11-10 03:16:00'),
                ('host-b', TIMESTAMP '2026-11-10 03:17:00')
            ) AS t(hostname, time)
        """)
        projection = inspect_family(self.con, "pidstat", [str(self.path)])
        self.assertEqual(projection.host_column, "hostname")
        self.assertEqual(projection.time_mode, "timestamp")
        result = aggregate_family(self.con, projection, [str(self.path)], START, END)
        self.assertEqual(result.rows, 3)
        self.assertEqual(result.host_count, 2)

    def test_computer_column_is_a_hostname_alias(self):
        copy_values(self.con, self.path, """
            SELECT 'host-from-computer' AS Computer,
                   TIMESTAMP '2026-11-10 04:15:00' AS Time
        """)
        projection = inspect_family(self.con, "pidstat", [str(self.path)])
        self.assertEqual(projection.host_column, "Computer")
        result = aggregate_family(self.con, projection, [str(self.path)], START, END)
        self.assertEqual(result.points[0]["hostname"], "host-from-computer")

    def test_file_activity_prefers_first_seen_filetime_over_unix_event_time(self):
        rows = [
            ("activity-in-window", int((START + dt.timedelta(minutes=1)).timestamp()),
             filetime(START + dt.timedelta(minutes=1)), filetime(START + dt.timedelta(minutes=3))),
            ("activity-outside-window", int((START + dt.timedelta(minutes=2)).timestamp()),
             filetime(START - dt.timedelta(minutes=1)), filetime(START - dt.timedelta(seconds=1))),
            ("activity-lastseen-fallback", int((START + dt.timedelta(minutes=3)).timestamp()),
             None, filetime(START + dt.timedelta(minutes=4))),
        ]
        values = ",".join(
            f"({sql_literal(host)}, {event_time}, "
            f"{first_seen if first_seen is not None else 'NULL'}, {last_seen})"
            for host, event_time, first_seen, last_seen in rows
        )
        copy_values(
            self.con,
            self.path,
            f"SELECT * FROM (VALUES {values}) AS t(Hostname, EventTime, FirstSeen, LastSeen)",
        )
        projection = inspect_family(self.con, "raw_process_file", [str(self.path)])
        self.assertEqual(
            tuple((column, mode) for column, _type, _expr, mode in projection.time_projections),
            (("FirstSeen", "filetime"), ("LastSeen", "filetime"), ("EventTime", "unix_seconds")),
        )
        result = aggregate_family(self.con, projection, [str(self.path)], START, END)
        self.assertEqual(result.rows, 2)
        self.assertEqual(
            {point["hostname"] for point in result.points},
            {"activity-in-window", "activity-lastseen-fallback"},
        )

    def test_process_file_exact_aggregation_bypasses_raw_cap_but_bounds_groups(self):
        rows = [
            ("alpha", 1),
            ("alpha", 2),
            ("alpha", 6),
            ("beta", 1),
            (None, 1),
        ]
        values = ",".join(
            f"({sql_literal(host)}, {int((START + dt.timedelta(minutes=minute)).timestamp())}, "
            f"{filetime(START + dt.timedelta(minutes=minute))}, "
            f"{filetime(START + dt.timedelta(minutes=minute))})"
            for host, minute in rows
        )
        copy_values(
            self.con,
            self.path,
            f"SELECT * FROM (VALUES {values}) AS t(Hostname, EventTime, FirstSeen, LastSeen)",
        )
        projection = inspect_family(self.con, "raw_process_file", [str(self.path)])

        result = aggregate_family(self.con, projection, [str(self.path)], START, END, max_rows=1)
        self.assertEqual(result.rows, 4)
        self.assertEqual(result.rows_without_hostname, 1)
        self.assertEqual(result.host_count, 2)
        self.assertEqual(result.bucket_minutes, 5)
        counts = {(point["hostname"], point["bucket_utc"], point["raw_rows"]) for point in result.points}
        self.assertEqual(
            counts,
            {
                ("alpha", START.replace(tzinfo=None), 2),
                ("alpha", (START + dt.timedelta(minutes=5)).replace(tzinfo=None), 1),
                ("beta", START.replace(tzinfo=None), 1),
            },
        )

        with self.assertRaisesRegex(ValueError, "Intermediate host/time group budget exceeded"):
            aggregate_family(
                self.con,
                projection,
                [str(self.path)],
                START,
                END,
                max_intermediate_groups=2,
            )

    def test_process_file_coarsens_exact_groups_to_fit_chart_point_budget(self):
        values = ",".join(
            f"('host-{index}', {int((START + dt.timedelta(minutes=index + 1)).timestamp())}, "
            f"{filetime(START + dt.timedelta(minutes=index + 1))}, "
            f"{filetime(START + dt.timedelta(minutes=index + 1))})"
            for index in range(20)
        )
        copy_values(
            self.con,
            self.path,
            f"SELECT * FROM (VALUES {values}) AS t(Hostname, EventTime, FirstSeen, LastSeen)",
        )
        projection = inspect_family(self.con, "raw_process_file", [str(self.path)])
        result = aggregate_family(self.con, projection, [str(self.path)], START, END, point_budget=100)
        self.assertEqual(result.rows, 20)
        self.assertEqual(result.host_count, 20)
        self.assertGreater(result.bucket_minutes, 5)
        self.assertLessEqual(len(result.points), 100)
        self.assertEqual(sum(point["raw_rows"] for point in result.points), 20)

    def test_process_file_aggregation_timeout_interrupts_without_driver_detail(self):
        class InterruptibleConnection:
            def __init__(self):
                self.interrupted = threading.Event()

            def execute(self, _sql, _params):
                self.interrupted.wait(1)
                raise RuntimeError("mock query interrupted with sensitive detail")

            def interrupt(self):
                self.interrupted.set()

        con = InterruptibleConnection()
        with self.assertRaisesRegex(ValueError, "0.01-second time budget") as raised:
            queries._execute_with_timeout(con, "SELECT 1", [], 0.01)
        self.assertNotIn("sensitive detail", str(raised.exception))

        with self.assertRaisesRegex(ValueError, "0.01-second time budget"):
            queries._execute_with_timeout(
                self.con,
                "SELECT sum(i) FROM range(100000000000) t(i)",
                [],
                0.01,
            )

    def test_known_unix_eventtime_families_use_seconds_but_process_stays_filetime(self):
        unix_path = Path(self.temp.name) / "unix.parquet"
        seconds = int((START + dt.timedelta(minutes=1)).timestamp())
        copy_values(self.con, unix_path, f"SELECT 'host-unix' AS Hostname, {seconds}::BIGINT AS EventTime")
        host_projection = inspect_family(self.con, "raw_host", [str(unix_path)])
        self.assertEqual(host_projection.time_mode, "unix_seconds")
        host_result = aggregate_family(self.con, host_projection, [str(unix_path)], START, END)
        self.assertEqual(host_result.rows, 1)

        process_projection = inspect_family(self.con, "raw_process", [str(unix_path)])
        self.assertEqual(process_projection.time_mode, "filetime")
        process_result = aggregate_family(self.con, process_projection, [str(unix_path)], START, END)
        self.assertEqual(process_result.rows, 0)

        string_path = Path(self.temp.name) / "unix-string.parquet"
        copy_values(self.con, string_path, f"SELECT 'host-unix-string' AS Hostname, '{seconds}' AS EventTime")
        string_projection = inspect_family(self.con, "raw_host", [str(string_path)])
        self.assertEqual(string_projection.time_mode, "unix_seconds_or_iso_timestamp")
        string_result = aggregate_family(self.con, string_projection, [str(string_path)], START, END)
        self.assertEqual(string_result.rows, 1)

        connection_path = Path(self.temp.name) / "connection.parquet"
        copy_values(
            self.con,
            connection_path,
            f"SELECT 'host-connection' AS Hostname, {seconds}::BIGINT AS EventTime, "
            f"{filetime(START + dt.timedelta(minutes=1))}::BIGINT AS FirstSeenMs, "
            f"{filetime(START + dt.timedelta(minutes=2))}::BIGINT AS LastSeenMs",
        )
        connection_projection = inspect_family(self.con, "raw_process_conn_incr", [str(connection_path)])
        self.assertEqual(
            tuple((column, mode) for column, _type, _expr, mode in connection_projection.time_projections),
            (("FirstSeenMs", "filetime"), ("LastSeenMs", "filetime"), ("EventTime", "unix_seconds")),
        )
        connection_result = aggregate_family(self.con, connection_projection, [str(connection_path)], START, END)
        self.assertEqual(connection_result.rows, 1)

    def test_schema_drift_falls_back_across_host_and_time_columns(self):
        first = Path(self.temp.name) / "first.parquet"
        second = Path(self.temp.name) / "second.parquet"
        copy_values(self.con, first, f"SELECT 'host-filetime' AS Hostname, {filetime(START + dt.timedelta(minutes=4))}::BIGINT AS EventTime")
        copy_values(self.con, second, "SELECT 'host-timestamp' AS Computer, TIMESTAMP '2026-11-10 00:06:00' AS Time")
        projection = inspect_family(self.con, "raw_process", [str(first), str(second)])
        self.assertEqual(projection.host_columns, ("Hostname", "Computer"))
        self.assertEqual({projection.time_column, projection.time_projections[-1][0]}, {"EventTime", "Time"})
        result = aggregate_family(self.con, projection, [str(first), str(second)], START, END)
        self.assertEqual(result.rows, 2)
        self.assertEqual({point["hostname"] for point in result.points}, {"host-filetime", "host-timestamp"})

    def test_iso_timestamp_offsets_are_normalized_to_utc(self):
        copy_values(self.con, self.path, """
            SELECT * FROM (VALUES
                ('host-a', '2026-11-10T03:15:00-05:00'),
                ('host-b', '2026-11-10T08:16:00Z')
            ) AS t(Hostname, Time)
        """)
        projection = inspect_family(self.con, "pidstat", [str(self.path)])
        self.assertEqual(projection.time_mode, "iso_timestamp")
        result = aggregate_family(self.con, projection, [str(self.path)], START, END)
        self.assertEqual(result.rows, 2)
        self.assertTrue(all(point["bucket_utc"].hour == 8 for point in result.points))

    def test_unsupported_schemas_are_reportable(self):
        copy_values(self.con, self.path, "SELECT 7::BIGINT AS pid, 42::BIGINT AS EventTime")
        with self.assertRaisesRegex(ValueError, "hostname"):
            inspect_family(self.con, "raw_process", [str(self.path)])

        self.path.unlink()
        copy_values(self.con, self.path, "SELECT 'host-a' AS Hostname, 1700000000::BIGINT AS time")
        with self.assertRaisesRegex(ValueError, "Numeric time column"):
            inspect_family(self.con, "raw_process", [str(self.path)])

    def test_row_and_point_budgets_fail_closed_and_adapt_bucket_size(self):
        tuples = ",".join(
            f"('host-{index}', {filetime(START + dt.timedelta(minutes=index))}::BIGINT)"
            for index in range(8)
        )
        copy_values(self.con, self.path, f"SELECT * FROM (VALUES {tuples}) AS t(Hostname, EventTime)")
        projection = inspect_family(self.con, "raw_process", [str(self.path)])
        with self.assertRaisesRegex(ValueError, "Raw-row budget exceeded"):
            aggregate_family(self.con, projection, [str(self.path)], START, END, max_rows=4)
        with self.assertRaisesRegex(ValueError, "point budget is too small"):
            aggregate_family(self.con, projection, [str(self.path)], START, END, point_budget=1)
        result = aggregate_family(self.con, projection, [str(self.path)], START, END, point_budget=100)
        self.assertGreaterEqual(result.bucket_minutes, 5)
        self.assertLessEqual(len(result.points), 100)
        self.assertGreater(result.bucket_minutes, 5)

    def test_normalized_chart_is_host_peak_relative_and_filterable(self):
        tuples = ",".join(
            f"({sql_literal(host)}, {filetime(START + dt.timedelta(minutes=minute))}::BIGINT)"
            for host, minute in (("alpha", 0), ("alpha", 1), ("alpha", 6), ("beta", 0), ("beta", 1))
        )
        copy_values(self.con, self.path, f"SELECT * FROM (VALUES {tuples}) AS t(Hostname, EventTime)")
        projection = inspect_family(self.con, "raw_process", [str(self.path)])
        result = aggregate_family(self.con, projection, [str(self.path)], START, END)
        chart = chart_points(result, normalized=True)
        alpha = [point["value"] for point in chart if point["hostname"] == "alpha"]
        beta = [point["value"] for point in chart if point["hostname"] == "beta"]
        self.assertEqual(max(alpha), 1.0)
        self.assertEqual(max(beta), 1.0)
        only_alpha = chart_points(result, hosts=["alpha"])
        self.assertTrue(all(point["hostname"] == "alpha" for point in only_alpha))

    def test_bucket_width_respects_host_point_budget(self):
        width = choose_bucket_minutes(24, point_budget=500)
        self.assertGreater(width, 5)
        self.assertLessEqual(24 * (720 // width + 2), 500)


class DashboardControlTests(unittest.TestCase):
    def test_manual_refresh_reports_progress_and_scans_only_selected_family(self):
        class Context:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        class Status:
            def __init__(self):
                self.messages = []
                self.updates = []

            def write(self, message):
                self.messages.append(message)

            def update(self, **kwargs):
                self.updates.append(kwargs)

        class FakeStreamlit(types.ModuleType):
            def __init__(self):
                super().__init__("streamlit")
                self.session_state = {}
                self.sidebar = Context()
                self.status_widget = Status()

            def __getattr__(self, name):
                if name == "button":
                    return lambda *_args, **_kwargs: True
                if name == "selectbox":
                    return lambda _label, options, index=0, **_kwargs: options[index]
                if name == "status":
                    return lambda *_args, **_kwargs: self.status_widget
                if name == "empty":
                    return lambda: types.SimpleNamespace()
                return lambda *_args, **_kwargs: None

        class Connection:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        fake_streamlit = FakeStreamlit()
        fake_altair = types.ModuleType("altair")
        fake_pandas = types.ModuleType("pandas")
        connection = Connection()
        result = types.SimpleNamespace(
            rows=2,
            rows_without_hostname=0,
            bucket_minutes=5,
            host_count=1,
            points=(),
        )
        with patch.dict(sys.modules, {"streamlit": fake_streamlit, "altair": fake_altair, "pandas": fake_pandas}):
            main_module = importlib.import_module("main")
            try:
                with patch.dict(os.environ, {"WINTAP_DBT_DATASET": "s3://bucket/root"}, clear=True), \
                        patch.object(main_module, "open_connection", return_value=connection), \
                        patch.object(main_module, "discover_files", return_value={"raw_process": ("file.parquet",)}) as discover, \
                        patch.object(main_module, "inspect_family", return_value=types.SimpleNamespace(time_projections=())), \
                        patch.object(main_module, "aggregate_family", return_value=result):
                    main_module.main()
            finally:
                sys.modules.pop("main", None)

        discover.assert_called_once()
        self.assertEqual(discover.call_args.kwargs["event_types"], ("raw_process",))
        self.assertTrue(connection.closed)
        self.assertEqual(len(fake_streamlit.session_state["host_activity_snapshot"]["results"]), 1)
        self.assertEqual(len(fake_streamlit.status_widget.messages), 3)
        self.assertIn("Listing objects", fake_streamlit.status_widget.messages[0])
        self.assertIn("Inspecting schemas", fake_streamlit.status_widget.messages[1])
        self.assertIn("Filtering exact event timestamps", fake_streamlit.status_widget.messages[2])
        self.assertEqual(fake_streamlit.status_widget.updates[-1]["state"], "complete")
        self.assertIn("Refresh finished in", fake_streamlit.status_widget.updates[-1]["label"])

    def test_dashboard_does_not_query_until_manual_refresh(self):
        class Context:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        class FakeStreamlit(types.ModuleType):
            def __init__(self):
                super().__init__("streamlit")
                self.session_state = {}
                self.sidebar = Context()

            def __getattr__(self, name):
                if name == "button":
                    return lambda *_args, **_kwargs: False
                if name == "selectbox":
                    return lambda _label, options, index=0, **_kwargs: options[index]
                if name == "empty":
                    return lambda: types.SimpleNamespace()
                return lambda *_args, **_kwargs: None

        fake_streamlit = FakeStreamlit()
        fake_altair = types.ModuleType("altair")
        fake_pandas = types.ModuleType("pandas")
        with patch.dict(sys.modules, {"streamlit": fake_streamlit, "altair": fake_altair, "pandas": fake_pandas}):
            main_module = importlib.import_module("main")
            try:
                with patch.dict(os.environ, {"WINTAP_DBT_DATASET": "s3://bucket/root"}, clear=True), \
                        patch.object(main_module, "open_connection", side_effect=AssertionError("S3 query must wait")):
                    main_module.main()
            finally:
                sys.modules.pop("main", None)


class StreamlitRenderTests(unittest.TestCase):
    def test_real_streamlit_renders_without_refreshing_s3(self):
        from streamlit.testing.v1 import AppTest

        app_file = Path(__file__).with_name("main.py")
        configured_env = {
            "WINTAP_DBT_RAW_SENSOR_DATASET": "",
            "WINTAP_DBT_DATASET": "s3://example.invalid/test-dataset",
            "WINTAP_DATA_ROOT": "",
        }
        with patch.dict(os.environ, configured_env):
            app = AppTest.from_file(str(app_file)).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual([item.value for item in app.title], ["Recent Host Activity"])
            self.assertEqual([item.label for item in app.button], ["Refresh last 12 hours"])
            self.assertEqual([item.label for item in app.selectbox], ["Event family"])
            self.assertEqual(app.selectbox[0].value, "Process")
            self.assertTrue(any("query the selected **Process** family" in item.value for item in app.info))
            self.assertNotIn("host_activity_snapshot", app.session_state)

            app.selectbox[0].select("Process file").run()
            self.assertEqual(app.selectbox[0].value, "Process file")
            self.assertNotIn("host_activity_snapshot", app.session_state)
            self.assertTrue(any("query the selected **Process file** family" in item.value for item in app.info))

            # Hot-reloading from the earlier all-family snapshot should request a
            # refresh rather than crashing on its missing selected-family marker.
            app.session_state["host_activity_snapshot"] = {
                "settings_fingerprint": load_settings(configured_env).fingerprint,
            }
            app.selectbox[0].select("Process").run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("does not match the selected family" in item.value for item in app.info))
            app.selectbox[0].select("Process file").run()

            class Connection:
                closed = False

                def close(self):
                    self.closed = True

            connection = Connection()
            with patch.object(s3_source, "open_connection", return_value=connection), \
                    patch.object(s3_source, "discover_files", return_value={"raw_process_file": ("mock.parquet",)}) as discover, \
                    patch.object(
                        queries,
                        "inspect_family",
                        return_value=queries.FamilyProjection(
                            "raw_process_file",
                            ("Hostname",),
                            (
                                ("FirstSeen", "BIGINT", '"FirstSeen"', "filetime"),
                                ("LastSeen", "BIGINT", '"LastSeen"', "filetime"),
                                ("EventTime", "BIGINT", '"EventTime"', "unix_seconds"),
                            ),
                        ),
                    ), \
                    patch.object(
                        queries,
                        "aggregate_family",
                        return_value=queries.FamilyResult(
                            "raw_process_file",
                            7_923_378,
                            0,
                            5,
                            5,
                            ({
                                "bucket_utc": dt.datetime(2026, 11, 10, 0, 5),
                                "hostname": "synthetic-host",
                                "raw_rows": 123,
                            },),
                        ),
                    ):
                app.button[0].click().run()

            self.assertEqual(len(app.exception), 0)
            self.assertEqual(discover.call_args.kwargs["event_types"], ("raw_process_file",))
            self.assertTrue(connection.closed)
            snapshot = app.session_state["host_activity_snapshot"]
            self.assertEqual(snapshot["event_type"], "raw_process_file")
            self.assertEqual(snapshot["results"]["raw_process_file"]["rows"], 7_923_378)
            self.assertEqual(snapshot["results"]["raw_process_file"]["host_count"], 5)
            self.assertEqual(snapshot["timestamp_sources"][0]["column"], "FirstSeen")
            self.assertGreaterEqual(snapshot["elapsed_seconds"], 0)
            self.assertTrue(any("Refresh:" in item.value for item in app.caption))
            self.assertTrue(any("FirstSeen (filetime)" in item.value for item in app.caption))
            self.assertTrue(any("counted exactly in DuckDB (not sampled)" in item.value for item in app.caption))
            self.assertTrue(any("Host-attributed raw rows: 7,923,378" in item.value for item in app.caption))


if __name__ == "__main__":
    unittest.main()
