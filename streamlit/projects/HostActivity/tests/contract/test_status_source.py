"""Offline advisory contract controls; no coordinator database or remote reads."""

import copy
import datetime as dt
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import status_source as source

NOW = dt.datetime(2026, 11, 15, 12, tzinfo=dt.timezone.utc)
BINDING = {
    "dataset_id": "synthetic-fixture",
    "roots": {
        "raw": "s3://example.invalid/fixture/raw_sensor",
        "compacted": "s3://example.invalid/fixture/compacted",
    },
    "entity": None,
}
LEDGER = "a" * 32


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def page():
    return {
        "version": 1,
        "advisory": True,
        "observed_at": "2026-11-15T12:00:00Z",
        "ledger_id": LEDGER,
        "binding": copy.deepcopy(BINDING),
        "state": {
            "mode": "OPEN",
            "next_hour": "2026-11-15T10:00:00Z",
            "active_run_id": None,
            "block_reason": "",
            "readers": 2,
            "waiting": 1,
        },
        "authority_high_water": None,
        "jobs": [
            {
                "job_id": "b" * 32,
                "state": "GRANTED",
                "first_seen": "2026-11-15T11:59:00Z",
                "grant_id": "c" * 32,
            }
        ],
        "runs": [
            {
                "run_id": "d" * 32,
                "cli_run_id": "e" * 32,
                "hour_start": "2026-11-15T09:00:00Z",
                "hour_end": "2026-11-15T10:00:00Z",
                "state": "COMPLETED",
                "started_at": "2026-11-15T11:00:00Z",
            }
        ],
        "maintenance": [],
        "next_job": None,
        "next_run": None,
        "next_maintenance": None,
        "scope": "bounded ledger summaries; not a partition inventory or completion certificate",
    }


class AdvisorySourceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "status.json"
        self.env = {
            "WINTAP_STATUS_EXPORT": str(self.path),
            "WINTAP_STATUS_BINDING_SHA256": fingerprint(BINDING),
            "WINTAP_STATUS_LEDGER_ID": LEDGER,
        }

    def read(self, value=None, **kwargs):
        self.path.write_text(json.dumps(page() if value is None else value))
        return source.read_snapshot(self.env, now=NOW, **kwargs)

    def test_real_shape_and_reported_completion_remain_advisory(self):
        result = self.read()
        self.assertEqual(result.availability, "available")
        self.assertEqual(result.age_seconds, 0)
        self.assertEqual(result.state["readers"], 2)
        self.assertEqual(result.runs[0]["reported_state"], "COMPLETED")
        self.assertIsNone(result.runs[0]["finished_at"])
        self.assertEqual(result.runs[0]["completion"], "Reported only; certificate unavailable")
        self.assertIsNone(result.sequence)
        self.assertIsNone(result.grant_delivery)
        self.assertIsNone(result.entity_runs)
        self.assertIsNone(result.partition_catalog)

    def test_missing_configuration_performs_no_open(self):
        with patch.object(
            source.os, "open", side_effect=AssertionError("No configuration, no I/O")
        ):
            self.assertEqual(source.read_snapshot({}, now=NOW).availability, "unavailable")

    def test_requires_explicit_binding_and_ledger_pins(self):
        self.read()
        for field in ("WINTAP_STATUS_BINDING_SHA256", "WINTAP_STATUS_LEDGER_ID"):
            env = {k: v for k, v in self.env.items() if k != field}
            with (
                self.subTest(field=field),
                patch.object(source.os, "open", side_effect=AssertionError("No unpinned read")),
            ):
                self.assertEqual(source.read_snapshot(env, now=NOW).availability, "unavailable")

    def test_wrong_binding_and_replaced_ledger_are_unavailable(self):
        for field, value in (
            ("binding", {**BINDING, "dataset_id": "other"}),
            ("ledger_id", "f" * 32),
        ):
            candidate = page()
            candidate[field] = value
            with self.subTest(field=field):
                self.assertEqual(self.read(candidate).availability, "unavailable")

    def test_unknown_version_non_advisory_and_extra_fields_refused(self):
        for field, value in (
            ("version", 2),
            ("version", True),
            ("advisory", False),
            ("secret", "DO-NOT-RENDER"),
        ):
            candidate = page()
            candidate[field] = value
            result = self.read(candidate)
            self.assertEqual(result.availability, "unavailable")
            self.assertNotIn("DO-NOT-RENDER", repr(result))

    def test_partial_duplicate_and_nonfinite_json_refused(self):
        for text in (
            '{"version":',
            '{"version":1,"version":1}',
            '{"x":NaN}',
            '{"x":1e999}',
            "[1]",
            "[" * 1100,
        ):
            self.path.write_text(text)
            result = source.read_snapshot(self.env, now=NOW)
            self.assertEqual(result.availability, "unavailable")

    def test_missing_file_is_unavailable_not_open_or_empty(self):
        result = source.read_snapshot(self.env, now=NOW)
        self.assertEqual(result.availability, "unavailable")
        self.assertIsNone(result.state)
        self.assertIsNone(result.runs)

    def test_byte_budget_and_nonregular_sources_fail_without_blocking(self):
        self.path.write_bytes(b" " * (source.MAX_BYTES + 1))
        self.assertEqual(source.read_snapshot(self.env, now=NOW).availability, "unavailable")
        self.path.unlink()
        os.mkfifo(self.path)
        self.assertEqual(source.read_snapshot(self.env, now=NOW).availability, "unavailable")

    def test_symlink_and_database_path_are_not_read(self):
        target = self.path.parent / "ledger.duckdb"
        target.write_text("PRIVATE-DATABASE")
        self.path.symlink_to(target)
        self.assertEqual(source.read_snapshot(self.env, now=NOW).availability, "unavailable")
        env = {**self.env, "WINTAP_STATUS_EXPORT": str(target)}
        with patch.object(source.os, "open", side_effect=AssertionError("Never open a DB")):
            self.assertEqual(source.read_snapshot(env, now=NOW).availability, "unavailable")
        self.assertEqual(target.read_text(), "PRIVATE-DATABASE")

    def test_stale_observation_does_not_become_fresh_on_reread(self):
        self.read()
        later = NOW + dt.timedelta(minutes=4)
        result = source.read_snapshot(self.env, now=later)
        self.assertEqual(result.availability, "stale")
        self.assertEqual(result.age_seconds, 240)
        self.assertEqual(result.observed_at, NOW)
        self.assertEqual(result.retrieved_at, later)

    def test_future_and_time_rollback_observations_fail_closed(self):
        candidate = page()
        candidate["observed_at"] = "2026-11-15T12:00:01Z"
        self.assertEqual(self.read(candidate).availability, "unavailable")
        candidate["observed_at"] = "2026-11-15T11:59:59Z"
        self.assertEqual(self.read(candidate, high_water=NOW).availability, "unavailable")

    def test_malformed_state_and_page_grains_refused(self):
        for field, value in (
            ("mode", "SAFE"),
            ("readers", -1),
            ("waiting", True),
            ("next_hour", "2026-11-15T10:01:00Z"),
        ):
            candidate = page()
            candidate["state"][field] = value
            self.assertEqual(self.read(candidate).availability, "unavailable")
        candidate = page()
        candidate["runs"][0]["hour_end"] = candidate["runs"][0]["hour_start"]
        self.assertEqual(self.read(candidate).availability, "unavailable")

    def test_paging_and_unknown_inventory_are_not_zero_counts(self):
        candidate = page()
        candidate["next_run"] = candidate["runs"][-1]["run_id"]
        result = self.read(candidate)
        self.assertTrue(result.has_more["runs"])
        self.assertIsNone(result.partition_catalog)
        self.assertIsNone(result.entity_runs)

    def test_page_order_duplicates_and_oversized_lists_refused(self):
        candidate = page()
        candidate["jobs"] *= 2
        self.assertEqual(self.read(candidate).availability, "unavailable")
        candidate["jobs"] *= 101
        self.assertEqual(self.read(candidate).availability, "unavailable")

    def test_block_reason_and_roots_never_reach_renderable_result(self):
        candidate = page()
        candidate["state"]["mode"] = "BLOCKED"
        candidate["state"]["block_reason"] = "DO-NOT-RENDER diagnostic with payload"
        result = self.read(candidate)
        self.assertEqual(result.availability, "available")
        self.assertTrue(result.state["block_reason_present"])
        self.assertNotIn("DO-NOT-RENDER", repr(result))
        self.assertNotIn("s3://", repr(result))

    def test_validation_mutations_remove_the_specific_refusals(self):
        # Prove binding/version checks are actually responsible for refusal,
        # rather than another malformed field masking the tested control.
        for field, value in (("binding", {**BINDING, "dataset_id": "other"}), ("version", 2)):
            candidate = page()
            candidate[field] = value
            self.assertEqual(self.read(candidate).availability, "unavailable")
            calls = 0
            original = source._require

            def bypass_one(condition, original=original):
                nonlocal calls
                if not condition:
                    calls += 1
                    return
                original(condition)

            with patch.object(source, "_require", side_effect=bypass_one):
                self.assertEqual(self.read(candidate).availability, "available")
            self.assertEqual(calls, 1)


class StatusUITests(unittest.TestCase):
    def setUp(self):
        from streamlit.testing.v1 import AppTest

        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "status.json"
        value = page()
        value["observed_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.path.write_text(json.dumps(value))
        self.env = {
            "WINTAP_STATUS_EXPORT": str(self.path),
            "WINTAP_STATUS_BINDING_SHA256": fingerprint(BINDING),
            "WINTAP_STATUS_LEDGER_ID": LEDGER,
        }
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "main.py"))

    def test_status_runs_catalog_never_open_data_or_reserve(self):
        # Omit dataset/AWS settings entirely: status must work without them.
        with (
            patch.dict(os.environ, self.env, clear=True),
            patch("s3_source.open_metadata_client", side_effect=AssertionError("No S3")),
            patch("s3_source.open_connection", side_effect=AssertionError("No DuckDB")),
        ):
            app = self.app.run()
            app.selectbox[0].select("Status").run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("unobserved" in item.value.lower() for item in app.info))
            self.assertNotIn("status_snapshot", app.session_state)
            app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.session_state["status_snapshot"].state["mode"], "OPEN")
            self.assertTrue(any("not permission" in item.value for item in app.warning))
            self.assertTrue(any("grant-delivery" in item.value for item in app.caption))
            original = self.path.read_bytes()
            with patch.object(
                source.os, "open", side_effect=AssertionError("Navigation is cached")
            ):
                app.selectbox[0].select("Runs").run()
                self.assertEqual(len(app.exception), 0)
                self.assertTrue(any("intent markers" in item.value for item in app.caption))
                self.assertTrue(any("Reported only" in str(item.value) for item in app.dataframe))
                app.selectbox[0].select("Partitions").run()
                self.assertEqual(len(app.exception), 0)
                self.assertTrue(
                    any("Unknown counts are not zero" in item.value for item in app.info)
                )
            self.assertEqual(self.path.read_bytes(), original)

    def test_failure_and_changed_pins_hide_old_results(self):
        with patch.dict(os.environ, self.env, clear=True):
            app = self.app.run()
            app.selectbox[0].select("Status").run()
            app.button[0].click().run()
            self.path.write_text("PRIVATE-MALFORMED-DIAGNOSTIC")
            app.button[0].click().run()
            self.assertEqual(app.session_state["status_snapshot"].availability, "unavailable")
            self.assertEqual(len(app.dataframe), 0)
            self.assertNotIn("PRIVATE-MALFORMED", str([item.value for item in app.error]))
            with patch.dict(os.environ, {"WINTAP_STATUS_LEDGER_ID": "f" * 32}):
                app.run()
                self.assertNotIn("status_snapshot", app.session_state)
                self.assertNotIn("status_high_water", app.session_state)
                self.assertEqual(len(app.exception), 0)

    def test_activity_warning_is_visible_even_without_status(self):
        with patch.dict(
            os.environ, {"WINTAP_DBT_DATASET": "s3://example.invalid/fixture"}, clear=True
        ):
            app = self.app.run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(
                any(
                    "Live diagnostic" in item.value and "mixed-generation" in item.value
                    for item in app.warning
                )
            )
            self.assertNotIn("status_snapshot", app.session_state)


if __name__ == "__main__":
    unittest.main()
