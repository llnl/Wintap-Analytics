"""Opt-in real HTTP/S3 transport with synthetic objects, not a Garage acceptance test."""
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit
from xml.sax.saxutils import escape
from unittest.mock import patch

import duckdb

from queries import evaluate_run, load_manifests, prepare_data, quote
from page_views import materialize_run
from s3_source import discover_files, open_source
from test_durable import publish


@unittest.skipUnless(os.environ.get("SMOKE_S3_HTTP_TEST") == "1", "Opt in to loopback HTTP test with cached httpfs")
class HTTPSourceTest(unittest.TestCase):
    def test_real_signed_client_listing_and_duckdb_range_reads_are_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = dict(smokeManifestVersion=1, test="file-capture", runId="http-fixture",
                       host={"hostname": "vm-fixture"}, status="passed",
                       startedAtUtc="2026-10-25T12:00:00Z", completedAtUtc="2026-10-25T12:00:02Z",
                       smokeEvidenceRevision=2, smokeEvidencePhase="finished",
                       selectors=[dict(domain="file", pids=[42], paths=["/fixture/file"], expectedActivities=["Open"])])
            import datetime as dt
            evidence = publish(run, root, 2, "finished", dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
            telemetry = root / "telemetry.parquet"
            with duckdb.connect(":memory:") as con:
                con.execute(f"COPY (SELECT 'vm-fixture' Hostname, 42 PID, TIMESTAMP '2026-10-25 12:00:01' EventTime, '/fixture/file' File_Path, 'Open' ActivityType) TO {quote(telemetry)} (FORMAT PARQUET)")
            objects = {"run/" + evidence.relative_to(root).as_posix(): evidence.read_bytes(),
                       "run/raw_sensor/raw_process_file/dayPK=20261025/hourPK=12/events.parquet": telemetry.read_bytes()}
            methods = []

            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass

                def do_HEAD(self):
                    self.respond(True)

                def do_GET(self):
                    self.respond(False)

                def respond(self, head):
                    methods.append(self.command)
                    parsed = urlsplit(self.path)
                    query = parse_qs(parsed.query)
                    if query.get("list-type") == ["2"]:
                        prefix = query.get("prefix", [""])[0]
                        keys = sorted(k for k in objects if k.startswith(prefix))
                        entries = []
                        if query.get("delimiter"):
                            prefixes = sorted({prefix + k[len(prefix):].split("/")[0] + "/" for k in keys})
                            entries = [f"<CommonPrefixes><Prefix>{escape(p)}</Prefix></CommonPrefixes>" for p in prefixes]
                        else:
                            entries = [f"<Contents><Key>{escape(k)}</Key><Size>{len(objects[k])}</Size></Contents>" for k in keys]
                        body = ("<ListBucketResult xmlns='http://s3.amazonaws.com/doc/2006-03-01/'>"
                                "<Name>fixture-bucket</Name><IsTruncated>false</IsTruncated>" + "".join(entries) + "</ListBucketResult>").encode()
                        self.send_response(200)
                        self.send_header("Content-Type", "application/xml")
                    else:
                        key = unquote(parsed.path).removeprefix("/fixture-bucket/")
                        if key not in objects:
                            self.send_error(404)
                            return
                        body = objects[key]
                        total = len(body)
                        byte_range = self.headers.get("Range")
                        if byte_range and not head:
                            start, end = byte_range.removeprefix("bytes=").split("-")
                            first, last = int(start), int(end) if end else total - 1
                            body = body[first:last + 1]
                            self.send_response(206)
                            self.send_header("Content-Range", f"bytes {first}-{last}/{total}")
                        else:
                            self.send_response(200)
                        self.send_header("Accept-Ranges", "bytes")
                        self.send_header("ETag", '"synthetic-fixture"')
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    if not head:
                        self.wfile.write(body)

            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                config = dict(endpoint=f"http://127.0.0.1:{server.server_port}", region="us-east-1",
                              datasets=["s3://fixture-bucket/run"], max_files=100)
                env = dict(AWS_ACCESS_KEY_ID="synthetic-key", AWS_SECRET_ACCESS_KEY="synthetic-secret",
                           AWS_SESSION_TOKEN="synthetic-token", AWS_EC2_METADATA_DISABLED="true", AWS_PROFILE="")
                # Remove AWS_PROFILE rather than selecting an empty named profile.
                with patch.dict(os.environ, env):
                    os.environ.pop("AWS_PROFILE", None)
                    con, client = open_source(config)
                    try:
                        evidence_files, telemetry_files = discover_files(client, config, "20261025", "20261025")
                        runs, errors = load_manifests("", connection=con, evidence_files=evidence_files)
                        self.assertFalse(errors)
                        self.assertEqual(len(runs), 1)
                        _, errors, available = prepare_data(con, "", telemetry_files=telemetry_files)
                        self.assertFalse(errors)
                        before = evaluate_run(con, runs[0], available)
                        materialize_run(con, runs[0], 15)
                        self.assertEqual(evaluate_run(con, runs[0], available), before)
                        self.assertEqual(before["state"], "green")
                        plan = con.execute('EXPLAIN SELECT * FROM smoke_data').fetchall()[-1][-1]
                        self.assertNotIn('READ_PARQUET', plan)
                    finally:
                        con.close()
                self.assertTrue(methods)
                self.assertTrue(set(methods) <= {"GET", "HEAD"})
            finally:
                server.shutdown()
                server.server_close()
                thread.join(5)


if __name__ == "__main__":
    unittest.main()
