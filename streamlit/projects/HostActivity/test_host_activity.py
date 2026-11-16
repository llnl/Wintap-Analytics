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
import file_metadata
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
    discover_object_metadata,
    load_settings,
    partition_globs,
    partition_count,
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
        self.assertEqual(settings.dataset_env_name, "WINTAP_DBT_RAW_SENSOR_DATASET")
        self.assertEqual(settings.region_env_name, "AWS_REGION")
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
        long_end = START + dt.timedelta(hours=49)
        self.assertEqual(len(partition_hours(START, long_end)), 49)
        self.assertEqual(partition_count(START, long_end), 49)
        self.assertEqual(partition_hours(START, long_end)[-1], ("20261112", "00"))
        with self.assertRaisesRegex(ValueError, "timezone"):
            partition_hours(dt.datetime(2026, 11, 10), END)

    def test_metadata_discovery_lists_a_multi_day_range(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        client = FakeS3MetadataClient({})
        found = discover_object_metadata(
            client,
            settings,
            START,
            START + dt.timedelta(hours=30),
            event_types=("raw_host",),
        )
        self.assertEqual(found, ())
        self.assertEqual(len(client.calls), 30)
        prefixes = {call["Prefix"] for call in client.calls}
        self.assertTrue(any("hourPK=00/" in prefix for prefix in prefixes))
        self.assertTrue(any("hourPK=05/" in prefix for prefix in prefixes))

    def test_long_raw_discovery_builds_partition_globs_in_bounded_chunks(self):
        class RecordingConnection:
            def __init__(self):
                self.pattern_batches = []

            def execute(self, _sql, params):
                self.pattern_batches.append(params[0])
                return self

            def fetchall(self):
                return []

        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        connection = RecordingConnection()
        found = discover_files(
            connection,
            settings,
            START,
            START + dt.timedelta(hours=30),
            event_types=("raw_host",),
        )
        self.assertEqual(found, {})
        self.assertEqual([len(batch) for batch in connection.pattern_batches], [24, 6])
        self.assertTrue(all(len(batch) <= s3_source.PARTITION_GLOB_CHUNK_HOURS for batch in connection.pattern_batches))

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
        files = [(f"s3://bucket/root/raw_sensor/raw_host/dayPK=20261110/hourPK=00/{i}.parquet",) for i in range(3)]
        with self.assertRaisesRegex(ValueError, "file limit exceeded"):
            discover_files(FakeConnection(files), settings, START, END, max_files=2)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            discover_files(FakeConnection([]), settings, START, END, max_files=0)
        with self.assertRaisesRegex(ValueError, "Unsupported raw_sensor event"):
            discover_files(FakeConnection([]), settings, START, END, event_types=("not_a_family",))
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

    def test_object_metadata_listing_is_partition_scoped_paginated_and_size_only(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        client = FakeS3MetadataClient({
            "root/raw_sensor/raw_host/dayPK=20261110/hourPK=00/host+raw_host_sensor+133000000000000000.parquet": 2048,
            "root/raw_sensor/raw_host/dayPK=20261110/hourPK=00/host2+raw_host_sensor+133000000050000000.parquet": 1024,
            "root/raw_sensor/raw_host/dayPK=20261110/hourPK=01/protoPK=tcp/host+raw_host_sensor+133000000100000000.parquet": 4096,
        }, page_size=1)
        objects = discover_object_metadata(
            client, settings, START, END, event_types=("raw_host",)
        )
        self.assertEqual(len(objects), 3)
        self.assertEqual({item.size_bytes for item in objects}, {1024, 2048, 4096})
        self.assertTrue(all(item.event_type == "raw_host" for item in objects))
        self.assertEqual(len(client.calls), 13)
        self.assertTrue(all(call["Bucket"] == "bucket" for call in client.calls))
        self.assertTrue(all("hourPK=12/" not in call["Prefix"] for call in client.calls))
        self.assertTrue(all(call["MaxKeys"] == 1000 for call in client.calls))
        self.assertEqual(
            {call["Prefix"] for call in client.calls},
            {
                f"root/raw_sensor/raw_host/dayPK=20261110/hourPK={hour:02d}/"
                for hour in range(12)
            },
        )
        self.assertTrue(any("ContinuationToken" in call for call in client.calls))

    def test_object_metadata_discovery_fails_closed_on_size_and_object_budgets(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        prefix = "root/raw_sensor/raw_host/dayPK=20261110/hourPK=00/"
        client = FakeS3MetadataClient({prefix + "a.parquet": 4, prefix + "b.parquet": 8})
        with self.assertRaisesRegex(ValueError, "file limit exceeded"):
            discover_object_metadata(client, settings, START, END, max_files=1, event_types=("raw_host",))
        client = FakeS3MetadataClient({prefix + "a.parquet": None})
        with self.assertRaisesRegex(RuntimeError, "invalid object size"):
            discover_object_metadata(client, settings, START, END, event_types=("raw_host",))


class FakeS3MetadataClient:
    def __init__(self, sizes, page_size=1000):
        self.sizes = sizes
        self.page_size = page_size
        self.calls = []

    def list_objects_v2(self, **kwargs):
        self.calls.append(kwargs)
        prefix = kwargs["Prefix"]
        contents = [
            {"Key": key, "Size": size}
            for key, size in sorted(self.sizes.items())
            if key.startswith(prefix)
        ]
        offset = int(kwargs.get("ContinuationToken", "0"))
        page = contents[offset:offset + self.page_size]
        next_offset = offset + self.page_size
        truncated = next_offset < len(contents)
        return {
            "Contents": page,
            "IsTruncated": truncated,
            **({"NextContinuationToken": str(next_offset)} if truncated else {}),
        }


class FileMetadataTests(unittest.TestCase):
    def test_missing_metadata_buckets_are_zero_filled_across_window(self):
        end = START + dt.timedelta(minutes=20)
        objects = tuple(
            s3_source.S3ObjectMetadata(
                f"raw_sensor/raw_host/dayPK=20261110/hourPK=00/alpha+raw_host_sensor+{filetime(START + dt.timedelta(minutes=minute))}.parquet",
                "raw_host",
                1024,
            )
            for minute in (1, 11)
        )

        result = file_metadata.aggregate_file_metadata(objects, START, end)

        self.assertEqual(result.bucket_minutes, 5)
        self.assertEqual(
            [(point["bucket_utc"], point["file_count"], point["size_bytes"]) for point in result.points],
            [
                (START, 1, 1024),
                (START + dt.timedelta(minutes=5), 0, 0),
                (START + dt.timedelta(minutes=10), 1, 1024),
                (START + dt.timedelta(minutes=15), 0, 0),
            ],
        )

    def test_filename_filetime_and_s3_size_aggregation(self):
        objects = (
            s3_source.S3ObjectMetadata(
                f"raw_sensor/raw_host/dayPK=20261110/hourPK=00/alpha+raw_host_sensor+{filetime(START + dt.timedelta(minutes=1))}.parquet",
                "raw_host",
                1024,
            ),
            s3_source.S3ObjectMetadata(
                f"raw_sensor/raw_host/dayPK=20261110/hourPK=00/alpha+raw_host_sensor+{filetime(START + dt.timedelta(minutes=6))}.parquet",
                "raw_host",
                2048,
            ),
            s3_source.S3ObjectMetadata(
                f"raw_sensor/raw_host/dayPK=20261110/hourPK=00/beta+raw_host_sensor+{filetime(END - dt.timedelta(seconds=1))}.parquet",
                "raw_host",
                1024,
            ),
            s3_source.S3ObjectMetadata(
                f"raw_sensor/raw_host/dayPK=20261109/hourPK=23/early+raw_host_sensor+{filetime(START - dt.timedelta(seconds=1))}.parquet",
                "raw_host",
                512,
            ),
            s3_source.S3ObjectMetadata(
                f"raw_sensor/raw_host/dayPK=20261110/hourPK=12/end+raw_host_sensor+{filetime(END)}.parquet",
                "raw_host",
                10,
            ),
            s3_source.S3ObjectMetadata(
                "raw_sensor/raw_host/dayPK=20261110/hourPK=00/not-a-structured-name.parquet",
                "raw_host",
                50,
            ),
        )
        result = file_metadata.aggregate_file_metadata(objects, START, END)
        self.assertEqual(result.listed_files, 6)
        self.assertEqual(result.files_in_window, 3)
        self.assertEqual(result.total_size_bytes, 4096)
        self.assertEqual(result.unparsed_files, 1)
        self.assertEqual(result.unparsed_size_bytes, 50)
        self.assertEqual(result.outside_window_files, 2)
        self.assertEqual(result.outside_window_size_bytes, 522)
        self.assertEqual(result.host_count, 2)
        observed = [point for point in result.points if point["file_count"]]
        self.assertEqual(
            {(point["hostname"], point["file_count"], point["size_bytes"]) for point in observed},
            {("alpha", 1, 1024), ("alpha", 1, 2048), ("beta", 1, 1024)},
        )
        self.assertEqual(len(result.points), 2 * (12 * 60 // result.bucket_minutes))
        self.assertTrue(any(point["hostname"] == "alpha" and point["file_count"] == 0 for point in result.points))
        self.assertEqual(sum(point["file_count"] for point in result.points), result.files_in_window)
        self.assertEqual(sum(point["size_bytes"] for point in result.points), result.total_size_bytes)
        self.assertEqual(result.host_summary[0]["hostname"], "alpha")
        self.assertEqual(result.host_summary[0]["file_count"], 2)

    def test_custom_multi_day_window_uses_adaptive_buckets_and_exact_file_times(self):
        start = START
        end = start + dt.timedelta(hours=48)
        timestamp = filetime(start + dt.timedelta(hours=36, minutes=2))
        obj = s3_source.S3ObjectMetadata(
            f"raw_sensor/raw_host/dayPK=20261111/hourPK=12/alpha+raw_host_sensor+{timestamp}.parquet",
            "raw_host",
            4096,
        )
        result = file_metadata.aggregate_file_metadata((obj,), start, end)
        self.assertEqual(result.files_in_window, 1)
        self.assertGreaterEqual(result.bucket_minutes, 5)
        self.assertEqual(result.points[0]["hostname"], "alpha")


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "raw.parquet"
        self.con = duckdb.connect(":memory:")

    def tearDown(self):
        self.con.close()
        self.temp.cleanup()

    def test_missing_raw_row_buckets_are_zero_filled_across_window(self):
        end = START + dt.timedelta(minutes=20)
        values = ",".join(
            f"('alpha', {filetime(START + dt.timedelta(minutes=minute))}::BIGINT)"
            for minute in (1, 11)
        )
        copy_values(self.con, self.path, f"SELECT * FROM (VALUES {values}) AS t(Hostname, EventTime)")
        projection = inspect_family(self.con, "raw_process", [str(self.path)])

        result = aggregate_family(self.con, projection, [str(self.path)], START, end)

        self.assertEqual(result.bucket_minutes, 5)
        self.assertEqual(
            [(point["bucket_utc"], point["raw_rows"]) for point in result.points],
            [
                (START.replace(tzinfo=None), 1),
                ((START + dt.timedelta(minutes=5)).replace(tzinfo=None), 0),
                ((START + dt.timedelta(minutes=10)).replace(tzinfo=None), 1),
                ((START + dt.timedelta(minutes=15)).replace(tzinfo=None), 0),
            ],
        )

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
        counts = {(p["hostname"], p["raw_rows"]) for p in result.points if p["raw_rows"]}
        self.assertEqual(counts, {("alpha", 2), ("beta", 1), ("gamma", 1)})
        self.assertTrue(any(point["raw_rows"] == 0 for point in result.points))
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
        counts = {
            (point["hostname"], point["bucket_utc"], point["raw_rows"])
            for point in result.points
            if point["raw_rows"]
        }
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
        self.assertTrue(all(point["bucket_utc"].hour == 8 for point in result.points if point["raw_rows"]))

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
        long_width = choose_bucket_minutes(24, point_budget=500, window_minutes=48 * 60)
        self.assertGreater(long_width, width)
        self.assertLessEqual(24 * ((48 * 60 + long_width - 1) // long_width), 500)

    def test_raw_aggregation_accepts_multi_day_window_and_keeps_row_budget(self):
        start = START
        end = start + dt.timedelta(hours=48)
        times = (start + dt.timedelta(hours=1), start + dt.timedelta(hours=36))
        values = ",".join(
            f"('long-window-host', {int(value.timestamp())}::BIGINT)" for value in times
        )
        copy_values(self.con, self.path, f"SELECT * FROM (VALUES {values}) AS t(Hostname, EventTime)")
        projection = inspect_family(self.con, "raw_host", [str(self.path)])
        result = aggregate_family(self.con, projection, [str(self.path)], start, end, max_rows=2)
        self.assertEqual(result.rows, 2)
        self.assertEqual(len(result.points), 48 * 60 // result.bucket_minutes)
        self.assertEqual(sum(point["raw_rows"] for point in result.points), 2)
        self.assertEqual(sum(point["raw_rows"] == 0 for point in result.points), len(result.points) - 2)
        with self.assertRaisesRegex(ValueError, "Raw-row budget exceeded"):
            aggregate_family(self.con, projection, [str(self.path)], start, end, max_rows=1)


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
                if name == "radio":
                    return lambda label, options, index=0, **_kwargs: options[1] if label == "Query mode" else options[index]
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

    def test_metadata_refresh_lists_keys_and_sizes_without_opening_duckdb(self):
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

        class Placeholder:
            def multiselect(self, _label, _options, default=()):
                return default

        class FakeStreamlit(types.ModuleType):
            def __init__(self):
                super().__init__("streamlit")
                self.session_state = {}
                self.sidebar = Context()
                self.status_widget = Status()

            def __getattr__(self, name):
                if name == "button":
                    return lambda *_args, **_kwargs: True
                if name == "radio":
                    return lambda _label, options, index=0, **_kwargs: options[index]
                if name == "selectbox":
                    return lambda _label, options, index=0, **_kwargs: options[index]
                if name == "status":
                    return lambda *_args, **_kwargs: self.status_widget
                if name == "empty":
                    return lambda: Placeholder()
                if name == "columns":
                    return lambda count: [types.SimpleNamespace(metric=lambda *_a, **_k: None) for _ in range(count)]
                return lambda *_args, **_kwargs: None

        class MetadataClient:
            closed = False

            def close(self):
                self.closed = True

        fake_streamlit = FakeStreamlit()
        fake_altair = types.ModuleType("altair")
        fake_pandas = types.ModuleType("pandas")
        client = MetadataClient()
        metadata_result = types.SimpleNamespace(
            listed_files=1,
            files_in_window=0,
            total_size_bytes=0,
            unparsed_files=1,
            unparsed_size_bytes=15,
            outside_window_files=0,
            outside_window_size_bytes=0,
            bucket_minutes=5,
            host_count=0,
            host_summary=(),
            points=(),
        )
        with patch.dict(sys.modules, {"streamlit": fake_streamlit, "altair": fake_altair, "pandas": fake_pandas}):
            main_module = importlib.import_module("main")
            try:
                with patch.dict(os.environ, {"WINTAP_DBT_DATASET": "s3://bucket/root"}, clear=True), \
                        patch.object(main_module, "open_metadata_client", return_value=client), \
                        patch.object(main_module, "discover_object_metadata", return_value=(object(),)) as discover, \
                        patch.object(main_module, "aggregate_file_metadata", return_value=metadata_result), \
                        patch.object(main_module, "open_connection", side_effect=AssertionError("Parquet connection must not open")), \
                        patch.object(main_module, "inspect_family", side_effect=AssertionError("Parquet schema must not be inspected")), \
                        patch.object(main_module, "aggregate_family", side_effect=AssertionError("Parquet rows must not be read")):
                    main_module.main()
            finally:
                sys.modules.pop("main", None)

        self.assertTrue(client.closed)
        self.assertEqual(discover.call_args.kwargs["event_types"], s3_source.RAW_EVENT_TYPES)
        snapshot = fake_streamlit.session_state["host_activity_snapshot"]
        self.assertEqual(snapshot["query_mode"], "File metadata")
        self.assertEqual(snapshot["event_type"], "__all__")
        self.assertEqual(snapshot["metadata"]["listed_files"], 1)
        self.assertTrue(any("Parquet contents are not read" in message for message in fake_streamlit.status_widget.messages))
        self.assertEqual(fake_streamlit.status_widget.updates[-1]["state"], "complete")

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
                if name == "radio":
                    return lambda _label, options, index=0, **_kwargs: options[index]
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


class ChartTooltipTests(unittest.TestCase):
    def setUp(self):
        app_file = Path(__file__).with_name("main.py")
        spec = importlib.util.spec_from_file_location("host_activity_tooltip_test_main", app_file)
        self.dashboard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.dashboard)

    def _capture_tooltip(self, render_chart):
        charts = []
        with patch.object(self.dashboard.st, "altair_chart", side_effect=lambda chart, **_kwargs: charts.append(chart)):
            render_chart()
        self.assertEqual(len(charts), 1)
        return charts[0].to_dict()["encoding"]["tooltip"]

    def test_metadata_hover_shows_only_selected_metric(self):
        point = {
            "bucket_utc": START,
            "hostname": "synthetic-host",
            "file_count": 3,
            "size_bytes": 2_097_152,
        }

        file_tooltip = self._capture_tooltip(
            lambda: self.dashboard._metadata_chart((point,), ("synthetic-host",), "File count")
        )
        size_tooltip = self._capture_tooltip(
            lambda: self.dashboard._metadata_chart((point,), ("synthetic-host",), "File size (MiB)")
        )

        self.assertEqual([item["field"] for item in file_tooltip], ["bucket_utc", "hostname", "metric_value"])
        self.assertEqual([item["title"] for item in file_tooltip], ["UTC", "Host", "Files"])
        self.assertEqual([item["field"] for item in size_tooltip], ["bucket_utc", "hostname", "metric_value"])
        self.assertEqual([item["title"] for item in size_tooltip], ["UTC", "Host", "Object size (MiB)"])

    def test_raw_row_hover_shows_concise_count_or_peak_ratio(self):
        result = queries.FamilyResult(
            "raw_process",
            rows=3,
            rows_without_hostname=0,
            bucket_minutes=5,
            host_count=1,
            points=({"bucket_utc": START.replace(tzinfo=None), "hostname": "synthetic-host", "raw_rows": 3},),
        )

        raw_tooltip = self._capture_tooltip(lambda: self.dashboard._chart(result, ("synthetic-host",), False, False))
        relative_tooltip = self._capture_tooltip(lambda: self.dashboard._chart(result, ("synthetic-host",), True, False))

        self.assertEqual([item["field"] for item in raw_tooltip], ["bucket_utc", "hostname", "raw_rows"])
        self.assertEqual([item["title"] for item in raw_tooltip], ["UTC", "Host", "Rows"])
        self.assertEqual([item["field"] for item in relative_tooltip], ["bucket_utc", "hostname", "value"])
        self.assertEqual([item["title"] for item in relative_tooltip], ["UTC", "Host", "Peak ratio"])


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
            self.assertEqual([item.label for item in app.selectbox], ["View", "Event family"])
            self.assertEqual([item.label for item in app.radio], ["Query mode", "Time range"])
            self.assertEqual(app.radio[0].value, "File metadata")
            self.assertEqual(app.selectbox[0].value, "Activity")
            self.assertEqual(app.selectbox[1].value, "All event families")
            self.assertTrue(any("all event families" in item.value for item in app.info))
            environment_info = next(item.value for item in app.info if "Credential values: hidden" in item.value)
            self.assertIn("WINTAP_DBT_DATASET", environment_info)
            self.assertIn("s3://example.invalid/test-dataset", environment_info)
            self.assertFalse(any("AWS_ACCESS_KEY_ID" in item.value for item in app.info))
            self.assertFalse(any("AWS_SECRET_ACCESS_KEY" in item.value for item in app.info))
            self.assertFalse(any("AWS_SESSION_TOKEN" in item.value for item in app.info))
            self.assertNotIn("host_activity_snapshot", app.session_state)

            app.selectbox[1].select("Process file").run()
            self.assertEqual(app.selectbox[1].value, "Process file")
            self.assertNotIn("host_activity_snapshot", app.session_state)
            self.assertTrue(any("Process file" in item.value for item in app.info))

            app.selectbox[1].select("All event families").run()

            class MetadataClient:
                closed = False

                def close(self):
                    self.closed = True

            metadata_client = MetadataClient()

            def metadata_objects(_client, _settings, start, _end, event_types):
                self.assertEqual(event_types, s3_source.RAW_EVENT_TYPES)
                timestamp = filetime(start + dt.timedelta(minutes=1))
                return (s3_source.S3ObjectMetadata(
                    f"root/raw_sensor/raw_host/dayPK=20261110/hourPK=00/synthetic-host+raw_host_sensor+{timestamp}.parquet",
                    "raw_host",
                    2_097_152,
                ),)

            with patch.object(s3_source, "open_metadata_client", return_value=metadata_client), \
                    patch.object(s3_source, "discover_object_metadata", side_effect=metadata_objects), \
                    patch.object(s3_source, "open_connection", side_effect=AssertionError("Metadata mode must not open DuckDB")):
                app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(metadata_client.closed)
            metadata_snapshot = app.session_state["host_activity_snapshot"]["metadata"]
            self.assertEqual(metadata_snapshot["files_in_window"], 1)
            self.assertEqual(metadata_snapshot["total_size_bytes"], 2_097_152)
            self.assertEqual(metadata_snapshot["host_summary"][0]["hostname"], "synthetic-host")
            self.assertTrue(any("S3 LastModified/upload time is ignored" in item.value for item in app.caption))
            self.assertEqual(
                [item.value for item in app.subheader if item.value not in {"Source", "Activity source environment"}],
                ["File count by collect time", "S3 object size by collect time (MiB)"],
            )

            app.radio[1].set_value("Custom dayPK/hourPK range").run()
            self.assertEqual([item.label for item in app.button], ["Refresh selected range"])
            app.date_input[0].set_value(dt.date(2026, 11, 10))
            app.selectbox[1].select("00")
            app.date_input[1].set_value(dt.date(2026, 11, 11))
            app.selectbox[2].select("00")
            app.run()
            self.assertTrue(any("over 24 hours" in item.value for item in app.warning))

            def custom_metadata_objects(_client, _settings, start, end, event_types):
                self.assertEqual(start, dt.datetime(2026, 11, 10, 0, 0, tzinfo=UTC))
                self.assertEqual(end, dt.datetime(2026, 11, 11, 1, 0, tzinfo=UTC))
                self.assertEqual(event_types, s3_source.RAW_EVENT_TYPES)
                timestamp = filetime(start + dt.timedelta(minutes=1))
                return (s3_source.S3ObjectMetadata(
                    f"root/raw_sensor/raw_host/dayPK=20261110/hourPK=00/synthetic-host+raw_host_sensor+{timestamp}.parquet",
                    "raw_host",
                    2_097_152,
                ),)

            with patch.object(s3_source, "open_metadata_client", return_value=metadata_client), \
                    patch.object(s3_source, "discover_object_metadata", side_effect=custom_metadata_objects):
                app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            custom_snapshot = app.session_state["host_activity_snapshot"]
            self.assertEqual(custom_snapshot["start"], "2026-11-10T00:00:00+00:00")
            self.assertEqual(custom_snapshot["end"], "2026-11-11T01:00:00+00:00")
            self.assertEqual(custom_snapshot["partition_count"], 25)

            # Hot-reloading from the earlier all-family snapshot should request a
            # refresh rather than crashing on its missing selected-family marker.
            app.session_state["host_activity_snapshot"] = {
                "settings_fingerprint": load_settings(configured_env).fingerprint,
                "query_mode": "File metadata",
                "event_type": "__all__",
            }
            app.selectbox[3].select("Process").run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("does not match the selected query/family" in item.value for item in app.info))
            app.radio[0].set_value("Raw Parquet rows").run()
            app.selectbox[3].select("Process file").run()

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
            self.assertEqual(snapshot["query_mode"], "Raw Parquet rows")
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
