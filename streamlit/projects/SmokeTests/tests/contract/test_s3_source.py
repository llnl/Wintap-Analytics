"""Synthetic S3 listings/configs and transport-free DuckDB source parity."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import duckdb

from queries import evaluate_run, load_manifests, prepare_data, quote
from s3_source import dataset_parts, day_range, discover_files, load_config, open_source
from test_durable import publish


class Paginator:
    def __init__(self, keys):
        self.keys = keys
        self.calls = []

    def paginate(self, **kwargs):
        self.calls.append(kwargs)
        prefix = kwargs["Prefix"]
        if kwargs.get("Delimiter"):
            events = sorted({prefix + k[len(prefix):].split("/")[0] + "/"
                             for k in self.keys if k.startswith(prefix)})
            return [{"CommonPrefixes": [{"Prefix": e} for e in events]}]
        items = [{"Key": k} for k in self.keys if k.startswith(prefix)]
        # Two pages exercise pagination rather than only the first page.
        return [{"Contents": items[:1]}, {"Contents": items[1:]}]


class S3SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = dict(endpoint="https://garage.example.invalid", region="us-east-1",
                           datasets=["s3://test-bucket/run"], max_files=10000)

    def config_file(self, **changes):
        path = self.root / "fixture.local.json"
        path.write_text(json.dumps(dict(self.config, **changes)))
        return path

    def test_config_defaults_and_explicit_days(self):
        config = load_config(self.config_file(start_day="20261024", end_day="20261025"))
        self.assertEqual(day_range(config["start_day"], config["end_day"]), ["20261024", "20261025"])
        self.assertEqual(dataset_parts("s3://test-bucket/run/raw_sensor/"), ("test-bucket", "run/raw_sensor/"))
        self.assertEqual(dataset_parts("s3://test-bucket"), ("test-bucket", "raw_sensor/"))

    def test_reject_credentials_and_unknown_fields_without_echo(self):
        for field in ("access_key", "secret_key", "verify", "typo"):
            with self.subTest(field=field), self.assertRaises(ValueError) as caught:
                load_config(self.config_file(**{field: "synthetic-secret-sentinel"}))
            self.assertNotIn("synthetic-secret-sentinel", str(caught.exception))

    def test_reject_unsafe_endpoints_and_dataset_urls(self):
        for endpoint in ("https://user:synthetic-secret@garage.example.invalid", "https://example.invalid/base",
                         "https://example.invalid?token=synthetic-secret", "file:///fixture"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                load_config(self.config_file(endpoint=endpoint))
        for uri in ("https://example.invalid", "s3://user:secret@bucket", "s3://bucket/a*", "s3://bucket/../run"):
            with self.subTest(uri=uri), self.assertRaises(ValueError):
                dataset_parts(uri)

    def test_days_reject_inverted_invalid_and_unbounded_windows(self):
        for start, end in (("20261025", "20261024"), ("20260230", "20260301"),
                           ("20260101", "20261231"), ("2026102", "20261025")):
            with self.subTest(start=start), self.assertRaises(ValueError):
                day_range(start, end)

    def test_explicit_http_allowed_without_tls_bypass_option(self):
        self.assertEqual(load_config(self.config_file(endpoint="http://127.0.0.1:3900"))["endpoint"],
                         "http://127.0.0.1:3900")

    def listing(self, keys, **changes):
        paginator = Paginator(keys)
        client = MagicMock()
        client.get_paginator.return_value = paginator
        result = discover_files(client, dict(self.config, **changes), "20261024", "20261025")
        client.get_paginator.assert_called_once_with("list_objects_v2")
        return result, paginator

    def test_paginated_partition_pruning_evidence_and_active_exclusion(self):
        keys = ["run/raw_sensor/raw_smoke_test/dayPK=20261025/hourPK=01/evidence.parquet",
                "run/raw_sensor/raw_process/dayPK=20261024/hourPK=23/events.parquet",
                "run/raw_sensor/raw_process/dayPK=20261025/hourPK=01/second.parquet",
                "run/raw_sensor/raw_process/dayPK=20261025/hourPK=01/partial.parquet.active",
                "run/raw_sensor/raw_process/dayPK=20261023/hourPK=01/old.parquet",
                "elsewhere/raw_sensor/raw_process/dayPK=20261025/other.parquet"]
        (evidence, telemetry), paginator = self.listing(keys)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(len(telemetry), 2)
        self.assertFalse(any("20261023" in c["Prefix"] for c in paginator.calls))

    def test_empty_listing_is_explicit_absence(self):
        self.assertEqual(self.listing([])[0], ([], []))

    def test_file_cap_fails_closed_without_partial_results(self):
        keys = [f"run/raw_sensor/raw_process/dayPK=20261025/{i}.parquet" for i in range(2)]
        with self.assertRaisesRegex(ValueError, "file limit exceeded"):
            self.listing(keys, max_files=1)

    def test_duplicate_datasets_do_not_duplicate_observations(self):
        keys = ["run/raw_sensor/raw_process/dayPK=20261025/events.parquet"]
        result, _ = self.listing(keys, datasets=self.config["datasets"] * 2)
        self.assertEqual(len(result[1]), 1)

    def test_sdk_errors_are_suppressed(self):
        client = MagicMock()
        client.get_paginator.side_effect = RuntimeError("synthetic-secret-sentinel")
        with self.assertRaises(RuntimeError) as caught:
            discover_files(client, self.config, "20261024", "20261025")
        self.assertNotIn("synthetic-secret-sentinel", str(caught.exception))

    def test_source_connection_uses_temporary_secret_path_style_and_session_token(self):
        session = MagicMock()
        credentials = session.get_credentials.return_value.get_frozen_credentials.return_value
        credentials.access_key = "synthetic-key"
        credentials.secret_key = "synthetic-secret"
        credentials.token = "synthetic-token"
        con = MagicMock()
        with patch("boto3.Session", return_value=session), patch("duckdb.connect", return_value=con):
            actual, client = open_source(dict(self.config, extension_directory=str(self.root)))
        self.assertIs(actual, con)
        sql = con.execute.call_args.args[0]
        self.assertIn("CREATE TEMPORARY SECRET", sql)
        self.assertIn("URL_STYLE 'path'", sql)
        self.assertIn("SESSION_TOKEN 'synthetic-token'", sql)
        self.assertIn("USE_SSL true", sql)
        con.install_extension.assert_called_once_with("httpfs")
        self.assertEqual(session.client.call_args.kwargs["config"].s3["addressing_style"], "path")
        self.assertNotIn("verify", session.client.call_args.kwargs)

    def test_connection_failure_hides_secret_and_closes(self):
        session = MagicMock()
        creds = session.get_credentials.return_value.get_frozen_credentials.return_value
        creds.access_key, creds.secret_key, creds.token = "key", "synthetic-secret-sentinel", None
        con = MagicMock()
        con.execute.side_effect = RuntimeError("synthetic-secret-sentinel")
        with patch("boto3.Session", return_value=session), patch("duckdb.connect", return_value=con):
            with self.assertRaises(RuntimeError) as caught:
                open_source(self.config)
        self.assertNotIn("synthetic-secret-sentinel", str(caught.exception))
        con.close.assert_called_once()

    def test_explicit_file_sources_use_same_manifest_validation_and_queries(self):
        run = dict(smokeManifestVersion=1, test="file-capture", runId="fixture",
                   host={"hostname": "vm-fixture"}, status="passed",
                   startedAtUtc="2026-10-25T12:00:00Z", completedAtUtc="2026-10-25T12:00:02Z",
                   smokeEvidenceRevision=2, smokeEvidencePhase="finished",
                   selectors=[dict(domain="file", pids=[42], paths=["/fixture/file"], expectedActivities=["Open"])])
        evidence = publish(run, self.root, 2, "finished")
        telemetry = self.root / "events.parquet"
        with duckdb.connect(":memory:") as con:
            con.execute(f"COPY (SELECT 'vm-fixture' Hostname, 42 PID, TIMESTAMP '2026-10-25 12:00:01' EventTime, '/fixture/file' File_Path, 'Open' ActivityType) TO {quote(telemetry)} (FORMAT PARQUET)")
            runs, errors = load_manifests("", connection=con, evidence_files=[str(evidence)])
            self.assertFalse(errors)
            self.assertEqual(len(runs), 1)
            count, errors, available = prepare_data(con, "", telemetry_files=[str(telemetry)])
            self.assertEqual((count, errors, available), (1, [], True))
            self.assertEqual(evaluate_run(con, runs[0], available)["state"], "green")


if __name__ == "__main__":
    unittest.main()
