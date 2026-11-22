---
title: "Implementation Plan: Implement sensor fixes and cleanup test code"
type: concept
confidence: medium
grounded_by:
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief.md
  - wiki/overview/test-suite-organization-and-classification.md
  - streamlit/projects/HostActivity/README.md
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/tests
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan.md
policy: agent-editable
last_validated: 2026-11-22
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/HostActivity; ../Wintap-PyUtil/tests; wiki/work/implement-sensor-fixes-and-cleanup-test-code
tags: [feature-work, testing, test-organization, iterative-development, verification]
---

# Implementation Plan: Implement sensor fixes and cleanup test code

## Operating Model

This is an iterative development loop, not a one-shot test-suite rewrite:

1. Make a small first draft of the test changes and run lightweight affected checks.
2. In the separate sensor session, implement a selected small sensor change and
   capture a fresh, small dataset.
3. Run the relevant dataset checks against that capture.
4. Repair, simplify, and refine the tests without weakening the intended semantics.
5. Repeat, expanding scope only when the preceding small slice is understandable.
<!-- HUMAN-DECISION: conversation 2026-11-22 — iterative first-cut development with lightweight checks, separate sensor work/captures, dataset testing, and refinement. -->

Synthetic regression passes establish test/code contracts, not sensor capture
correctness. A dataset can reveal an incorrect test assumption or a genuine sensor
defect; report which one the evidence supports rather than making every capture green.

## Scope and Ownership

- **This session:** Analytics/PyUtil test organization, discovery/import fixes,
  classification and documentation; approved Wintap first-slice test cleanup; later
  dataset checks for agreed sensor slices.
- **Separate sensor session:** Wintap behavior changes, platform execution, workload
  ground truth, and new captures. Specific fixes are not selected by this plan.
- **Excluded from the original TC-02 first cut:** Wintap .NET test restructuring.
  The human has since added and approved its first slice, tracked separately below.
- **Still excluded:** sensor/schema changes here, Lintap packaging, deployment,
  historical-data repair, or production acceptance.
- Both test repos use `feature/implement-sensor-fixes-and-cleanup-test-code`.
  Coordinate file ownership before simultaneous edits; do not switch or overwrite
  another session's active work.

### Wintap Extension — Static-Checked First Draft

[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis]]
records 63 C# files in the existing Windows-targeted project plus seven Python
control files, with native/source/global-state boundaries. The approved
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]] first
slice now adds class traits and five whole-file moves. The human explicitly
deferred the unavailable Windows baseline for a static-checked draft on the
shared feature checkout at `a418aa4`. No sensor files, dependencies, or CI were
changed by this session. Its 77 moved/84 focused-case figures are static
expectations, not runs. Windows acceptance remains pending; Wintap static audits
and the shared verification page record the boundary.
<!-- HUMAN-DECISION: conversation 2026-11-22 — include Wintap repo tests; prepare initial analysis and plan. -->
<!-- HUMAN-DECISION: conversation 2026-11-22 — approve first-slice implementation, defer the Windows baseline for a static draft, and share the feature checkout with the sensor worker. -->

## TC-01 — Freeze the Current Slice

1. Check branch/worktree state and applicable instructions; preserve unrelated work.
2. Count tracked test files, excluding dependencies, caches, local configs, and data.
3. Collect only the proposed slice and record per-file counts and execution boundary.
4. Freeze test identities in a temporary manifest before moving files; compare
   normalized identities afterward, not merely total counts.
5. Inspect file-relative paths, imports between tests, and current documentation.

Initial tracked inventory on November 22: Analytics applications **11** Python test
files, validation **10**, feature-work evidence **14**; PyUtil main **60**, isolated
compactor **20**, and DBT **7 SQL** test files. These are file counts, not full-suite
collection or execution results.

The selected baseline is **59 HostActivity cases** and **224 PyUtil cases** across
configuration and four SQL files. Full PyUtil/compactor collection is deferred.

## TC-02 — First Draft: Mechanical Organization and Explicit Classification

### Analytics

- Move the three HostActivity test files intact into `tests/contract/`.
- Add package markers so recursive `unittest` discovery still works.
- Update the four application-file references for the new directory depth.
- Document the discovery command, counts, synthetic inputs, and no-live-I/O boundary.
- Record co-resident UI/transport checks as secondary coverage. Do not split large
  files or extract their fixtures in the same mechanical change.
- Update canonical live-path citations; preserve old commands in historical logs
  and dated verification records, with a current-path pointer where needed.

### PyUtil

- Move only `test_config.py` into `tests/unit/config/` and add package markers.
- Register `unit` and `contract` pytest markers; mark configuration as `unit` and
  the four existing synthetic SQL modules as `contract`.
- Keep SQL modules in place in this draft: they share relative imports, and
  `test_compacted_inputs.py` imports the network SQL renderer.
- Add a partial inventory/command README. Preserve existing full-suite defaults;
  unclassified files must not disappear because of a new global marker filter.
- Leave coordination, platform, compactor, DBT SQL, and historical suites untouched.

### Lightweight Gate

- Run all 59 affected HostActivity tests; they take only a few seconds locally.
- Collect the five affected PyUtil modules and compare all 224 normalized identities.
- Run configuration's four cases and 13 representative SQL consumer cases, including
  the existing cross-module imports: **17 cases**, not a full SQL regression run.
- Check marker-filtered collection in those same explicit paths.
- Run syntax/diff checks on the changed files. No environment upgrade or dependency
  installation is required when the existing per-project environments work.

Use a **120-second ceiling per command** for this first cut. A timeout, import
error, count mismatch, or unexpected skip is recorded and repaired in the slice;
do not silently substitute a broad full-suite run. Keep Streamlit and PyUtil in
their separate environments. The compactor's separate DuckDB environment is not used.

## TC-03 — Receive the Next Small Sensor Capture

The sensor session supplies a bounded handoff before dataset validation begins:

| Required item | Purpose |
|---|---|
| Fix identifier and exact sensor revision/build/configuration | Bind the result to the implementation actually run. |
| Platform and enabled sensors | Define the capture capability and applicability. |
| Explicit local dataset path or separately authorized remote scope | Avoid implicit searches of private/live datasets. |
| UTC capture/workload interval and relevant event families | Keep the first validation small and repeatable. |
| Named workload actions and independent expected observations | Prevent the recorded output from defining its own oracle. |
| Known exclusions, losses, and partial observations | Distinguish missing evidence from a test failure. |
| Expected semantic changes and compatibility constraints | Explain why an assertion may legitimately change. |

Prefer a read-only local snapshot for the first validation. Do not download data,
open S3, run a collector, invoke DBT on a private capture, or mutate source files
without the concrete scope being authorized. Real identifiers remain outside the
persistent wiki; store sanitized summaries, counts, and generic capture labels.

## TC-04 — Test Against the Fresh Dataset

1. Select the affected validator in Analytics/validation or the SmokeTests analysis
   layer. HostActivity's presentation regressions are not a sensor-completeness gate.
2. Record the dataset label, revision, source layer, schema, workload interval, and
   read budgets. Keep raw telemetry, normalized data, and DBT-derived data distinct.
3. Add the smallest explicit dataset-check entry point needed for that fix. Keep
   real-data reads opt-in and out of default synthetic discovery. Do not introduce
   a generic framework until repeated needs justify it.
4. Verify relevant fields, identity/counters/timestamps, and workload correspondence
   against independent expectations, not merely non-empty tables or schema presence.
5. Report pass/fail and unsupported/missing evidence separately. A skip is not a pass;
   unrelated event-family absence does not fail an out-of-scope test.
6. Save a concise, sanitized round result and a minimal reproduction for each failure.

Concrete assertions depend on the selected sensor change; do not invent expected
counts, timestamps, field meanings, or quality thresholds before that handoff.

## TC-05 — Repair, Clean, Refine, Repeat

For each failure:

1. Classify it as test/discovery defect, incorrect oracle, sensor defect, downstream
   semantic defect, environment limit, or insufficient capture evidence.
2. For a test defect, reduce it to a small synthetic reproduction where possible,
   then repair only that behavior and rerun the changed check plus immediate neighbors.
3. For a sensor defect, return the narrow finding to the sensor session; retain the
   failing expectation and await a fresh revision/capture.
4. Split mixed files and extract fixtures only after the coverage map shows what
   remains independent. Avoid helpers that recreate the implementation being tested.
5. Rerun the relevant dataset check against the same immutable capture to verify
   a test repair, then the next fresh capture when producer behavior changes.
6. Record the result and next action before starting the following round.

Round record: round ID; test/sensor revisions; sanitized capture label; affected
commands; executed/collected/passed/failed/skipped counts; observed defect; repair;
evidence limits; next capture/check. Keep unrelated fixes and mass formatting out
of the round. Any changed assertion must explain the intended semantic contract.

## TC-06 — Expand the Refactor in Bounded Slices

After feedback from the first draft:

1. Separate HostActivity contract and UI cases, retaining independent test identities.
2. Apply the same inventory/move/check pattern to SmokeTests and individual validation
   harnesses, prioritizing the ones needed by the next sensor capture.
3. Relocate PyUtil's SQL/DBT/processing groups with explicit shared-helper import
   updates; retain `test_` filename prefixes for discovery.
4. Partition coordination/entity tests one behavior family at a time. Preserve
   platform skips, genuine retained-history controls, and independent verifiers.
5. Classify isolated compactor and historical suites separately; no evidence deletion
   based on filename or age. Merge/archive decisions still require coverage/provenance
   review and the existing human-review gates.

Expand verification only to match the current change's dependency surface. Broader
integration, platform, S3, and final regression gates are later scheduled milestones
with explicit environments and budgets, not prerequisites for every draft iteration.

## Compatibility and Rollback

- Preserve assertion bodies and fixtures during mechanical moves; only discovery,
  location-dependent paths, and explicit classification change in TC-02.
- Document relocated commands; do not keep forwarding test modules that would
  collect the same cases twice.
- Do not change telemetry schemas, package dependencies, collection semantics, or
  full-suite default selection in this first cut.
- If a move fails, reverse only this slice's moves/path edits. Never reset the repo,
  discard unrelated changes, or remove source/recorded datasets.

## Done Checklist

- [x] TC-01: inventory, affected baseline, and test identities frozen.
- [x] TC-02: first draft implemented and lightweight checks recorded in
  [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].
- [x] Wintap extension: initial analysis and proposed staged test plan recorded.
- [x] Wintap extension: first-slice scope approved; traits/five moves implemented
  and statically checked on the authorized shared feature checkout.
- [ ] Wintap extension: Windows baseline/build/discovery/filtering and focused
  runtime acceptance (explicitly deferred, see the extension plan).
- [ ] TC-03: selected sensor fix and first fresh capture handed off.
- [ ] TC-04: relevant explicit dataset checks implemented and first round recorded.
- [ ] TC-05: repairs/refinements recorded for each subsequent round.
- [ ] TC-06: remaining organization slices completed with scoped discovery proof.
- [ ] Final: agreed sensor checks and organization boundaries accepted; broader
  gates and unresolved limitations recorded; durable facts promoted to canonical pages.

TC-02 completion is a first-cut milestone only. The overall workflow stays open
until sensor-fix scope and final acceptance criteria are supplied and reviewed.
