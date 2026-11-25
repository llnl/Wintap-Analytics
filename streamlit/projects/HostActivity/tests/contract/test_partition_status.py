"""Offline tests for the metadata-only raw/compacted partition overview."""
import datetime as dt
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from partition_status import PartitionCell, discover_partition_status
from s3_source import load_settings


UTC = dt.timezone.utc


class FakePartitionClient:
    def __init__(self, event_prefixes, hours):
        self.event_prefixes = event_prefixes
        self.hours = hours
        self.calls = []

    def list_objects_v2(self, **request):
        self.calls.append(request)
        prefix = request["Prefix"]
        delimiter = request.get("Delimiter")
        if delimiter == "/" and prefix in self.event_prefixes:
            return {"CommonPrefixes": [{"Prefix": value} for value in self.event_prefixes[prefix]]}
        return {"CommonPrefixes": [{"Prefix": value} for value in self.hours.get(prefix, ())]}


class PartitionStatusTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            "partition_chart_test_main", Path(__file__).resolve().parents[2] / "main.py"
        )
        self.dashboard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.dashboard)

    def test_chart_uses_one_nominal_column_per_utc_day(self):
        days = tuple(dt.date(2026, 11, day) for day in range(1, 4))
        cells = tuple(PartitionCell("raw_process", day, 1, 1, 1) for day in days)
        with patch.object(self.dashboard.st, "altair_chart") as render:
            self.dashboard._render_partition_chart(cells, ("raw_process",), days)
        chart = render.call_args.args[0].to_dict(validate=True)
        self.assertEqual(chart["encoding"]["x"]["type"], "nominal")
        self.assertEqual(chart["encoding"]["x"]["sort"], [day.isoformat() for day in days])
        self.assertTrue(render.call_args.kwargs["use_container_width"])

    def test_full_compacted_day_reaches_one(self):
        cell = PartitionCell("raw_process", dt.date(2026, 11, 1), 24, 0, 0)
        self.assertEqual(cell.observed_hours, 24)
        self.assertEqual(cell.compaction_ratio, 1.0)

    def test_union_presence_uses_full_day_denominator_and_exposes_overlap(self):
        settings = load_settings({"WINTAP_DBT_DATASET": "s3://bucket/root"})
        event_prefixes = {
            "root/raw_sensor/": [
                "root/raw_sensor/raw_process/",
                "root/raw_sensor/raw_host/",
            ],
            "root/compacted/": [
                "root/compacted/raw_process/",
                "root/compacted/new_family/",
            ],
        }
        hours = {
            "root/raw_sensor/raw_process/dayPK=20261101/": [
                "root/raw_sensor/raw_process/dayPK=20261101/hourPK=00/",
                "root/raw_sensor/raw_process/dayPK=20261101/hourPK=01/",
            ],
            "root/compacted/raw_process/dayPK=20261101/": [
                "root/compacted/raw_process/dayPK=20261101/hourPK=00/",
            ],
            "root/compacted/new_family/dayPK=20261102/": [
                "root/compacted/new_family/dayPK=20261102/hourPK=23/",
            ],
        }
        client = FakePartitionClient(event_prefixes, hours)
        cells = discover_partition_status(
            client,
            settings,
            dt.datetime(2026, 11, 1, tzinfo=UTC),
            dt.datetime(2026, 11, 3, tzinfo=UTC),
        )

        process_day = next(cell for cell in cells if cell.event_type == "raw_process" and cell.day == dt.date(2026, 11, 1))
        self.assertEqual(process_day.compacted_hours, 1)
        self.assertEqual(process_day.raw_hours, 2)
        self.assertEqual(process_day.overlap_hours, 1)
        self.assertEqual(process_day.observed_hours, 2)
        self.assertAlmostEqual(process_day.compaction_ratio, 1 / 24)

        empty_day = next(cell for cell in cells if cell.event_type == "raw_process" and cell.day == dt.date(2026, 11, 2))
        self.assertIsNone(empty_day.compaction_ratio)

        compacted_only = next(cell for cell in cells if cell.event_type == "new_family" and cell.day == dt.date(2026, 11, 2))
        self.assertEqual(compacted_only.compacted_hours, 1)
        self.assertEqual(compacted_only.raw_hours, 0)
        self.assertAlmostEqual(compacted_only.compaction_ratio, 1 / 24)
        self.assertEqual(
            {request["Prefix"] for request in client.calls},
            {
                "root/raw_sensor/",
                "root/compacted/",
                "root/raw_sensor/raw_process/dayPK=20261101/",
                "root/raw_sensor/raw_process/dayPK=20261102/",
                "root/raw_sensor/raw_host/dayPK=20261101/",
                "root/raw_sensor/raw_host/dayPK=20261102/",
                "root/raw_sensor/new_family/dayPK=20261101/",
                "root/raw_sensor/new_family/dayPK=20261102/",
                "root/compacted/raw_process/dayPK=20261101/",
                "root/compacted/raw_process/dayPK=20261102/",
                "root/compacted/new_family/dayPK=20261101/",
                "root/compacted/new_family/dayPK=20261102/",
                "root/compacted/raw_host/dayPK=20261101/",
                "root/compacted/raw_host/dayPK=20261102/",
            },
        )


if __name__ == "__main__":
    unittest.main()
