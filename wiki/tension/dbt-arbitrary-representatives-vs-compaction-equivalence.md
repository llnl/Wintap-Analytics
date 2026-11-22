---
title: "Tension: DBT arbitrary representatives vs. compaction equivalence"
type: tension
status: resolved
poles:
  - "Compaction permits row reordering while preserving payloads and multiplicities; full-model migration qualification expects stable analysis results."
  - "Existing DBT models select unordered ANY_VALUE representatives, allowing unchanged input to yield different derived names, paths, identities and downstream counts."
resolution: "Human explicitly accepts existing ANY_VALUE data-quality debt as non-blocking for compaction; source/bronze fidelity and build/schema gates remain, with affected downstream differences reported. See wiki/work/raw-sensor-file-aggregation/interview.md §ANY_VALUE Debt Does Not Block Compaction."
confidence: high
grounded_by:
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_file.sql
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../Wintap-PyUtil/tests/test_compacted_s3_migration.py
  - wiki/work/raw-sensor-file-aggregation/verification.md
  - wiki/work/raw-sensor-file-aggregation/interview.md
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
source_paths: wintap_dbt/models; tests/test_compacted_inputs.py
tags: [tension, dbt, compaction, determinism, process-identity]
---

# DBT arbitrary representatives vs. compaction equivalence

**Resolved by an accepted separation of concerns, not a determinism fix.**
The human explicitly says existing `ANY_VALUE` quality issues do not block
compaction. Bronze/source fidelity, schemas, and full DBT build/tests still gate
migration; affected downstream differences remain visible diagnostics. The
production representative-selection policy is unchanged and remains separate
data-quality work.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/interview.md §ANY_VALUE Debt Does Not Block Compaction -->

## Observed conflict

The full-model copied-S3 migration test for 2026-11-11 08:00 UTC passed all
139 DBT gates in raw and mixed states, but 17 model snapshots differed after
only host migration. Rebuilding the identical mixed input with no further S3
mutation passed 139 gates again and changed 18 model snapshots. All model
schemas matched; some downstream file-model row counts also changed.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/verification.md §Full-Model Live-Copy Expansion -->

`process.sql` groups by process identity but uses unordered `ANY_VALUE` for
name, path, parent and other representatives. Selected path/name flows into
derived filename/file_id and downstream analysis. `process_file.sql` also uses
unordered `ANY_VALUE(pid)`. A diagnostic executing the shipping process SQL
shows identical input rows/multiplicities in reversed order select different
paths, filenames and file IDs.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §process_base/with_filename/with_file_id; ../Wintap-PyUtil/wintap_dbt/models/silver/process_file.sql; ../Wintap-PyUtil/tests/test_compacted_inputs.py §test_existing_process_model_depends_on_row_order -->

This is derived analytics instability, not evidence that raw telemetry was
dropped or changed by compaction. Every bronze snapshot matched in the first
raw/mixed comparison; non-host sources had not yet been compacted. The identical
input replay proves strict result hashes are not currently a reliable causal
compaction test across the full graph. It does not explain every changed column
or waive further source-fidelity checks.
<!-- SYNTHESIS: inferred from the unchanged-input replay and shipping SQL diagnostic documented in wiki/work/raw-sensor-file-aggregation/verification.md -->

## Ownership and accepted comparison contract

PyUtil owns DBT semantic changes and the isolated compactor. Analytics hosts these evidence
artifacts; no sensor change or production migration has been made. Exact full
result-equivalence was initially blocked. The human now accepts the diagnosed
quality debt as non-blocking for compaction; scoped host/pidstat and synthetic
fixture passes remain valid within their stated scope.

The test's explicit `any-value-diagnostics` mode computes the ANY_VALUE model/
dependent closure from DBT's manifest. Every schema and the model set must match;
every bronze result remains exact even if it were in that closure. Results outside
the closure must also match. Changed rows/counts/hashes inside the closure are
saved/reported, not normalized away. Dependency membership does not prove every
difference is caused by ANY_VALUE; no such causal/full-equivalence claim is made.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_compacted_s3_migration.py §any_value_model_closure/compare_snapshots -->

Future representative work still needs a documented policy (including ties and
whether name/path/parent fields come from the same observation). No production
thread-count changes, compactor sorting, deduplication or DBT semantic repair
were introduced here to manufacture stability.

Context: [[wiki/work/raw-sensor-file-aggregation/implementation_plan]],
[[wiki/work/raw-sensor-file-aggregation/verification]],
[[wiki/repo/wintappy-pipeline-repo]].
