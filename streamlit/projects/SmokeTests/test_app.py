"""Real Streamlit multipage navigation; synthetic fixtures and no live S3."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import duckdb
from streamlit.testing.v1 import AppTest

from test_durable import publish


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'WINTAP_SMOKE_CONFIG': '', 'WINTAP_DATA_ROOT': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    def run_value(self, test='file-capture', run_id='fixture', stimulus=False, pid=42):
        return dict(smokeManifestVersion=1, test=test, runId=run_id,
            host={'hostname': 'vm-fixture'}, status='passed', stimulusOnly=stimulus,
            startedAtUtc='2026-10-25T12:00:00Z', completedAtUtc='2026-10-25T12:00:02Z',
            smokeEvidenceRevision=2, smokeEvidencePhase='finished',
            selectors=[dict(domain='file', case='files', pids=[pid], paths=['/fixture/file'], expectedActivities=['Open'])])

    def telemetry(self):
        with duckdb.connect() as con:
            con.execute(f"COPY (SELECT 'vm-fixture' Hostname, 42 PID, TIMESTAMP '2026-10-25 12:00:01' EventTime, '/fixture/file' File_Path, 'Open' ActivityType) TO '{self.root / 'events.parquet'}' (FORMAT PARQUET)")

    def app(self):
        app = AppTest.from_file(str(Path(__file__).with_name('main.py')), default_timeout=20).run()
        app.sidebar.text_input[0].set_value(str(self.root)).run()
        self.assertFalse(app.exception)
        return app

    def validate(self, app):
        next(b for b in app.button if b.label == 'Validate selected run').click().run()
        self.assertFalse(app.exception)
        return app

    def test_overview_never_prepares_or_evaluates_telemetry(self):
        publish(self.run_value(), self.root, 2, 'finished')
        with patch('page_views.prepare_data', side_effect=AssertionError('No overview scan')), \
             patch('page_views.evaluate_run', side_effect=AssertionError('No overview evaluation')):
            app = self.app()
            self.assertFalse(app.error)
            self.assertTrue(any('Manifest-only' in i.value for i in app.info))
            self.assertTrue((app.dataframe[0].value['capture'] == 'not evaluated').all())
            app.switch_page('views/devtime.py').run()
            self.assertFalse(app.exception)
            self.assertEqual(app.selectbox(key='run-False').value, 'fixture')

    def test_empty_multipage_app(self):
        app = self.app()
        for page, header in [('views/canary.py', 'Canary Tests'), ('views/devtime.py', 'Dev-time Tests')]:
            app.switch_page(page).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.header[0].value, header)
            self.assertTrue(any('No runs supplied' in i.value for i in app.info))

    def test_canary_devtime_partition_and_legacy_stimulus_classification(self):
        for test, stimulus, run_id in [('canary-file', True, 'new-canary'),
                                      ('telemetry-workload', True, 'legacy-canary'),
                                      ('file-capture', False, 'dev')]:
            publish(self.run_value(test, run_id, stimulus), self.root, 2, 'finished')
        app = self.app().switch_page('views/canary.py').run()
        self.assertEqual(len(app.selectbox(key='family-True').options), 2)
        app.switch_page('views/devtime.py').run()
        self.assertEqual(app.selectbox(key='run-False').value, 'dev')
        self.assertEqual(len(app.selectbox(key='family-False').options), 1)

    def test_selected_run_only_and_no_auto_revalidation(self):
        self.telemetry()
        for index, pid in enumerate([42, 43]):
            publish(self.run_value(run_id=f'run-{index}', pid=pid), self.root, 2, 'finished')
        from page_views import evaluate_run
        with patch('page_views.evaluate_run', wraps=evaluate_run) as evaluator:
            app = self.app().switch_page('views/devtime.py').run()
            self.assertEqual(evaluator.call_count, 0)
            app.selectbox(key='run-False').select('run-0').run()
            self.validate(app)
            self.assertEqual(evaluator.call_count, 1)
            self.assertEqual(evaluator.call_args.args[1]['runId'], 'run-0')
            self.assertTrue(any('Green' in m.value for m in app.markdown))
            app.selectbox(key='run-False').select('run-1').run()
            self.assertEqual(evaluator.call_count, 1)
            self.validate(app)
            self.assertEqual(evaluator.call_count, 2)
            self.assertTrue(any('no matching events' in c.value for c in app.caption))

    def test_null_selector_warns_without_losing_valid_run(self):
        valid = self.run_value()
        (self.root / 'valid.json').write_text(json.dumps(valid))
        (self.root / 'invalid.json').write_text(json.dumps(dict(valid, runId='bad', selectors=[None])))
        app = self.app()
        app.sidebar.text_input[1].set_value(str(self.root)).run()
        self.assertTrue(any('must be an object' in w.value for w in app.warning))
        app.switch_page('views/devtime.py').run()
        self.assertEqual(len(app.selectbox(key='run-False').options), 1)

    def test_s3_canary_stays_stimulus_only_after_validation(self):
        config = self.root / 'fixture.local.json'
        config.write_text(json.dumps(dict(endpoint='https://garage.example.invalid', datasets=['s3://fixture-bucket/run'])))
        evidence = publish(self.run_value('canary-file', stimulus=True), self.root, 2, 'finished')
        self.telemetry()
        with patch.dict(os.environ, {'WINTAP_SMOKE_CONFIG': str(config)}), \
             patch('s3_source.open_source', side_effect=lambda _: (duckdb.connect(), object())), \
             patch('s3_source.discover_files', return_value=([str(evidence)], [str(self.root / 'events.parquet')])):
            app = AppTest.from_file(str(Path(__file__).with_name('main.py')), default_timeout=20).run()
            self.assertFalse(app.exception)
            app.switch_page('views/canary.py').run()
            self.validate(app)
            self.assertTrue(any('stimulus only' in m.value for m in app.markdown))
            self.assertTrue(any('Yellow' in m.value for m in app.markdown))

    def test_s3_listing_failure_has_no_partial_results(self):
        config = self.root / 'fixture.local.json'
        config.write_text(json.dumps(dict(endpoint='https://garage.example.invalid', datasets=['s3://fixture-bucket/run'])))
        with patch.dict(os.environ, {'WINTAP_SMOKE_CONFIG': str(config)}), \
             patch('s3_source.open_source', side_effect=lambda _: (duckdb.connect(), object())), \
             patch('s3_source.discover_files', side_effect=ValueError('S3 file limit exceeded')):
            app = AppTest.from_file(str(Path(__file__).with_name('main.py')), default_timeout=20).run()
            self.assertFalse(app.exception)
            self.assertTrue(app.error)
            self.assertFalse(app.metric)

    def test_working_set_failure_does_not_evaluate_truncated_data(self):
        self.telemetry()
        publish(self.run_value(), self.root, 2, 'finished')
        with patch('page_views.materialize_run', side_effect=ValueError('budget exceeded')), \
             patch('page_views.evaluate_run') as evaluator:
            app = self.app().switch_page('views/devtime.py').run()
            self.validate(app)
            self.assertTrue(app.error)
            evaluator.assert_not_called()
            self.assertFalse(any('Green' in m.value for m in app.markdown))

    def test_skipped_canary_without_selectors_never_scans_telemetry(self):
        run = self.run_value('canary-clone', stimulus=True)
        run['selectors'] = []
        run['results'] = {'cases': [dict(case='native-clone', status='skipped', reason='No helper')]}
        publish(run, self.root, 2, 'finished')
        with patch('page_views.prepare_data', side_effect=AssertionError('No selectors to scan')):
            app = self.app().switch_page('views/canary.py').run()
            self.validate(app)
            self.assertFalse(app.error)
            self.assertTrue(any('Skipped stimulus' in w.value for w in app.warning))
            self.assertTrue(any('Yellow' in m.value for m in app.markdown))

    def test_all_canary_validation_persists_reuses_and_warns_stale(self):
        self.telemetry()
        run = self.run_value('canary-file', stimulus=True)
        run['canaryRoundId'] = 'round-synthetic'
        publish(run, self.root, 2, 'finished')
        import batch_views
        with patch('batch_views.analyze_round', wraps=batch_views.analyze_round) as analyze:
            app = self.app().switch_page('views/canary.py').run()
            analyze.assert_not_called()
            app.button(key='validate-canary-round').click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertEqual(analyze.call_count, 1)
            self.assertEqual(len(list((self.root / 'analysis').rglob('*.json'))), 2)
            app.button(key='validate-canary-round').click().run()
            self.assertEqual(analyze.call_count, 1)
            app = self.app().switch_page('views/canary.py').run()
            self.assertEqual(analyze.call_count, 1)
            self.assertTrue(any('Persisted summary loaded' in c.value for c in app.caption))
            # A new unrelated parquet object changes the source snapshot, but prior
            # expensive analysis remains visible only with a prominent stale warning.
            (self.root / 'new-object.parquet').write_bytes((self.root / 'events.parquet').read_bytes())
            app.sidebar.button[0].click().run()
            self.assertTrue(any('STALE snapshot' in w.value for w in app.warning))
            self.assertEqual(analyze.call_count, 1)
            app.button(key='validate-canary-round').click().run()
            self.assertEqual(analyze.call_count, 2)
            self.assertFalse(any('STALE snapshot' in w.value for w in app.warning))

    def test_all_canary_validation_reports_save_failure_and_retries(self):
        self.telemetry()
        publish(self.run_value('canary-file', stimulus=True), self.root, 2, 'finished')
        import batch_views
        with patch('batch_views.analyze_round', wraps=batch_views.analyze_round) as analyze, \
             patch('batch_views.save_result', side_effect=PermissionError('synthetic-private')) as save:
            app = self.app().switch_page('views/canary.py').run()
            app.button(key='validate-canary-round').click().run()
            self.assertEqual(analyze.call_count, 1)
            self.assertTrue(any('NOT persisted' in w.value for w in app.warning))
            self.assertFalse(any('synthetic-private' in w.value for w in app.warning))
            app.button(key='validate-canary-round').click().run()
            self.assertEqual(analyze.call_count, 1)
            self.assertEqual(save.call_count, 2)

    def test_all_canary_round_evaluates_every_family_once(self):
        self.telemetry()
        for test in ('canary-file', 'canary-process', 'canary-clone', 'canary-cross-domain', 'canary-network-endpoints'):
            run = self.run_value(test, run_id=test, stimulus=True)
            run['canaryRoundId'] = 'round-synthetic'
            publish(run, self.root, 2, 'finished')
        import analysis
        with patch('analysis.evaluate_run', wraps=analysis.evaluate_run) as evaluate, \
             patch('analysis.prepare_data', wraps=analysis.prepare_data) as prepare, \
             patch('analysis.materialize_runs', wraps=analysis.materialize_runs) as materialize:
            app = self.app().switch_page('views/canary.py').run()
            evaluate.assert_not_called(); prepare.assert_not_called()
            app.button(key='validate-canary-round').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(evaluate.call_count, 5)
            self.assertEqual(prepare.call_count, 1)
            self.assertEqual(materialize.call_count, 1)
            self.assertEqual(len(materialize.call_args.args[1]), 5)


if __name__ == '__main__':
    unittest.main()
