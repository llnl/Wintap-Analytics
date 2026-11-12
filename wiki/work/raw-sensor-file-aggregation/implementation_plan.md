---
title: "Implementation Plan: Raw Sensor File Aggregation"
type: concept
confidence: medium
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/brief.md
  - wiki/work/raw-sensor-file-aggregation/references.md
  - wiki/todo/raw-sensor-upload-time-partition.md
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/test_s3_http.py
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - https://duckdb.org/docs/2.0/sql/statements/copy.html
  - https://duckdb.org/docs/2.0/data/parquet/overview.html
  - https://duckdb.org/docs/2.0/core_extensions/httpfs/s3api.html
  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
policy: agent-editable
last_validated: 2026-11-10
repo_scope: Wintap-Analytics
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/raw-sensor-file-aggregation/implementation_plan.md
tags: [feature-work, implementation-plan, raw_sensor, parquet, duckdb, s3, compaction, verification]
---

# Implementation Plan: Raw Sensor File Aggregation

**Status:** Planning complete; implementation and runtime verification have not
started. DuckDB 2.0.0 and per-partition count validation are confirmed. Proposed
CLI and publication details remain recommendations. Evidence belongs in
[[wiki/work/raw-sensor-file-aggregation/verification]].

## Scope

Implement the [[wiki/work/raw-sensor-file-aggregation/brief]] as a standalone
Wintap-Analytics CLI with an isolated, exactly pinned DuckDB 2.0.0 environment.
Read selected completed UTC hours directly from S3 and write a separate mirrored
dataset. Group across hosts only within each exact event-type/day/hour/optional
protocol leaf. Preserve payload rows, duplicate multiplicities, and fields.

The operation is a name-aligned **UNION ALL of recorded raw_sensor Parquet**:
Parquet in, Parquet out, using DuckDB 2.0.0 for processing and validation.
The user-confirmed validation is simple: total source rows must equal total
merged rows in each partition, both in development and operation. Parquet is
the interchange boundary; a separate DuckDB 1.5.6/DBT compatibility gate is not
part of this plan. See [[wiki/work/raw-sensor-file-aggregation/interview]].

Existing timestamps, identities, hostnames, units, and protocol values remain
unchanged. Daily rollup, scheduling, and the separate .NET upload correction
remain later work.

## Review Findings

1. **Publication requires a reader contract.** S3 provides atomic updates to
   individual keys, not multi-key transactions. Copying staged shards into a
   live prefix, deleting old shards, or writing a completion marker does not
   protect a reader that globs every Parquet file. Wintappy currently constructs
   such recursive globs. Track the unresolved choice in
   [[wiki/tension/raw-sensor-compaction-publication-vs-glob-readers]].
   <!-- GROUND_TRUTH: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html §ConsistencyModel; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_glob/raw_sensor_partition_globs -->
2. **Payload equality differs from file provenance equality.** Pidstat bronze
   requests DuckDB's virtual `filename`, and silver carries it forward. The
   path necessarily changes when files are compacted. The user confirmed on
   2026-11-10 that object filenames may change: preserve the partition scheme,
   not filename consistency. Output reads allow derived object-path differences.
   Physical telemetry fields remain preserved.
   <!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql §parquet_scan; ../Wintap-PyUtil/wintap_dbt/models/silver/pidstat_metrics.sql -->
   See the recorded clarification in
   [[wiki/work/raw-sensor-file-aggregation/interview]].
3. **Use name-aligned union-all and count validation.** Keep source fields,
   fill missing columns with NULL, and reject incompatible types. Small fixtures
   exercise these behaviors; the shared development/operational validation
   compares total source and merged row counts in each exact leaf.
   <!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/brief.md §Goals/Acceptance Criteria; wiki/work/raw-sensor-file-aggregation/interview.md §Processing and validation clarification -->
4. **Shard sizes are approximate.** DuckDB documents `FILE_SIZE_BYTES` as an
   approximate target. Threaded output can increase file count; remote directory
   overwrite is unsupported. Qualify the exact 2.0.0 `COPY` combination on S3
   before designing reruns around it.
   <!-- GROUND_TRUTH: https://duckdb.org/docs/2.0/sql/statements/copy.html §COPY TO options -->
5. **A completed clock hour is not yet a final source snapshot.** The .NET
   delayed-upload behavior still targets old partitions. Manual results must
   identify the exact observed source set. Scheduling without lookback remains
   dependent on [[wiki/todo/raw-sensor-upload-time-partition]].

## Implementation Decisions To Settle

| ID | Recommendation | Evidence/decision needed |
| --- | --- | --- |
| D1 | Immutable per-run dataset roots, explicitly selected only after verification; each root covers exactly its requested window/families. | Confirm that manual root switching and non-accumulating window snapshots satisfy AC6. A stable accumulating root requires a different reader/publication contract. |
| D2 | Python CLI using DuckDB's Python API for Parquet data and boto3 for discovery/control metadata. | Prove the exact 2.0.0 package, extensions, target endpoint, and credential flow in P0; finalize flag names and supported Python version. |
| D4 | Configurable approximate compressed-file target, with codec/threads/row-group settings recorded. | Benchmark before assigning a default; enforce AC10 file-count reduction on multi-file partitions. |
| D5 | Default event discovery lists only immediate family prefixes; row reads list only selected hour prefixes. Empty selections are reported explicitly. | Finalize missing-family/empty-hour behavior, resource defaults, and supported authentication modes in P0/P1. |

These choices should be recorded in this folder as implementation starts. A
failed feasibility result revises the affected step; it must not silently relax
the brief or substitute another DuckDB version.

## Proposed Interfaces And Data Flow

### Standalone package and CLI

Use `extras/raw-sensor-compact/`, alongside existing standalone diagnostics.
Keep its `pyproject.toml`, `uv.lock`, environment, tests, and README local to the
tool. Proposed console command: `raw-sensor-compact` with `plan`, `compact`, and
`verify` subcommands.

```text
uv run --project extras/raw-sensor-compact raw-sensor-compact plan \
  --source-dataset s3://test-bucket/source \
  --destination-base s3://test-bucket/compacted \
  --start-hour 2026-11-09T10:00:00Z --end-hour 2026-11-09T11:00:00Z \
  --event-type raw_process --event-type pidstat
```

- Roots mean the parent of `raw_sensor`, never an ambiguous raw_sensor suffix.
  Reject overlapping source/destination namespaces, glob-bearing roots, and
  invalid paths. Treat endpoint + bucket + key prefix as the storage identity.
- Hours use an inclusive start/exclusive end, explicit UTC, whole-hour bounds;
  reject current/future hours, reversed ranges, and ambiguous local time.
  Multi-hour requests still produce independent hourly leaves, never daily files.
- Repeated `--event-type` limits families; omission discovers immediate family
  prefixes without scanning their histories. Preserve family names/aliases.
- `plan` is read-only: show exact scope, object counts/bytes, schema conflicts,
  and proposed groups. `compact` revalidates discovery before writing; a saved
  plan is not authority to read changed objects unnoticed.
- Expose `--target-size`, `--threads`, `--memory-limit`, `--temp-directory`,
  `--max-temp-size`, and `--timeout`. Use explicit target size until D4 is
  benchmarked. Record all effective settings. Local DuckDB spill is allowed;
  the data path still uses direct S3 reads and `COPY` writes.
- Support AWS profile/environment credentials and temporary session tokens;
  explicitly define endpoint, region, URL style, TLS, and extension cache setup.
  Ensure boto3 and DuckDB use the same intended identity and endpoint. Follow
  existing named-profile conventions; qualify refresh/expiry rather than
  assuming frozen credentials work indefinitely. Secrets stay out of manifests
  and reports. Limit initial support to the modes actually tested.
- `verify --dataset <completed-run-root>` uses a fresh DuckDB 2.0.0 connection
  to count the recorded source files and merged files per partition. Return
  partition keys, `source_rows`, `merged_rows`, `row_delta`, and pass/fail.
  Exit nonzero for unequal counts, read errors, or incomplete/conflicting work.
  Report empty selections distinctly rather than claiming data was compacted.

### Source snapshot and partition plan

List with pagination at exact `raw_sensor/<event>/dayPK=.../hourPK=.../`
prefixes. Validate every returned key against the requested family and complete
leaf grammar; preserve optional `protoPK` literally. Unexpected partition
dimensions must fail explicitly rather than being silently flattened.

Freeze a sorted explicit object list per leaf: endpoint/bucket/key, size, ETag,
last-modified, and version ID when available. Deduplicate repeated listing
entries by object identity, **never by row values**. Record enumeration scope,
empty leaves, schemas, and the run's engine/configuration identity. Pass explicit
file lists to DuckDB, not a broad live glob.

Recheck identities and selected-prefix membership before completion. Added,
removed, or changed objects during processing invalidate that attempt. ETag is
an identity signal, not a universal content checksum. These checks do not create
an atomic S3 snapshot: the initial operating assumption is immutable source keys
and a quiescent selected window. Post-completion arrivals belong to a new
explicitly requested rebuild; no automatic lookback is introduced. Qualify
version-pinned reads separately if mutable source keys must be supported.

### Union-all processing and partition row-count validation

- Use `read_parquet` on each leaf's explicit source-file list with
  `union_by_name=true`, then `COPY` the rows to Parquet. Preserve all physical
  fields, fill missing columns with NULL, and reject incompatible column types.
  Keep hive inference disabled for the payload copy so directory keys do not
  accidentally become added data columns.
- Preserve physical fields even when named `filename`, `dayPK`, `hourPK`, or
  `protoPK`. If a physical hive value conflicts with its directory, report the
  conflict rather than replacing the field. Test name alignment and type handling
  with small known-value fixtures.
- Use `UNION ALL` semantics: every input row contributes to output, including
  identical rows from one or multiple source files. Do not deduplicate, aggregate
  values, normalize fields, or filter by event time.
- For each leaf, count **all source rows** and **all merged rows across every
  output shard**. Use `COUNT(*)`, not `COUNT(column)` or `COUNT(DISTINCT ...)`.
  Require `source_rows == merged_rows`; record both totals and their difference.
  Do not use a dataset-wide total that could hide a mismatch between partitions.
- Count the actual source/output Parquet files, rather than relying only on
  the writer's reported row count. Use the same function after compaction, in
  development tests, and in the standalone read-only `verify` command.
- Report an empty file list as zero without passing an empty list to
  `read_parquet`; retain the distinction between no input files and zero-row
  Parquet files. A missing output for nonempty input fails the comparison.
- Read errors, timeouts, or count mismatches fail validation and prevent
  completion. Include count-query time in the benchmark.

Illustrative DuckDB 2.0.0 validation SQL for one nonempty source/output file
list pair; bind `$source_files` and `$merged_files` to the exact leaf's lists:

```sql
WITH counts AS (
    SELECT
        (SELECT count(*) FROM read_parquet(
            $source_files, union_by_name=true, hive_partitioning=false
        )) AS source_rows,
        (SELECT count(*) FROM read_parquet(
            $merged_files, union_by_name=true, hive_partitioning=false
        )) AS merged_rows
)
SELECT source_rows, merged_rows,
       merged_rows - source_rows AS row_delta,
       source_rows = merged_rows AS passed
FROM counts;
```

### Proposed publication and rerun contract (D1 still open)

```text
<destination-base>/runs/<unique-run-id>/
  raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/part-*.parquet
  _compaction/manifest.json
```

1. Allocate a fresh unique run root outside every currently selected consumer
   root. Write directly there; it is an unpublished candidate while in progress.
2. Process and validate each leaf. Keep progress metadata outside `raw_sensor`.
   A run is eligible for completion only when all requested leaves have a
   successful or explicitly empty result and the source recheck passes.
3. Reread the exact output set and compare its listing with the expected shard
   list. Write one final completion manifest last, containing source inventory,
   schemas, coverage, settings, output identities, counts, and validation results.
   A failed manifest write leaves the run unadvertised; retry must handle an
   acknowledged-late successful PUT without overwriting completed data.
4. Return a consumer-ready root only after the manifest can be reread and
   verified. The operator starts a **fresh consumer** with that exact root.
   Never select the common `runs/` parent or switch a running reader mid-scan.
5. Unchanged source inventory/scope/configuration may reuse a verified completed
   run as a no-op. Changed inputs or settings create a new run root. A failed
   attempt is rebuilt in a fresh root; resuming partial shard writes is deferred.
   Never append to or overwrite a completed dataset.

This is atomic **selection of a completed immutable dataset**, not atomic S3
directory publication. Candidate objects are visible to direct S3 listing;
consumers must not select candidates or ignore the completion contract. The
manifest is checked by the CLI/operator, not automatically by current DBT globs.
AC6 must explicitly accept this interpretation before D1 is considered settled.

Each run covers only its recorded hours/families. Replacing a consumer root with
a one-hour run does not retain yesterday's or another family's data. For a wider
view, request that full window. A stable accumulating history is unresolved,
with storage/rebuild cost documented in the linked tension.

Concurrent attempts use different run roots and cannot interleave shards. No
shared `latest` pointer is proposed. Rerun idempotence means the selected dataset
has the same row multiset, not identical file bytes, shard boundaries, or absence
of unselected historical generations. Abandoned-run cleanup may remove only
recorded, unselected destination runs; source deletion is never a recovery step.

## Sequenced Implementation Steps

### P0 — Qualify runtime and settle the contracts

Create the isolated package/lockfile and a small disposable S3 read/write spike.
Prove `duckdb.__version__` and `SELECT version()` are 2.0.0; record Python, OS,
extensions, endpoint product/version, and credential mode. Verify direct reads,
multi-shard `COPY`, available file/stat reporting, fresh output reads, and
multipart failure behavior. Determine exact codec/row-group/size/thread options.
Use official 2.0 docs as guidance, not evidence that the installed binary works.

**Exit:** D1/D2/D5 recorded; endpoint/runtime feasibility demonstrated; credential
expiry behavior and extension acquisition documented. Block unsupported runtime
or endpoint modes rather than claiming compatibility. Initial feasibility cases
from T01/T02/T05/T08 pass; subsequent steps complete those suites.

### P1 — Implement read-only planning and immutable input inventory

Implement CLI parsing, exact UTC prefix selection, pagination, complete leaf
grouping, schema inventory, overlap rejection, deterministic run fingerprint,
and configurable limits. Fingerprint the sorted object identities, selected
scope (including empties), engine/tool version, and write settings.

**Exit:** a dry run explains exactly what it would read/write; missing/invalid
scope and cap overflow never silently truncate. T01/T04/T07 pass.

### P2 — Implement local union-all compaction and count validation

Implement name-aligned Parquet reads, leaf-scoped `COPY`, source/output
`COUNT(*)` comparison, and structured per-leaf results. Process leaves
sequentially initially; use bounded DuckDB parallelism within a leaf. Record
input/output row counts, row delta, bytes, shard sizes, and schemas.
Empty Parquet inputs retain a typed zero-row output when needed to preserve
their schema; no-files selections record no output. Single-file leaves need no
file-count reduction and must not gain extra shards.

**Exit:** T02–T05 pass: small schema fixtures retain expected fields/values,
cross-host input rows are concatenated, and unequal row totals fail validation.

### P3 — Implement direct-S3 execution, completion, and reruns

Integrate source rechecks, unique output roots, final manifests, fresh verification,
no-op reuse, and bounded retries. Enforce no source mutation in the storage API
and credentials. Stop on leaf failure; already written candidate files remain
unselected. Add failure recovery and destination-only cleanup instructions.

**Exit:** T06–T08 prove successful publication and every failed/interrupted run
leaves the previously selected dataset readable and unchanged. Qualify actual
multipart writes; the existing read-only loopback test is not sufficient.

### P4 — Expose and verify the operational count command

Implement `verify` around the same per-partition count function used by
`compact`. Open a fresh DuckDB 2.0.0 connection, resolve the recorded source and
output files, and report partition keys, file counts, row totals, delta, and
status. Confirm the output is readable at the preserved day/hour/protocol paths.
Exercise process, file, TCP/UDP, pidstat, multiple shards, and empty selections.

**Exit:** T09 passes with Parquet input/output on DuckDB 2.0.0. A correct merge
has zero delta for every partition; removed/extra rows fail both the development
check and operational command. Verification performs no S3 mutations.

### P5 — Benchmark representative S3 hours and choose the shard default

Measure an isolated representative corpus: high-volume file events, process,
network protocol leaves, pidstat, and a sparse family, across multiple hosts.
Include many tiny objects, a skewed/big leaf, and heterogeneous compatible schemas.
Use a read-only approved source or a representative copy in the test dataset;
all derived writes stay in isolated test prefixes.

Start with **64, 128, and 256 MiB as experiment candidates**, not defaults.
Control and record compression, threads, row groups, connection/cache state, and
machine resources. Measure cold/fresh-process and warm DuckDB 2.0.0 scans separately;
repeat candidates enough to report variation (at least three measured runs).

Record per leaf/family: input/output files, compressed bytes, rows, shard-size
distribution, compression ratio, discovery/schema/read-write/validation/total
time, peak RSS, spill usage, and DuckDB scan time. Record object requests and
transfer bytes when observable; mark unavailable measurements rather than infer
them. Include per-partition source/output row totals and delta for each output.

**Exit:** T10 chooses and explains a configurable default. Every multi-file
acceptance leaf has fewer output files; single-file leaves have at most one.
If a requested size/thread policy produces equal or more files, do not certify
AC10 or publish that result as successful compaction: revise the policy and rerun.
The target is approximate; report outliers instead of promising a hard maximum.
Do not invent a speedup threshold absent from the brief.

### P6 — Operational documentation and feature closeout

Document installation, credentials/extensions, dry run, explicit hour selection,
compaction, verification, consumer root/coverage selection, rerun, failure cleanup,
and rollback. Summarize schema handling/endpoints, count-validation costs, and
the current upload-time TODO. Run the end-to-end manual example on isolated S3.

**Exit:** acceptance map below has evidence; all deferred gaps are explicit.
Update this checklist, verification record, wiki index/log, and promote verified
operating facts into a canonical tool page. Scheduling remains a separate step
requiring T11; it is not implied by successful manual compaction.

## Files Likely To Change

Proposed paths; create only during authorized implementation:

| Path | Responsibility |
| --- | --- |
| `extras/raw-sensor-compact/pyproject.toml`, `uv.lock`, `README.md` | Isolated package, exact dependency lock, console entrypoint, operating guide. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/cli.py`, `config.py` | Commands, validated scope/resources, structured exit/results. |
| `.../storage.py`, `inventory.py` | Endpoint/auth setup, scoped listing/identities, control metadata; DuckDB handles Parquet data. |
| `.../schema.py`, `compact.py`, `verify.py`, `publication.py` | Name alignment/type checks, leaf writer, shared row-count validation, run lifecycle. |
| `extras/raw-sensor-compact/tests/` | Small Parquet fixtures, local count tests, opt-in S3 transport/acceptance and operational CLI tests, all on DuckDB 2.0.0. |
| `extras/raw-sensor-compact/benchmarks/` | Reproducible corpus descriptors, benchmark driver and result schema. |
| `wiki/work/raw-sensor-file-aggregation/verification.md` | Commands, results, evidence locations, benchmark decision, unresolved gaps. |
| `wiki/tool/raw-sensor-compaction.md` (at closeout), `wiki/index.md`, `wiki/log.md` | Verified durable usage and progress. |

## Tests And Acceptance-Criteria Mapping

AC numbers refer to the brief, including the confirmed filename and row-count clarifications.
Tests should assert observable payload, storage, and reader behavior, not merely
generated SQL or mocked call shapes.

| ID / level | Required cases and pass condition | AC |
| --- | --- | --- |
| T01 — CLI/discovery | Exact requested UTC prefixes, midnight/year rollover, repeated events, multiple listing pages, duplicate listing entries, absent hour, no files, malformed/overlapping roots, out-of-scope returned key, limits and current/future hours. Assert no out-of-window object GETs or mutation during `plan`. | 1 |
| T02 — schema fixtures | Small known-value Parquet fixtures with multiple hosts, reordered/missing/all-NULL columns, compatible drift, incompatible types, and physical fields sharing hive/filename names. Expected fields and values survive; incompatible input fails before completion. | 3 |
| T03 — partition row counts | Count all source rows and all merged rows for each leaf. Cover duplicates within/across files, NULLs, zero-row files, multiple output shards, omitted rows and extra rows. Correct merges have equal totals; missing/extra rows produce nonzero delta and fail. Use the same validation function as operational `verify`. | 2 |
| T04 — partition fidelity | Mixed families, multiple hosts, adjacent hours/days, no-protocol leaves and separate TCP/UDP leaves, old/future event timestamps inside selected upload partitions. Exact directory keys and physical field values survive; no cross-leaf rows or event-time filtering. | 1, 4 |
| T05 — sharding | Below/near/above target sizes, incompressible/skewed data, thread settings, single-file and zero-row leaves. Record approximate size behavior; verify every shard and no leftover Parquet. Multi-file success reduces file count. | 2, 7, 10 |
| T06 — publication/faults | Fail after first shard, during multipart upload, validation, source recheck, and final manifest PUT; lose completion response; interrupt/SIGKILL; timeout/spill exhaustion; corrupt/delete/add output; rerun unchanged and changed input; two concurrent attempts. No failed candidate is returned as consumer-ready; previous selected root remains intact; retry never mixes generations or duplicates selected rows. | 3, 6 |
| T07 — immutability/drift | Source role denies mutation; record API methods and fixture SHA-256 before/after success, failure, rerun, and cleanup. Alter/add/remove a source object during processing: attempt fails. ETag/version metadata supplements rather than substitutes for fixture byte equality. | 1, 5, 6 |
| T08 — real S3 transport | SDK listing/control and actual DuckDB range GETs/multipart writes on isolated S3; pagination, profile versus environment selection, session tokens, custom endpoint/path-style/TLS, denied reads/writes, transient errors/retry exhaustion. Qualify every advertised endpoint; emulator/mocked success alone is insufficient. | 1, 5, 6 |
| T09 — operational verify | Fresh DuckDB 2.0.0 reads completed Parquet at the preserved partition paths. Report source/merged file and row totals per leaf, zero/nonzero delta, and matching success/failure exit status. Exercise the same count check as development, partial/missing output, empty inputs, and read-only behavior. | 2, 4, 8 |
| T10 — S3 benchmark | Representative corpus, candidate sizes, repeatable settings, equal partition row totals on each output, before/after files/bytes/runtime/resources and DuckDB 2.0.0 scans. Written rationale selects a default; fewer files is measured, not assumed. | 7, 10 |
| T11 — upstream dependency | Record the separate upload-time TODO's status. Before scheduling, obtain source/deployment evidence and boundary/delayed-retry verification for every producer feeding the scheduled root. No automatic lookback is added here. | 9 |

## Migration, Rollback, And Limits

- Consumer cutover changes only the explicitly selected raw dataset root and
  matching hour/family scope. Keep source and compacted scans disjoint; never
  union generations or fall back to raw files within a completed compacted leaf.
- Physical telemetry fields remain payload. Object filenames and the derived
  object `filename` may change, as confirmed by the user; file counts and
  file-layout diagnostics also reflect compaction. Record source-object lineage
  in the manifest, not by injecting new raw columns.
- Roll back by starting a fresh consumer with the original source root or a
  previous verified root covering the requested window. Existing materialized
  consumer databases are separate artifacts; rebuild them into a disposable/new
  database rather than assuming a root change rewrites their contents.
- Abandon failed candidate roots; clean only explicitly identified unselected
  destination data and multipart uploads. Preserve manifests needed for evidence
  and any selected root. Never use source deletion or in-place overwrite to repair
  a failed run.

## Done Checklist

- [x] Brief and live producer/consumer/API references reviewed; plan/test map written.
- [ ] P0: D1/D2/D5 recorded; exact runtime, extension, authentication, and S3 write spike pass.
- [ ] P1: read-only planning, exact-hour inventory, grouping, and limits pass.
- [ ] P2: schema fixtures, union-all compaction, and partition row-count tests pass.
- [ ] P3: S3 publication, immutability, fault injection, concurrent/rerun tests pass.
- [ ] P4: fresh DuckDB 2.0.0 operational row-count verification passes.
- [ ] P5: representative benchmark selects D4 default and demonstrates file reduction.
- [ ] P6: manual S3 acceptance, operational guide, rollback, and durable wiki promotion complete.
- [ ] AC1–AC8/AC10 have recorded passing evidence; AC9 dependency state is explicit.
- [x] Object filename consistency is not required; partition preservation is confirmed.
- [x] DuckDB 2.0.0 and per-partition count equality are confirmed for development/operation.
- [ ] Publication tension is resolved by a recorded decision.

Scheduled readiness is tracked separately from manual-feature completion and
remains unqualified while T11 is open.
