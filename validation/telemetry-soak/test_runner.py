"""Portable orchestration tests with fake Linux tools; no sensors/network involved."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.devtools = self.root / "devtools with spaces"
        self.devtools.mkdir()
        self.python = self.bin / "test-python"
        self.tool("uname", "#!/bin/bash\necho Linux\n")
        self.tool("flock", '#!/bin/bash\nexit "${LOCK_FAIL:-0}"\n')
        self.tool("timeout", '#!/bin/bash\nshift 3\nexec "$@"\n')
        self.tool("sleep", "#!/bin/bash\nexit 0\n")
        self.tool("realpath", """#!/usr/bin/env python3
import sys
from pathlib import Path
print(Path([a for a in sys.argv[1:] if a not in ('--', '-m')][0]).resolve())
""")
        self.tool("test-python", """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
if sys.argv[1] == '-':
    source = sys.stdin.read()
    if 'import duckdb' in source:
        raise SystemExit(int(os.environ.get('PREFLIGHT_FAIL', '0')))
    sys.argv = sys.argv[1:]
    exec(compile(source, '<stdin>', 'exec'))
else:
    args = sys.argv
    path = Path(args[args.index('--manifest') + 1])
    path.write_text(json.dumps(dict(completedAtUtc='fixture', selectors=[{}],
        durableExportError='fixture' if os.environ.get('EXPORT_FAIL') else None)))
    if path.stem == 'named' and os.environ.get('FAIL_NAMED'):
        raise SystemExit(1)
""")
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"])

    def tool(self, name, text):
        path = self.bin / name
        path.write_text(text)
        path.chmod(0o755)

    def run_runner(self, extra=(), **env):
        return subprocess.run([
            "bash", str(HERE / "run-smoke-soak.sh"),
            "--python", str(self.python), "--devtools", str(self.devtools),
            "--data-root", str(self.root / "data"),
            "--evidence-root", str(self.root / "evidence"),
            "--rounds", "1", *extra,
        ], env=dict(self.env, **env), capture_output=True, text=True, timeout=20)

    def statuses(self):
        return next((self.root / "evidence").glob("session.*/status.tsv")).read_text().splitlines()

    def test_sequential_round_and_private_evidence(self):
        result = self.run_runner()
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = self.statuses()
        self.assertEqual(len(rows), 3)
        self.assertIn("\tnamed\t0\trecorded", rows[1])
        self.assertIn("\tendpoints\t0\trecorded", rows[2])
        self.assertEqual(next((self.root / "evidence").glob("session.*")).stat().st_mode & 0o777, 0o700)

    def test_failure_continues_across_rounds(self):
        result = self.run_runner(["--rounds", "2", "--interval", "1"], FAIL_NAMED="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = self.statuses()
        self.assertEqual(len(rows), 5)
        self.assertIn("\tnamed\t1\t", rows[1])
        self.assertIn("\tendpoints\t0\t", rows[4])

    def test_export_error_is_not_recorded_success(self):
        result = self.run_runner(EXPORT_FAIL="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("export-error", self.statuses()[1])

    def test_lock_refusal(self):
        result = self.run_runner(LOCK_FAIL="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Another runner", result.stderr)

    def test_preflight_failure_before_evidence(self):
        result = self.run_runner(PREFLIGHT_FAIL="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "evidence").exists())

    def test_reject_zero_interval(self):
        self.assertNotEqual(self.run_runner(["--interval", "0"]).returncode, 0)

    def test_reject_invalid_timeout(self):
        self.assertNotEqual(self.run_runner(["--timeout", "-1"]).returncode, 0)

    def test_reject_unknown_option(self):
        self.assertNotEqual(self.run_runner(["--start-lintap"]).returncode, 0)

    def test_reject_repository_evidence(self):
        result = self.run_runner(["--evidence-root", str(HERE / "should-not-be-created")])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside Git", result.stderr)
        self.assertFalse((HERE / "should-not-be-created").exists())

    def test_help(self):
        result = self.run_runner(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("stimuli", result.stdout)

    def test_endpoint_stimulus_records_deferred_selectors_without_queries(self):
        (self.devtools / "smoke_manifest.py").write_text('''
import json
import os
values = {}
def record(**fields):
    values.update(fields)
def smoke_run(name):
    def decorate(function):
        def wrapped():
            result = function()
            values['test'] = name
            with open(os.environ['FIXTURE_RESULT'], 'w') as output:
                json.dump(values, output)
            return result
        return wrapped
    return decorate
''')
        (self.devtools / "network_endpoint_smoke_test.py").write_text('''
def host_address(explicit):
    assert explicit == '192.0.2.10'
    return explicit
def generate_cases(ip):
    return [{'case': 'fixture', 'domain': 'network', 'pids': [123]}]
def read_rows(*args):
    raise AssertionError('Stimulus runner must not query local telemetry')
''')
        output = self.root / "endpoint-fixture.json"
        result = subprocess.run([
            sys.executable, str(HERE / "network-endpoint-stimulus.py"),
            "--devtools", str(self.devtools), "--host-ip", "192.0.2.10",
        ], env=dict(self.env, FIXTURE_RESULT=str(output)), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(output.read_text())
        self.assertTrue(manifest["stimulusOnly"])
        self.assertTrue(manifest["results"]["validationDeferred"])
        self.assertEqual(manifest["test"], "network-endpoints")
        self.assertEqual(len(manifest["selectors"]), 1)


if __name__ == "__main__":
    unittest.main()
