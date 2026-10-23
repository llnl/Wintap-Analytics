import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest

import duckdb
from queries import coverage, load_manifests, prepare_data, selector_query, timestamp


class SmokeQueryTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect()
        self.con.execute("SET TimeZone='UTC'")
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run = dict(smokeManifestVersion=1, runId="a", test="file-capture", host={"hostname": "vm-a"},
                        startedAtUtc="2026-10-22T12:00:00+00:00", completedAtUtc="2026-10-22T12:00:02+00:00", selectors=[])

    def tearDown(self):
        self.con.close()
        self.temp.cleanup()

    def parquet(self, name, sql):
        self.con.execute(f"COPY ({sql}) TO '{self.root / name}' (FORMAT PARQUET)")

    def query(self, selector):
        result = self.con.execute(selector_query(self.run, selector, padding=0))
        columns = [r[0] for r in result.description]
        return [dict(zip(columns, r)) for r in result.fetchall()]

    def test_host_pid_path_and_run_time_isolation(self):
        self.parquet("file.parquet", """SELECT * FROM (VALUES
            ('VM-A', 42, 1792670401, '/vm/test/first.bin', 'Open'),
            ('VM-B', 42, 1792670401, '/vm/test/first.bin', 'Write'),
            ('VM-A', 42, 1792670500, '/vm/test/first.bin', 'Delete'),
            ('VM-A', 42, 1792670401, '/other/file.bin', 'Write'))
            t(Hostname, PID, EventTime, File_Path, ActivityType)""")
        self.assertTrue(prepare_data(self.con, self.root)[2])
        rows = self.query(dict(domain="file", pids=[42], pathPrefix="/vm/test/"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["activity"], "open")

    def test_timestamp_formats(self):
        epoch = 1792670401
        for value in (str(epoch), str(epoch * 1000), str(epoch * 1000000),
                      str(epoch * 1000000000), str(epoch * 10000000 + 116444736000000000),
                      "'2026-10-22T12:00:01Z'"):
            actual = self.con.execute("SELECT epoch(" + timestamp(value) + ")").fetchone()[0]
            self.assertAlmostEqual(actual, epoch, places=3)

    def test_direct_host_must_be_explicit_and_mixed_schemas(self):
        self.parquet("process.parquet", "SELECT 'Process' MessageType, 'Start' ActivityType, 42 PID, 134371440010000000 EventTime, 'identity' PidHash")
        self.parquet("network.parquet", "SELECT 'TcpConnection' MessageType, 'TcpIpConnect' ActivityType, 42 PID, TIMESTAMP '2026-10-22 12:00:01' CapturedUtc, 7890 TcpConnection_DestinationPort")
        prepare_data(self.con, self.root)
        self.assertEqual(self.query(dict(domain="process", pids=[42])), [])
        prepare_data(self.con, self.root, "vm-a")
        self.assertEqual(len(self.query(dict(domain="network", pids=[42], ports=[7890]))), 1)
        rows = self.query(dict(domain="process", pids=[42], threadIds=[43]))
        self.assertEqual(len(rows), 1)
        self.assertTrue(all(c["observed"] for c in coverage(rows, dict(domain="process", pids=[42], threadIds=[43], expectedActivities=["Start"]))))

    def test_normal_network_uses_first_seen_and_ip_event(self):
        self.parquet("normal-network.parquet", "SELECT 'VM-A' Hostname, 'TcpConnection' MessageType, 'TcpIpSend' IpEvent, 42 PID, 1792671000 EventTime, 134371440010000000 FirstSeenMs, 80 RemotePort, 'tcp' Protocol, 5 EventCount")
        prepare_data(self.con, self.root)
        rows = self.query(dict(domain="network", pids=[42], ports=[80]))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["event_count"], 5)
        self.assertEqual(rows[0]["activity"], "tcpipsend")

    def test_empty_missing_broken_files(self):
        self.assertEqual(prepare_data(self.con, self.root), (0, [], False))
        (self.root / "broken.parquet").write_text("not parquet")
        count, errors, available = prepare_data(self.con, self.root)
        self.assertEqual(count, 1)
        self.assertTrue(errors)
        self.assertFalse(available)

    def test_uploaded_manifests_do_not_need_vm_paths(self):
        self.run["selectors"] = [dict(domain="file", paths=["/only/on/vm/file.bin"], pids=[42])]
        runs, errors = load_manifests("", [("downloaded.json", json.dumps(self.run).encode())])
        self.assertFalse(errors)
        self.assertEqual(runs[0]["runId"], "a")
        other = dict(self.run, runId="b")
        runs, errors = load_manifests("", [("a.json", json.dumps(self.run).encode()), ("b.json", json.dumps(other).encode())])
        self.assertEqual(len(runs), 2)
        conflict = dict(self.run, status="failed")
        runs, errors = load_manifests("", [("a.json", json.dumps(self.run).encode()), ("conflict.json", json.dumps(conflict).encode())])
        self.assertFalse(runs)
        self.assertTrue(errors)

    def test_host_receipt_run_id_exact_match(self):
        value = json.dumps({"captureRunId": "receipt-1"})
        self.parquet("host.parquet", f"SELECT 'VM-A' Hostname, '{value}' RuntimeCapabilitiesJson")
        prepare_data(self.con, self.root)
        self.assertEqual(len(self.query(dict(domain="host", captureRunId="receipt-1"))), 1)
        self.assertEqual(len(self.query(dict(domain="host", captureRunId="receipt-2"))), 0)

    def test_exported_aggregate_file_schema(self):
        self.parquet("file-etl.parquet", "SELECT 'VM-A' Hostname, 'PROCESS_FILE' MessageType, 42 PID, 1792671000 EventTime, 134371440010000000 FirstSeen, '/vm/file.bin' File_Path, 'Read' ActivityType, 2 EventCount")
        prepare_data(self.con, self.root)
        rows = self.query(dict(domain="file", pids=[42], paths=["/vm/file.bin"]))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["activity"], "read")

    def test_apostrophes_in_file_paths_are_values_not_sql(self):
        self.parquet("file.parquet", "SELECT 'VM-A' Hostname, 42 PID, 1792670401 EventTime, '/vm/it''s.bin' File_Path, 'Open' ActivityType")
        prepare_data(self.con, self.root)
        self.assertEqual(len(self.query(dict(domain="file", pids=[42], paths=["/vm/it's.bin"]))), 1)


if __name__ == "__main__":
    unittest.main()
