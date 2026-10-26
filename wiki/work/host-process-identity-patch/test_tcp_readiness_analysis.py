import unittest

from tcp_readiness_analysis import analyze_readiness


class ReadinessAnalysisTests(unittest.TestCase):
    def rows(self):
        queries = [dict(Stage=stage, Serializer='tcpconnectionserializer', QueryPath='tcp.epl',
                        QueryName='one', MonotonicTicks=ticks)
                   for stage, ticks in [('query-registration-begin', 20), ('query-deployed', 30),
                                        ('query-listener-attached', 40), ('query-registration-complete', 50)]]
        events = []
        for event, begin, end in [(1, 10, 19), (2, 19, 21), (3, 51, 52)]:
            for stage, ticks in [('tcp-esper-call', begin), ('esper-return', end)]:
                events.append(dict(Stage=stage, EventId=event, MonotonicTicks=ticks, Stream='TcpConnection',
                    Pid=42, PidHash='canonical', Activity='TcpIpSend', SourceAddress='a', SourcePort=22,
                    DestinationAddress='b', DestinationPort=62000))
        return queries + events

    def test_strict_brackets_do_not_fabricate_missing_aggregate_inputs(self):
        result = analyze_readiness(self.rows(), True)
        self.assertEqual(result['handoff_bands'], {'before-registration': 1,
            'registration-overlap': 1, 'after-listener-ready': 1})
        self.assertTrue(result['absence_interpretable'])
        self.assertFalse(result['historical_failure_resolved'])

    def test_incomplete_history_never_qualifies_absence(self):
        result = analyze_readiness(self.rows(), False)
        self.assertEqual(result['handoff_bands'], {'unclassified': 3})
        self.assertFalse(result['absence_interpretable'])

    def test_missing_repeated_and_out_of_order_registration_fail_closed(self):
        rows = self.rows()
        for altered in (rows[1:], rows + [rows[0]],
                        [dict(rows[0], MonotonicTicks=100)] + rows[1:]):
            result = analyze_readiness(altered, True)
            self.assertFalse(result['registration_receipts_qualified'])

    def test_missing_or_duplicate_handoff_is_not_a_complete_bracket(self):
        rows = self.rows()
        for altered in (rows[:4] + rows[5:], rows + [rows[4]]):
            result = analyze_readiness(altered, True)
            self.assertFalse(result['handoff_brackets_complete'])
            self.assertFalse(result['absence_interpretable'])

    def test_callback_initialization_receipt_has_no_query_path(self):
        rows = self.rows() + [dict(Stage='tcp-callback-initialized', Serializer='tcpconnectionserializer',
                                  QueryPath=None, QueryName=None, MonotonicTicks=60)]
        result = analyze_readiness(rows, True)
        self.assertTrue(result['registration_receipts_qualified'])
        self.assertEqual(len(result['callback_initialization_receipts']), 1)

    def test_startup_order_requires_initialized_callbacks_and_no_early_handoffs(self):
        rows = self.rows()[:4]  # No producer events yet.
        rows += [dict(Stage=stage, MonotonicTicks=ticks) for stage, ticks in
                 [('tcp-callback-initialized', 60), ('etl-callbacks-ready', 70),
                  ('etl-readiness-passed', 80), ('collector-start-call', 90)]]
        self.assertTrue(analyze_readiness(rows, True)['collector_start_after_etl_callbacks'])
        self.assertFalse(analyze_readiness(rows[:-1], True)['collector_start_after_etl_callbacks'])
        rows[-1]['MonotonicTicks'] = 65
        self.assertFalse(analyze_readiness(rows, True)['collector_start_after_etl_callbacks'])

    def test_projection_links_are_exact_ids_not_just_matching_keys(self):
        rows = self.rows()
        base = dict(ProjectionId=100, Pid=42, PidHash='canonical', Activity='TcpIpSend',
            SourceAddress='a', SourcePort=22, DestinationAddress='b', DestinationPort=62000,
            Stream='TcpConnection', EventCount=3)
        rows += [dict(base, Stage='tcp-projection-enter'),
                 dict(base, Stage='tcp-projection-row-ready', RowId=200),
                 dict(base, Stage='tcp-projection-return', RowId=200),
                 dict(base, Stage='serializer-accepted', RowId=201, Stream='PROCESS_CONN_INCR')]
        # Serializer receipts do not carry ProjectionId.
        rows[-1].pop('ProjectionId')
        result = analyze_readiness(rows, True)
        self.assertTrue(result['projection_terminal_receipts_complete'])
        self.assertFalse(result['exact_projection_row_ids_vs_acceptance']['equal'])
        self.assertTrue(result['stage_count_joins']['tcp-projection-row-ready -> serializer-accepted']['equal'])


if __name__ == '__main__':
    unittest.main()
