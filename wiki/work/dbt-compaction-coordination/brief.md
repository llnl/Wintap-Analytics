---
title: "Feature Brief: Scheduled DBT and Compaction Coordination"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint.md
policy: agent-editable
last_validated: 2026-11-14
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, dbt, compaction, coordination, cron, duckdb, s3]
---

# Scheduled DBT and compaction coordination

## Human direction

The human accepted a cron-driven coordinator with S3 request/grant/release
messages and explicitly selected **DuckDB for its local ledger**. The requested
deliverables are an editable sequence diagram and a companion artifact/design
document. This is next-phase planning; the implementation is proposed.

- One controlled server performs hourly compaction of eligible prior UTC hours.
- Three to five researchers run occasional time-ranged DBT builds locally,
  reading the shared S3 raw/compacted dataset and writing local results.
- DBT readers may overlap each other. Compaction and readers must exclude each
  other for the entire operation.
- Existing S3 access can carry coordination messages. Minute-scale waiting is
  acceptable; an always-running coordinator service is unnecessary.
- Keep the compaction engine behind a scheduling/coordination wrapper while its
  independent deeper qualification continues.
- Preserve the easy single-user, local-raw-data workflow. S3, coordination,
  compaction and durable process-entity state are optional deployment features.

## Proposed user-facing behavior

For shared S3 inputs, `make dbt-build` requests shared access, reports its waiting
status, runs source validation plus the complete build after a grant, and releases
after its child processes stop. A once-per-minute cron tick grants readers until
compaction is due, then drains existing readers, compacts exclusively, and resumes
reader admission when caught up. Missed hours remain queued in the ledger.

With one-minute ticks and ten-second client polling, the nominal polling budget
is 70 seconds before DBT starts plus 60 seconds for the coordinator to observe
release. The client returns after successful release upload; it does not wait for
that next tick. Processing/network time and contention are additional.

For entirely local inputs, the same `make dbt-build` directly validates and builds
the local dataset. With overrides unset, only `WINTAP_DATA_ROOT` is needed: read
its `raw_sensor/` tree, discover the local date range, and write the usual local
DuckDB output. A missing `compacted/` directory is accepted; an unset/empty
`WINTAP_DBT_PROCESS_ENTITY_ROOT` disables durable enrichment. The future wrapper
must preserve this path without coordinator setup, grants, waiting or job state.
See [[wiki/workflow/wintap-etl-data-flow#Local-only single-user workflow]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §defaults/dbt-build; ../Wintap-PyUtil/scripts/check_dbt_config.py §validate; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_process_entities; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

## Deliverables

- [[wiki/work/dbt-compaction-coordination/design]] — companion document: protocol,
  proposed Python files, cron/config, DuckDB tables, client integration and recovery.
- [[wiki/work/dbt-compaction-coordination/dev_handoff]] — implementation prompt,
  five work units, local compatibility, polling budget and acceptance checks.
- [[wiki/work/dbt-compaction-coordination/implementation-review]] — post-pull review
  of durable entities, checkpoint/recovery impacts and reproduced correctness gaps.
- [Editable draw.io sequence diagram](sequence.drawio) — two pages: shared DBT
  access; scheduled compaction draining readers and admitting the next reader.

## Acceptance criteria for eventual implementation

1. Every granted-but-unreleased reader excludes compaction, including a reader
   whose grant has not yet been delivered.
2. Due compaction stops new reader grants and waits for active readers to release.
3. A durable DuckDB transaction precedes publishing a grant or launching a writer.
4. Cron restarts, delayed messages and lost acknowledgments cannot erase ownership
   or cause duplicate starts. One local process lock serializes ledger access.
5. DBT holds one grant across all remote source preflight, build and test reads.
6. Writer failure/uncertain completion preserves a blocked dataset until resolved;
   source/output overlap cannot be cleared merely by releasing a mutex.
7. The oldest eligible uncompleted hour is remembered across delays/restarts.
8. Both main DBT and isolated compactor runtime environments remain usable.
9. A local raw-only build succeeds with the normal main DBT environment, no
   compacted directory, and no AWS, entity or coordination configuration. It
   requires no compactor runtime or durable entity bootstrap and creates no
   coordination messages, ledger or client job records.
10. Routing examines all effective input roots after defaults/overrides: a remote
    raw, compacted, entity or active processing-metrics root selects coordination; AWS credentials or
    stale coordination settings alone do not turn a local build into a remote job.
    An unused metrics override with entities disabled must be ignored consistently
    by routing and S3 setup.
11. Writer ownership spans entity publication, raw migration and final checkpoint
    verification. Preserve migration receipts independently of replayable coverage
    checkpoints; recovery reconciles all three phases before reopening.
12. Missing entity-hour coverage fails preflight clearly and releases the reader;
    a grant must not be held while waiting for the writer to create that coverage.
13. Before writer launch, durably retain an allowlisted, non-secret execution and
    effective-configuration receipt bound to the committed intent. Bind the actual
    executable/arguments, roots, UTC hour, run identities, events, entity policy,
    deletion options and budgets after resolving defaults/overrides. Missing or
    mismatched settings refuse launch; later uncertainty remains blocked. Never
    capture the whole environment or credentials, or treat an environment-omitting
    command manifest as sufficient configuration evidence.

Criterion 13 was expressly requested by the human during the November 14 dcc-02
review. It is an unimplemented requirement, not a property of the current
supervisor manifest. Details and acceptance checks:
[[wiki/work/dbt-compaction-coordination/design#Required execution and configuration receipt]].

## Ownership and boundaries

Wintap-PyUtil owns the proposed coordinator/client code and existing DBT/compactor.
Wintap-Analytics owns this design and its diagram. Sensor/packaging repositories
are context only. The new scheduling ledger is separate from the compactor's
disposable working state, S3 process-entity snapshots and processing checkpoints.

DBT currently scans both event roots using UNION ALL without overlap suppression.
The proposed exclusion addresses movement between those roots; sensor uploads
continue, so it does not create a frozen snapshot of active collection.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_partition_globs -->

## Proposed defaults still subject to review

Manual recovery of abandoned grants; no automatic age-based revocation. Cron
ticks every minute, clients poll every ten seconds, deletion grace is ten minutes,
and each tick runs at most one eligible compaction hour. Deployment roots, first
scheduled hour, event allowlist, optional entity configuration and operating
limits are selected at implementation/deployment time. Detailed future tests and
the source-review record are in the companion design.
