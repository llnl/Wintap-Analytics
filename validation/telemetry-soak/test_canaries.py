"""Canary adapters with mocked generators: no sensor, host stimuli or S3 access."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch, MagicMock


HERE = Path(__file__).resolve().parent


class CanaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location('canary_stimulus', HERE / 'canary-stimulus.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.values = {}
        manifest = ModuleType('smoke_manifest')
        manifest.record = lambda **fields: self.values.update(fields)
        def decorate(test):
            def wrapper(fn):
                self.values['test'] = test
                return fn
            return wrapper
        manifest.smoke_run = decorate
        manifest.epoch_utc = lambda value: '2026-10-25T12:00:00Z'
        manifest.utc_now = lambda: '2026-10-25T12:00:02Z'
        manifest.process_selector = lambda text, start: dict(domain='process', pids=[42], threadIds=[43],
            records=[dict(case='fork', pid=42, tid=42, parentPid=1)], skips=['clone3 unsupported'])
        self.manifest = manifest

    def invoke(self, suite, modules=None, extra=()):
        argv = ['canary-stimulus.py', '--devtools', str(self.root), '--suite', suite,
                '--output', str(self.root / 'fresh'), *extra]
        with patch.object(sys, 'argv', argv), patch.object(sys, 'path', sys.path[:]), \
             patch.object(sys, 'platform', 'linux'), \
             patch.dict(sys.modules, {'smoke_manifest': self.manifest, **(modules or {})}):
            return self.module.main()

    def test_process_reuses_generator_only_and_requires_all_stops(self):
        generator = ModuleType('process_capture_smoke_test')
        generator.spawn_process_suite = MagicMock(return_value=SimpleNamespace(start_epoch=1,
            extra_pids=(41, 42), short_lived_parent_pid=41, short_lived_child_pids=(43,),
            links=[SimpleNamespace(name='fork', parent_pid=41, child_pid=42)]))
        generator.query_duckdb = MagicMock(side_effect=AssertionError('No telemetry queries'))
        generator.start_lintap_direct_parquet = MagicMock(side_effect=AssertionError('No collector starts'))
        self.assertEqual(self.invoke('process', {'process_capture_smoke_test': generator}), 0)
        generator.spawn_process_suite.assert_called_once_with(short_lived_children=6)
        self.assertEqual(self.values['test'], 'canary-process')
        self.assertTrue(self.values['stimulusOnly'])
        self.assertEqual(self.values['selectors'][0]['pids'], [41, 42, 43])
        self.assertTrue(self.values['selectors'][0]['requireStopPerPid'])
        generator.query_duckdb.assert_not_called()
        generator.start_lintap_direct_parquet.assert_not_called()

    def test_eight_file_bound_and_private_prefix(self):
        generator = ModuleType('file_capture_smoke_test')
        generator.generate_file_activity = MagicMock(return_value=SimpleNamespace(pid=42,
            path_prefix='/fixture/fresh/file-', start_epoch=1))
        self.invoke('file', {'file_capture_smoke_test': generator})
        generator.generate_file_activity.assert_called_once_with(self.root / 'fresh', unique_file_count=8)
        self.assertEqual(self.values['selectors'][0]['expectedPaths'], 8)
        self.assertEqual(self.values['selectors'][0]['expectedActivities'], ['Open', 'Read', 'Write', 'Close', 'Delete'])

    def test_missing_clone_helper_is_explicit_skip(self):
        self.invoke('clone')
        self.assertEqual(self.values['results']['cases'][0]['status'], 'skipped')
        self.assertNotIn('selectors', self.values)

    def test_clone_is_one_bounded_helper_round_no_sensor_management(self):
        with patch.object(subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='fixture', stderr='')) as run:
            self.invoke('clone', extra=['--clone-helper', str(self.root / 'helper')])
        self.assertEqual(run.call_args.args[0], [str((self.root / 'helper').resolve()), '--rounds=1'])
        self.assertEqual(run.call_args.kwargs['timeout'], 30)
        self.assertTrue(self.values['selectors'][0]['requireStopPerPid'])
        self.assertEqual(self.values['selectors'][0]['skips'], ['clone3 unsupported'])

    def test_named_generator_uses_new_outer_canary_manifest(self):
        generator = ModuleType('telemetry_smoke_workload')
        generator.main = MagicMock()
        generator.main.__wrapped__ = MagicMock()
        self.invoke('cross-domain', {'telemetry_smoke_workload': generator})
        generator.main.assert_not_called()
        generator.main.__wrapped__.assert_called_once()
        self.assertEqual(self.values['test'], 'canary-cross-domain')

    def test_sensor_control_option_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.invoke('file', extra=['--start-lintap'])


if __name__ == '__main__':
    unittest.main()
