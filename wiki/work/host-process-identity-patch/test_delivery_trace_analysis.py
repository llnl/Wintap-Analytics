import json
from pathlib import Path
import tempfile
import unittest

from delivery_trace_analysis import load_trace, file_totals, compare_multisets, file_row_key
from collections import Counter


class DeliveryTraceTests(unittest.TestCase):
    def trace(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'trace.jsonl'
            path.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
            return load_trace(path)

    def summary(self):
        return dict(Kind='summary', RuleVersion='attribution-trace-v2', Counts=dict(
            Accepted=1, Written=1, Refused=0, ByteRefused=0, Errors=0,
            DiscardedOnError=0, Truncated=0, Closed=True))

    def test_clean_scoped_observer_is_not_native_or_durable_proof(self):
        _, result = self.trace([dict(Sequence=1), self.summary()])
        self.assertTrue(result['scoped_observer_complete'])
        self.assertFalse(result['native_producer_complete'])
        self.assertFalse(result['durable_fate_proven_by_summary'])

    def test_any_drop_error_truncation_or_missing_summary_blocks_completeness(self):
        for field in ['Refused', 'ByteRefused', 'Errors', 'DiscardedOnError', 'Truncated']:
            summary = self.summary(); summary['Counts'][field] = 1
            _, result = self.trace([dict(Sequence=1), summary])
            self.assertFalse(result['scoped_observer_complete'], field)
        _, result = self.trace([dict(Sequence=1)])
        self.assertFalse(result['scoped_observer_complete'])

    def test_duplicated_sequence_or_nonterminal_summary_is_not_complete(self):
        summary = self.summary(); summary['Counts'].update(Accepted=2, Written=2)
        for rows in [[dict(Sequence=1), dict(Sequence=1), summary],
                     [dict(Sequence=1), self.summary(), dict(Sequence=2)]]:
            self.assertFalse(self.trace(rows)[1]['scoped_observer_complete'])

    def test_multiset_preserves_counter_changes_and_duplicate_rows(self):
        row = dict(Pid=42, PidHash='canonical', Path='/proof/file', Activity='Write',
            EventCount=7, BytesRequested=12, FirstSeenEventTime=133000000000000001,
            LastSeenEventTime=133000000000000009)
        expected = Counter([file_row_key(row)])
        altered = dict(row, EventCount=6)
        self.assertFalse(compare_multisets(expected, Counter([file_row_key(altered)]))['equal'])
        self.assertFalse(compare_multisets(expected, Counter([file_row_key(row)] * 2))['equal'])

    def test_folding_compares_event_totals_not_number_of_receipts(self):
        base = dict(Pid=42, PidHash='canonical', Path='/proof/file', Activity='Write')
        rows = [dict(base, Stage='producer', EventCount=1) for _ in range(7)]
        rows.append(dict(base, Stage='summary', EventCount=7))
        self.assertEqual(file_totals(rows, 'producer'), file_totals(rows, 'summary'))

    def test_sequence_gap_without_reported_refusal_is_incomplete(self):
        self.assertFalse(self.trace([dict(Sequence=2), self.summary()])[1]['scoped_observer_complete'])

    def test_successful_late_attribution_preserves_counts_but_changes_snapshot_identity(self):
        base = dict(Pid=42, Path='/proof/file', Activity='Write', EventCount=1)
        rows = [dict(base, Stage='sender', PidHash=''), dict(base, Stage='esper', PidHash='canonical')]
        self.assertEqual(file_totals(rows, 'sender', False), file_totals(rows, 'esper', False))
        self.assertNotEqual(file_totals(rows, 'sender'), file_totals(rows, 'esper'))


if __name__ == '__main__':
    unittest.main()
