"""Synthetic round/context/store regressions; no collection host or live S3."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import duckdb

from analysis import (analyze_round, bind_hosts, canary_rounds, case_context, digest,
                      hostname_aliases, input_fingerprint, materialize_runs,
                      read_receipts, runtime_context)
from queries import evaluate_run
from result_store import (MAX_RESULT_BYTES, load_latest, load_result, location,
                          save_result)
from s3_source import discover_host_files
from test_s3_source import Paginator


def run(test='canary-process', run_id='fixture', host='fixture.example.invalid'):
    return dict(test=test, runId=run_id, host=dict(hostname=host), status='passed', stimulusOnly=True,
        canaryRoundId='synthetic-round', startedAtUtc='2026-10-25T12:00:00Z', completedAtUtc='2026-10-25T12:00:02Z',
        selectors=[dict(domain='process', pids=[42], expectedActivities=['Start'], requireStopPerPid=True)])


def receipt(**changes):
    value = dict(schemaVersion=1, captureRunId='synthetic-capture', phase='startup-complete',
        startedAtUtc='2026-10-25T11:00:00Z', completedAtUtc='2026-10-25T11:00:02Z',
        sensors={n: dict(enabled=True, status='running', tier='synthetic', hooks={}, features={})
                 for n in ('Execve', 'Clone', 'Exit', 'FileOps', 'Network')},
        settings=dict(etlStarted=dict(effectiveValue=True), dataPath=dict(effectiveValue='/private/fixture')))
    value.update(changes)
    return value


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect()
        self.addCleanup(self.con.close)
        self.con.execute("SET TimeZone='UTC'")
        self.con.execute("CREATE VIEW smoke_data AS SELECT 'process' AS domain, 'fixture' AS host, TIMESTAMP '2026-10-25 12:00:01' AS event_time, 42 AS pid, 1 AS parent_pid, 'identity' AS pid_hash, 'start' AS activity, NULL::VARCHAR AS protocol, 1 AS event_count")

    def test_round_membership_explicit_old_directory_and_standalone(self):
        first, second = run(), run('canary-file', 'second')
        self.assertEqual(len(canary_rounds([first, second])), 1)
        second['canaryRoundId'] = 'different'
        self.assertEqual(len(canary_rounds([first, second])), 2)
        for r in (first, second):
            r.pop('canaryRoundId')
            r['command'] = ['python', '--manifest', '/synthetic/session/round.fixture/run.json']
        self.assertEqual(len(canary_rounds([first, second])), 1)
        second['command'] = ['python', '--manifest=/synthetic/session/round.other/run.json']
        self.assertEqual(len(canary_rounds([first, second])), 2)
        first.pop('command'); second.pop('command')
        self.assertEqual(len(canary_rounds([first, second])), 2)

    def test_aliases_are_unique_and_do_not_mutate_manifests(self):
        r = run()
        aliases = hostname_aliases([r], [('fixture', receipt())])
        self.assertEqual(aliases, {'fixture.example.invalid': 'fixture'})
        self.assertEqual(bind_hosts([r], aliases)[0]['host']['hostname'], 'fixture')
        self.assertEqual(r['host']['hostname'], 'fixture.example.invalid')
        collision = run(run_id='other', host='fixture.other.invalid')
        self.assertFalse(hostname_aliases([r, collision], [('fixture', receipt())]))
        self.assertFalse(hostname_aliases([r], [('fixture', receipt()), ('fixture.other.invalid', receipt())]))
        self.assertFalse(hostname_aliases([r], [('fixture.other.invalid', receipt())]))

    def test_temporal_context_latest_preceding_and_duplicates(self):
        r = run(host='fixture')
        values = [('fixture', receipt()), ('fixture', receipt())]
        context = runtime_context(r, values)
        self.assertEqual(context['status'], 'temporal')
        self.assertNotIn('dataPath', context['settings'])
        self.assertEqual(runtime_context(r, values, ['bad'])['status'], 'unknown')
        self.assertEqual(runtime_context(run(), values)['status'], 'unknown')
        newer = receipt(captureRunId='newer', startedAtUtc='2026-10-25T11:30:00Z', completedAtUtc='2026-10-25T11:30:02Z')
        self.assertEqual(runtime_context(r, values + [('fixture', newer)])['capture_run_id'], 'newer')

    def test_temporal_conflicts_startup_race_restart_future_and_invalid(self):
        r = run(host='fixture')
        self.assertEqual(runtime_context(r, [('fixture', receipt()), ('fixture', receipt(captureRunId='conflict'))])['status'], 'ambiguous')
        race = receipt(completedAtUtc='2026-10-25T12:00:01Z')
        self.assertEqual(runtime_context(r, [('fixture', race)])['status'], 'ambiguous')
        restart = receipt(startedAtUtc='2026-10-25T12:00:01Z', completedAtUtc='2026-10-25T12:00:02Z')
        self.assertEqual(runtime_context(r, [('fixture', receipt()), ('fixture', restart)])['status'], 'ambiguous')
        self.assertEqual(runtime_context(r, [('fixture', restart)])['status'], 'unknown')
        self.assertEqual(runtime_context(r, [('fixture', receipt(startedAtUtc='bad'))])['status'], 'unknown')

    def test_disabled_failed_partial_and_unknown_explanations(self):
        for status in ('disabled', 'failed', 'partial'):
            context = dict(sensors={'Network': dict(status=status)})
            self.assertIn('may explain', case_context(dict(domain='network'), context)['explanation'])
        self.assertIn('unknown', case_context(dict(domain='network'), {})['explanation'])
        self.assertIn('not explained', case_context(dict(domain='network'), dict(sensors=receipt()['sensors']))['explanation'])

    def test_shared_materialization_parity_dedup_and_budget(self):
        r = run(host='fixture')
        before = evaluate_run(self.con, r, True)
        materialize_runs(self.con, [r, r])
        self.assertEqual(evaluate_run(self.con, r, True), before)
        self.assertEqual(self.con.execute('SELECT count(*) FROM canary_events').fetchone()[0], 1)
        self.con.execute("CREATE OR REPLACE TEMP VIEW smoke_data AS SELECT 'process' AS domain, 'fixture' AS host, TIMESTAMP '2026-10-25 12:00:01' AS event_time, 42 AS pid")
        with self.assertRaisesRegex(ValueError, 'budget exceeded'):
            materialize_runs(self.con, [r], max_rows=0)

    def test_round_alias_stop_gap_and_runtime_context(self):
        r = run()
        with patch('analysis.prepare_data', return_value=(1, [], True)), \
             patch('analysis.read_receipts', return_value=([('fixture', receipt())], [])):
            report = analyze_round(self.con, [r], [r], [], [])
        result = report['results'][0]
        self.assertEqual(result['state'], 'yellow')
        self.assertEqual(result['runtime']['status'], 'temporal')
        self.assertIn('inferred', result['runtime']['hostname_correlation'])
        self.assertEqual(result['cases'][0]['missing'], ['PID 42 Stop', 'PID 42 Start identities linked to Stop'])
        self.assertEqual(len(report['missing_families']), 4)

    def test_budget_failure_never_accepts_partial_evaluation(self):
        r = run(host='fixture')
        with patch('analysis.prepare_data', return_value=(1, [], True)), \
             patch('analysis.evaluate_run') as evaluator:
            report = analyze_round(self.con, [r], [r], [], [], max_rows=0)
        evaluator.assert_not_called()
        self.assertTrue(report['errors'])
        self.assertFalse(report['results'][0]['cases'])
        self.assertEqual(report['results'][0]['state'], 'yellow')

    def test_all_skipped_never_reads_telemetry(self):
        r = run('canary-clone'); r['selectors'] = []
        r['results'] = dict(cases=[dict(case='native', status='skipped', reason='No synthetic helper')])
        with patch('analysis.prepare_data') as prepare:
            result = analyze_round(self.con, [r], [r], [], [])['results'][0]
        prepare.assert_not_called()
        self.assertEqual(result['state'], 'yellow')
        self.assertEqual(len(result['skips']), 1)

    def test_hidden_overlap_remains_in_summary(self):
        r = run(host='fixture'); hidden = run(run_id='hidden', host='fixture')
        with patch('analysis.prepare_data', return_value=(1, [], True)):
            result = analyze_round(self.con, [r], [r, hidden], [], [])['results'][0]
        self.assertTrue(any('Overlapping same-host' in reason for reason in result['reasons']))
        self.assertEqual(result['state'], 'yellow')

    def test_query_error_details_are_not_saved(self):
        r = run(host='fixture')
        case = dict(selector=r['selectors'][0], checks=[], rows=0, violations=[], error='fixture-private-signed-url')
        evaluation = dict(state='yellow', reasons=['case: fixture-private-signed-url'], cases=[case])
        with patch('analysis.prepare_data', return_value=(0, [], False)), \
             patch('analysis.evaluate_run', return_value=evaluation):
            report = analyze_round(self.con, [r], [r], [], [])
        self.assertNotIn('fixture-private-signed-url', json.dumps(report))
        self.assertEqual(report['results'][0]['cases'][0]['observation'], 'unavailable')

    def test_alias_opt_out_keeps_exact_hostname(self):
        r = run()
        with patch('analysis.prepare_data', return_value=(1, [], True)), \
             patch('analysis.read_receipts', return_value=([('fixture', receipt())], [])):
            result = analyze_round(self.con, [r], [r], [], [], allow_hostname_aliases=False)['results'][0]
        self.assertEqual(result['cases'][0]['rows'], 0)
        self.assertEqual(result['runtime']['status'], 'unknown')
        self.assertEqual(result['runtime']['hostname_correlation'], 'exact hostname')

    def test_red_violations_survive_disabled_runtime_and_errors(self):
        self.con.execute("CREATE OR REPLACE VIEW smoke_data AS SELECT 'process' AS domain, 'fixture' AS host, TIMESTAMP '2026-10-25 12:00:01' AS event_time, 42 AS pid, 1 AS parent_pid, 'identity' AS pid_hash, 'start' AS activity, NULL::VARCHAR AS protocol, 1 AS event_count")
        r = run(host='fixture'); r['selectors'] = [dict(domain='process', threadIds=[42])]
        v = receipt(); v['sensors']['Clone']['status'] = 'disabled'
        with patch('analysis.prepare_data', return_value=(1, ['unreadable'], True)), \
             patch('analysis.read_receipts', return_value=([('fixture', v)], [])):
            result = analyze_round(self.con, [r], [r], [], [])['results'][0]
        self.assertEqual(result['state'], 'red')
        self.assertTrue(result['cases'][0]['violations'])
        self.assertIn('may explain', result['cases'][0]['runtime']['explanation'])

    def test_fingerprint_changes_for_objects_settings_evaluator_errors_and_hidden_runs(self):
        r = run(); snapshot = {'synthetic': ['etag', 10, 'time']}; settings = {'padding': 15}
        original = input_fingerprint([r], [r], snapshot, settings, 'source')
        for args in (([r], [r], {'synthetic': ['new', 10, 'time']}, settings, 'source'),
                     ([r], [r], snapshot, {'padding': 16}, 'source'),
                     ([r], [r, run(run_id='hidden')], snapshot, settings, 'source'),
                     ([r], [r], snapshot, settings, 'other')):
            self.assertNotEqual(original, input_fingerprint(*args))
        self.assertEqual(original, input_fingerprint([r], [r], snapshot, settings, 'source'))

    def test_receipts_schema_null_malformed_and_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'host.parquet'
            self.con.execute('CREATE TABLE receipts (Hostname VARCHAR, RuntimeCapabilitiesJson VARCHAR)')
            self.con.executemany('INSERT INTO receipts VALUES (?, ?)', [('fixture', json.dumps(receipt())), ('fixture', None)])
            self.con.execute('COPY receipts TO ? (FORMAT PARQUET)', [str(p)])
            values, errors = read_receipts(self.con, [p])
            self.assertEqual(len(values), 1); self.assertFalse(errors)
            values, errors = read_receipts(self.con, [p], max_receipts=0)
            self.assertFalse(values); self.assertTrue(errors)
            self.con.execute("INSERT INTO receipts VALUES ('fixture', 'invalid')")
            self.con.execute('COPY receipts TO ? (FORMAT PARQUET)', [str(p)])
            self.assertTrue(read_receipts(self.con, [p])[1])

    def test_host_history_listing_deduplicates_and_caps(self):
        client = MagicMock()
        client.get_paginator.return_value = Paginator(['root/raw_sensor/raw_host/dayPK=20261020/h.parquet',
                                                      'root/raw_sensor/raw_process/dayPK=20261025/p.parquet'])
        cfg = dict(datasets=['s3://fixture-bucket/root'], max_files=3)
        snapshot = {}
        paths = discover_host_files(client, cfg, snapshot)
        self.assertEqual(len(paths), 1)
        self.assertEqual(set(paths), set(snapshot))
        cfg['max_files'] = 0
        with self.assertRaises(ValueError):
            discover_host_files(client, cfg)


class MemoryS3:
    def __init__(self):
        self.objects = {}
        self.writes = []

    def put_object(self, **kwargs):
        self.writes.append(kwargs['Key'])
        self.objects[(kwargs['Bucket'], kwargs['Key'])] = kwargs['Body']

    def get_object(self, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            raise FileNotFoundError()
        return dict(Body=io.BytesIO(self.objects[(Bucket, Key)]))


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ctx = dict(remote=False, data_root=self.temp.name, analysis_group=digest('round'))
        self.report = dict(schema_version=1, fingerprint=digest('inputs'), results=[], missing_families=[], errors=[],
                           analyzed_at='2026-10-25T12:00:00Z', scope='synthetic')

    def test_local_save_load_latest_and_raw_sensor_sibling(self):
        self.ctx['data_root'] = str(Path(self.temp.name) / 'raw_sensor')
        save_result(self.ctx, self.report)
        loaded = load_result(self.ctx, self.report['fingerprint'])
        self.assertEqual(loaded['fingerprint'], self.report['fingerprint'])
        self.assertEqual(load_latest(self.ctx), loaded)
        self.assertTrue((Path(self.temp.name) / 'analysis').is_dir())
        self.assertFalse((Path(self.temp.name) / 'raw_sensor').exists())
        self.assertIsNone(load_result(self.ctx, digest('different')))
        self.assertEqual(load_latest(self.ctx)['fingerprint'], self.report['fingerprint'])

    def test_store_rejects_git_and_symlink_escape(self):
        (Path(self.temp.name) / '.git').mkdir()
        with self.assertRaisesRegex(ValueError, 'Git'):
            save_result(self.ctx, self.report)
        (Path(self.temp.name) / '.git').rmdir()
        with tempfile.TemporaryDirectory() as elsewhere:
            (Path(self.temp.name) / 'analysis').symlink_to(elsewhere)
            with self.assertRaisesRegex(ValueError, 'escapes'):
                save_result(self.ctx, self.report)

    def test_s3_writes_only_summary_prefix_and_read_verifies(self):
        client = MemoryS3()
        ctx = dict(remote=True, client=client, config=dict(datasets=['s3://fixture-bucket/root/raw_sensor']), analysis_group=digest('round'))
        save_result(ctx, self.report)
        self.assertEqual(len(client.writes), 2)
        self.assertTrue(all(k.startswith('root/analysis/smoke-tests/v1/') for k in client.writes))
        self.assertEqual(load_latest(ctx)['fingerprint'], self.report['fingerprint'])
        with patch.object(client, 'put_object', side_effect=PermissionError('private fixture secret')):
            with self.assertRaisesRegex(RuntimeError, 'details suppressed') as error:
                save_result(ctx, self.report)
        self.assertNotIn('private fixture secret', str(error.exception))

    def test_checksum_schema_identity_and_oversize_fail_closed(self):
        save_result(self.ctx, self.report)
        _, path = location(self.ctx, self.report['fingerprint'])
        value = json.loads(path.read_text()); value['results'] = [{'state': 'green'}]
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(RuntimeError, 'corrupt'):
            load_result(self.ctx, self.report['fingerprint'])
        path.write_bytes(b'x' * (MAX_RESULT_BYTES + 1))
        with self.assertRaises(RuntimeError):
            load_result(self.ctx, self.report['fingerprint'])
        with self.assertRaises(ValueError):
            location(self.ctx, '../raw_sensor')
        with self.assertRaises(ValueError):
            save_result(self.ctx, dict(self.report, schema_version=2))

    def test_unverified_write_is_not_acknowledged(self):
        client = MemoryS3()
        ctx = dict(remote=True, client=client, config=dict(datasets=['s3://fixture-bucket/root']))
        with patch.object(client, 'put_object'), patch.object(client, 'get_object', return_value=dict(Body=io.BytesIO(b'wrong'))):
            with self.assertRaisesRegex(RuntimeError, 'verification failed'):
                save_result(ctx, self.report)


if __name__ == '__main__':
    unittest.main()
