---
title: "Verification: Durable Process Entity Manager"
type: concept
confidence: medium
grounded_by:
  - wiki/work/durable-process-entity-manager/brief.md
  - wiki/work/durable-process-entity-manager/design.md
  - wiki/work/durable-process-entity-manager/implementation_plan.md
  - wiki/diagnostic/process-tree-context-completeness.md
  - wiki/workflow/process-ancestry-completeness-qa.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/tests/process_entity_context_integrity.sql
  - ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql
  - ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/tests/test_process_entities.py
  - ../Wintap-PyUtil/tests/test_process_entities_s3.py
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: reviewed
source_paths: wiki/work/durable-process-entity-manager
tags: [feature-work, verification, entity-state, ancestry]
---

# Verification: Durable Process Entity Manager

## Current result

Follow-up review of the pulled `c782f63` implementation:
[[wiki/work/dbt-compaction-coordination/implementation-review]]. Fresh focused
regressions pass, while local probes reproduce snapshot/checkpoint freshness,
SQL integrity-validation and incremental bootstrap-provenance gaps. The imported
qualification below remains evidence for its executed scenarios; it does not
qualify those additional recovery/corruption cases.

### Durable processing checkpoint coverage — 2026-11-13

The hourly entity-enabled writer now maintains the dedicated sibling prefix
`<dataset>/processing_metrics/`, with one verified Parquet checkpoint per requested
UTC hour. The checkpoint schema includes operation/entity status, namespace and
expected-host count, snapshot identities, source/compacted process inventory
fingerprints, file/byte/row totals, deletion outcome and completion time. It is
separate from raw telemetry and from the durable entity snapshots.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py -->

DBT preflight now derives required hours from the selected `raw_process` raw or
compacted inputs and requires exactly one successful entity-enabled metric row for
each hour with the configured namespace and schema version. Missing, duplicate,
failed, or incompatible checkpoint coverage fails closed instead of consuming a
stale entity snapshot. A regression that removes the checkpoint files passed by
failing the DBT operation as expected.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

Focused verification after formatting/import cleanup:

* standalone compactor entity/CLI tests: **35 passed**;
* DBT durable-process-entity regression tests, including missing-checkpoint
  coverage: **12 passed**;
* changed standalone Python files pass `ruff format --check` and `ruff check`.

Commands:

```text
uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests/test_entities.py extras/raw-sensor-compact/tests/test_cli.py -q
uv run --project . --dev python -m pytest tests/test_process_entities.py tests/test_dbt_source_validation.py -q
uv run --project extras/raw-sensor-compact --locked ruff format --check <changed standalone Python files>
uv run --project extras/raw-sensor-compact --locked ruff check <changed standalone Python files>
```

A one-hour synthetic entity initialization also produced the expected fixed
Parquet schema and exclusive hour end (`00:00`–`01:00` UTC) under the local
`processing_metrics/` sibling. The opt-in S3 test was discovered and skipped
because its explicit isolated-write approval variables were not set.

The opt-in S3 qualification remains separate and was not treated as a local test
result; no live dataset or credential was written by this verification step.

### Three-day raw-source qualification and DBT baseline — 2026-11-14

The isolated three-day raw qualification covered 72 UTC hours and all 12 event
families discovered in the source. Raw compaction merged **27,402 source files**
into **752 outputs**, preserving **151,733,675 rows**; the source/destination
verification passed all **752/752 partitions** with zero row deltas. Source
deletion was disabled. The retained qualification output is isolated from the
source dataset.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py -->

An earlier entity attempt did not qualify: it failed before publication on **18**
raw process rows: **16** negative-PID `unknown-sys` Refresh records and **2**
positive-PID Stop records carrying the producer unknown-hash sentinel. The
threshold-enabled rerun instead reached the decoded-state byte budget first and
also published no durable entity snapshots or processing-metrics checkpoints. An
explicitly configured retry raised the entity limits to **10,000,000 rows** and
**2 GiB decoded state**, with **8 GiB DuckDB memory** and **16 GiB temporary
storage**; it failed closed on the same decoded-state byte-budget condition.
Both outcomes are fail-closed; no rows were silently filtered and no identity or
ancestor was invented.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §unknown/load_inputs -->

Because the durable cache was not initialized, the requested entity-enabled DBT
build and post-cache tree qualification were not run. A clearly separate
non-entity DBT baseline over the isolated compacted output completed successfully:
**54 models, 84 data tests, 140/140 resources passed**. The gold
`process_summary` relation contained **2,613,680** process rows. Direct parent
classification found **2,341,914 (89.60%)** parent-present rows, **271,478
(10.39%)** missing ancestors, **282 (0.01%)** parent-PID mismatches, 5 missing
parents and one root/self row.

The corresponding baseline `process_path` terminal classification reached only
**3 roots (0.0001%)**, with **2,589,960 (99.09%)** terminal missing-ancestor
verdicts and **23,717 (0.91%)** missing-parent verdicts. This poor terminal result
is explainable for a three-day activity-only window without historical durable
ancestors; it is not evidence that the durable cache works. A valid next gate is
an explicit identity-policy decision and rerun of entity bootstrap, followed by
the entity-enabled DBT build and gold comparison.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql; ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql -->

### Identity-policy resolution — 2026-11-13

The unknown-identity decision is now explicit rather than implicit. `reject`
remains the default and fails before entity publication. The authorized
qualification policy is `quarantine`: raw evidence with an unknown/sentinel hash,
missing or negative PID, or invalid hostname remains in raw telemetry but is not
reduced into durable entity snapshots. The writer records the policy, per-hour
counts, reason/host breakdowns and stable fingerprints in the durable
`processing_metrics` checkpoint. DBT entity mode requires an explicitly matching
`WINTAP_DBT_PROCESS_UNKNOWN_IDENTITY_POLICY`; it does not treat quarantined rows
as entity coverage.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §identity_reasons/load_inputs; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §SCHEMA/metric_rows; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

### Bounded quarantine threshold — 2026-11-13

The explicit qualification policy now permits quarantine only up to a configurable
**5% per-UTC-hour** identity-exclusion ceiling. The entity loader records the
distinct process-input denominator, excluded-row numerator, observed ratio,
configured ceiling, reason/host breakdowns and stable fingerprints for every
partition, including hours with zero exclusions. Any hourly ratio above the
ceiling fails before entity publication; raw evidence remains untouched. The
checkpoint schema is version 3, and DBT preflight requires the recorded ceiling,
denominator, numerator and ratio to match its configuration.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §load_inputs; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §SCHEMA/metric_rows; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

Focused validation passed: **140** standalone tests with two expected skips,
**56** DBT/config tests, and formatter/linter checks for the changed standalone
Python files. The isolated three-day quarantine bootstrap was restarted with the
explicit 0.05 ceiling after correcting the command's hour-window limit. It then
failed closed on the existing decoded-state byte budget before publication;
there are no entity snapshots or processing-metrics checkpoints in the fresh
qualification prefixes. This is a capacity blocker, not evidence to relax the
budget or to treat the pre-threshold attempt as qualification.

### SQL-backed capacity rerun — completed, 2026-11-13

The reducer was changed to keep working entity state in DuckDB 2.0.0 relations:
distinct evidence values, bounds, parent classification and scalar projection are
managed by SQL, while Python retains only paths and publication metadata. Parquet
remains the durable snapshot format and retains `evidence_json` for DBT
interoperability. Local validation passes with **140 standalone tests and 2
expected skips**, **56 DBT/config tests**, and changed-file formatter/linter
checks. <!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

An isolated three-day bootstrap completed with the explicit quarantine ceiling
and node-local limits of **16 threads**, **128 GB DuckDB memory** and **256 GB
temporary storage**. The command used `max-entity-rows=10,000,000` and
`max-entity-bytes=64 GiB`; its output prefixes are isolated from both the source
dataset and earlier failed attempts. All **7** requested host snapshots were
published and the SQL verification command passed all of them: **2,613,678
entities** and **280,529,521 bytes** of Parquet. The aggregate input projection
contained **12,878,058** source-plus-compacted rows; **28** duplicate-source
identity exclusions were quarantined at ratio **2.1742408676836212e-06**, below
the **0.05** ceiling. The exclusion reasons were `negative_pid=24` and
`unknown_pid_hash=4`.

### Entity-enabled DBT and post-cache ancestry QA — completed, 2026-11-13

The entity-enabled DBT build used the isolated compacted-only root and matching
processing checkpoints, avoiding a reread of the original raw copies. Its source
preflight and build completed with **59 models, 85 data tests and 2 hooks/
operations: 146 PASS, 0 WARN, 0 ERROR, 0 SKIP**. The materialized
`process`, `process_summary` and `process_path` relations each contain
**2,613,680** rows. Compared with the non-entity baseline, process key sets,
per-key row counts, process-summary counts and process-path counts are identical;
the two process keys excluded from the durable entity snapshot remain visible as
window rows and are explicitly reported as missing entity context.

The expected enrichment differences are retained rather than hidden: durable
parent resolution changes parent-hash/PID selections where retained evidence
resolves conflicts or sentinels, and cached display candidates change selected
name/path/argument values for metadata-conflicted keys. One OS-PID selection
difference belongs to an excluded key with multiple source names; it does not
change row or key counts. The comparison therefore confirms row/count semantics
while treating enriched field differences as intentional entity-mode behavior.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_entities.sql; ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql -->

Post-cache tree QA executed against `process_context`, `process_path` and
`process_ancestry_quality`. The context relation contains **2,618,147** rows:
2,340,776 linked, 255,347 missing-ancestor, 11,474 sentinel, 6,076
parent-conflict, 4 missing-parent, 4,469 missing-entity and 1 root row. The
terminal ancestry relation contains **2,613,680** window seeds: **2 root-reached**,
**2,569,888 missing-ancestor**, **23,726 missing-parent**, **8,583
parent-conflict**, **11,479 sentinel** and **2 missing-entity** verdicts. There
were **0 cycles**, **0 unresolved verdicts**, **0 resolved-parent PID mismatches**,
and all **2,613,678** available terminals came from the durable entity store.

This proves that the SQL-backed cache is readable, structurally validated and
does not fabricate ancestry, but it does **not** pass a complete-tree gate: only
2 of 2,613,680 terminal seeds reached a declared root, while the three-day
bootstrap has no history before the selected window. The cache/DBT qualification
is consequently successful for durable-state construction, evidence preservation,
DBT execution and row/count compatibility; historical ancestry completeness and
production rollout remain unqualified. The machine-readable aggregate QA report
is retained outside the wiki; no raw telemetry or actual host identifiers are
copied into persistent documentation.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql; ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql -->

### Repeat three-day round — completed, 2026-11-13

One additional isolated round reproduced the durable-cache result from a fresh
S3 prefix. Raw compaction merged **27,402** source files into **752** outputs,
preserved **151,733,675** rows with zero row delta across **752/752** partition
checks, and performed no source deletion. SQL entity initialization then
published and verified **7** snapshots containing **2,613,678** entities and
**280,529,605** bytes of Parquet, plus **71** processing-metrics checkpoints.
The identity result repeated exactly: **28** quarantined rows at
`2.1742408676836212e-06`, below the **0.05** hourly ceiling.

The fresh entity-enabled DBT build completed **146/146 PASS**; the matching
non-entity baseline completed **140/140 PASS**. Process, process-summary and
process-path row counts and key sets again matched exactly. The ancestry QA
distribution also repeated: **2 root-reached**, **2,569,888 missing-ancestor**,
**23,726 missing-parent**, **8,583 parent-conflict**, **11,479 sentinel** and
**2 missing-entity** terminal verdicts, with **0 cycles**, **0 unresolved
verdicts** and **0 resolved-parent PID mismatches**. This confirms reproducible
SQL-state construction and DBT behavior; it does not change the limitation that
the selected three-day bootstrap lacks earlier history and is not ancestry-complete.
<!-- EVIDENCE: ../Wintap-PyUtil/.opencode-work/dpe-3day-round2/reports/compact.json; ../Wintap-PyUtil/.opencode-work/dpe-3day-round2/reports/entities-init.json; ../Wintap-PyUtil/.opencode-work/dpe-3day-round2/reports/entities-verify.json; ../Wintap-PyUtil/.opencode-work/dpe-3day-round2/reports/post-cache-qa.json -->

The preserved compacted process files were also audited read-only for per-hour
identity denominator/numerator evidence; that evidence is recorded below. The
later SQL-backed bootstrap and DBT run supersede the earlier no-publication
blocker, while the ancestry completeness result above remains an explicit
qualification limitation.

### Read-only identity audit — 2026-11-13

The audit replayed the exact distinct-input projection and identity predicate
against the preserved compacted `raw_process` files. It covered **71
process-bearing UTC hours** (the 72-hour window had one hour with no process
input), **6,439,029** distinct inputs, and **14** exclusions. The aggregate ratio
was **2.1742408676836212e-06** (**0.000217424%**) versus the **0.05** ceiling;
the largest hourly ratio was **2.19346347883e-05** (**0.00219346%**). The
exclusion reasons were `negative_pid=12` and `unknown_pid_hash=2`; no invalid
hostname or missing-PID exclusions occurred. All 14 exclusions mapped to one
anonymized host token, `host-3eb51f0e72ac`. The aggregate evidence fingerprint
was `134df80547c50489e578b0a8aa3d73ff063b146ec2cc9326405c431d7445b698`.

Command form: the project-local `uv run --project extras/raw-sensor-compact
--locked python` DuckDB audit was run against the preserved compacted root with
read-only S3 access; no source, compacted, entity, or metrics object was opened
for writing.

The table reports every process-bearing hour. Host tokens are stable one-way
identifiers, not hostnames. An em dash means zero exclusions and therefore an
empty reason/host/fingerprint value.

| UTC hour | input rows | excluded | ratio | reasons | anonymized hosts | fingerprint |
|---|---:|---:|---:|---|---|---|
| 20261110 00Z | 91,786 | 1 | 1.08949077201e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `ca89b46f360a22502760b26e3a1239fcdbe67e0be74cbf3ce919fc01c9f53ea7` |
| 20261110 01Z | 78,287 | 1 | 1.27735128438e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `900bc5892c1be2fc6f34ca3fe9fc51202f07aa17f0619ce9aab428c4f4ad23c3` |
| 20261110 02Z | 78,967 | 0 | 0 | — | — | — |
| 20261110 03Z | 84,191 | 0 | 0 | — | — | — |
| 20261110 04Z | 84,829 | 0 | 0 | — | — | — |
| 20261110 05Z | 118,472 | 0 | 0 | — | — | — |
| 20261110 06Z | 108,882 | 0 | 0 | — | — | — |
| 20261110 07Z | 104,550 | 0 | 0 | — | — | — |
| 20261110 08Z | 101,010 | 0 | 0 | — | — | — |
| 20261110 09Z | 89,491 | 0 | 0 | — | — | — |
| 20261110 10Z | 86,870 | 0 | 0 | — | — | — |
| 20261110 11Z | 81,709 | 0 | 0 | — | — | — |
| 20261110 12Z | 83,603 | 0 | 0 | — | — | — |
| 20261110 13Z | 86,230 | 1 | 1.15968920329e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `bbb7b47df75bb0457c2a961628d796a52110b57259bfb566c87d1cc065322bdd` |
| 20261110 14Z | 93,252 | 0 | 0 | — | — | — |
| 20261110 15Z | 96,929 | 1 | 1.03168298445e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `c1378e8291f9a1f0a04d8c0cf388169b18e74431bf112fd73f81332066267d58` |
| 20261110 16Z | 92,450 | 1 | 1.08166576528e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `72335932e718c5509f32a0da535d6b91b4ca4b6b52860e2adac0b55fba6b9a0d` |
| 20261110 17Z | 89,986 | 0 | 0 | — | — | — |
| 20261110 18Z | 90,221 | 0 | 0 | — | — | — |
| 20261110 19Z | 90,122 | 1 | 1.10960697721e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `4e2ae52e535b6537aab17cced3fd455dc0b2ce216a4ddbe80786b5ee1527ae1b` |
| 20261110 20Z | 91,996 | 1 | 1.08700378277e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `7ba20aa7fa13fb0608e0dc506bc1e0701ddb36f6cb285c7e98c9a159147ec320` |
| 20261110 21Z | 90,157 | 0 | 0 | — | — | — |
| 20261110 22Z | 114,037 | 0 | 0 | — | — | — |
| 20261110 23Z | 109,182 | 1 | 9.1590188859e-06 | negative_pid=1 | host-3eb51f0e72ac=1 | `64869ba10f68e0ec2575ebd2e668336bb114316b3bba4ddd4da060b25a96c486` |
| 20261111 00Z | 98,745 | 1 | 1.01270950428e-05 | unknown_pid_hash=1 | host-3eb51f0e72ac=1 | `fa29ccd1fef8a3a70d9f5059af1e4bd5e79f47c282a16f017b2c615720511e3f` |
| 20261111 01Z | 77,860 | 0 | 0 | — | — | — |
| 20261111 02Z | 79,385 | 0 | 0 | — | — | — |
| 20261111 03Z | 82,732 | 0 | 0 | — | — | — |
| 20261111 04Z | 83,569 | 0 | 0 | — | — | — |
| 20261111 05Z | 133,298 | 0 | 0 | — | — | — |
| 20261111 06Z | 98,404 | 0 | 0 | — | — | — |
| 20261111 07Z | 105,379 | 0 | 0 | — | — | — |
| 20261111 08Z | 101,996 | 0 | 0 | — | — | — |
| 20261111 09Z | 91,126 | 0 | 0 | — | — | — |
| 20261111 10Z | 86,813 | 0 | 0 | — | — | — |
| 20261111 11Z | 82,782 | 0 | 0 | — | — | — |
| 20261111 12Z | 83,031 | 0 | 0 | — | — | — |
| 20261111 13Z | 99,394 | 0 | 0 | — | — | — |
| 20261111 14Z | 86,992 | 0 | 0 | — | — | — |
| 20261111 15Z | 95,811 | 1 | 1.04372149336e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `6c67a45da12b73d9e65659e3145927602809077c7d9fb3459a16763524ddb69e` |
| 20261111 16Z | 99,705 | 1 | 1.00295872825e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `bfd15084dbcd5ec2c18533c279f02a403be8cdd1feeb257a3aa00ddf54e6337a` |
| 20261111 17Z | 91,180 | 2 | 2.19346347883e-05 | negative_pid=1; unknown_pid_hash=1 | host-3eb51f0e72ac=2 | `e5b181097cebb11d54ee94697d46fa862a0931eee27e7943e1bbaaf25124346d` |
| 20261111 18Z | 91,300 | 1 | 1.09529025192e-05 | negative_pid=1 | host-3eb51f0e72ac=1 | `f93caf6090cdeeae6f4a138fc81174fba9e432e3bf26041d91407b95a2ec995b` |
| 20261111 19Z | 88,513 | 0 | 0 | — | — | — |
| 20261111 20Z | 85,903 | 0 | 0 | — | — | — |
| 20261111 21Z | 82,039 | 0 | 0 | — | — | — |
| 20261111 22Z | 79,631 | 0 | 0 | — | — | — |
| 20261111 23Z | 82,203 | 0 | 0 | — | — | — |
| 20261112 00Z | 84,729 | 0 | 0 | — | — | — |
| 20261112 01Z | 81,004 | 0 | 0 | — | — | — |
| 20261112 02Z | 75,068 | 0 | 0 | — | — | — |
| 20261112 03Z | 81,269 | 0 | 0 | — | — | — |
| 20261112 04Z | 84,212 | 0 | 0 | — | — | — |
| 20261112 05Z | 134,635 | 0 | 0 | — | — | — |
| 20261112 06Z | 95,768 | 0 | 0 | — | — | — |
| 20261112 07Z | 103,714 | 0 | 0 | — | — | — |
| 20261112 08Z | 103,985 | 0 | 0 | — | — | — |
| 20261112 09Z | 98,301 | 0 | 0 | — | — | — |
| 20261112 10Z | 79,678 | 0 | 0 | — | — | — |
| 20261112 11Z | 81,028 | 0 | 0 | — | — | — |
| 20261112 12Z | 84,377 | 0 | 0 | — | — | — |
| 20261112 13Z | 93,034 | 0 | 0 | — | — | — |
| 20261112 14Z | 80,883 | 0 | 0 | — | — | — |
| 20261112 15Z | 82,034 | 0 | 0 | — | — | — |
| 20261112 16Z | 83,245 | 0 | 0 | — | — | — |
| 20261112 17Z | 82,167 | 0 | 0 | — | — | — |
| 20261112 18Z | 76,514 | 0 | 0 | — | — | — |
| 20261112 19Z | 80,998 | 0 | 0 | — | — | — |
| 20261112 20Z | 84,224 | 0 | 0 | — | — | — |
| 20261112 21Z | 83,277 | 0 | 0 | — | — | — |
| 20261112 22Z | 79,885 | 0 | 0 | — | — | — |

The complete machine-readable audit evidence is retained at
`../Wintap-PyUtil/.opencode-work/dpe-3day-quarantine-v2/reports/identity-exclusion-evidence.json`.
This is read-only evidence and does not convert the blocked capacity run into a
durable-state qualification.

### Bounded read-only on-prem fixture check — 2026-11-13

The selected `seeded_fixture_counts` test passed against the approved synthetic
one-hour fixture: **1 passed, 1 deselected in 2.18 seconds**. The expected
**24 rows** were present and the source/destination row delta was zero. A separate
read-only object listing found **24 source objects / 17,544 bytes** and **one
compacted object / 970 bytes**; neither listing was truncated. The pytest duration
includes process and test overhead and is not a pure network measurement.

The run used the approved Garage profile, endpoint and path-style access from the
on-prem development host. Only the read-only `verify` path ran; no S3 writes,
deletions, DBT, or access to preserved qualification data occurred. Dependencies
were installed into an isolated temporary environment outside the repository.
The fixture URI and profile values are intentionally omitted from this persistent
record. The archived laptop/VPN week aggregate is not an apples-to-apples baseline;
run this same bounded fixture check from the laptop before drawing a path comparison.

### Actual-data extension — run completed with failures, 2026-11-13

The human authorized several days/a week of testing after asking whether the
earlier real-data timeframe had been qualified. The earlier actual hour now passes
raw/mixed/compacted DBT and independent entity checks. The week driver completed
**168 hours: 165 successful raw compactions, 3 deletion-verification failures**.
Historical bootstrap failed identity validation; only **one combined entity/raw
hour** passed before the driver explicitly continued raw-only qualification.
This is not a successful week-long entity qualification or full historical DBT repair.

### Nov 7 compacted-only DBT build with durable enrichment — 2026-11-13

The completed mitigated Nov 7 destination was built with the repository's exact
`make dbt-build` target. The final invocation used the disposable source parent
(whose `raw_sensor` subtree was empty after successful deletion) together with the
240-file compacted destination; it did not union the immutable baseline with its
compacted copy. Durable enrichment used the retained nine-host snapshot root and
its declared identity namespace. `dbt-check-source` passed, including S3 listing,
Parquet access and schema preflight.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §dbt-build; ../Wintap-PyUtil/wintap_dbt/README.md §Durable process context -->
<!-- EVIDENCE: /tmp/opencode/dpe-nov7-mitigated/run.json; /tmp/opencode/dpe-nov7-mitigated/full-day-verify.json -->

The build materialized all **58 models** and evaluated **85 data tests**. Across
145 total DBT resources, **127 passed**, **17 were skipped**, and one errored. It
returned exit code 1 because the existing
`unique_selinux_interaction_event_id` test reported **19** duplicate rows. This
failure is unrelated to durable process context. The enabled
`process_entity_context_integrity` test passed, as did entity snapshot preflight;
no duplicate durable entity keys or invalid stored parent evidence were reported.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/tests/process_entity_context_integrity.sql; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql -->

Process-tree completeness **failed** on the retained week-limited state: the
`process_ancestry_quality` table contains **919,508** window seeds, of which only
**2** reached a root. The remaining verdicts are **908,487 missing ancestors**,
**2,861 parent conflicts**, **8,156 sentinel terminals**, and **2 missing
entities**. There were zero cycles, unresolved verdicts, or parent-PID mismatch
verdicts. The context relation independently reports 820,609 linked rows, 88,701
missing ancestors, 3,010 missing entities, 2,042 parent conflicts, 8,153
sentinels, and one root. Thus the optional enrichment executes and passes its
structural integrity gate, but this snapshot does **not** provide complete Nov 7
process trees; the previously documented stale week-limited state must not be
promoted to a production DBT input.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql -->
<!-- EVIDENCE: /tmp/opencode/dbt-nov7-mitigated/process-tree-validation-compacted-only.json -->

#### Investigation of the high missing-ancestor count — 2026-11-13

The **908,487** value is not a count of distinct missing parent processes. It is
one terminal verdict per window seed, so descendants sharing one broken ancestor
are counted repeatedly. In the direct context relation there are **88,701**
`missing_ancestor` rows but only **2,203** distinct missing parent keys. The top
one breakpoint accounts for **577,191** affected seeds; the top three account for
**800,504 (88.1%)**, and the top ten account for **876,276 (96.5%)**. This is the
same descendant-amplification pattern documented by the earlier short-window
audit; its absent-key metric explicitly was not a count of proven missing real
processes.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql; ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql -->
<!-- SYNTHESIS: wiki/diagnostic/process-tree-context-completeness.md; wiki/workflow/process-ancestry-completeness-qa.md -->

The durable cache nevertheless had **no effective coverage for this Nov 7
window**. All **33,824** loaded snapshot rows have `first_partition` and
`last_partition` equal to `2026110500`. Of **919,508** current process keys,
**zero** overlap a durable row; there are **zero** current-child-to-durable-parent
links; and the materialized `process_context` relation contains **zero**
`from_store` rows. The cache had rows, but they were stale state from the first
hour of the earlier week run, not a bootstrap/replay through Nov 7. Previous work
records that historical bootstrap failed identity validation and week maintenance
halted, and explicitly labels this nine-snapshot state stale and unsuitable for
production DBT input.
<!-- EVIDENCE: /tmp/opencode/dbt-nov7-mitigated/process-tree-investigation.json -->
<!-- SYNTHESIS: wiki/work/durable-process-entity-manager/verification.md §Completed week; wiki/work/durable-process-entity-manager/dev_handoff.md §Next, in order -->

The configured root-PID set was not the primary explanation: the current materialized
process graph contains only one self-parent root candidate (the PID-4 case) and no
PID-2 process records. The missing-root result is therefore consistent with absent
historical process context, not with counting every Linux PID-2 process as a gap.
The correct next experiment is a validated historical entity bootstrap/rebuild
covering the Nov 7 source, followed by the same direct-gap and breakpoint-impact
queries; no parent should be invented or repaired by PID alone.

### Intermediate milestone disposition — 2026-11-13

The three failed-hour partial outputs were compared with the retained immutable
local input evidence: all **25 compacted Parquet objects** match their corresponding
input rows exactly. The **142 source objects still present at final inspection**
also match their immutable copies. The three failed event/hour source prefixes were
empty on the later S3 inspection. The human accepts the failed-hour compacted data
as correct for this milestone and chooses to proceed on that assumption. This is
an operational disposition supported by the local evidence comparison; it does
not turn the three commands into successful runs, explain why immediate deletion
verification failed, or establish a reusable production deletion guarantee.

No production repair, additional mutation of qualification data, or DBT run is
authorized by this milestone. The original failure should remain visible in the
run record, while further root-cause work is optional follow-up rather than a
blocker to this intermediate handoff.

Read-only discovery located the original six-host materialized audit and its
explicit process globs for November 11 hours 08–22 (configured inclusive end 23).
An independent walk reproduces the earlier major breakpoint concentration. A
rebuild now uses a larger retained source inventory, so comparisons must distinguish
original saved populations from today's data and recorded-self-root policy from
the older PID-1/2/4 root convention.

Inventoried **71,155 objects / 5,958,506,820 bytes**: all nine available telemetry
families for **November 5–11**, plus process-only history **October 25–November 4**.
The frozen inventory excludes November 12/13 despite their discoverability.
Copying verifies each original inventory identity and SHA-256 against a full GET
of its isolated S3 copy; original keys are read-only. Planned tests cover the
earlier 08:00–09:00 hour, 168 sequential hours, historical bootstrap/default-budget
capacity, replay and DBT bronze/window/summary invariants. Failed hours/snapshots
will be retained rather than silently cleaned up or treated as passing.

Private scripts/inventories and ongoing evidence are retained at
`/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/dpe-actual-week-1vnezp50/`.
The first copy command hit its explicit two-minute harness timeout, then resumed
from already hash-verified copies without discarding data. An initial hour-harness
query referenced a nonexistent Refresh-count column; corrected to the model's
existing Start/Stop counters. These are harness repairs, not shipped-code changes.
No deployment, private environment edits, commits, pushes or output cleanup.

Human also requested compaction file-count/size metrics. The qualification harness
now aggregates validated leaf reports into overall, per-day, per-hour and per-event
input/output files and bytes, reduction percentages/factors, output-size distribution,
rows conserved, elapsed time and throughput. Entity snapshot bytes are separate.
Failed/partial outputs and untouched bootstrap copies are excluded from success
savings; byte expansion is reported as negative savings rather than hidden.
Metrics helper checks pass for reduction, expansion, grouping, throughput and
failed-command exclusion. Completed week aggregates and exclusions follow below.

#### Earlier real hour completed — November 11, 08:00–09:00 UTC

Fresh `earlier-hour` copy under the run root recorded in private `run.json`:
**399 original SHA-256 hashes unchanged**, copied sources verified before optional
deletion, all **2,668,265 rows** preserved across nine families/ten protocol leaves.
Current disabled baseline builds **54 models/140 gates**; entity-enabled raw,
mixed and compacted each build **58 models/145 gates**. Bronze/schema comparisons,
all host-level Start/Stop counts and **40,982 process/summary seeds** are preserved.
Four accepted ANY_VALUE-reachable downstream differences are recorded per migration
state, not hidden as equivalence: `file_chart`, `process_file`,
`process_file_summary`, `telemetry_event_summary`.

One-hour entity init/replay/GET verification and combined migration pass with
**40,982 entities**, **86 direct parent conflicts**, five snapshots/**3,277,708 bytes**.
Terminal QA reports 40,893 missing-ancestor seeds and 89 parent-conflict seeds
(including descendants of conflicting entities). Zero recorded-root-reached seeds:
this deliberately hour-only state is **not** a successful historical ancestry
repair, nor proof that full bootstrap would solve never-collected ancestors.
Raw and compacted-only replay are semantic no-ops. Entity init took 70.66 seconds;
raw replay 41.86 seconds, compacted replay 12.18 seconds, verify 3.88 seconds.

Measured raw compaction (decimal MB; entity storage excluded):

| Metric | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Files | 399 | 10 | 389 / 97.49% / 39.9× |
| Bytes | 35,471,263 | 32,792,809 | 2,678,454 / 7.55% |
| Rows | 2,668,265 | 2,668,265 | None; all preserved |

| Family | Files before → after | MB before → after | Byte saving |
| --- | ---: | ---: | ---: |
| pidstat | 24 → 1 | 2.339 → 7.892 | **−237.44% (expansion)** |
| host | 5 → 1 | 0.038 → 0.009 | 75.39% |
| MAC/IP | 5 → 1 | 0.010 → 0.003 | 71.67% |
| process | 114 → 1 | 5.697 → 3.292 | 42.21% |
| network (TCP/UDP) | 114 → 2 | 1.380 → 0.450 | 67.38% |
| file | 57 → 1 | 20.028 → 15.522 | 22.50% |
| SELinux AVC | 22 → 1 | 0.088 → 0.007 | 91.61% |
| SELinux interaction | 35 → 1 | 5.803 → 5.609 | 3.34% |
| SELinux transition | 23 → 1 | 0.089 → 0.008 | 91.13% |

Two successful combined commands total **238.10 seconds**, approximately 11,207
rows/second including entity no-op validation, raw validation and deletion; not a
pure writer benchmark. Source mean size 88,900 bytes; output mean 3,279,281 bytes.
Raw compacted plus entity storage is **36,070,517 bytes / 15 files**: adding the
new dimension makes this hour's combined storage 1.69% larger than raw alone,
despite the raw compaction saving. Full historical dimension growth remains separate.

#### PIDstat size diagnosis / local layout experiment

Read-only Parquet metadata shows raw pidstat: **24 row groups**, 28,005–46,335
rows/group; compacted: **426 row groups**, 424–3,745 rows/group. Both use ZSTD.
Shipping COPY requests `ROW_GROUP_SIZE 2048`; the changed layout is a credible
explanation for byte expansion, not a codec upgrade or row-count change.

A controlled **local-only DuckDB 2.0.0** rewrite of the same 897,390 pidstat rows
measured one output per candidate:

| Requested row-group size | Output bytes |
| ---: | ---: |
| 2,048 | 7,969,344 |
| 32,768 | 1,699,092 |
| 122,880 | 1,122,558 |
| 524,288 | 1,013,378 |

Counts and all-column row-hash sums match each candidate. These are local layout
measurements (input materialized once), not full multiset proof or S3 timings.
No shipping setting or S3 output was changed: larger row groups are a measured
tuning opportunity, not silently adopted during this qualification.

Private evidence: `hour-summary.json`, `hour-compaction-metrics.json`,
`hour/<state>/{snapshot,metrics,comparison}.json`, `pidstat-layout-evidence.json`
and `pidstat-layout-ab/evidence.json` under the previously recorded run directory.
At this earlier-hour checkpoint, seven-day results were pending; completed results
are recorded below.

#### Seven-day execution started / independent real-hour checks

Full copy preparation has completed: all **71,155 objects / 5,958,506,820 bytes**
have immutable inventory identity and original-versus-copy SHA-256 verification.
The resumed command took 1,628.44 seconds, in addition to the earlier timed-out
attempt; this is copy/verification time, not compaction throughput. The sequential
historical-capacity and 168-hour driver subsequently completed as recorded below.

Independent raw SQL reduction of the earlier hour's **114 physical process files**
matches the **40,982 persisted entities** exactly as a multiset over hostname/hash,
OS PID, paired parent fields/status, identity status, birth/Stop FILETIMEs,
lifetime status and Start/Refresh/Stop flags. A separate iterative Python graph walk
matches every per-host terminal ancestry-status count from DBT. Evidence:
`hour-independent-verification.json`. This verifies real evidence reduction and
QA correctness, without claiming historical ancestors exist in hour-only state.

#### Completed week — November 5–11 UTC, 2026-11-13

`qualify_week.py` completed all 168 selected UTC hours. **165 passed** their
reported schema/partition/count/inventory/deletion gates; **3 failed** immediate
source-deletion verification. Recomputed metrics match the saved final totals.
All successful leaves report `passed=true` and zero row delta. Final read-only S3
listing independently matches the **1,650 successful-hour files / 4,623,379,532
bytes**. Final full-GET reread confirms **all 71,155 original SHA-256 hashes unchanged**.

| Successful-hour raw metric | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Parquet files | 53,415 | 1,650 | 51,765 / **96.91% / 32.37×** |
| Bytes | 4,841,533,292 | 4,623,379,532 | 218,153,760 / **4.51%** |
| Rows | 360,027,830 | 360,027,830 | None; all count-preserved |

Successful command time totals **23,691.38 seconds / 6.58 hours**, including
configured validation/deletion and the first hour's entity phase: **15,197 rows/s**,
0.204 decimal MB/s. Mean hour 143.58 seconds; median 138.48; nearest-rank p95
181.11; range 119.16–192.29 seconds. All compact attempts, including the three
deletion failures and failed combined attempt, took 24,094.42 seconds. Copy,
bootstrap, initialization, DBT and final rehash time are excluded from these
compaction timings. This is sequential end-to-end test performance, not a pure
writer benchmark or production capacity certificate.

Mean file size rises from 90,640 to 2,802,048 bytes; output median 240,707 bytes,
p95 11,300,308 and maximum 17,870,355. The fixed hour/family/protocol boundaries
still produce many small files despite the 128 MiB target; no cross-hour merging.

Daily breakdown excludes each failed hour in its entirety (decimal MB):

| UTC day | Passed hours | Files before → after | MB before → after | Byte saving |
| --- | ---: | ---: | ---: | ---: |
| November 5 | 23 | 7,080 → 230 | 698.464 → 659.990 | 5.51% |
| November 6 | 24 | 7,491 → 240 | 729.302 → 690.136 | 5.37% |
| November 7 | 24 | 7,360 → 240 | 788.009 → 740.919 | 5.98% |
| November 8 | 24 | 7,147 → 240 | 739.331 → 701.433 | 5.13% |
| November 9 | 23 | 7,222 → 230 | 603.931 → 584.780 | 3.17% |
| November 10 | 24 | 7,493 → 240 | 639.417 → 630.301 | 1.43% |
| November 11 | 23 | 9,622 → 230 | 643.079 → 615.821 | 4.24% |

| Family | Files before → after | MB before → after | Byte saving |
| --- | ---: | ---: | ---: |
| pidstat | 3,960 → 165 | 467.563 → 1,395.968 | **−198.56% (expansion)** |
| host | 690 → 165 | 4.959 → 1.346 | 72.87% |
| MAC/IP | 686 → 165 | 1.441 → 0.451 | 68.67% |
| process | 15,097 → 165 | 830.075 → 482.944 | 41.82% |
| network (TCP/UDP) | 12,910 → 330 | 175.335 → 61.754 | 64.78% |
| file | 6,454 → 165 | 2,586.247 → 1,978.081 | 23.52% |
| SELinux AVC | 3,826 → 165 | 15.405 → 1.248 | 91.90% |
| SELinux interaction | 5,881 → 165 | 746.053 → 700.405 | 6.12% |
| SELinux transition | 3,911 → 165 | 14.455 → 1.183 | 91.81% |

All **165 pidstat leaves expanded**. Other families combined shrink from
4,373,969,817 to 3,227,411,221 bytes (**26.21%**). Earlier local layout evidence
identifies a tuning opportunity; no row-group setting or remote output changed.
Week gates prove row-count conservation and reported validations, not an independent
all-column multiset comparison over all 360 million rows or week-wide DBT equivalence.

#### Failure diagnosis, storage separation and remaining gates

Identity guard inspection of immutable local `raw_evidence` finds **81 negative-PID
Refresh observations** and **15 sentinel-key Stop observations with positive PIDs**
across the expanded history/week. **32 rejected observations** precede November 5;
November 5/hour 01 contains two PID −1 Refresh observations, explaining the
combined-mode stop. These match the
existing fail-closed predicate, not permission to filter evidence or repair by PID.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §unknown/load_inputs -->

Historical default bootstrap fails before publication on this identity guard,
**not demonstrated capacity exhaustion**. Independent full October 25–November 11
SQL inventory counts 13,688,390 host-scoped identities; **two hosts exceed the
one-million-row default**. This full expanded count is not
a measured initialized snapshot or the exact pre-week bootstrap cardinality.
Identity policy, large-host memory/row/byte budgets, complete historical bootstrap,
original audit-window DBT comparison and external writer/reader exclusion remain
unqualified. No silent pruning, budget increase or source-code repair was applied.

The separate week-limited init succeeds from November 5/hour 00 with **33,824
entities / nine snapshots / 2,730,739 bytes**, including five acknowledged empty
hosts. The one combined hour is a no-op update of that state; subsequent hourly
entity maintenance halted. This retained dimension is **stale, not a week-complete
snapshot** and must not be promoted to a DBT production input.

Deletion failures all report phase `delete_source` / "Source prefix remains after
deletion; manual repair required":

| UTC hour | Event whose immediate deletion check failed |
| --- | --- |
| November 5 / 06 | raw_process_conn_incr |
| November 9 / 11 | raw_selinuxtransition |
| November 11 / 20 | raw_selinuxinteraction |

All three exact failed event/hour prefixes are empty on the later read-only listing.
A transient/stale listing is possible, but **not established** from the available
request evidence. Their commands remain failed; later emptiness does not certify
the entire hour or waive manual reconciliation. Existing-output skips make a blind
rerun inappropriate. Preserved across failed hours: **25 partial compacted objects /
60,900,907 bytes** and **142 unprocessed source objects / 28,481,517 bytes**.
Remaining inputs are November 5/hour 06 file/SELinux families (118 files) and
November 11/hour 20 SELinux transition (24). November 9/hour 11 has no inputs left,
but its failed command still lacks a successful full-hour report.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py §delete_hour -->

#### Controlled Garage delete diagnostic — synthetic isolated prefixes

Two isolated synthetic runs against the current Garage S3 endpoint exercised the
real compactor at the historical input-object counts. The 72-object case retained
the 36-TCP/36-UDP shape; the other cases used 24 and 35 objects. In all three
baseline cases, `DeleteObjects` returned HTTP 200 with no per-object errors and
zero retries; the immediate prefix listing was empty. The outputs matched all
synthetic input rows exactly as multisets (72, 24 and 35 rows respectively).

A separate four-object case injected one synthetic marker **after** a successful
`DeleteObjects` response and before the compactor's immediate prefix check. The
check found exactly that marker, and the CLI returned the same
`Source prefix remains after deletion; manual repair required` error in
`delete_source`. Its four original rows still matched the compacted outputs.
This validates the failure path and shows that an object arriving in that interval
can produce the message; it does **not** show that this was the historical cause.
The ordinary cases did not reproduce an unexplained Garage deletion/listing error.

Garage's responses exposed no request ID or `x-amz` correlation header to the
client (only content/date headers). The harness cleaned its isolated prefixes;
an independent final listing found zero objects. No Garage logging configuration
was changed. The harness and detailed reports are temporary laptop artifacts,
not committed qualification data.

**Potential follow-up, not part of the accepted milestone:** if root-cause evidence
is needed later, rerun the same level of test from the on-prem development host on
a new synthetic prefix while Garage debug logging is enabled on every node. Record
server-side delete/list sequence and timing, compare any available correlation
metadata, retain the exact object found by the immediate check, and verify cleanup.
The current client response has no request ID, so server-side logs are needed for
useful correlation. Keep this distinct from a read-only performance comparison;
do not retarget the test to production or mutate the preserved qualification copy.

Final test-root storage accounting, deliberately not all claimed as compacted savings:

| Storage class | Objects | Bytes |
| --- | ---: | ---: |
| Successful week raw outputs | 1,650 | 4,623,379,532 |
| Failed-hour partial raw outputs | 25 | 60,900,907 |
| Remaining week raw inputs | 142 | 28,481,517 |
| Untouched pre-week process copies | 16,723 | 1,028,909,068 |
| Week-limited entity snapshots | 9 | 2,730,739 |
| Separate earlier-hour outputs plus entities | 15 | 36,070,517 |

Private evidence under the recorded run directory: `week-summary.json`,
`week-compaction-metrics.json` (overall/day/hour/event), `history-preflight.json`,
`week-reports/*.json`, `original-recheck.jsonl`, `week-final-object-inventory.json`
and `week-final-inspection.json`. Executed: main-env `.venv/bin/python
<run-dir>/qualify_week.py`; isolated locked writer invoked by that harness;
main-env read-only Python metric recomputation/validation and SDK final listing;
read-only DuckDB inspection of `independent-history.duckdb`. No main/standalone
runtime mixing, original mutations, private environment edits, commits, pushes,
cleanup or production deployment. Failed-hour reconciliation and identity-policy
changes require a bounded follow-up rather than relabeling this run as passing.

Final documentation checks pass: `git diff --check`; three updated frontmatters,
24 grounding paths and six wikilinks; independently summed day/event/hour metrics
all match overall file/byte/row totals, and rejection-category counts match the
read-only diagnosis. These are scoped checks, not a whole-wiki lint.

Milestone commit authorization received November 13. Fresh pre-commit targeted
checks pass: main `.venv/bin/python -m pytest -q tests/test_process_entities.py`
**11 passed (37.86 seconds)**; isolated standalone `uv run --locked pytest -q
tests/test_entities.py` **25 passed (1.06 seconds)**. No additional S3 writes or
full-suite rerun; earlier full-suite evidence remains recorded below. Handoff:
[[wiki/work/durable-process-entity-manager/dev_handoff]].

Implementation committed as Wintap-PyUtil `2cfbad1` (25 scoped files) on
`work/raw-sensor-compacted-union`; private `wintap-run.env-lintap-alpha` and
`wintap-run.env-micro-range` remain untracked/excluded. That implementation branch
is unchanged by the Garage diagnostic. The current Analytics handoff/wiki update
is a separate documentation commit; no Wintap-PyUtil commit or push is included.

First-round implementation is complete in Wintap-PyUtil following the human's
explicit "Proceed!" instruction. The standalone writer remains DuckDB 2.0.0;
DBT remains 1.5.6. Canonical facts:
[[wiki/tool/durable-process-entity-manager]]. No production bootstrap/cutover or
scheduler deployment; no original telemetry or private run-env modifications.

Current regression results: **132 passed, 2 skipped** in the standalone extra;
**310 passed, 3 skipped** in the main suite. Main collection now intentionally
excludes the isolated extra, whose dependencies/runtime must not enter DBT's env.
The previous generic root-wide collection failed for that reason; `testpaths`
now expresses the intended isolation. Optional pre-existing/live tests remain
skipped unless explicitly authorized; the entity S3 test was run separately.

Actual S3 synthetic qualification passed completed snapshot replacement, no-op
replay, full GET verification, entity-before-delete migration and compacted-only
replay/DBT. Final read-only DBT qualification passes **58 models/145 gates**, with
**33 root-reachable window seeds, 33 summaries, 36 durable entities and 2 context-only
ancestors**. Original hostname spelling is preserved in window outputs after a
new summary-population assertion exposed and fixed a normalized-host join bug.

## Research and source review (pre-implementation baseline)

Read the durable-process concept, optional process-context note, refresh tension,
anonymized ancestry audit, runtime-retention page, identity conventions and
ancestry QA. Read live PyUtil compaction, bronze process, silver process/path,
and gold process-summary SQL.

Confirmed integration boundaries:

- Raw `process_hours` skips an existing destination before source discovery and
  deletes only after its current leaf/inventory checks. State ingestion therefore
  needs a separate phase; raw skip cannot become a state completion checkpoint.
- Bronze `stg_raw_process` performs window filtering and duplicate accounting;
  historical entity rows must not be inserted there as raw observations.
- Silver `process` uses ANY_VALUE for parent/hash and metadata, and counts both
  Start and Refresh. A non-null arbitrary parent is not automatically correct.
- `process_path` currently seeds and joins only `process`, in hostname scope;
  a separate durable/context lookup is needed for out-of-window ancestors.
- Gold `process_summary` is seeded from `process`; adding all historical context
  as seeds would change summary populations and requires an explicit contract.

These facts describe the original/disabled-mode baseline. Current opt-in behavior
adds a separate entity phase/context lookup; no historical rows enter raw bronze.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql; ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql -->

## Planning and implementation verification

### Planning validation — 2026-11-12

- `git diff --check`: passed.
- Read-only `python3` scoped structural check: passed **7 frontmatters, 35 local
  grounding paths, 25 wikilinks and 4 feature index entries**. This checks required
  keys/path/link existence, not full YAML typing or whole-wiki health.
- Reviewed all four feature artifacts for consistency; added explicit cross-phase
  process inventory binding before source deletion and file metadata for typed
  empty host snapshots. These remain design requirements, not tested behavior.

No entity implementation tests or S3 qualification had been run at that planning checkpoint.

### Executed commands and evidence — 2026-11-12

- Extra: `.venv/bin/python -m pytest -q`, followed by `uv run --locked pytest -q`:
  **132 passed, 2 skipped**. Reducer permutations/duplicates/Stop replay, PID reuse,
  host isolation, empty metadata, missing-state/unknown identity, resource failures,
  cross-phase new/changed/removed input, raw COPY failure after state publication,
  partial hosts/init-resume and mocked lost-ACK/corrupt publication all pass.
- Main: `.venv/bin/python -m pytest -q`: **310 passed, 3 skipped**. Entity fixture
  tests use the nested locked UV runner, never import the writer into DBT's env.
  Full raw/mixed/compacted builds test known ancestry and preserve window counts;
  extra targeted locked tests verify the final entry point/metadata enrichment.
  Final targeted `uv run --locked --dev pytest tests/test_process_entities.py -q`:
  **11 passed**.
- Live synthetic: `RAW_ENTITY_S3_TEST_APPROVED=isolated-write`,
  `RAW_ENTITY_S3_TEST_PROFILE=lintap-alpha`, and a new
  `RAW_ENTITY_S3_TEST_ROOT` with main pytest `tests/test_process_entities_s3.py -q -s`:
  **1 passed in 67 seconds**. Completed replacement/no-op replay, fixture hashes,
  DBT builds and entity-before-delete migration verified. Initial builds had
  144 gates before the subsequently added context-integrity gate.
- Final current-code read-only build of retained S3 fixture: **58 models/145 gates**,
  33 complete seed paths and 33 summaries. Evidence/database/compiled SQL retained
  at `/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/dpe-final-s3-read-kjwzgceo/`.
- `git diff --check` passes in PyUtil and Analytics. No commits/pushes requested
  or performed for this feature; private run-env files stay untouched/untracked.
- Final scoped wiki check: **10 parsed YAML frontmatters, 61 local grounding paths,
  47 wikilinks**, all passed. Final locked reducer/store test: **25 passed**.

### Fixture model and repair iterations

Fixtures independently declare a historical root and exited bridge, 33 selected
lifecycle seeds, and one activity-only key whose lifecycle is outside the window.
Known expected chains are `[child, bridge, root]`, not derived from production SQL.
Replayed duplicates/overlapping archives add no state. In mixed raw/compacted
facts, bronze `num_dups` reflects the overlap; legacy lifecycle counts remain
counts of grouped window observations, not raw duplicate copies or entity history.
Context-only ancestors/activity-only keys do not become summary seeds.

Negative graphs cover incompatible paired parents, a never-collected ancestor,
non-root cycles and a non-root self-link. Root policy requires consistent recorded
self-parent evidence plus the declared root PID set (default 0/1/4, dataset/OS
review required). Missing nodes never appear as fabricated path steps.

During verification, corrected fixture-only physical-column casing (the shipping
schema gate properly rejected drift), corrected a duplicate-folding test expectation,
and repaired the real uppercase-output hostname/host-summary join regression by
normalizing lookups while preserving window hostname payloads. Initial Black
check reported formatting differences; no passing formatter check is claimed.

### Exact S3 scope and retained artifacts

All S3 input was generated, not copied from original telemetry. Exact root:
`s3://lintap-alpha/entity-tests/dpe-20261112-e6a7a0f0-c1b8-43c5-a4ae-5560eed3d78f`.
Verified **32 generated source hashes unchanged** before intentional migration;
the combined job then validated and deleted those **32 generated sources**.
Retained **14 compacted outputs plus 1 entity snapshot**, **48,182 bytes total**;
the 36-entity snapshot is **5,843 bytes**. Zero raw fixture objects remain.
No broader bucket operation, original key access/deletion or output cleanup.

Real endpoint qualification covered normal completed PUT replacement/GET, not
actual network-interruption atomicity or concurrent readers. Lost acknowledgment
and corrupt content were injected with mocks. External writer/reader exclusion
remains mandatory; no multi-host transaction guarantee is claimed.

| Gate | Required evidence | Status |
| --- | --- | --- |
| Schema/reducer | Cross-version Parquet, order/replay equivalence, paired conflicts/Stop/PID reuse | Passed |
| Local persistence | Fresh-worker recovery, empty/missing-state guard, no-op, init-resume and budget failures | Passed |
| S3 publisher | Actual completed replacement/GET; mocked lost response/corruption; no original access/deletion | Passed within stated limits |
| Combined job | Publication failure/input drift blocks deletion; raw failure/skip/replay contract | Passed |
| DBT | Historical/exited ancestors, context-only counters, deterministic edges, flags and disabled regressions | Passed |
| Graph QA | Independently specified bridge/root/missing/conflict/cycle fixtures | Passed; broad K95/concentration audit remains separate |
| Capacity/operations | Fixture measured; budget failures and rebuild tested; production-scale resources and schedule exclusion | Production review outstanding |

Save fixture input identities, expected semantic entities, output hashes, state
publication report, DBT schemas/rows/lineage QA and source immutability results.
Do not confuse raw row conservation with entity count conservation: this reducer
intentionally collapses repeated evidence and needs full-content/graph assertions.

## Known limitations pending review

Full retained history grows per-host snapshots. Partial/missing original archives
limit bootstrap and rebuild completeness. Fixed host files have no multi-host
transaction or historical as-of snapshot guarantee. Parent contradictions and
never-collected ancestors remain gaps. These limits must be visible to consumers.
