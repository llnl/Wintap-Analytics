"""Streamlit rendering regressions, synthetic parquet only."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

import duckdb
from streamlit.testing.v1 import AppTest
from test_durable import publish
from queries import TESTS


class DashboardTests(unittest.TestCase):
    def test_automatic_parquet_discovery_overview_and_run_navigation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, status in enumerate(("failed", "passed")):
                value = dict(smokeManifestVersion=1, test="file-capture", runId=f"run-{index}",
                             host={"hostname": f"VM-{index}"}, status=status,
                             startedAtUtc="2026-10-22T12:00:00Z", completedAtUtc="2026-10-22T12:00:02Z",
                             smokeEvidenceRevision=2, smokeEvidencePhase="finished", selectors=[])
                publish(value, root, 2, "finished")
            app = AppTest.from_file(str(Path(__file__).with_name("main.py")), default_timeout=20).run()
            app.sidebar.text_input[0].set_value(str(root)).run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertEqual(len(app.selectbox(key="file-capture").options), 2)
            self.assertEqual([m.value for m in app.metric], ["1", "1", "0", str(2 * (len(TESTS) - 1))])
            self.assertTrue(any("Jump to" in m.value for m in app.markdown))
            target = app.selectbox(key="overview-target")
            target.select(1).run()
            next(b for b in app.button if b.label == "Select this run in its section").click().run()
            self.assertEqual(app.selectbox(key="file-capture").value, "run-1")
            app.sidebar.multiselect[0].set_value(["vm-0"]).run()
            self.assertEqual(len(app.selectbox(key="file-capture").options), 1)
            self.assertEqual(app.selectbox(key="file-capture").value, "run-0")

    def test_empty_app_has_all_sections_and_commands(self):
        app = AppTest.from_file(str(Path(__file__).with_name("main.py")), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.header), len(TESTS))
        self.assertEqual(len(app.code), len(TESTS))
        self.assertEqual(sum("No smoke runs" in i.value for i in app.info), len(TESTS))

    def test_null_selector_manifest_warns_without_aborting_valid_run_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = dict(smokeManifestVersion=1, test="process-capture", runId="valid",
                         host={"hostname": "VM-A"}, status="passed",
                         startedAtUtc="2026-10-22T12:00:00Z", completedAtUtc="2026-10-22T12:00:02Z",
                         selectors=[])
            (root / "valid.json").write_text(json.dumps(valid))
            (root / "bad.json").write_text(json.dumps(dict(valid, runId="invalid", selectors=[None])))
            app = AppTest.from_file(str(Path(__file__).with_name("main.py")), default_timeout=20).run()
            app.sidebar.text_input[1].set_value(str(root)).run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertTrue(any("Manifest selector 0 must be an object" in w.value for w in app.warning))
            self.assertEqual(len(app.selectbox(key="process-capture").options), 1)
            self.assertEqual(app.selectbox(key="process-capture").value, "valid")
            self.assertEqual(len(app.header), len(TESTS))

    def test_separate_runs_query_only_selected_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifests = root / "manifests"
            manifests.mkdir()
            con = duckdb.connect()
            con.execute(f"COPY (SELECT 'VM-A' Hostname, 42 PID, 1792670401 EventTime, '/vm/file.bin' File_Path, 'Open' ActivityType) TO '{root / 'events.parquet'}' (FORMAT PARQUET)")
            con.close()
            for index, pid in enumerate((42, 43)):
                manifest = dict(smokeManifestVersion=1, test="file-capture", runId=f"run-{index}",
                                host={"hostname": "VM-A"}, status="passed",
                                startedAtUtc="2026-10-22T12:00:00Z", completedAtUtc="2026-10-22T12:00:02Z",
                                selectors=[dict(domain="file", case="files", pids=[pid], paths=["/vm/file.bin"], expectedActivities=["Open"])])
                (manifests / f"{index}.json").write_text(json.dumps(manifest))
            app = AppTest.from_file(str(Path(__file__).with_name("main.py")), default_timeout=20).run()
            app.sidebar.text_input[0].set_value(str(root))
            app.sidebar.text_input[1].set_value(str(manifests))
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.selectbox(key="file-capture").options), 2)
            self.assertEqual(len(app.dataframe), 4)
            app.selectbox(key="file-capture").select("run-1").run()
            self.assertFalse(app.exception)
            self.assertTrue(any("No matching collected events" in i.value for i in app.info))


if __name__ == "__main__":
    unittest.main()
