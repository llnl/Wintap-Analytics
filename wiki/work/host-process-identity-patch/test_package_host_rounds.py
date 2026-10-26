"""Regression guards for the failed installed-host harness attempt."""
from pathlib import Path
import io
import json
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'wintap' / 'devtools'))
from package_host_rounds import sample_service, service_stopped_cleanly, systemd_override, exit_recovery_environment, main


class InstalledHarnessTests(unittest.TestCase):
    def test_exit_recovery_pair_changes_only_recovery_not_birth_or_capacity(self):
        off, on = exit_recovery_environment(False), exit_recovery_environment(True)
        self.assertEqual(off.pop('WINTAP_EXPERIMENT_EXIT_IDENTITY_RECOVERY'), 'false')
        self.assertEqual(on.pop('WINTAP_EXPERIMENT_EXIT_IDENTITY_RECOVERY'), 'true')
        self.assertEqual(off, on)
        self.assertEqual(on['WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY'], '1024')
        for sensor in ('CLONE', 'EXECVE', 'PROCESS_RUNDOWN'):
            self.assertEqual(on[f'WINTAP_ENABLE_{sensor}_SENSOR'], 'false')

    def test_exit_recovery_rejects_mixed_modes_before_writing_evidence(self):
        for mode in (['--shutdown-window'], ['--soak-seconds', '1800'], ['--retry-capacity-ab'], ['--experiment-exit-recovery']):
            with patch('sys.argv', ['harness', '--qa-root', '/unused', '--data-root', '/unused-data',
                                    '--exit-recovery-ab'] + mode), \
                 patch('package_host_rounds.Path.mkdir') as mkdir, patch('sys.stderr', io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main()
                self.assertEqual(error.exception.code, 2)
                mkdir.assert_not_called()

    def test_paths_use_later_environment_file_not_lower_precedence_environment(self):
        text = systemd_override('/native/evidence/quality.env')
        self.assertIn('EnvironmentFile=/native/evidence/quality.env\n', text)
        self.assertNotIn('Environment=', text)
        self.assertIn('KillSignal=SIGTERM\n', text)
        self.assertIn('TimeoutStopSec=120\n', text)

    def test_systemd_success_does_not_certify_signal_termination(self):
        self.assertFalse(service_stopped_cleanly(
            'Result=success\nExecMainCode=2\nExecMainStatus=2\nActiveState=inactive\nNRestarts=0\n'))

    def test_clean_exit_without_restart_passes(self):
        self.assertTrue(service_stopped_cleanly(
            'Result=success\nExecMainCode=1\nExecMainStatus=0\nActiveState=inactive\nNRestarts=0\n'))

    def test_timeout_or_restart_fails_even_if_final_exit_zero(self):
        for result, restarts in [('timeout', '0'), ('success', '1')]:
            self.assertFalse(service_stopped_cleanly(
                f'Result={result}\nExecMainCode=1\nExecMainStatus=0\nActiveState=inactive\nNRestarts={restarts}\n'))

    def test_monitor_handles_spaces_and_parentheses_in_process_name(self):
        fields = ['0'] * 22
        fields[11], fields[12], fields[19] = '100', '23', '456'
        stat = '42 (collector (worker)) ' + ' '.join(fields)
        with patch('package_host_rounds.Path.read_text', side_effect=[stat, 'VmRSS:\t1024 kB\nThreads:\t5\n']), \
             patch('package_host_rounds.shutil.disk_usage', return_value=SimpleNamespace(free=8192)):
            output = io.StringIO()
            sample_service('42', '456', output)
        row = json.loads(output.getvalue())
        self.assertEqual((row['cpu_ticks'], row['rss_kib'], row['threads'], row['native_free_bytes']),
                         (123, 1024, 5, 8192))

    def test_monitor_rejects_reused_pid_without_writing_a_sample(self):
        fields = ['0'] * 22
        fields[19] = '789'
        with patch('package_host_rounds.Path.read_text', return_value='42 (collector) ' + ' '.join(fields)):
            output = io.StringIO()
            with self.assertRaisesRegex(RuntimeError, 'PID reused'):
                sample_service('42', '456', output)
        self.assertEqual('', output.getvalue())

    def test_monitor_does_not_hide_missing_collector(self):
        with patch('package_host_rounds.Path.read_text', side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                sample_service('42', '456', io.StringIO())


if __name__ == '__main__':
    unittest.main()
