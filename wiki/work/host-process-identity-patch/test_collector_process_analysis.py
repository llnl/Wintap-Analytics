import unittest
import duckdb
from collector_process_analysis import collector_checks
from experiment_live_analysis import digest


class CollectorProcessAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.connection = duckdb.connect(':memory:')
        self.connection.execute('''create table process(pid integer,activitytype varchar,
            eventtime bigint,pidhash varchar,agentid varchar,processpath varchar,
            commandline varchar,parentpid integer,username varchar)''')
        self.truth = dict(pid=42,start_ticks=100,clock_ticks=100,parent_pid=1,
                          executable='/usr/lib/lintap/Lintap',commandline='Lintap --collect')
        self.host = dict(hostname='host',boot_unix_seconds=100)
        self.birth = 116444736000000000 + 101 * 10_000_000

    def tearDown(self):
        self.connection.close()

    def add(self, activity='Refresh', birth=None, hash_=None):
        self.connection.execute('insert into process values (?,?,?,?,?,?,?,?,?)',
            [42,activity,birth or self.birth,hash_ or digest('HOST',42,self.birth),
             'agent','/usr/lib/lintap/Lintap','Lintap --collect',1,'root'])

    def checks(self):
        return collector_checks(self.connection,self.truth,self.host,'agent')['gates']

    def test_empty_capture_never_passes(self):
        self.assertFalse(any(self.checks().values()))

    def test_actual_refresh_passes(self):
        self.add()
        self.assertTrue(all(self.checks().values()))

    def test_wrong_birth_and_reused_pid_fail(self):
        self.add(birth=self.birth+100,hash_=digest('HOST',42,self.birth+100))
        self.assertFalse(self.checks()['collector_canonical_identity'])
        self.assertFalse(self.checks()['collector_refresh_uses_actual_birth'])

    def test_stop_only_does_not_prove_inventory(self):
        self.add(activity='Stop')
        self.assertFalse(self.checks()['collector_refresh_recorded'])
        self.assertTrue(self.checks()['collector_canonical_identity'])

    def test_wrong_parent_and_executable_fail(self):
        self.add()
        self.connection.execute("update process set parentpid=2,processpath='/wrong'")
        self.assertFalse(self.checks()['collector_parent_pid_matches'])
        self.assertFalse(self.checks()['collector_executable_matches'])

    def test_invented_start_is_not_a_refresh(self):
        self.add(activity='Start')
        self.assertFalse(self.checks()['collector_refresh_recorded'])
        self.assertFalse(self.checks()['collector_preexisting_not_fabricated_start'])

    def test_agent_and_commandline_mismatch_are_visible(self):
        self.add()
        self.connection.execute("update process set agentid='copied-agent',commandline='wrong'")
        self.assertFalse(self.checks()['collector_agent_matches'])
        self.assertFalse(self.checks()['collector_commandline_matches'])


if __name__ == '__main__':
    unittest.main()
