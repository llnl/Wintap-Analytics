"""Producer→parquet→read-only dashboard contract and triage regressions."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import duckdb
from queries import evaluate_run, load_manifests, mark_overlaps, overview, prepare_data, quote

# Read the live producer rather than copying its schema into analysis tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "wintap" / "devtools"))
from smoke_parquet import publish


class DurableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.con = duckdb.connect()
        self.run = dict(smokeManifestVersion=1, runId="run-a", test="file-capture", host={"hostname": "vm-a"},
                        status="passed", startedAtUtc="2026-10-22T23:59:00Z", completedAtUtc="2026-10-23T00:00:02Z",
                        selectors=[dict(domain="file", pids=[42], paths=["/qa/file"], expectedActivities=["Open"])])

    def tearDown(self):
        self.con.close()
        self.temp.cleanup()

    def snapshot(self, revision, value=None, published=None):
        value = dict(value or self.run, smokeEvidenceRevision=revision, smokeEvidencePhase="finished" if revision == 2 else "started")
        return publish(value, self.root, revision, value["smokeEvidencePhase"], published)

    def events(self, sql):
        self.con.execute(f"COPY ({sql}) TO {quote(self.root / 'events.parquet')} (FORMAT PARQUET)")
        return prepare_data(self.con, self.root)[2]

    def test_latest_reordered_cross_partition_multi_host_no_json_needed(self):
        self.snapshot(2, published=dt.datetime.fromisoformat("2026-10-23T00:01:00+00:00"))
        self.snapshot(0, dict(self.run, status="running", completedAtUtc=None), dt.datetime.fromisoformat("2026-10-22T23:59:00+00:00"))
        self.snapshot(2, dict(self.run, runId="run-b", host={"hostname": "vm-b"}))
        for root in (self.root, self.root / "raw_sensor"):
            runs, errors = load_manifests("", data_root=root, connection=self.con)
            self.assertFalse(errors)
            self.assertEqual(len(runs), 2)
            self.assertTrue(all(r["smokeEvidenceRevision"] == 2 for r in runs))
        self.assertEqual(prepare_data(self.con, self.root), (0, [], False))
        # A transferred identical JSON final copy deduplicates.
        final = next(r for r in runs if r["runId"] == "run-a")
        runs, errors = load_manifests("", [("manual.json", json.dumps(final))], self.root)
        self.assertEqual(len(runs), 2)
        self.assertFalse(errors)

    def test_conflicting_revision_and_corrupt_arriving_file(self):
        self.snapshot(2)
        self.snapshot(2, dict(self.run, status="failed"))
        runs, errors = load_manifests("", data_root=self.root)
        self.assertFalse(runs)
        self.assertTrue(any("Conflicting" in e for e in errors))
        evidence = self.root / "raw_sensor" / "raw_smoke_test"
        (evidence / "partial.parquet").write_text("partial")
        (evidence / "ignore.parquet.active").write_text("partial")
        _, errors = load_manifests("", data_root=self.root)
        self.assertTrue(any("refresh" in e for e in errors))
        self.assertFalse(any("active" in e for e in errors))

    def test_hash_or_typed_metadata_mismatch_is_rejected(self):
        path = self.snapshot(2)
        text = json.dumps(dict(self.run, smokeEvidenceRevision=2, smokeEvidencePhase="finished"))
        self.con.execute(f"CREATE TABLE tampered AS SELECT * FROM read_parquet({quote(path)})")
        self.con.execute("UPDATE tampered SET manifest_sha256='bad'")
        path.unlink()
        self.con.execute(f"COPY tampered TO {quote(path)} (FORMAT PARQUET)")
        runs, errors = load_manifests("", data_root=self.root)
        self.assertFalse(runs)
        self.assertTrue(errors)
        self.con.execute("UPDATE tampered SET manifest_sha256=?, manifest_json=?, hostname='wrong'", [hashlib.sha256(text.encode()).hexdigest(), text])
        path.unlink()
        self.con.execute(f"COPY tampered TO {quote(path)} (FORMAT PARQUET)")
        runs, errors = load_manifests("", data_root=self.root)
        self.assertFalse(runs)
        self.assertTrue(any("disagrees" in e for e in errors))

    def test_green_scoped_capture_yellow_absence_stimulus_skip_red_failure(self):
        self.assertEqual(evaluate_run(self.con, self.run, False)["state"], "yellow")
        available = self.events("SELECT 'vm-a' Hostname, 42 PID, TIMESTAMP '2026-10-23 00:00:01' EventTime, '/qa/file' File_Path, 'Open' ActivityType")
        self.assertEqual(evaluate_run(self.con, self.run, available)["state"], "green")
        for altered in (dict(self.run, stimulusOnly=True), dict(self.run, status="running"),
                        dict(self.run, selectors=[]), dict(self.run, results={"cases": [{"status": "skipped"}]})):
            self.assertEqual(evaluate_run(self.con, altered, available)["state"], "yellow")
        self.assertEqual(evaluate_run(self.con, dict(self.run, status="failed"), available)["state"], "red")
        trace = dict(self.run, test="clone-trace", results={"false_thread_births": 0})
        self.assertEqual(evaluate_run(self.con, trace, False)["state"], "green")
        self.assertEqual(evaluate_run(self.con, dict(trace, results={}), False)["state"], "yellow")

    def test_thread_identity_parent_violations_and_positive_companion(self):
        available = self.events("""SELECT * FROM (VALUES
            ('vm-a',42,'Start','identity-a',10), ('vm-a',42,'Start','identity-b',11),
            ('vm-a',43,'Start','thread',10)) t(Hostname,PID,ActivityType,PidHash,ParentPid)
            CROSS JOIN (SELECT TIMESTAMP '2026-10-23 00:00:01' EventTime, 'Process' MessageType)""")
        selector = dict(domain="process", pids=[42], threadIds=[43], links=[dict(case="worker", childPid=42, parentPid=10)])
        evaluation = evaluate_run(self.con, dict(self.run, selectors=[selector]), available)
        self.assertEqual(evaluation["state"], "red")
        self.assertEqual(len(evaluation["cases"][0]["violations"]), 3)
        negative = dict(self.run, selectors=[dict(domain="process", threadIds=[44], pids=[])])
        self.assertEqual(evaluate_run(self.con, negative, available)["state"], "yellow")
        # Positive companion captured, no false Start or identity split in it.
        positive = dict(domain="process", pids=[43])
        self.assertEqual(evaluate_run(self.con, dict(negative, selectors=[positive, negative["selectors"][0]]), available)["state"], "green")

    def test_overview_latest_history_gray_and_overlap(self):
        older = dict(self.run, runId="older", startedAtUtc="2026-10-22T23:58:00Z", status="failed")
        newer = dict(self.run)
        runs = [older, newer]
        evaluations = {(r["test"], r["runId"]): evaluate_run(self.con, r, False) for r in runs}
        rows = overview(runs, evaluations)
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(r["state"] == "gray" for r in rows), 7)
        self.assertEqual(next(r["run_id"] for r in rows if r["test_key"] == "file-capture"), "run-a")
        self.assertEqual(len(overview(runs, evaluations, history=True)), 9)
        mark_overlaps(runs, evaluations)
        self.assertTrue(any("Overlapping" in r for r in evaluations[("file-capture", "run-a")]["reasons"]))

    def test_limited_startup_receipts_stay_yellow(self):
        receipt = json.dumps({"captureRunId": "capture-a", "sensors": {"Clone": {"status": "partial"}}})
        available = self.events(f"SELECT 'vm-a' Hostname, {quote(receipt)} RuntimeCapabilitiesJson")
        run = dict(self.run, test="runtime-capabilities", selectors=[dict(domain="host", captureRunId="capture-a")])
        result = evaluate_run(self.con, run, available)
        self.assertEqual(result["state"], "yellow")
        self.assertTrue(any("Clone: partial" in reason for reason in result["reasons"]))

    def test_overlapping_passed_harnesses_preserve_observed_red_violations(self):
        available = self.events("""SELECT 'vm-a' Hostname, 43 PID, 'Start' ActivityType,
            'thread' PidHash, 'Process' MessageType,
            TIMESTAMP '2026-10-23 00:00:01' EventTime""")
        runs = [dict(self.run, test="process-capture", runId=run_id,
                     selectors=[dict(domain="process", pids=[], threadIds=[43])])
                for run_id in ("run-a", "run-b")]
        evaluations = {(r["test"], r["runId"]): evaluate_run(self.con, r, available) for r in runs}
        for evaluation in evaluations.values():
            self.assertEqual(evaluation["harness"], "passed")
            self.assertEqual(evaluation["state"], "red")
        mark_overlaps(runs, evaluations)
        for evaluation in evaluations.values():
            self.assertEqual(evaluation["state"], "red")
            self.assertEqual(evaluation["coverage"], "ambiguous")
            self.assertIn("Thread 43 recorded as a process Start", evaluation["reasons"])
            self.assertTrue(any("Overlapping" in reason for reason in evaluation["reasons"]))

    def test_overlapping_green_runs_become_yellow(self):
        available = self.events("SELECT 'vm-a' Hostname, 42 PID, TIMESTAMP '2026-10-23 00:00:01' EventTime, '/qa/file' File_Path, 'Open' ActivityType")
        runs = [dict(self.run, runId=run_id) for run_id in ("run-a", "run-b")]
        evaluations = {(r["test"], r["runId"]): evaluate_run(self.con, r, available) for r in runs}
        self.assertTrue(all(e["state"] == "green" for e in evaluations.values()))
        mark_overlaps(runs, evaluations)
        self.assertTrue(all(e["state"] == "yellow" for e in evaluations.values()))

    def test_invalid_selector_entries_are_excluded_without_losing_valid_runs(self):
        for selector in (None, 43, "process", [], {}, {"domain": None}, {"domain": "unknown"}):
            with self.subTest(selector=selector):
                invalid = dict(self.run, runId="invalid", selectors=[selector])
                runs, errors = load_manifests("", [("bad.json", json.dumps(invalid)),
                                                 ("valid.json", json.dumps(self.run))])
                self.assertEqual(runs, [self.run])
                self.assertEqual(len(errors), 1)
                self.assertIn("bad.json: Manifest selector 0", errors[0])
                evaluation = evaluate_run(self.con, runs[0], False)
                self.assertEqual(len(overview(runs, {(self.run["test"], self.run["runId"]): evaluation})), 8)
        # Empty selector lists are valid early lifecycle snapshots.
        runs, errors = load_manifests("", [("early.json", json.dumps(dict(self.run, selectors=[])))])
        self.assertEqual(len(runs), 1)
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
