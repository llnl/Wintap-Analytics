"""Selected working-set parity, budgets, lifecycle requirements and attribution."""
import unittest

import duckdb

from page_views import materialize_run, manifest_rows, is_canary
from queries import evaluate_run, mark_overlaps


class PageQueryTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect()
        self.addCleanup(self.con.close)
        self.con.execute("SET TimeZone='UTC'")
        self.con.execute("CREATE VIEW smoke_data AS SELECT 'process' AS domain, 'fixture' AS host, TIMESTAMP '2026-10-25 12:00:01' AS event_time, 42 AS pid, 1 AS parent_pid, 'id' AS pid_hash, 'start' AS activity, NULL::VARCHAR AS protocol, 1 AS event_count")
        self.run = dict(test='canary-process', runId='fixture', host={'hostname': 'fixture'}, status='passed',
            stimulusOnly=True, startedAtUtc='2026-10-25T12:00:00Z', completedAtUtc='2026-10-25T12:00:02Z',
            selectors=[dict(domain='process', pids=[42], expectedActivities=['Start'])])

    def test_working_set_preserves_evaluation_and_does_not_duplicate_overlap(self):
        self.run['selectors'] *= 2
        before = evaluate_run(self.con, self.run, True)
        materialize_run(self.con, self.run, 15)
        after = evaluate_run(self.con, self.run, True)
        self.assertEqual(before, after)
        self.assertEqual(self.con.execute('SELECT count(*) FROM selected_events').fetchone()[0], 1)

    def test_budget_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'budget exceeded'):
            materialize_run(self.con, self.run, 15, max_rows=0)

    def test_per_pid_stop_not_satisfied_by_other_pid_stop(self):
        self.run['selectors'][0]['requireStopPerPid'] = True
        evaluation = evaluate_run(self.con, self.run, True)
        check = next(c for c in evaluation['cases'][0]['checks'] if c['expectation'] == 'PID 42 Stop')
        self.assertFalse(check['observed'])
        self.assertEqual(evaluation['state'], 'yellow')

    def test_unevaluated_manifest_success_is_not_green(self):
        self.assertEqual(manifest_rows([self.run])[0]['status'], 'yellow')
        self.assertEqual(manifest_rows([self.run])[0]['capture'], 'not evaluated')
        self.assertTrue(is_canary(self.run))

    def test_overlap_with_hidden_run_preserves_warning(self):
        other = dict(self.run, runId='hidden')
        evaluation = evaluate_run(self.con, self.run, True)
        mark_overlaps([self.run, other], {('canary-process', 'fixture'): evaluation})
        self.assertEqual(evaluation['coverage'], 'ambiguous')


if __name__ == '__main__':
    unittest.main()
