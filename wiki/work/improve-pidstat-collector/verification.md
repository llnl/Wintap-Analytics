---
title: "Verification: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-pidstat-collector/implementation_plan.md
policy: agent-editable
last_validated: 2026-08-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-pidstat-collector/verification.md
tags: [feature-work, verification, lintap, pidstat]
---

# Verification: Improve pidstat Collector

## Slice 2 Completion Note

Slice 2 is complete on branch `grantj-rhel8-testing` across
`Wintap-Analytics/`, `../Lintap`, and `../Wintappy`.

- The bash collector was retired and replaced with a Python `/proc` sampler.
- The collector now writes typed parquet with `hostname` and container
  attribution columns.
- The Wintappy bronze pidstat input was migrated from CSV to parquet.
- Validation passed in `lintap-dev` for pytest, live collector smoke runs, the
  `uv`-managed runtime bootstrap/launcher flow, and DBT fixture/empty-input
  builds.
- Remaining closeout items are operational, not design: package-install/systemd
  verification on a target host, optional live container fixture coverage, and
  the separate upload-delete fix needed for end-to-end S3/delete confirmation.

## Test Commands

Commands are recorded in the order executed.

1. `pwd && ls -la`
Result: repo root confirmed.

2. `ls -la ..`
Result: sibling checkouts present: `../Lintap`, `../wintap`, `../Wintappy`.

3. `command -v pidstat && pidstat -V`
Result: `pidstat` present (`sysstat version 11.7.3`).

4. `command -v duckdb && duckdb --version`
Result: `duckdb` present (`v1.5.5`).

5. `command -v shellcheck && shellcheck --version`
Result: `shellcheck` not found on host.

6. `pidstat -u -d -r -w -h 1 1`
Result: host `pidstat` output included an `AM/PM` token in the time column,
which would misalign the old tab-split CSV loader.

7. `S_TIME_FORMAT=ISO pidstat -u -d -r -w -h 1 1`
Result: `S_TIME_FORMAT=ISO` produced stable `HH:MM:SS` sample times suitable
for deterministic parsing in the new collector.

8. `bash -n ../Lintap/pidstat-collector.sh`
Result: syntax check passed.

9. `bash -n ../Lintap/tests/pidstat-collector-tests.sh`
Result: syntax check passed.

10. `bash ../Lintap/tests/pidstat-collector-tests.sh`
Result: 3 tests passed: parquet conversion into `dayPK=/hourPK=` partitions,
startup salvage of a leftover active spool, and oldest-first byte-cap pruning.

11. `ls -la /tmp/opencode`
Result: temp-work parent confirmed before creating the live smoke-run directory.

12. `chmod +x ../Lintap/pidstat-collector.sh ../Lintap/tests/pidstat-collector-tests.sh`
Result: collector and test harness marked executable.

13. `WINTAP_DATA_ROOT=$(mktemp -d /tmp/opencode/pidstat-smoke.XXXXXX) PIDSTAT_INTERVAL_SEC=1 PIDSTAT_ROTATE_INTERVAL_SEC=2 PIDSTAT_MAX_UNSHIPPED_BYTES=0 timeout --signal=TERM 5 ../Lintap/pidstat-collector.sh`
Result: live smoke run started the collector, captured real `pidstat` output,
and flushed a partitioned parquet file on shutdown; `timeout` interrupted the
follow-up inspection commands, so file inspection ran separately.

14. `duckdb -csv -c "select count(*) as parquet_files from glob('/tmp/opencode/pidstat-smoke.C4I3cw/parquet/raw_sensor/pidstat/**/*.parquet');"`
Result: 1 parquet file present after the live smoke run.

15. `duckdb -csv -c "select count(*) as rows from read_parquet('/tmp/opencode/pidstat-smoke.C4I3cw/parquet/raw_sensor/pidstat/**/*.parquet');"`
Result: 1 live-sampled row loaded successfully from the produced parquet.

16. `bash -n ../Lintap/tests/pidstat-collector-tests.sh`
Result: syntax check passed after adding the max-age accumulation-guard test.

17. `bash ../Lintap/tests/pidstat-collector-tests.sh`
Result: initial 4-test rerun failed; the new age-cap test exposed a bug where
`find -printf '%T@'` produced fractional mtimes that broke integer arithmetic in
`enforce_accumulation_guard`.

18. `bash -n ../Lintap/pidstat-collector.sh`
Result: syntax check passed after normalizing age-guard mtimes to whole seconds.

19. `bash -n ../Lintap/tests/pidstat-collector-tests.sh`
Result: syntax check passed after updating the age-cap test fixture.

20. `bash ../Lintap/tests/pidstat-collector-tests.sh`
Result: final 4-test suite passed: parquet conversion into `dayPK=/hourPK=`
partitions, startup salvage of a leftover active spool, oldest-first byte-cap
pruning, and stale-file age pruning.

21. `ls -la /tmp/opencode`
Result: temp-work parent confirmed before starting the 15-minute collector run.

22. `run_root=$(mktemp -d "/tmp/opencode/pidstat-15m.XXXXXX") && timeout --signal=TERM 905 env WINTAP_DATA_ROOT="$run_root" ../Lintap/pidstat-collector.sh; ... duckdb ...`
Result: 15-minute real collector run completed at `/tmp/opencode/pidstat-15m.U6zwhN`.
The collector produced 4 partitioned parquet files under
`parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=08/` and DuckDB loaded 15
rows across those files.

23. `duckdb -csv -c "select * from read_parquet('/tmp/opencode/pidstat-15m.U6zwhN/parquet/raw_sensor/pidstat/**/*.parquet') limit 25"`
Result: parquet contents were clearly wrong: only one `tmux: server`-style row
per minute, confirming the loss happened before parquet conversion.

24. `timeout --signal=TERM 12 env S_TIME_FORMAT=ISO pidstat -u -d -r -w -h 5 > "$tmp"` and `... -p ALL 5 > "$tmp"`
Result: raw non-interactive `pidstat` output itself was healthy (hundreds to
thousands of lines in ~10 seconds), so the undercount was in the collector's
parser, not `pidstat` or DuckDB.

25. `source ../Lintap/pidstat-collector.sh; ... normalize_pidstat_line ...`
Result: isolated repro showed the parser was splitting fields incorrectly and
accepted only rows whose `Command` column contained spaces.

26. `bash ../Lintap/tests/pidstat-collector-tests.sh`
Result: after fixing `normalize_pidstat_line` to use explicit whitespace
splitting and the correct field indexes, the test suite passed with 5 tests,
including a regression test for loop-IFS parsing.

27. `timeout --signal=TERM 16 env WINTAP_DATA_ROOT=/tmp/opencode/pidstat-fixcheck.YwrUoU ../Lintap/pidstat-collector.sh`
Result: post-fix end-to-end smoke run produced 1 parquet file with 307 rows in
~16 seconds, confirming that detailed per-process rows are now retained.

28. `bash ../Lintap/tests/pidstat-collector-tests.sh`
Result: after adding a deterministic joined-record regression test and a live
row-preservation validation, the suite passed with 7 tests total.

29. `timeout --signal=TERM 905 env WINTAP_DATA_ROOT=/tmp/opencode/pidstat-15m-clean.dyb7fq ../Lintap/pidstat-collector.sh`
Result: fresh clean 15-minute run completed with no conversion retries. The
collector produced 4 parquet files under
`/tmp/opencode/pidstat-15m-clean.dyb7fq/parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=09/`.

30. `duckdb -csv -c "select count(*) as rows from read_parquet('/tmp/opencode/pidstat-15m-clean.dyb7fq/parquet/raw_sensor/pidstat/**/*.parquet');"`
Result: DuckDB loaded `59097` rows from the clean 15-minute run.

31. `duckdb -csv -c "select filename, count(*) as rows from read_parquet('/tmp/opencode/pidstat-15m-clean.dyb7fq/parquet/raw_sensor/pidstat/**/*.parquet', filename=true) group by 1 order by 1"`
Result: per-file row counts were `4731`, `19839`, `19631`, and `14896`.

## Manual Checks

- Read-only Linux ride-along verification:
  the Linux service examples/package env set `WINTAP_DISABLE_ETL=false`, which
  causes `PluginManager` to instantiate `WintapETL`, which starts
  `CacheManager`. The shipped `ETLConfig.json` defaults `UploadIntervalSec` to
  `300` and leaves `S3Adapter.Enabled=false`, so S3 ride-along requires a
  deployment ETL config that explicitly enables S3.

## Results

- Environment expectations met for `../Lintap`, `../wintap`, `../Wintappy`,
  plus host `pidstat` and `duckdb`.
- Missing host tool: `shellcheck`.
- First implementation slice completed:
  `../Lintap/pidstat-collector.sh` now spools outside `raw_sensor/`, rotates on
  configurable wall-clock windows, writes typed parquet into
  `parquet/raw_sensor/pidstat/dayPK=/hourPK=/`, salvages leftover active spools
  on startup, and enforces a configurable oldest-first local accumulation cap.
- Added `../Lintap/tests/pidstat-collector-tests.sh` and ran it successfully
  with 7 passing tests, covering conversion, loop-IFS parsing, joined-record
  recovery, salvage, byte-cap pruning, age-cap pruning, and live end-to-end
  row preservation.
- Live smoke run produced readable parquet from real `pidstat` output.
- 15-minute real collector run completed and is ready for manual inspection at
  `/tmp/opencode/pidstat-15m.U6zwhN`.
- Root cause of the bad 15-minute output: `normalize_pidstat_line()` inherited
  the loop's empty `IFS` and also used the wrong field count/index for
  `pidstat` rows, so it only retained commands with embedded spaces and dropped
  normal per-process rows.
- Secondary root cause of later conversion failures: some raw `pidstat` chunks
  arrived with two records glued together at the sample boundary. The parser
  now splits glued timestamp tokens and emits multiple normalized rows from a
  joined raw chunk.
- Post-fix smoke run at `/tmp/opencode/pidstat-fixcheck.YwrUoU` produced 307
  rows in ~16 seconds, which is in the expected order of magnitude.
- Formal validation now includes an end-to-end live row-preservation test:
  raw `pidstat` detail-row count == normalized TSV row count == parquet row
  count.
- Fresh clean 15-minute run completed at `/tmp/opencode/pidstat-15m-clean.dyb7fq`
  with `59097` rows across 4 parquet files.

## Known Gaps

- `shellcheck` not installed on host; shell lint verification is currently blocked.
- S3 upload was not exercised; this slice intentionally kept upload verification
  read-only/manual because deployment-specific `ETLConfig.json` enablement is
  required and no external access is assumed.

## Independent Review (2026-08-12)

Reviewed by the wiki-maintainer session after the first-slice commits landed
(`../Lintap` c76ea87; this repo c16c6b7, c77f026).

- Test suite independently re-run on the reviewer host: all 7 tests passed.
- Boundary check: no tracked changes in `../wintap` or `../Wintappy`;
  `pidstat-collect.sh` untouched. Authorization respected.
- Parquet schema confirmed to match `stg_pidstat_metrics` output columns plus
  `hostname`; `filename` provenance deferred to `read_parquet(filename=true)`
  in the Wintappy slice.
- `shellcheck` also unavailable on the reviewer host; lint gap remains open.
- Review verdict: slice accepted. Findings (fixes assigned to slice 2 in the
  implementation plan):
  1. `-p ALL` sampling deviated from the design — accepted and documented as a
     post-review decision in [[wiki/work/improve-pidstat-collector/design]];
     volume can be reduced in the ETL layer later if needed.
  2. `sample_date` uses processing-time date; samples in flight at midnight
     get a ~24h-forward timestamp. Fix: derive the date from the window-start
     epoch.
  3. A malformed second record in a glued pidstat chunk drops the whole chunk,
     including the valid first record.
  4. DuckDB conversion errors are discarded (`>/dev/null 2>&1`); failures log
     no cause.

## Follow-Ups

- Install `shellcheck` (or run lint in a container/CI) before calling shell lint “verified”.
- Manual inspection of `/tmp/opencode/pidstat-15m-clean.dyb7fq/parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=09/` is pending.
- The earlier 15-minute dataset at `/tmp/opencode/pidstat-15m.U6zwhN` should be
  treated as invalid after the parser bug discovery.
- Install the packaged files onto a target host and start `lintap-pidstat.service`
  through the real systemd unit before calling the packaging path fully
  verified.
- Add a live containerized-process fixture if a suitable container runtime is
  available in the validation environment.

## Slice 2 Verification (2026-08-15)

### Test Commands

Commands are recorded in the order executed.

1. `multipass info lintap-dev`
Result: VM running, Ubuntu 24.04, LLNL repos mounted at `/home/ubuntu/git`.

2. `multipass exec lintap-dev -- bash -lc "python3 --version && command -v uv && uv --version && command -v pidstat && pidstat -V && command -v duckdb"`
Result: VM has Python 3.12.3, `uv 0.12.2`, `pidstat` (`sysstat 12.6.1`), and DuckDB CLI.

3. `multipass exec lintap-dev -- bash -lc "python3 -m py_compile /home/ubuntu/git/Lintap/pidstat-collector.py /home/ubuntu/git/Lintap/tests/test_pidstat_collector.py"`
Result: Python syntax check passed for the new collector and pytest suite.

4. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Lintap -- bash -lc "UV_PROJECT_ENVIRONMENT=/tmp/lintap-venv uv lock"`
Result: `uv.lock` regenerated for the updated `requires-python >=3.11,<3.13` and pytest dev dependency.

5. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Lintap -- bash -lc "UV_PROJECT_ENVIRONMENT=/tmp/lintap-venv uv run --group dev pytest tests/test_pidstat_collector.py -q"`
Result: `12 passed`.

6. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Lintap -- bash -lc "UV_PROJECT_ENVIRONMENT=/tmp/lintap-venv uv run python -c 'import sys, duckdb; print(sys.executable); print(duckdb.__version__)'"`
Result: the project `uv` environment resolved correctly in-VM (`/tmp/lintap-venv/bin/python3`, DuckDB Python `1.5.2`).

7. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Lintap -- bash -lc "mkdir -p /var/tmp/opencode && run_root=$(mktemp -d -p /var/tmp/opencode pidstat-live.XXXXXX) && UV_PROJECT_ENVIRONMENT=/tmp/lintap-venv WINTAP_DATA_ROOT=\"$run_root\" PIDSTAT_ROTATE_INTERVAL_SEC=2 timeout --signal=TERM 6 uv run python ./pidstat-collector.py; RUN_ROOT=\"$run_root\" UV_PROJECT_ENVIRONMENT=/tmp/lintap-venv uv run python -c \"import duckdb, os; root=os.environ['RUN_ROOT']; print(duckdb.connect().execute(f'select count(*), count(distinct command) from read_parquet(\\\"{root}/parquet/raw_sensor/pidstat/**/*.parquet\\\")').fetchone())\""`
Result: live collector smoke run passed in `lintap-dev`. The collector rotated a parquet window on SIGTERM and the post-run query returned `(138, 115)` meaning 138 rows across 115 distinct commands.

8. `multipass exec lintap-dev -- bash -lc "command -v systemd-analyze >/dev/null 2>&1 && systemd-analyze verify /home/ubuntu/git/Lintap/packaging/lintap-rpm/lintap-pidstat.service /home/ubuntu/git/Lintap/packaging/lintap-deb/lintap-pidstat.service"`
Result: superseded later in the session when the hardcoded interpreter design was replaced with the `uv`-managed launcher flow below.

9. `multipass exec lintap-dev -- bash -lc "bash -n /home/ubuntu/git/Lintap/packaging/lintap-rpm/build-rpm.sh /home/ubuntu/git/Lintap/packaging/lintap-deb/build-deb.sh"`
Result: packaging script syntax checks passed.

10. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Wintappy -- bash -lc "UV_PROJECT_ENVIRONMENT=/tmp/wintappy-venv uv run dbt --version"`
Result: Wintappy dev environment bootstrapped under `uv`; dbt core `1.12.2`, duckdb adapter `1.9.6`.

11. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Wintappy -- bash -lc "... create parquet fixture ... && export WINTAP_DATA_ROOT=/tmp/opencode/wintappy-pidstat-fixture && export WINTAP_DBT_DATASET=/tmp/opencode/wintappy-pidstat-fixture/parquet && export WINTAP_DBT_DATABASE=/tmp/opencode/wintappy-pidstat-fixture/duckdb/wintap.duckdb && export WINTAP_DBT_START_DAY=20260812 && export WINTAP_DBT_END_DAY=20260812 && export PIDSTAT_DATA_PATH=/tmp/opencode/wintappy-pidstat-fixture/parquet/raw_sensor/pidstat && UV_PROJECT_ENVIRONMENT=/tmp/wintappy-venv uv run dbt run --project-dir wintap_dbt --profiles-dir wintap_dbt --select stg_pidstat_metrics pidstat_metrics && duckdb /tmp/opencode/wintappy-pidstat-fixture/duckdb/wintap.duckdb -csv -c \"select count(*) as rows, min(hostname) as hostname, max(container_runtime) as runtime from stg_pidstat_metrics\""`
Result: parquet-backed bronze/silver pidstat models built successfully. Verification query returned `rows=2`, `hostname=fixture-host`, `runtime=docker`.

12. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Wintappy -- bash -lc "mkdir -p /tmp/opencode/wintappy-pidstat-empty/parquet/raw_sensor /tmp/opencode/wintappy-pidstat-empty/duckdb /tmp/opencode/wintappy-pidstat-empty/empty-pidstat && export WINTAP_DATA_ROOT=/tmp/opencode/wintappy-pidstat-empty && export WINTAP_DBT_DATASET=/tmp/opencode/wintappy-pidstat-empty/parquet && export WINTAP_DBT_DATABASE=/tmp/opencode/wintappy-pidstat-empty/duckdb/wintap.duckdb && export WINTAP_DBT_START_DAY=20260812 && export WINTAP_DBT_END_DAY=20260812 && export PIDSTAT_DATA_PATH=/tmp/opencode/wintappy-pidstat-empty/empty-pidstat && UV_PROJECT_ENVIRONMENT=/tmp/wintappy-venv uv run dbt run --project-dir wintap_dbt --profiles-dir wintap_dbt --select stg_pidstat_metrics && duckdb /tmp/opencode/wintappy-pidstat-empty/duckdb/wintap.duckdb -csv -c \"select count(*) as rows from stg_pidstat_metrics; select name, type from pragma_table_info('stg_pidstat_metrics') where name in ('hostname','cgroup_path','pid_ns_inode','container_runtime','container_id') order by name\""`
Result: empty-input path still builds an empty typed table. Verified the new columns exist with expected types: `hostname/cgroup_path/container_runtime/container_id` as `VARCHAR`, `pid_ns_inode` as `BIGINT`.

13. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Lintap -- bash -lc 'bash -n ./pidstat-collector-bootstrap.sh ./pidstat-collector-launch.sh ./packaging/lintap-rpm/build-rpm.sh ./packaging/lintap-deb/build-deb.sh'`
Result: syntax checks passed for the new bootstrap/launcher scripts and updated packaging scripts.

14. `multipass exec lintap-dev --working-directory /home/ubuntu/git/Lintap -- bash -lc 'mkdir -p /var/tmp/opencode; export PIDSTAT_VENV_DIR=/var/tmp/opencode/pidstat-service-312/.venv; export PIDSTAT_BOOTSTRAP_PYTHON=3.12; bash ./pidstat-collector-bootstrap.sh; "$PIDSTAT_VENV_DIR/bin/python" -c "import sys; print(sys.version)"; run_root=$(mktemp -d -p /var/tmp/opencode pidstat-launch.XXXXXX); WINTAP_DATA_ROOT="$run_root" PIDSTAT_ROTATE_INTERVAL_SEC=2 PIDSTAT_VENV_DIR="$PIDSTAT_VENV_DIR" timeout --signal=TERM 6 bash ./pidstat-collector-launch.sh; RUN_ROOT="$run_root" "$PIDSTAT_VENV_DIR/bin/python" -c "import duckdb, os; root=os.environ[\"RUN_ROOT\"]; sql = \"select count(*), count(distinct command) from read_parquet(\" + chr(39) + root + \"/parquet/raw_sensor/pidstat/**/*.parquet\" + chr(39) + \")\"; print(duckdb.connect().execute(sql).fetchone())"'`
Result: the `uv` bootstrap/launcher flow passed end-to-end in `lintap-dev`. `uv` created a dedicated Python 3.12.3 venv at `/var/tmp/opencode/pidstat-service-312/.venv`, installed DuckDB there, and the launcher produced parquet successfully. The post-run query returned `(137, 114)` rows/distinct commands.

15. `multipass exec lintap-dev -- bash -lc 'command -v systemd-analyze >/dev/null 2>&1 && printf "%s\n" "[Unit]" "Description=Test pidstat collector" "[Service]" "EnvironmentFile=-/home/ubuntu/git/Lintap/packaging/lintap-rpm/lintap.env" "WorkingDirectory=/home/ubuntu/git/Lintap" "ExecStart=/bin/bash /home/ubuntu/git/Lintap/pidstat-collector-launch.sh" "User=root" > /tmp/lintap-pidstat-verify.service && systemd-analyze verify /tmp/lintap-pidstat-verify.service'`
Result: a temp unit using the new launcher shape verified cleanly in `lintap-dev`.

### Results

- Branch note: the slice-2 implementation work is recorded on
  `grantj-rhel8-testing` in `Wintap-Analytics/`, `../Lintap`, and
  `../Wintappy`.
- Slice 2 core implementation completed in `../Lintap`: the bash collector was retired and replaced with `pidstat-collector.py`, a single-process `/proc` sampler using the DuckDB Python API.
- The new pytest suite passed with 12 tests on `lintap-dev`, covering: parquet conversion/partitioning, pidstat-oracle parsing, glued-record handling, malformed-tail partial emission, salvage, byte cap, age cap, midnight/window-date behavior, container-path parsing, pidstat-oracle agreement, zero-child fork regression, and a live uv-run collector smoke test.
- The chosen telemetry source is option B (`/proc`) with pidstat retained only as the oracle in tests.
- Container attribution columns are now present end-to-end from collector output through Wintappy bronze.
- Wintappy now reads pidstat from parquet (`read_parquet(..., filename=true)`) and no longer uses the legacy tab-CSV bronze path.
- The runtime packaging decision is now validated in `lintap-dev`: a root-run
  systemd unit can point at a small launcher script, while `uv` bootstraps a
  dedicated collector venv (`PIDSTAT_VENV_DIR`) using a compatible Python
  version (`PIDSTAT_BOOTSTRAP_PYTHON`, default `3.12`). No host interpreter
  path is hardcoded anymore.

### Known Gaps

- The real packaged service was not installed and started under systemd in the
  VM; validation used the launcher directly plus `systemd-analyze verify` on a
  temp unit with the same `ExecStart` shape.
- The container-attribution tests cover v1/v2 cgroup parsing, but not a live containerized-process fixture on this VM.
- The end-to-end S3/local-delete validation remains blocked by the separate sensor-side delete-after-upload defect in [[wiki/work/fix-upload-cache-deletion/brief]].

## Independent Review — Slice 2 (2026-08-16)

Reviewed by the wiki-maintainer session after the slice-2 commits landed
(`../Lintap` 8eaae5c, `../Wintappy` ccbf783 on `grantj-rhel8-testing`; this
repo 3cafcbf/74ce903/2323d33).

Independently re-verified: pytest 12/12 in `../Lintap` (uv, python 3.12),
covering the seven ported cases plus oracle-tolerance, midnight/window-date,
container v1/v2 parsing, and the steady-state-no-children fork guard.

Code-review assessment of `pidstat-collector.py`:

- `/proc` stat field offsets all verified correct against proc(5) with the
  post-`)` indexing (minflt/majflt, utime/stime, starttime, vsize/rss,
  processor, delayacct_blkio_ticks, guest_time).
- Rate semantics match pidstat: %usr excludes guest time, %CPU =
  user+system+guest, %wait from schedstat run-delay deltas, iodelay as delta
  ticks. PID reuse handled via starttime comparison; first sample correctly
  emits nothing.
- Zero-child hot loop confirmed by construction and by the fork regression
  test; conversion is in-process duckdb with atomic `os.replace` and full
  traceback logging (review finding 4 absorbed as specified, likewise
  midnight and glued-record findings).
- Wintappy migration matches spec: `read_parquet(filename=true)`, container
  columns included, empty-input typed table preserved, `PIDSTAT_DATA_PATH`
  override honored with the new `parquet/raw_sensor/pidstat` default.
- Boundary check: no pidstat-slice-2 changes in `../wintap` (its new commits
  belong to the retention/eBPF thread).
- The uv-managed venv launcher pivot (after the pinned `python3.11` proved
  brittle) is a sound field-driven packaging decision, properly recorded in
  the design page.

Findings (minor, none blocking):

1. `enforce_accumulation_guard` calls `.stat()` on files between listing and
   deletion with no `FileNotFoundError` tolerance, and runs inside the
   conversion `try` — once the upload-delete fix lands, the sensor's uploader
   will delete these files concurrently, making the race real and its error
   report misleading ("parquet conversion failed"). Queued as a checklist
   follow-up.
2. Open items are honestly tracked, not hidden: live container fixture test,
   package-install/systemd verification on a target host, and the
   S3/delete-after-upload end-to-end (blocked on fix-upload-cache-deletion).

Review verdict: slice 2 accepted. Remaining checklist items are operational
verification plus the closeout promotion — the feature is code-complete.
