import unittest
from shutdown_trace_analysis import analyze_shutdown


class ShutdownTraceTests(unittest.TestCase):
    def rows(self):
        return [dict(Stage='serializer-shutdown-begin', Component='tcpconnectionserializer', MonotonicTicks=10),
                dict(Stage='serializer-shutdown-end', Component='tcpconnectionserializer',
                     MonotonicTicks=20, Complete=True, QueueDepth=0),
                dict(Stage='serializer-accepted', Activity='TcpIpSend', RowId=42,
                     MonotonicTicks=21, EventCount=3),
                dict(Stage='serializer-accepted', Activity='TcpIpRecv', RowId=43,
                     MonotonicTicks=22, EventCount=3)]

    def test_complete_empty_drain_then_exact_late_rows_is_demonstrated(self):
        result = analyze_shutdown(self.rows(), True)
        self.assertTrue(result['complete_shutdown_then_late_acceptance'])
        self.assertTrue(result['exact_stranded_rows_are_late'])
        self.assertEqual(result['accepted_without_drain_events'], 6)

    def test_incomplete_or_ambiguous_receipts_do_not_prove_absence(self):
        rows = self.rows()
        for altered, complete in ((rows, False), (rows[1:], True), (rows + [rows[1]], True)):
            result = analyze_shutdown(altered, complete)
            self.assertFalse(result['complete_shutdown_then_late_acceptance'])
            self.assertFalse(result['exact_stranded_rows_are_late'])

    def test_row_key_match_cannot_substitute_for_exact_drain_id(self):
        rows = self.rows() + [dict(Stage='serializer-drained', Activity='TcpIpSend', RowId=99)]
        self.assertEqual(analyze_shutdown(rows, True)['accepted_without_drain_events'], 6)
        rows[-1]['RowId'] = 42
        result = analyze_shutdown(rows, True)
        self.assertEqual(result['accepted_without_drain_events'], 3)
        self.assertFalse(result['exact_stranded_rows_are_late'])

    def test_terminal_barrier_horizon_and_callback_join_order_fail_closed(self):
        rows = self.rows()[:2]
        rows += [dict(Stage=stage, Component='etl', MonotonicTicks=ticks, QueueDepth=clock) for stage, ticks, clock in
                 [('esper-shutdown-clock-freeze-begin', 1, -1), ('esper-shutdown-clock-frozen', 2, 12345),
                  ('esper-shutdown-window-advance-begin', 3, 22345), ('esper-shutdown-window-advance-end', 4, 22345),
                  ('esper-shutdown-callbacks-quiesced', 6, -1)]]
        rows += [dict(Stage='serializer-callbacks-joined', Component='tcpconnectionserializer',
                      ActiveCallbacks=0, MonotonicTicks=5)]
        rows[1]['ActiveCallbacks'] = 0
        result = analyze_shutdown(rows, True)
        self.assertTrue(result['barrier_order_and_horizon_qualified'])
        self.assertTrue(result['all_serializers_quiesced_before_drain'])
        self.assertTrue(result['shutdown_complete_and_no_late_acceptance'])
        rows[5]['QueueDepth'] = 22346
        self.assertFalse(analyze_shutdown(rows, True)['barrier_order_and_horizon_qualified'])
        rows[-1]['MonotonicTicks'] = 11
        self.assertFalse(analyze_shutdown(rows, True)['all_serializers_quiesced_before_drain'])


if __name__ == '__main__':
    unittest.main()
