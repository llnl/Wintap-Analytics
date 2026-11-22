"""Adversarial synthetic quality checks; no private datasets or identities."""
import unittest
from pathlib import Path
import tempfile

import duckdb
from queries import evaluate_case, evaluate_run, prepare_data, selector_query


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

    def test_rename_paths_use_only_ground_truth_activities(self):
        self.insert(domain='file', activity='write', path='/fixture/original')
        self.insert(domain='file', activity='delete', path='/fixture/renamed')
        selector = dict(domain='file', pids=[42], pathPrefix='/fixture/', expectedPaths=2,
            expectedActivities=['Write', 'Delete'], pathExpectations=[
                dict(path='/fixture/original', expectedActivities=['Write']),
                dict(path='/fixture/renamed', expectedActivities=['Delete'])])
        self.assertTrue(all(c['observed'] for c in self.evaluate(selector)['checks']))
        selector['pathExpectations'][1]['expectedActivities'].append('Read')
        self.assertTrue(any(not c['observed'] for c in self.evaluate(selector)['checks']))

    def test_case_folding_does_not_prove_distinct_linux_path_identity(self):
        self.insert(domain='file', activity='open', path='/fixture/a')
        selector = dict(domain='file', pids=[42], pathPrefix='/fixture/', paths=['/fixture/A', '/fixture/a'],
            expectedPaths=2, expectedActivities=['Open'])
        result = self.evaluate(selector)
        self.assertTrue(result['warnings'])
        self.assertTrue(any(not c['observed'] for c in result['checks']))

    def test_udp_tuple_checks_not_satisfied_by_tcp_or_extra_wrong_row(self):
        selector = self.network()
        selector['expectedProtocols'] = ['udp']
        selector['expectedActivities'] = ['UdpIpSend', 'UdpIpRecv']
        selector['endpointExpectations'][0]['protocol'] = 'udp'
        self.socket_row(activity='udpipsend', protocol='udp')
        self.socket_row(activity='udpiprecv', protocol='udp', source_port=4321, destination_port=1234)
        self.assertTrue(all(c['observed'] for c in self.evaluate(selector)['checks']))
        self.socket_row(activity='udpipsend', protocol='udp', source_port=9999)
        self.assertTrue(self.evaluate(selector)['violations'])

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

    def test_source_normalization_requires_real_breadcrumb_field(self):
        with tempfile.TemporaryDirectory() as directory, duckdb.connect() as con:
            path = Path(directory) / 'process.parquet'
            con.execute("COPY (SELECT 'fixture' Hostname, 'Process' MessageType, 42 PID, "
                "'PROC_START_SRC=execve_or_execveat FLAGS=0x0' Process_Arguments) TO ? (FORMAT PARQUET)", [str(path)])
            _, errors, available = prepare_data(con, directory)
            self.assertFalse(errors)
            self.assertTrue(available)
            self.assertEqual(con.execute('SELECT start_source FROM smoke_data').fetchone()[0], 'execve_or_execveat')
            con.execute('DROP VIEW smoke_data')
            path.unlink()
            con.execute("COPY (SELECT 'fixture' Hostname, 'Process' MessageType, 42 PID, "
                "'PROC_START_SRC=sched_exec' CommandLine) TO ? (FORMAT PARQUET)", [str(path)])
            prepare_data(con, directory)
            self.assertIsNone(con.execute('SELECT start_source FROM smoke_data').fetchone()[0])

    def test_normal_process_projection_source_field_is_used(self):
        with tempfile.TemporaryDirectory() as directory, duckdb.connect() as con:
            path = Path(directory) / 'process.parquet'
            con.execute("COPY (SELECT 'fixture' Hostname, 'Process' MessageType, 42 PID, "
                "'sched_fork' ProcessStartSource, 'PROC_START_SRC=sched_exec' Process_Arguments) TO ? (FORMAT PARQUET)", [str(path)])
            _, errors, available = prepare_data(con, directory)
            self.assertFalse(errors)
            self.assertTrue(available)
            self.assertEqual(con.execute('SELECT start_source FROM smoke_data').fetchone()[0], 'sched_fork')

    def test_wrong_extra_directed_row_not_hidden_by_good_rows(self):
        self.socket_row()
        self.socket_row('tcpiprecv')
        self.socket_row(source_port=1111, destination_port=2222)
        result = self.evaluate(self.network())
        self.assertEqual(result['rows'], 3)
        self.assertTrue(any('incorrect endpoint/directed provenance' in v for v in result['violations']))

    def test_known_contradiction_survives_missing_field(self):
        self.socket_row()
        self.socket_row('tcpiprecv')
        self.socket_row(source_port=9999, local_address=None)
        result = self.evaluate(self.network())
        self.assertTrue(result['violations'])
        self.assertTrue(result['warnings'])

    def test_partial_fields_must_match_one_consistent_role(self):
        selector = self.network()
        selector['endpointExpectations'].append(dict(selector['endpointExpectations'][0],
            localIp='192.0.2.3', remoteIp='192.0.2.4'))
        self.socket_row(local_address='192.0.2.1', remote_address='192.0.2.4', source_port=None)
        self.assertTrue(self.evaluate(selector)['violations'])
        self.con.execute('DELETE FROM smoke_data')
        self.socket_row(local_address='192.0.2.3', remote_address=None, source_port=None)
        self.assertFalse(self.evaluate(selector)['violations'])

    def test_source_tokens_and_explicit_null_are_conservative(self):
        cases = [
            (None, None), ('', None), ('xPROC_START_SRC=sched_exec', None),
            ('PROC_START_SRC=sched_exec123', None), ('PROC_START_SRC=unknown', None),
            ('PROC_START_SRC=sched_fork PROC_START_SRC=sched_exec', None),
            ('PROC_START_SRC=sched_exec PROC_START_SRC=unknown', None),
            ('PROC_START_SRC=sched_exec PROC_START_SRC=sched_exec', 'sched_exec'),
            ('\tPROC_START_SRC=execve_or_execveat\nFLAGS=0x0', 'execve_or_execveat'),
        ]
        with tempfile.TemporaryDirectory() as directory, duckdb.connect() as con:
            for arguments, expected in cases:
                with self.subTest(arguments=arguments):
                    path = Path(directory) / 'process.parquet'
                    # Bind data in a table: COPY target placeholders can precede
                    # SELECT placeholders in DuckDB's parameter ordering.
                    con.execute('CREATE OR REPLACE TABLE fixture AS SELECT ?::VARCHAR Arguments', [arguments])
                    con.execute('COPY fixture TO ? (FORMAT PARQUET)', [str(path)])
                    prepare_data(con, directory)
                    self.assertEqual(con.execute('SELECT start_source FROM smoke_data').fetchone()[0], expected)
                    con.execute('DROP VIEW smoke_data')
                    path.unlink()
            for source in (None, '', 'unknown'):
                con.execute("CREATE OR REPLACE TABLE fixture AS SELECT ?::VARCHAR ProcessStartSource, 'PROC_START_SRC=sched_exec' Arguments", [source])
                con.execute('COPY fixture TO ? (FORMAT PARQUET)', [str(path)])
                prepare_data(con, directory)
                self.assertIsNone(con.execute('SELECT start_source FROM smoke_data').fetchone()[0])
                con.execute('DROP VIEW smoke_data')
                path.unlink()

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

    def test_missing_host_relative_address_stays_incomplete_not_contradiction(self):
        self.socket_row(local_address=None)
        result = self.evaluate(self.network())
        self.assertFalse(result['violations'])
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
