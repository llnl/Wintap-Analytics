"""Adversarial synthetic quality checks; no private datasets or identities."""
import unittest

import duckdb
from queries import evaluate_case, evaluate_run, selector_query


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect()
        self.con.execute("SET TimeZone='UTC'")
        self.con.execute('''CREATE TABLE smoke_data (
            domain VARCHAR, host VARCHAR, event_time TIMESTAMP, pid BIGINT,
            parent_pid BIGINT, pid_hash VARCHAR, activity VARCHAR, protocol VARCHAR,
            event_count BIGINT, path VARCHAR, local_port INTEGER, remote_port INTEGER,
            source_port INTEGER, destination_port INTEGER, local_address VARCHAR,
            remote_address VARCHAR, start_source VARCHAR)''')
        self.run = dict(test='canary-process', runId='synthetic', status='passed', stimulusOnly=True,
            host=dict(hostname='fixture'), startedAtUtc='2026-10-25T12:00:00Z', completedAtUtc='2026-10-25T12:00:02Z')

    def tearDown(self):
        self.con.close()

    def insert(self, **values):
        values = dict(host='fixture', event_time='2026-10-25 12:00:01', parent_pid=1, event_count=1,
            **values)
        values.setdefault('pid', 42)
        values.setdefault('pid_hash', 'fixture-identity')
        self.con.execute('INSERT INTO smoke_data (' + ','.join(values) + ') VALUES (' +
            ','.join('?' for _ in values) + ')', list(values.values()))

    def evaluate(self, selector):
        result = evaluate_case(self.con, self.run, selector, True)
        self.assertIsNone(result['error'])
        return result

    def lifecycle(self, **values):
        return dict(domain='process', pids=[42], expectedActivities=['Start', 'Stop'], requireStopPerPid=True, **values)

    def network(self):
        return dict(domain='network', pids=[42], ports=[1234, 4321], expectedProtocols=['tcp'],
            expectedActivities=['TcpIpSend', 'TcpIpRecv'], endpointExpectations=[dict(role='client', pid=42,
                localPort=1234, remotePort=4321, localIp='192.0.2.1', remoteIp='192.0.2.2')])

    def socket_row(self, activity='tcpipsend', **values):
        inbound = activity == 'tcpiprecv'
        row = dict(domain='network', protocol='tcp', activity=activity, local_port=1234,
            remote_port=4321, source_port=4321 if inbound else 1234, destination_port=1234 if inbound else 4321,
            local_address='192.0.2.1', remote_address='192.0.2.2')
        row.update(values)
        self.insert(**row)

    def test_activities_distributed_across_eight_paths_are_incomplete(self):
        required = ['Open', 'Read', 'Write', 'Close', 'Delete']
        for i, activity in enumerate(['open', 'read', 'write', 'close', 'delete', 'open', 'read', 'write']):
            self.insert(domain='file', activity=activity, path=f'/fixture/file-{i}')
        result = self.evaluate(dict(domain='file', pids=[42], pathPrefix='/fixture/file-', expectedPaths=8,
            expectedActivities=required))
        self.assertTrue(any(not c['observed'] and c['expectation'].startswith('Paths with all') for c in result['checks']))
        self.assertFalse(result['violations'])  # Missing/arrival evidence remains yellow.

    def test_exact_missing_path_not_replaced_by_extra_prefix_path(self):
        self.insert(domain='file', activity='open', path='/fixture/other')
        result = self.evaluate(dict(domain='file', pids=[42], pathPrefix='/fixture/', paths=['/fixture/expected'],
            expectedPaths=1, expectedActivities=['Open']))
        self.assertTrue(any(not c['observed'] for c in result['checks']))

    def test_complete_per_path_matrix(self):
        for path in ('/fixture/A', '/fixture/a'):
            for activity in ('open', 'read'):
                self.insert(domain='file', activity=activity, path=path)
        result = self.evaluate(dict(domain='file', pids=[42], pathPrefix='/fixture/', expectedPaths=2,
            expectedActivities=['Open', 'Read']))
        self.assertTrue(all(c['observed'] for c in result['checks']))

    def test_blank_null_and_placeholder_lifecycle_identity_are_red(self):
        for identity in ('', None, ' ', 'FixMePid', 'unknown', '0'):
            with self.subTest(identity=identity):
                self.con.execute('DELETE FROM smoke_data')
                for activity in ('start', 'stop'):
                    self.insert(domain='process', activity=activity, pid_hash=identity)
                result = self.evaluate(self.lifecycle())
                self.assertTrue(result['violations'])
                self.assertTrue(any(not c['observed'] for c in result['checks']))

    def test_stop_from_different_identity_is_red_and_not_linked(self):
        self.insert(domain='process', activity='start', pid_hash='birth-1')
        self.insert(domain='process', activity='stop', pid_hash='birth-2')
        result = self.evaluate(self.lifecycle())
        self.assertTrue(any('Stop identity differs' in v for v in result['violations']))
        self.assertTrue(any(not c['observed'] for c in result['checks']))

    def test_repeated_starts_without_provenance_are_unconfirmed_not_duplicate_birth(self):
        for activity in ('start', 'start', 'stop'):
            self.insert(domain='process', activity=activity)
        result = self.evaluate(self.lifecycle())
        self.assertFalse(result['violations'])
        self.assertTrue(result['warnings'])
        self.assertEqual(result['lifecycle']['unclassified_repeat_groups'], 1)
        self.assertTrue(any(not c['observed'] for c in result['checks']))

    def test_clone_exec_observations_preserved_with_one_identity(self):
        for origin in ('sched_fork', 'execve_or_execveat', 'sched_exec'):
            self.insert(domain='process', activity='start', start_source=origin)
        self.insert(domain='process', activity='stop')
        result = self.evaluate(self.lifecycle())
        self.assertFalse(result['violations'])
        self.assertTrue(all(c['observed'] for c in result['checks']))
        self.assertEqual(result['rows'], 4)
        self.assertEqual(result['lifecycle']['start_rows'], 3)
        self.assertEqual(result['lifecycle']['unclassified_repeat_groups'], 0)

    def test_wrong_extra_directed_row_not_hidden_by_good_rows(self):
        self.socket_row()
        self.socket_row('tcpiprecv')
        self.socket_row(source_port=1111, destination_port=2222)
        result = self.evaluate(self.network())
        self.assertEqual(result['rows'], 3)
        self.assertTrue(any('incorrect endpoint/directed provenance' in v for v in result['violations']))

    def test_wrong_protocol_candidate_remains_in_bounded_selector(self):
        self.socket_row()
        self.socket_row('tcpiprecv')
        self.socket_row(protocol='udp')
        result = self.evaluate(self.network())
        self.assertEqual(result['rows'], 3)
        self.assertTrue(any('wrong/unknown protocol' in v for v in result['violations']))

    def test_directed_ports_recover_malformed_host_relative_candidates(self):
        self.socket_row(local_port=0, remote_port=0)
        self.assertEqual(len(self.con.execute(selector_query(self.run, self.network())).fetchall()), 1)
        self.assertTrue(self.evaluate(self.network())['violations'])

    def test_missing_provenance_stays_yellow(self):
        self.socket_row(source_port=None, destination_port=None)
        result = self.evaluate(self.network())
        self.assertFalse(result['violations'])
        self.assertTrue(result['warnings'])
        self.assertTrue(any(not c['observed'] for c in result['checks']))

    def test_unrelated_shared_pid_port_candidate_is_uncertain_not_red(self):
        self.socket_row()
        self.socket_row('tcpiprecv')
        self.socket_row(local_port=1234, remote_port=9999, source_port=1234, destination_port=9999)
        result = self.evaluate(self.network())
        self.assertFalse(result['violations'])
        self.assertTrue(result['warnings'])

    def test_error_and_warning_do_not_downgrade_red(self):
        self.insert(domain='process', activity='start', pid_hash='')
        self.insert(domain='process', activity='start', pid_hash='')
        run = dict(self.run, selectors=[self.lifecycle()])
        result = evaluate_run(self.con, run, True)
        self.assertEqual(result['state'], 'red')


if __name__ == '__main__':
    unittest.main()
