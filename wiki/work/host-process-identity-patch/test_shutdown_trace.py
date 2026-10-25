"""Regression guards for read-only final-lifetime reconstruction."""
import datetime as dt
import unittest
from trace_r6_shutdown import final_lifetime_contains_files


class FinalLifetimeChecksTests(unittest.TestCase):
    birth = 134372938000000000
    start = dt.datetime(1601, 1, 1) + dt.timedelta(microseconds=birth // 10)

    def records(self, start=None, end=True):
        return [(42, 'canonical', start or self.start,
                 self.start + dt.timedelta(seconds=1) if end else None, 'clone')]

    def check(self, records, first=None, last=None, birth=None):
        return final_lifetime_contains_files(records, self.birth if birth is None else birth,
                                             self.birth if first is None else first,
                                             self.birth + 10_000_000 if last is None else last)

    def test_exact_closed_boundaries_pass(self):
        self.assertTrue(self.check(self.records()))

    def test_file_before_birth_after_exit_and_inverted_bounds_fail(self):
        self.assertFalse(self.check(self.records(), first=self.birth - 10))
        self.assertFalse(self.check(self.records(), last=self.birth + 10_000_010))
        self.assertFalse(self.check(self.records(), first=self.birth + 100, last=self.birth))

    def test_missing_open_or_different_birth_is_not_final_evidence(self):
        self.assertFalse(self.check([]))
        self.assertFalse(self.check(self.records(end=False)))
        self.assertFalse(self.check(self.records(start=self.start - dt.timedelta(seconds=1))))
        self.assertFalse(final_lifetime_contains_files(self.records(), None, self.birth, self.birth))


if __name__ == '__main__':
    unittest.main()
