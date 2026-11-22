---
title: "Implementation Plan: Raw Sensor File Aggregation"
type: concept
confidence: high
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/brief.md
  - wiki/work/raw-sensor-file-aggregation/interview.md
  - wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/README.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../Wintap-PyUtil/tests/test_compacted_s3_migration.py
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: extras/raw-sensor-compact; wiki/work/raw-sensor-file-aggregation
tags: [feature-work, implementation-plan, raw_sensor, parquet, duckdb, compaction]
---

# Implementation Plan: Raw Sensor File Aggregation

**Current status:** fixed-root merge/skip plus optional validated source-prefix
deletion implemented; PyUtil reads raw_sensor + compacted. Compactor suite:
107 pass/2 opt-in skips; PyUtil: 299 pass/2 opt-in skips. Full local raw/mixed/
compacted migration: 54 models equivalent, 139 build/test gates per state.
Copied live pidstat/host migration: 897,395 rows, 4 equivalent models/10 gates per
state, 29 copied source objects deleted, 29 original hashes unchanged.
Expanded all-family live-copy testing passed full raw/mixed builds (139 gates
each) but strict equivalence failed; unchanged-input replay also changed model
results. Human explicitly accepts existing ANY_VALUE quality debt as non-blocking
for compaction. Full builds/tests, all schemas and exact bronze/unaffected results
still gate; affected downstream differences are reported. Expanded migration
**passed** under that contract: 54 models/139 gates in every state, all 11 bronze
results exact, 2,668,265 rows conserved, 399 copied sources → 10 outputs, all
399 original hashes unchanged. Details:
[[wiki/tension/dbt-arbitrary-representatives-vs-compaction-equivalence]].
No run IDs/manifests/reservations/conditional writes or overlap masking.
Benchmark/default and broader qualification remain open. Evidence:
[[wiki/work/raw-sensor-file-aggregation/verification]].

The earlier immutable generation plan is explicitly superseded by the human's
fixed-path correction, recorded in
[[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]]. Historical
generation evidence remains in verification and the superseded ADR; it is not
the current reader/recovery contract.

## Scope And Interfaces

```text
source: lintap/raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/...
dest:   lintap/compacted/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/<merged>.parquet

for each selected event/day/hour:
    if destination hour exists: skip
    else: merge all source files separately within each protocol leaf
```

- Python/UV package in `../Wintap-PyUtil/extras/raw-sensor-compact/`, exactly
  DuckDB 2.0.0, with its own lockfile/environment. PyUtil owns both compactor
  and DBT code; Analytics hosts this wiki and feature/evidence artifacts.
- `plan`, `compact`, `verify`: explicit `--source-root`, `--destination-root`,
  inclusive `--start-hour`, exclusive `--end-hour`, optional repeated `--event-type`.
  These are **direct event roots**; no appended raw_sensor directory in destination.
- `compact` needs explicit positive `--target-size-bytes` until benchmarked.
  `--delete-source` opts into whole source event/hour-prefix deletion after
  validation; `--grace-minutes` defaults to 10 and must be at least 5. S3
  deletion uses bounded post-delete exact-prefix confirmation retries (five
  attempts with one-second initial backoff by default); retry exhaustion is
  fail-closed and reports remaining keys/response metadata. `reconcile-delete`
  is a separate validation-gated cleanup path requiring `--confirm-delete`.
  Parquet names and approximate shard boundaries are implementation-defined.
- Same-bucket sibling source/destination roots are supported; overlapping roots,
  globs, malformed UTC bounds, symlinks and file-limit truncation are rejected.
- Missing source hour: empty result, no destination created. Existing destination
  hour: skipped before source discovery/schema reads. Any S3 object or local hour
  directory means exists, including failed/partial output. Skip is at the hour
  parent, not independently at TCP/UDP leaves.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py -->

## Processing And Validation

1. Select completed whole UTC hours; no automated lookback or event-time filtering.
2. Check destination hour existence before scanning its source.
3. Discover all explicit source Parquet objects for the hour; paginate, deduplicate
   identities, group by exact event/day/hour/optional protocol and enforce limits.
4. Preflight compatible schemas for every leaf in that hour before writes. Use
   name-aligned union-all; missing fields become NULL. Identical types/signed
   integer widening accepted, incompatible types rejected. Physical non-NULL hive
   fields must agree with directories. No row sorting, normalization or deduplication.
5. Recheck source inventory, check destination again, then directly COPY merged
   Parquet into the fixed hour. Process protocol leaves independently.
6. Reread every shard for schema and shared per-leaf `COUNT(*)` comparison.
   Report source/merged files, bytes, rows and delta; multi-file success reduces files.
7. Compare actual output inventory to the written leaf/file set and recheck source.
   A failure stops the command and identifies the destination hour for manual recovery.
8. With `--delete-source`, first complete compaction/validation for every selected
   event family in an hour, then delete each complete validated source event/hour
   prefix (all protocol leaves and markers). Preflight requires UTC end plus grace
   for the entire selected window before writes. List S3 keys before batching
   deletes; per-key errors or retry-exhausted remaining objects fail only that
   deletion phase, with diagnostics, while other event families continue. Keep
   output and reconcile explicitly.
9. `reconcile-delete --confirm-delete` validates existing destination/source
   per-leaf row counts and inventories before attempting deletion; it never
   rebuilds or overwrites an existing destination hour.

Operational `verify` uses a fresh DuckDB connection, discovers both direct roots,
and compares row totals for the union of leaf keys. Deliberately altered/extra or
missing rows produce nonzero deltas; deltas cannot cancel across partitions.
Count equality is the merge gate, not a full-row multiset proof. Source/output
verify applies before deletion/retain-source mode; post-migration tests compare
fresh DBT results to saved raw-only baselines with counts/sorted-result SHA-256.
For approved full live qualification, ANY_VALUE-containing models and their
descendants may have reported result/count differences; every bronze model,
schema and model outside that closure remains exact. This does not repair the
DBT quality issue or claim equivalent downstream results.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py -->

## Recovery, Readers And Approved Prefix Deletion

- **One writer per destination.** Existence checks are not a distributed lock.
  No atomic all-or-nothing visibility; do not read an hour while it is merging.
- Partial failed files remain in the fixed output. Rerun skips that hour until
  a human removes its exact derived subtree. Do not infer completion from existence.
- Source is retained by default. The human now approved validated prefix deletion
  under the UTC producer upload contract and 5–10 minute grace. Rare clock skew
  is accepted for these deployments; no per-object-only deletion restriction.
  Live tests delete isolated copies, not original data or earlier output/probes.
- Late source arrivals to an existing output hour are not automatically included.
  Manual cleanup/rebuild is the intentional way to refresh that hour.
- PyUtil reads raw_sensor and compacted together with UNION ALL/name alignment;
  no deduplication/preference rule. Shared event/alias/optional-column/preflight
  checks and local date discovery cover both roots. `WINTAP_DBT_COMPACTED_ROOT`
  overrides a direct compacted event root; default is sibling of raw_sensor.
  No engine upgrade. DBT builds follow successful migration/manual reconciliation;
  bronze views as well as materialized models must be rebuilt after migration.
- No manifest, run-root selection, conditional PUT, resume or automated cleanup.
  The endpoint's ignored conditionals no longer block basic S3 merge.

## Runtime And Resource Defaults

Verified on Python 3.14.0/macOS arm64/DuckDB 2.0.0. Frozen boto3/DuckDB identity,
resolved profile endpoint, path-style HTTP(S), session tokens and httpfs cache
setup are implemented. Refresh/expiry and additional endpoints remain unqualified.
DuckDB internal results use fully drained `.fetchall()` to avoid extension API
unfinished-result failures.

Development limits: 2 threads, 1 GB memory/spill, 300-second cooperative timeout,
24 hours and 10,000 processed source files. Skips do not consume source-file caps.
SDK calls/extension setup can overrun a deadline; this is not a hard process limit.
Actual source SHA-256 evidence covers the bounded live test, not arbitrary mutable
keys or atomic source snapshots.

## Remaining Delivery Steps And Acceptance Map

AC numbers refer to the corrected [[wiki/work/raw-sensor-file-aggregation/brief]].

| ID | Cases/evidence and remaining coverage | AC |
| --- | --- | --- |
| T01 CLI/discovery | Exact UTC prefixes, rollover, pagination, duplicate/out-of-scope entries, limits, absent hours, malformed/overlapping roots and read-only plan. Existing-hour skip before source scan tested. | 1 |
| T02 schema | Local drift/reordered/NULL/incompatibility fixtures pass. Live-copy 9 families/10 leaves pass schema/count/bronze comparisons; absent registry/image-load and broader datasets remain unqualified. | 3 |
| T03 row counts | Within/across-file duplicates, NULLs, zero-row schemas, multiple shards and missing/extra rows. Shared count function passes local and live pidstat/host checks. | 2 |
| T04 fidelity | Event/day/hour/protocol separation; no event-time filtering/sorting. Local skip/leaf cases and full live-copy TCP/UDP/file/process/SELinux migration pass for the recorded hour. | 1, 4 |
| T05 sharding | Explicit approximate target, single-file/zero-row cases and multi-shard count checks pass locally. Large/skewed live leaf and settings matrix pending. | 2, 7, 10 |
| T06 failures/reruns | Validation failure leaves output, rerun skips, manual removal allows rebuild; partial protocol hour skipped wholesale. Broader copy/multipart/SIGKILL/spill fault matrix pending. No atomic publication requirement. | 3, 6 |
| T07 immutability/drift | Inventory add/remove/change tests and live 29-source SHA-256 before/after match. Rerun output hashes unchanged. Optional deletion operates on isolated copies; original live sources remain untouched. | 1, 5, 6 |
| T08 S3 | Actual profile/httpfs/COPY/window verify and fixed-root rerun skip pass. Credential expiry, denied/transient requests, multipart faults and additional endpoints pending. | 1, 5, 6 |
| T09 verify | Fresh operational per-leaf totals/delta/exit status pass locally and on retained-source fixed live output. Post-deletion DBT baselines provide consumer evidence; no manifests. | 2, 4, 8 |
| T10 benchmark | Representative process/file/TCP/UDP/pidstat/sparse hours, 64/128/256 MiB candidates, repeated cold/warm scans, rows/files/bytes/runtime/resources. Still pending; current pidstat output bytes grow 3.37×. | 7, 10 |
| T11 scheduling | Separate actual-upload-time correction must be verified before no-lookback scheduling. No automatic lookback added. | 9 |
| T12 deletion/migration | Full copied-live migration passes accepted gates: 54 models/139 gates per state, exact bronze/schemas/unaffected results, 2,668,265 conserved rows and 399 copied sources deleted with original hashes unchanged. ANY_VALUE-affected differences reported, not repaired or claimed equivalent. | 2, 4, 5, 6, 8 |

## Done Checklist

- [x] Corrected human scope, fixed-path decision and manual recovery recorded.
- [x] P0: isolated DuckDB 2.0.0/httpfs and bounded profile S3 data path verified.
- [x] P1: planner, direct roots, inventory, caps and existence-based skip tested.
- [x] P2: local name-aligned union-all/schema/count/shard fixtures pass.
- [x] P3: fixed-root live merge and unchanged-output rerun skip pass.
- [x] P4: fresh operational count verification passes for the bounded live output.
- [ ] Broader live event/protocol and failure/credential/resource matrix qualified.
- [ ] P5: representative benchmark selects shard/default settings and measures scans.
- [ ] P6: broader live manual acceptance and full closeout completed.
- [x] Canonical tool, verification, index/log updated for current interfaces.
- [x] Retain-source default plus explicit validated prefix deletion/grace tested.
- [x] Bounded post-delete confirmation diagnostics, two-phase hourly deletion,
  and explicit validation-gated deletion reconciliation implemented and tested.
- [x] Approved PyUtil dual-root input/config/preflight adaptation implemented.
- [x] Full synthetic raw/mixed/compacted migration and duplicate/NULL/protocol tests pass.
- [x] Copied live pidstat/host S3 migration/deletion and original-byte preservation pass.
- [x] Full-model copied-live S3 migration across 9 available input families qualified under approved ANY_VALUE diagnostic contract; registry/image-load absent.
- [x] Relocate the unchanged standalone compactor into PyUtil; integration paths/docs updated, 107 compactor and 299 PyUtil regressions pass; full local migration passes all 54 models/139 gates per state. No S3 operations rerun.
- [ ] Original live rollout explicitly scoped and authorized; not performed here.
- [ ] T11 upload-time prerequisite verified before scheduling.
