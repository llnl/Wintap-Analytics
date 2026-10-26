import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'wintap' / 'devtools'))
from diagnostic_delivery_rounds import require_idle, round_environment, host_capture_root, stimulus_ready_deadline


class DiagnosticControlsTests(unittest.TestCase):
    def test_active_service_is_a_blocker_without_any_process_scan(self):
        with patch('diagnostic_delivery_rounds.Path.iterdir') as scan:
            with self.assertRaisesRegex(RuntimeError, 'not inactive'):
                require_idle('ActiveState=active\nMainPID=701\nNRestarts=0')
            scan.assert_not_called()

    def test_inactive_service_still_scans_for_competing_collectors(self):
        with patch('diagnostic_delivery_rounds.Path.iterdir', return_value=[]) as scan:
            require_idle('ActiveState=inactive\nMainPID=0\nNRestarts=0')
            scan.assert_called_once()

    def test_matched_controls_change_only_tracing_and_evidence_paths(self):
        with patch('diagnostic_delivery_rounds.Path.read_text', return_value='WINTAP_ENABLE_NETWORK_SENSOR=true\n'):
            off = round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'off')
            on = round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'on')
        trace_fields = {k: on.pop(k) for k in list(on) if k.startswith('WINTAP_EXPERIMENT_TRACE_') or k == 'WINTAP_EXPERIMENT_ATTRIBUTION_TRACE_PATH'}
        self.assertEqual(off, on)
        self.assertEqual(off['WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY'], '1024')
        self.assertEqual(off['WINTAP_EXPERIMENT_DRAIN_BATCH_WINDOWS'], 'false')
        self.assertEqual(trace_fields['WINTAP_EXPERIMENT_TRACE_BUDGET'], 'delivery')
        self.assertEqual(trace_fields['WINTAP_EXPERIMENT_TRACE_FILE_PREFIX'], '/qa/workload')

    def test_unknown_control_mode_is_not_silently_trace_off(self):
        with patch('diagnostic_delivery_rounds.Path.read_text', return_value=''):
            with self.assertRaises(ValueError):
                round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'typo')

    def test_readiness_policy_is_explicit_and_does_not_change_retry_or_drain(self):
        with patch('diagnostic_delivery_rounds.Path.read_text', return_value=''):
            legacy = round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'off')
            required = round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'off', 'required')
            self.assertEqual(required.pop('WINTAP_EXPERIMENT_ETL_READINESS'), 'true')
            self.assertEqual(legacy, required)
            with self.assertRaises(ValueError):
                round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'off', 'typo')

    def test_shutdown_barrier_is_explicit_without_the_old_sleep(self):
        with patch('diagnostic_delivery_rounds.Path.read_text', return_value=''):
            legacy = round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'off', 'required')
            required = round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'off', 'required', 'required')
            self.assertEqual(required.pop('WINTAP_EXPERIMENT_ETL_SHUTDOWN_BARRIER'), 'true')
            self.assertEqual(legacy, required)
            self.assertEqual(legacy['WINTAP_EXPERIMENT_DRAIN_BATCH_WINDOWS'], 'false')
            with self.assertRaises(ValueError):
                round_environment(Path('/env'), Path('/qa'), Path('/data'), Path('/runtime'), 'off', 'required', 'typo')

    def test_interior_stimulus_uses_latest_start_upper_bound_and_verified_offset(self):
        import datetime as dt
        log = '10/24/2026 11:00:00 FileOps sensor started\n10/24/2026 11:00:03 Network sensor started'
        target = stimulus_ready_deadline(log, -25200, 21)
        expected = dt.datetime(2026, 10, 24, 18, 0, 25, tzinfo=dt.timezone.utc).timestamp()
        self.assertEqual(target, expected)
        self.assertIsNone(stimulus_ready_deadline(log.splitlines()[0], -25200, 21))
        self.assertIsNone(stimulus_ready_deadline(log + '\n' + log, -25200, 21))

    def test_shared_data_mount_always_has_distinct_host_roots(self):
        self.assertNotEqual(host_capture_root(Path('/shared'), 'axon-target'), host_capture_root(Path('/shared'), 'caldera-host'))
        self.assertEqual(host_capture_root(Path('/shared'), 'axon-target'), Path('/shared/axon-target'))
        for host in ('', '.', '..', '../foreign', '/absolute'):
            with self.assertRaises(ValueError):
                host_capture_root(Path('/shared'), host)


if __name__ == '__main__':
    unittest.main()
