---
title: "Verification: Raw Sensor File Aggregation"
type: concept
confidence: medium
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/brief.md
  - wiki/work/raw-sensor-file-aggregation/implementation_plan.md
  - wiki/work/raw-sensor-file-aggregation/references.md
policy: agent-editable
last_validated: 2026-11-10
repo_scope: Wintap-Analytics
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/raw-sensor-file-aggregation/verification.md
tags: [feature-work, verification, raw_sensor, parquet, duckdb, s3, compaction]
---

# Verification: Raw Sensor File Aggregation

**Current result:** Planning only. No compactor code, DuckDB 2.0.0 runtime,
S3 write, benchmark, or operational row-count verification has been executed for
this feature. Required test IDs and acceptance mapping are defined in the
[[wiki/work/raw-sensor-file-aggregation/implementation_plan]].

## Shared Development And Operational Check

Use DuckDB 2.0.0 to count all source rows and all merged rows in each exact
event-type/day/hour/optional-protocol partition. The operation is `UNION ALL`:
duplicates and rows with NULL fields count toward both totals.

```text
source_rows = COUNT(*) across every selected source file in the partition
merged_rows = COUNT(*) across every merged output shard in the partition
row_delta   = merged_rows - source_rows
passed      = (row_delta == 0)
```

Run the same function in development tests, after `compact`, and through the
read-only `verify` command. Report partition keys, both counts, delta, and status;
a mismatch or unreadable/missing required file fails verification. Small schema
fixtures separately check field preservation and name-aligned NULL filling.

## Test Commands

Proposed commands below become runnable after the isolated package and tests
exist. They are requirements, not recorded passes. Run from Wintap-Analytics.

```bash
uv sync --project extras/raw-sensor-compact --locked --group dev
uv lock --project extras/raw-sensor-compact --check
uv run --project extras/raw-sensor-compact --locked python -c "import duckdb; print(duckdb.__version__); print(duckdb.sql('select version()').fetchone())"
uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests -m 'not s3'
uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests -m s3
uv run --project extras/raw-sensor-compact --locked raw-sensor-compact verify --dataset s3://test-bucket/compacted/runs/example-run
git diff --check
```

Register the `s3` marker. S3 tests require explicitly configured
isolated source/destination fixture roots and an identified endpoint; they must
not choose a default live bucket. A skipped integration suite is not acceptance.
All processing and verification use the tool's DuckDB 2.0.0 environment. Replace
the illustrative run URI with the actual isolated test output, and record the
benchmark/manual commands once those interfaces and destinations are established.

## Evidence To Record Per Run

- Date, tool commit, dependency-lock identity, Python/OS, actual DuckDB and
  extension versions.
- Test ID/AC mapping, exact command, exit code, pass/fail/skip counts, duration,
  and evidence location. Sanitize credentials and signed URLs.
- Source inventory identity and scope, endpoint product/version and auth mode,
  output run root/coverage, completion-manifest identity, and effective settings.
- Per-leaf keys, `source_rows`, `merged_rows`, `row_delta`, pass/fail, file counts,
  bytes, schemas, source immutability evidence, and fresh output read results.
- Injected failure point, observed run state, previously selected reader result,
  rerun outcome, and destination cleanup outcome for recovery cases.

## Results

| Area | Status | Required evidence |
| --- | --- | --- |
| Source/API review | Complete, 2026-11-10 | Live consumer/S3 patterns and official docs summarized in [[wiki/work/raw-sensor-file-aggregation/references]]. |
| Planning-document validation | Passed, 2026-11-10 | Six pages: YAML/required fields/date/inbound links valid; 49 grounding entries and 42 wikilinks valid after the count-validation clarification. `git diff --check` passed. |
| P0 / runtime and endpoint | Not run | Exact 2.0.0 install, extensions, actual S3 multipart write/read, D1/D2/D5 decisions. |
| P1–P2 / T01–T05 | Not run | CLI/discovery, small schema fixtures, shared partition row-count validation, leaf/sharding checks. |
| P3 / T06–T08 | Not run | Interrupted publication, concurrency/reruns, source bytes/API immutability, real S3 transport. |
| P4 / T09 | Not run | Fresh DuckDB 2.0.0 Parquet reads and read-only operational count verification. |
| P5 / T10 | Not run | Representative S3 benchmark and documented D4 default. |
| P6 / manual workflow | Not run | Dry run, compact, fresh count verification, partition-layout read, rerun and rollback. |
| T11 / scheduled readiness | Open dependency | [[wiki/todo/raw-sensor-upload-time-partition]] remains unresolved. |

### Planning Checks Executed — 2026-11-10

- `ruby -E UTF-8 -ryaml -rdate -ruri` with an inline read-only validator: passed
  YAML parsing, required fields, validation dates, grounding-path existence/URL
  syntax, and link/inbound-link checks for all five feature pages and the new
  publication tension. Also checked feature links in the existing index/log.
- `git diff --check`: passed. These are documentation checks, not execution of
  any planned compactor or S3 tests.

## Benchmark Record

For each candidate, retain the corpus description and effective size/codec/
threads/row-group settings, repeated cold/warm measurements, per-family file/
byte/row counts and row delta, shard-size distribution, compaction-plus-count time,
peak RSS/spill, and DuckDB 2.0.0 scan time. Include request/transfer measurements
where available. Candidates in the plan are experiments, not an adopted default.

**Selected default:** Undecided. **File reduction demonstrated:** Not yet.

## Manual Checks And Known Gaps

- Confirm D1's completed-root selection and exact coverage before a consumer
  switch; current globs do not enforce manifests. Publication tension:
  [[wiki/tension/raw-sensor-compaction-publication-vs-glob-readers]].
- Apply the confirmed filename rule: object filenames and derived pidstat
  `filename` values may change. Preserve `dayPK`/`hourPK` and existing `protoPK`
  leaves; use small fixtures to check physical payload fields.
- Verify count mismatches, schema/read errors, and resource-limit failures cannot
  produce a completed run. Development and operations share the count check.
- Compare a stable, recorded source inventory with the output. A completed hour
  alone does not prove that delayed upstream uploads have stopped.
- Confirm rollback to a source/previous root of the same coverage and that a
  fresh consumer database is used when materialized DBT results need rebuilding.

## Follow-Ups

Append real command results as each implementation step completes; update the
plan's checklist and wiki log. Promote supported operating behavior only after
manual acceptance. Track daily compaction and scheduling as later work.
