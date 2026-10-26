"""Independent parsing guards; counters do not imply identity resolution."""
import unittest

from package_host_analysis import retry_receipts, retry_configurations


class RetryReceiptTests(unittest.TestCase):
    line = ('[Info] Attribution retry cumulative: stream=File,scheduled=12,'
            'capacity_refused=2,stopped_refused=1,exhausted=3,invoked=12,'
            'callback_errors=0,shutdown_invoked=1,pending=0,high_water=10')

    def test_cumulative_fields_and_stream_preserved(self):
        rows, errors = retry_receipts('other log\n' + self.line)
        self.assertEqual([], errors)
        self.assertEqual(1, len(rows))
        self.assertEqual(('File', 2, 3, 1), (rows[0]['stream'], rows[0]['capacity_refused'],
                                         rows[0]['exhausted'], rows[0]['shutdown_invoked']))

    def test_absence_is_not_zero_receipt(self):
        self.assertEqual(([], []), retry_receipts('no receipt'))

    def test_effective_configuration_is_separate_from_environment_intent(self):
        rows, errors = retry_configurations('[Info] Attribution retry configuration: capacity=4096,max_attempts=10,interval_ms=1000,experimental_capacity=True')
        self.assertEqual([], errors)
        self.assertEqual([dict(capacity=4096, max_attempts=10, interval_ms=1000,
                              experimental_capacity=True)], rows)
        self.assertEqual(([], []), retry_configurations('no receipt'))

    def test_configuration_truncation_is_flagged(self):
        rows, errors = retry_configurations('Attribution retry configuration: capacity=4096,max_attempts=10')
        self.assertEqual([], rows)
        self.assertEqual(1, len(errors))

    def test_invalid_truncated_duplicate_or_negative_fields_are_flagged(self):
        for line in (self.line.rsplit(',', 1)[0], self.line + ',scheduled=0',
                     self.line.replace('pending=0', 'pending=-1'),
                     self.line.replace('invoked=12', 'invoked=oops')):
            rows, errors = retry_receipts(line)
            self.assertEqual([], rows)
            self.assertEqual(1, len(errors))


if __name__ == '__main__':
    unittest.main()
