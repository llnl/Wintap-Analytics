"""Offline utility regressions, not live Python/Go acceptance evidence."""

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import fields
import importlib.util
import io
import json
from pathlib import Path
import shutil
import struct
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import evidence
import capture_python


REPO = Path(__file__).resolve().parents[2]


def load_collector():
    source = REPO.parent / "Lintap" / "pidstat-collector.py"
    spec = importlib.util.spec_from_file_location("offline_pidstat_reference", source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, source


def elf(machine, segment=1, dynamic_tag=0):
    header = struct.pack("<16sHHIQQQIHHHHHH", b"\x7fELF\x02\x01" + b"\0" * 10,
                         2, machine, 1, 4096, 64, 0, 0, 64, 56, 1, 0, 0, 0)
    return header + struct.pack("<IIQQQQQQ", segment, 5, 120, 0, 0, 16, 16, 8) + struct.pack("<qQ", dynamic_tag, 0)


class UtilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pidstat-utility-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def row(self, **changes):
        return dict(time="2026-10-30T12:00:00", uid=0, pid=10, hostname="test",
                    partition=["dayPK=20261030", "hourPK=12"], window_start_epoch=300,
                    cpu_percent=125.0, container_id=None, **changes)

    def test_exact_multiset_and_order(self):
        a, b = self.row(), self.row(command="worker")
        self.assertTrue(evidence.compare_rows([a, b, a], [a, a, b])["equal"])

    def test_duplicate_missing_identifies_correct_row(self):
        a, b = self.row(), self.row(command="worker")
        result = evidence.compare_rows([a, b], [b])
        self.assertFalse(result["equal"])
        self.assertEqual(result["unmatched_python"], [a])
        self.assertEqual(evidence.compare_rows([a], [a, a])["unmatched_candidate"], [a])

    def test_each_column_difference_and_max_error(self):
        a = self.row()
        for name in evidence.COLUMNS:
            b = dict(a, **{name: "changed"})
            result = evidence.compare_rows([a], [b])
            self.assertFalse(result["equal"], name)
            if name not in evidence.KEY:
                self.assertEqual(result["columns"][name]["mismatches"], 1, name)
        result = evidence.compare_rows([a], [dict(a, cpu_percent=130.0)])
        self.assertEqual(result["columns"]["cpu_percent"]["max_absolute_error"], 5)

    def test_partition_window_and_null_changes(self):
        a = self.row()
        for changes in ({"partition": ["dayPK=20261030", "hourPK=13"]},
                        {"window_start_epoch": 600}, {"container_id": ""}):
            self.assertFalse(evidence.compare_rows([a], [dict(a, **changes)])["equal"])

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            evidence.value_json(float("nan"))

    def test_elf_both_architectures(self):
        for machine in (183, 62):
            path = self.root / str(machine)
            path.write_bytes(elf(machine))
            self.assertEqual(evidence.inspect_elf(path, machine)["machine"], machine)

    def test_elf_dynamic_wrong_architecture_and_truncation(self):
        path = self.root / "binary"
        for data in (elf(62), elf(183, 3), elf(183, 2, 1), elf(183)[:100], b"not ELF"):
            path.write_bytes(data)
            with self.assertRaises(ValueError):
                evidence.inspect_elf(path, 183)

    def test_archive_safety_and_normalized_duplicates(self):
        for index, names in enumerate((["../escape"], ["/absolute"], ["safe", "./safe"], ["link"])):
            archive = self.root / f"archive{index}.tar"
            with tarfile.open(archive, "w") as tar:
                for name in names:
                    member = tarfile.TarInfo(name)
                    if name == "link":
                        member.type = tarfile.SYMTYPE
                        member.linkname = "outside"
                    tar.addfile(member, io.BytesIO())
            with self.assertRaises(ValueError):
                evidence.extract_reference(archive, self.root / f"out{index}")
        self.assertFalse((self.root / "escape").exists())

    def test_command_exit_timeout_and_missing_executable(self):
        recorder = evidence.Recorder(self.root)
        good = recorder.run([sys.executable, "-c", "print('observed')"])
        self.assertEqual(good["returncode"], 0)
        self.assertEqual(Path(good["stdout"]).read_text().strip(), "observed")
        self.assertEqual(recorder.run([sys.executable, "-c", "raise SystemExit(7)"])["returncode"], 7)
        self.assertEqual(recorder.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.05)["returncode"], -1)
        self.assertEqual(recorder.run([str(self.root / "absent")])["returncode"], -1)

    def test_missing_evidence_and_database_errors_record_incomplete(self):
        with redirect_stdout(io.StringIO()):
            code = evidence.main(["--output", str(self.root / "missing"), "compare",
                                  "--reference", str(self.root / "absent"), "--candidate", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads((self.root / "missing/result.json").read_text())["status"], "INCOMPLETE")
        with patch.object(evidence, "compare", side_effect=RuntimeError("database error")), redirect_stdout(io.StringIO()):
            code = evidence.main(["--output", str(self.root / "error"), "compare",
                                  "--reference", str(self.root), "--candidate", str(self.root)])
        self.assertEqual(code, 2)
        self.assertIn("database error", (self.root / "error/result.json").read_text())

    def test_record_failure_and_existing_output_not_overwritten(self):
        with redirect_stdout(io.StringIO()):
            code = evidence.main(["--output", str(self.root / "record"), "record", "--",
                                  sys.executable, "-c", "raise SystemExit(3)"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads((self.root / "record/result.json").read_text())["status"], "FAIL")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                evidence.main(["--output", str(self.root / "record"), "static", "--arm64", "x", "--amd64", "y"])

    def test_smoke_hash_mismatch_never_starts_binary(self):
        binary = self.root / "arm64"
        binary.write_bytes(elf(183))
        def fake_run(recorder, argv, *args, **kwargs):
            path = recorder.output / "hash.stdout"
            path.write_text("bad-hash  /guest/binary\n")
            return {"returncode": 0, "stdout": str(path)}
        with patch.object(evidence.Recorder, "run", autospec=True, side_effect=fake_run) as run, redirect_stdout(io.StringIO()):
            code = evidence.main(["--output", str(self.root / "smoke"), "smoke",
                                  "--host-binary", str(binary), "--guest-binary", "/guest/binary"])
        self.assertEqual(code, 1)
        self.assertEqual(run.call_count, 1)


class PythonWriterTests(unittest.TestCase):
    """Actual source writer, controlled rows; NOT actual /proc or Go parity."""

    def setUp(self):
        UtilityTests.setUp(self)
        try:
            import duckdb
            self.module, self.source = load_collector()
        except (ImportError, FileNotFoundError):
            self.skipTest("requires existing DuckDB and live Lintap checkout")
        values = {field.name: 0 for field in fields(self.module.SampleRow)}
        values.update(date_col="2026-10-30", sample_time="12:00:00", uid=0, pid=10,
                      cpu_percent=125.125, command="worker", hostname="test",
                      cgroup_path="/", pid_ns_inode=None, container_runtime=None, container_id=None)
        self.reference = self.root / "reference"
        self.reference.mkdir()
        config = self.module.Config(data_root=self.reference / "data", interval_sec=5,
            rotate_interval_sec=300, min_rotate_interval_sec=300, parquet_root=self.reference / "data",
            spool_dir=self.reference / "runtime", parquet_compression="ZSTD", duckdb_threads=1,
            max_unshipped_bytes=0, max_unshipped_age_sec=0, hostname="test")
        collector = self.module.Collector(config, sampler=object())
        row = self.module.SampleRow(**values)
        try:
            collector.initialize_current_window(1793361600)
            collector.append_rows([row, row])
            collector.seal_current_spool()
            collector.process_pending_spools()
        finally:
            collector.close()
        # Fixture manifest exercises validation mechanics only. Its proc data is
        # deliberately empty and must never be presented as live acceptance evidence.
        (self.reference / "capture.json").write_text('{"offline_fixture": true}\n')
        (self.reference / "golden.tsv").write_text((row.to_tsv() + "\n") * 2)
        files = [self.reference / "capture.json", self.reference / "golden.tsv"] + list((self.reference / "data").rglob("*.parquet"))
        self.manifest = {"kind": "actual-python-proc-reference", "source_sha256": evidence.sha(self.source),
                         "rows": 2, "sample_count": 2,
                         "files": {str(p.relative_to(self.reference)): evidence.sha(p) for p in files}}
        evidence.write(self.reference / "reference.json", self.manifest)
        self.candidate = self.root / "candidate"
        shutil.copytree(self.reference / "data", self.candidate)
        self.output = self.root / "report"
        self.output.mkdir()

    def tearDown(self):
        UtilityTests.tearDown(self)

    def test_actual_python_writer_read_compare(self):
        passed, report = evidence.compare(self.reference, self.candidate, self.output)
        self.assertTrue(passed)
        self.assertEqual(report["python_rows"], 2)
        self.assertTrue(report["schemas_equal"])
        self.assertEqual(len(report["python_schema"][0]["columns"]), 26)

    def test_manifest_hash_and_file_set(self):
        extra = self.reference / "data/extra.parquet"
        extra.write_bytes(b"extra")
        with self.assertRaises(ValueError):
            evidence.validate_reference(self.reference)
        extra.unlink()
        (self.reference / "golden.tsv").write_text("tampered")
        with self.assertRaises(ValueError):
            evidence.validate_reference(self.reference)

    def test_partition_window_and_collision_filename(self):
        file = next(self.candidate.rglob("*.parquet"))
        file.rename(file.with_name(file.stem + "-123-456.parquet"))
        self.assertTrue(evidence.compare(self.reference, self.candidate, self.output)[0])
        file = next(self.candidate.rglob("*.parquet"))
        file.rename(file.with_name("test+pidstat+1793361900.parquet"))
        self.assertFalse(evidence.compare(self.reference, self.candidate, self.output)[0])

    def test_double_schema_drift_and_missing_column(self):
        import duckdb
        file = next(self.candidate.rglob("*.parquet"))
        for selection in ("* REPLACE (CAST(cpu_percent AS DOUBLE) AS cpu_percent)", "* EXCLUDE (container_id)"):
            with duckdb.connect() as db:
                db.execute("CREATE TABLE fixture AS SELECT * FROM read_parquet(?)", [str(next((self.reference / "data").rglob("*.parquet")))])
                file.unlink()
                db.execute(f"COPY (SELECT {selection} FROM fixture) TO '{file}' (FORMAT PARQUET)")
            self.assertFalse(evidence.compare(self.reference, self.candidate, self.output)[0])

    def test_corrupt_parquet_and_missing_partition(self):
        file = next(self.candidate.rglob("*.parquet"))
        moved = self.root / file.name
        shutil.copyfile(file, moved)
        with self.assertRaises(ValueError):
            evidence.read_dataset(moved)
        file.write_bytes(b"not parquet")
        with self.assertRaises(Exception):
            evidence.compare(self.reference, self.candidate, self.output)

    def test_capture_rejects_host_before_creating_output(self):
        with patch.object(capture_python.platform, "system", return_value="Darwin"):
            with self.assertRaises(RuntimeError):
                capture_python.capture(self.source, self.root / "capture", 2, 1)
        self.assertFalse((self.root / "capture").exists())

    def test_capture_helper_with_actual_sampler_writer_and_simulated_proc(self):
        proc = self.root / "proc"
        process = proc / "10"
        process.mkdir(parents=True)
        (proc / "meminfo").write_text("MemTotal: 1000000 kB\n")
        stat = ["0"] * 41
        stat[0], stat[19], stat[20], stat[21] = "S", "100", "4096", "1"
        (process / "stat").write_text("10 (worker) " + " ".join(stat))
        (process / "status").write_text("Uid: 0\nvoluntary_ctxt_switches: 0\nnonvoluntary_ctxt_switches: 0\n")
        (process / "cgroup").write_text("0::/\n")
        spec = importlib.util.spec_from_file_location("captured_fixture_reference", self.source)
        original_loader = spec.loader
        class FixtureLoader:
            def create_module(self, spec):
                return None
            def exec_module(self, module):
                original_loader.exec_module(module)
                sampler = module.ProcSampler
                module.ProcSampler = lambda hostname: sampler(hostname, proc_root=proc)
        spec.loader = FixtureLoader()
        original_read = Path.read_text
        def read_text(path, *args, **kwargs):
            return 'ID=ubuntu\n' if str(path) == "/etc/os-release" else original_read(path, *args, **kwargs)
        original_scandir, original_link = capture_python.os.scandir, capture_python.os.readlink
        output = self.root / "captured-fixture"
        with patch.object(capture_python.importlib.util, "spec_from_file_location", return_value=spec), \
             patch.object(capture_python.platform, "system", return_value="Linux"), \
             patch.object(capture_python.platform, "machine", return_value="aarch64"), \
             patch.object(Path, "read_text", read_text), \
             patch.object(capture_python.time, "sleep"), \
             patch.object(capture_python.time, "time", return_value=1793386800):
            manifest = capture_python.capture(self.source, output, 2, 1)
        self.assertEqual(manifest["rows"], 1)
        self.assertIs(capture_python.os.scandir, original_scandir)
        self.assertIs(capture_python.os.readlink, original_link)
        evidence.extract_reference(output / "reference.tar", self.root / "extracted")
        self.assertEqual(evidence.validate_reference(self.root / "extracted")["rows"], 1)
        captured = json.loads((output / "capture.json").read_text())
        self.assertEqual(len(captured["samples"]), 2)
        self.assertEqual(captured["samples"][0]["output_rows"], 0)
        self.assertIn(str(process / "stat"), captured["samples"][0]["reads"])


if __name__ == "__main__":
    unittest.main()
