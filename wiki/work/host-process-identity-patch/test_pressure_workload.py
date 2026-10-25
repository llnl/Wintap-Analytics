import unittest
from pathlib import Path
from pressure_workload import workload, receive


class PressureWorkloadTests(unittest.TestCase):
    def test_unqualified_tier_rejected_before_side_effects(self):
        for count in (0, 1, 512, -1):
            with self.assertRaises(ValueError):
                workload(Path('/uncreated-pressure-root'), count, '192.0.2.1')

    def test_tcp_fragmented_echo_is_counted_exactly(self):
        class Socket:
            def __init__(self):
                self.parts = iter([b'p' * 11, b'p' * 21])
            def recv(self, count):
                return next(self.parts)
        self.assertEqual(receive(Socket(), 32), b'p' * 32)

    def test_incomplete_echo_not_success(self):
        class Socket:
            def recv(self, count):
                return b''
        with self.assertRaises(RuntimeError):
            receive(Socket(), 32)
