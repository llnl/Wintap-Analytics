"""Independent receipt guards; never equate partial recovery with full lifecycle."""
import unittest
from experiment_live_analysis import exit_evidence_checks


class ExitEvidenceChecksTests(unittest.TestCase):
    def row(self, pid=42, retained=True, start=100, coverage='exit-only'):
        return dict(Pid=pid, ExitEvidenceRetained=retained,
                    StartBootNs=start, LifecycleCoverage=coverage)

    def test_authoritative_partial_receipt(self):
        result = exit_evidence_checks([self.row()], {42})
        self.assertTrue(all(value is True for key, value in result.items() if key != 'retained_children'))
        self.assertEqual(result['retained_children'], 1)

    def test_legacy_start_never_recovers(self):
        result = exit_evidence_checks([self.row(retained=False, start=0)], {42}, legacy=True)
        self.assertTrue(result['recovery_matches_authoritative_start'])
        self.assertFalse(exit_evidence_checks([self.row(start=0)], {42}, legacy=True)['recovery_matches_authoritative_start'])

    def test_missing_duplicate_and_incomplete_receipts_fail(self):
        for rows in ([], [self.row(), self.row()], [self.row(43)]):
            self.assertFalse(exit_evidence_checks(rows, {42})['every_child_has_one_exit_evidence_receipt'])
        self.assertFalse(exit_evidence_checks([dict(Pid=42)], {42})['every_receipt_explicitly_partial'])
        self.assertFalse(exit_evidence_checks([self.row(coverage='full')], {42})['every_receipt_explicitly_partial'])

    def test_recovery_requires_boolean_and_authoritative_start(self):
        for row in (self.row(retained='true'), self.row(start=0), self.row(retained=False)):
            self.assertFalse(exit_evidence_checks([row], {42})['recovery_matches_authoritative_start'])


if __name__ == '__main__':
    unittest.main()
