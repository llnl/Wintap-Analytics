---
title: "Verification: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-pidstat-collector/implementation_plan.md
policy: agent-editable
last_validated: 2026-08-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-pidstat-collector/verification.md
tags: [feature-work, verification, lintap, pidstat]
---

# Verification: Improve pidstat Collector

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
- Add the systemd unit/package wiring in the next slice.
- Update `../Wintappy` to read the new parquet layout in the later coordinated slice.
- Manual inspection of `/tmp/opencode/pidstat-15m-clean.dyb7fq/parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=09/` is pending.
- The earlier 15-minute dataset at `/tmp/opencode/pidstat-15m.U6zwhN` should be
  treated as invalid after the parser bug discovery.
