---
title: "Raw sensor hourly compaction"
type: tool
confidence: high
grounded_by:
  - ../Wintap-PyUtil/extras/raw-sensor-compact/README.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/inventory.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: extras/raw-sensor-compact
tags: [raw_sensor, parquet, duckdb, compaction, s3, fixed-root]
---

# Raw sensor hourly compaction

Wintap-PyUtil owns the isolated `extras/raw-sensor-compact/` Python/UV tool,
pinned to **DuckDB 2.0.0**, and the dual-root DBT consumer. The main pipeline's
DuckDB 1.5.6 environment and sensor code remain unchanged. Wintap-Analytics hosts
the shared wiki, feature planning and verification records. The human requested
this ownership relocation on 2026-11-12; compaction behavior is unchanged.
Current decision: [[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]].
The earlier UUID generation/manifest design is superseded, not an available mode.

**S3 cleanup (2026-11-12):** the human subsequently requested removal of all
artifacts created by this work. Removed 443 objects in its test prefixes plus
the two initial pidstat/host outputs at `lintap/compacted` for day 20261111/hour
08. All 399 original raw-source hashes matched before/after; no source deletion
or production cutover. Historical test results below are preserved, but their
S3 fixtures no longer exist. Saved-copy commands are historical; new live tests
require fresh approved fixtures. See
[[wiki/work/raw-sensor-file-aggregation/verification]] §S3 Artifact Cleanup.

## Layout And Commands

```text
source: lintap/raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/...
dest:   lintap/compacted/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/<merged>.parquet
```

`plan`, `compact`, `verify` use explicit **direct event roots**: `--source-root`,
`--destination-root`, whole UTC `--start-hour`/`--end-hour` (inclusive/exclusive),
optional repeated `--event-type`. `compact` needs `--target-size-bytes`; the
benchmark-selected default remains open. Full examples:
[package README](../../../Wintap-PyUtil/extras/raw-sensor-compact/README.md).
From the PyUtil repository root:

```bash
uv run --project extras/raw-sensor-compact --locked raw-sensor-compact --help
```
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py -->

## Merge, Skip And Failure Semantics

For each event/day/hour, **if destination exists, skip; else merge**. Skip occurs
before source discovery/Parquet reads. Any S3 object under the hour or an existing
local hour directory counts, including partial output/markers/empty local folders.
The hour parent governs optional TCP/UDP leaves: existing TCP skips the whole hour.

Merge is name-aligned `UNION ALL`, with no sorting/deduplication/event-time filter.
All recorded telemetry rows/fields survive; missing columns become NULL. Identical
types or signed-integer widening accepted; other drift fails before writing that
hour. Non-NULL physical hive values must agree with directories. Each leaf's actual
output schema/counts are reread and its source/merged row totals/delta reported.
Multi-file success requires fewer output objects; filename consistency is not required.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py -->

**Existence is not verified completion.** Failed/partial files remain directly
visible and reruns skip them until manually cleaned. One writer per destination;
do not read an hour during merge. No run IDs/manifests/conditional PUT/atomic
publication or automatic failed-output cleanup. Source is retained by default.
`compact --delete-source` validates **every leaf in the event/hour** before
deleting its whole source prefix, including markers. `--grace-minutes` defaults
to 10 (minimum 5); preflight rejects selected hours younger than UTC end plus grace.
The human accepts rare clock skew under the deployment's UTC upload-partition
contract. S3 pagination/batch deletion errors or remaining objects fail; local
deletion refuses symlinks. An existing destination is never a source-delete trigger.
Original live rollout is not authorized; deletion tests use isolated copies.
Daily rollup/scheduling/lookback remain deferred.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/interview.md §Dual-Root DBT And Prefix Deletion Approval; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py -->

`verify` opens a fresh DuckDB connection and compares the union of source/output
leaf keys. Count mismatch exits 1; invalid input/read/schema/drift errors exit 2.
Empty/skip is explicit. Count equality cannot detect same-count edits or balanced
dropped/extra rows. Inventory rechecks assume immutable sources/quiescent windows,
not atomic snapshots; late arrivals do not rebuild existing destinations.
Run source/output `verify` before deletion or in retain-source mode; after
migration compare unioned inputs/DBT results to a saved baseline. Merge reports
retain both totals and delta before source deletion. Deletion failures identify
source/destination hour and phase; reconcile manually before DBT.

## Runtime And Evidence

Frozen boto3/DuckDB identity and resolved profile endpoint, path-style HTTP(S),
temporary secrets and httpfs setup; no credential refresh. Default 2 threads,
1 GB memory/spill, 300-second cooperative timeout, 24 hours/10,000 processed source
files. Skips do not consume file caps. Secrets/backend details are suppressed;
report paths and spill still require appropriate privacy handling.

Live fixed-root test at `lintap/compacted`, pidstat/host on 2026-11-11 08:00 UTC:
**897,395 rows preserved, 29 → 2 objects, all 29 source hashes unchanged**. Fresh
verification passed; second run skipped both hours and output hashes stayed
unchanged. Pidstat bytes grew 3.37× under current settings; this is not a measured
compression/scan improvement. Broader live families, multipart failures/expiry,
and representative shard benchmark remain open.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/verification.md §Fixed Destination Tests -->

PyUtil now scans `<dataset>/raw_sensor/<event>/...` plus
`<dataset>/compacted/<event>/...`, with optional direct `WINTAP_DBT_COMPACTED_ROOT`
override. Partition globs, event existence, aliases, optional columns and preflight
include both stores. No overlap suppression; run DBT after successful migration
and rebuild bronze as well as materialized downstream models. Existing bronze
views bind discovered file globs and must not be reused after raw deletion.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql; ../Wintap-PyUtil/wintap_dbt/README.md §Compaction migration contract -->

Compaction baseline qualification: **107 compactor passes/2 opt-in skips** and **299 PyUtil
passes/2 opt-in skips**. Full local migration matches all 54 models (139 gates
per raw/mixed/compacted state). Copied live S3 host/pidstat migration matches 4
models/897,395 rows, deletes 29 copied objects and preserves all original hashes.
Full available-family live qualification is recorded below; broader datasets,
resource/transport qualification and rollout remain pending.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/verification.md §Dual-Root DBT And Prefix-Deletion Tests -->

Expanded live-copy full builds pass 139 gates in raw and mixed states, but strict
results differ. A fresh unchanged-input mixed rebuild also differs: existing
unordered `ANY_VALUE` representatives can change derived identities/downstream
counts. The human accepts this existing quality debt as **non-blocking** for
compaction. Explicit diagnostic mode retains exact bronze/schema/unaffected-model
gates and reports affected differences. The initial fixture stopped after host
migration (394 raw copies intact); a fresh all-family rerun **passed**. Across
raw/mixed/compacted states, all 54 models build with 139 gates, all 11 bronze
results/all schemas match, and 2,668,265 rows are conserved. The rerun deletes
399 copied sources → 10 outputs and verifies all 399 original hashes unchanged.
Thirty-six model results match across every state; differences in 18 affected
models remain diagnostics, not repaired semantics or full downstream-equivalence.
Historical full DBT fixture (now removed):
`s3://lintap-alpha/compaction-tests/dbt-union-all-20261112-02`, day 20261111/hour 08.
Registry/image-load remain absent. See
[[wiki/tension/dbt-arbitrary-representatives-vs-compaction-equivalence]].
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/verification.md §Full-Model Live-Copy Expansion; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql -->
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/verification.md §Accepted ANY_VALUE Diagnostics And All-Family Rerun; ../Wintap-PyUtil/wintap_dbt/README.md §Read-only full-model test of the surviving compacted copy -->

Feature context: [[wiki/work/raw-sensor-file-aggregation/brief]],
[[wiki/work/raw-sensor-file-aggregation/implementation_plan]],
[[wiki/work/raw-sensor-file-aggregation/verification]], and scheduling dependency
[[wiki/todo/raw-sensor-upload-time-partition]].

## Optional durable entity phase — 2026-11-12

[[wiki/tool/durable-process-entity-manager]] now adds an opt-in process-entity
phase before raw merge/deletion, with source inventory binding and persisted
snapshot verification. Raw COPY/duplicate/NULL/skip/grace semantics remain unchanged.
DBT ancestry uses separate state/context relations, not injected raw events.
Current combined regressions are 132 extra and 310 main passes; isolated synthetic
S3 qualification restores 33 seed paths without changing summary populations.
Production scheduling/capacity/bootstrap remains deferred; earlier compaction
qualification above is historical, separate evidence.
