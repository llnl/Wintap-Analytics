import unittest
import tempfile
from pathlib import Path
import sys
import duckdb
from pressure_endpoint_analysis import capture_filetime, read_pressure_rows

sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'wintap/devtools'))
from network_endpoint_smoke_test import read_rows, validate_rows


class PressureReceiptScopeTests(unittest.TestCase):
    def test_capture_time_conversion_stays_integer(self):
        self.assertEqual(capture_filetime(1792883423669544893),134373570236695448)
        self.assertEqual(capture_filetime(100),116444736000000001)
        self.assertEqual(capture_filetime(-1),116444735999999999)

    def test_floating_receipts_are_not_accepted(self):
        with self.assertRaises(ValueError):
            capture_filetime(1.1)

    def test_delayed_receive_time_is_not_mistaken_for_missing_tcp(self):
        temp='/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode'
        with tempfile.TemporaryDirectory(dir=temp) as directory:
            raw=Path(directory); folder=raw/'raw_process_conn_incr'; folder.mkdir()
            with duckdb.connect() as c:
                c.sql('''select PID,PidHash,IpEvent,LocalPort,RemotePort,SourcePort,DestinationPort,
                    3221225985::ubigint LocalIpAddr,3221225985::ubigint RemoteIpAddr,
                    116444736040000000::bigint FirstSeenMs
                    from (values (1,'a','TcpIpSend',1234,5678,1234,5678),
                        (1,'a','TcpIpRecv',1234,5678,5678,1234),
                        (2,'b','TcpIpSend',5678,1234,5678,1234),
                        (2,'b','TcpIpRecv',5678,1234,1234,5678))
                    t(PID,PidHash,IpEvent,LocalPort,RemotePort,SourcePort,DestinationPort)''').write_parquet(str(folder/'fixture.parquet'))
            selector=dict(case='delayed',pids=[1,2],ports=[1234,5678],
                startedAtUtc='1970-01-01T00:00:00+00:00',completedAtUtc='1970-01-01T00:00:01+00:00',
                endpointExpectations=[dict(role=role,pid=pid,localIp='192.0.2.1',remoteIp='192.0.2.1',
                    localPort=local,remotePort=remote) for role,pid,local,remote in
                    [('server',1,1234,5678),('client',2,5678,1234)]])
            narrow,error=read_rows(raw,[selector]); self.assertIsNone(error)
            self.assertEqual(narrow,[])
            rows,error=read_pressure_rows(raw,[selector],dict(clock_start={'unix_ns':0},clock_end={'unix_ns':10_000_000_000}))
            self.assertIsNone(error)
            self.assertEqual(validate_rows(rows,selector)['status'],'passed')
            rows,error=read_pressure_rows(raw,[selector],dict(clock_start={'unix_ns':0},clock_end={'unix_ns':3_000_000_000}))
            self.assertEqual(rows,[]) # Capture scope still excludes genuinely outside receipts.
