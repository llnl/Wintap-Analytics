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
  - streamlit/projects/HostActivity/tests/README.md
  - ../Wintap-PyUtil/tests/README.md
  - ../wintap/devtools/test_event_name_contracts.py
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md
  - ../wintap/developer_docs/audits/sfx-02-process-observation-refresh.md
  - ../wintap/developer_docs/audits/sfx-03-linux-command-line-provenance.md
  - ../wintap/developer_docs/audits/sfx-04-linux-exec-observation-kind.md
  - ../wintap/developer_docs/audits/sfx-05-linux-executable-path-source.md
  - validation/dataset-smoke/README.md
  - streamlit/projects/SmokeTests/tests/README.md
policy: agent-editable
last_validated: 2026-11-22
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/HostActivity; streamlit/projects/SmokeTests/tests; validation/dataset-smoke; ../Wintap-PyUtil/tests; wiki/work/implement-sensor-fixes-and-cleanup-test-code
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

## Current Linux Tranche — Test Development While Captures Are Pending

**Decision:** establish destination regression confidence, then implement a small
opt-in local dataset-readiness check. Continue bounded test cleanup independently
of the sensor engineer; fresh-capture correctness still requires TC-03.
The human assigns this session responsibility for test implementation/testing and
permits lightweight read-only smoke checks of the existing RHEL 8 dataset. This
does not select a sensor fix or authorize historical-data repair.
<!-- HUMAN-DECISION: conversation 2026-11-22 — prepare the test implementation plan; existing data/wintap-analysis/rhel8 may be used for environment/readiness smoke tests, with no heroics. -->

### Destination Baseline and Constraints

- All three reviewed commits are present: Analytics `0f8b414` (current `e6ff8ed`),
  Wintap `123bd70`, PyUtil `564ec43`; matching feature branches are retained.
  Analytics/Wintap tracked work is clean; unrelated PyUtil data/config artifacts
  remain untouched. Recheck ownership and dirty state before every edit.
- The destination is Linux x86_64 with a RHEL 8-series kernel. HostActivity's
  existing Python **3.13.13** / DuckDB **1.5.6** environment works: **59 tests pass**.
  Wintap's explicit stdlib-only event-name parser selection passes **7 tests**.
  Neither result is a managed Windows run or a sensor-capture check.
- PyUtil's `.venv/` exists but its expected Python executable is unavailable.
  Following explicit human approval, uv 0.13.5 provisioned an isolated environment
  under `/tmp/opencode/` using installed Python **3.12.15** and locked cached
  dependencies (DuckDB **1.5.6**, pytest **9.1.1**). The **17 representative cases
  pass**, and all **224 pre/post identities** match with **4 unit / 220 contract**.
  Keep the old environment untouched. The initial copy-based attempt ran out of
  root-filesystem space; only this session's partial temporary environment was
  removed, and `--link-mode symlink` succeeded with a small footprint. The ready
  environment depends on its uv cache; do not prune that cache during testing.
  No dependency upgrade or lockfile change occurred. Use the isolated interpreter,
  not HostActivity's Python 3.13, for PyUtil.
- `dotnet` is not on PATH. Keep the existing Windows/SDK 10.0.402 gate deferred;
  Linux parser/static checks cannot close it. Do not retarget or split the project.
- The authorized dataset resolves relative to **PyUtil**, not Analytics:
  `../Wintap-PyUtil/data/wintap-analysis/rhel8/`. At inspection `raw_sensor/` has
  no entries. `duckdb/wintap.duckdb` opens read-only with DuckDB 1.5.6: 24 catalog
  objects (14 base tables, 10 unexecuted views). One base-table sample is empty;
  that does not establish that all tables are empty. Raw readiness is **unavailable**,
  not a pass; do not search other datasets, sync S3, rebuild DBT, or repair this copy.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/pyproject.toml; ../Wintap-PyUtil/pyproject.toml; ../wintap/tests/Wintap.Tests/Wintap.Tests.csproj; wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md §Linux Destination Readiness and Existing-Data Smoke — 2026-11-22 -->

### TC-LNX-01 — Re-establish the Small Regression Baseline

1. Preserve existing moves; use the two test READMEs' explicit commands and separate
   environments. HostActivity's 59-case rerun is complete on this destination.
2. Completed using the approved isolated PyUtil environment: **17 representative
   cases** pass and collection of only the five selected modules preserves **224
   identities**, including **4 unit / 220 contract**. Pre-move test sources were
   reconstructed from git objects in temporary storage, using identical current
   production SQL/configuration sources. Future reruns use a clean temporary
   working directory and explicit pytest configuration/rootdir to avoid inherited
   private settings. Do not require transferring a Mac virtual environment.
3. Keep Wintap's seven parser controls separate from its static five-file comparison
   and pending Windows 77/84 lexical expectations. No broad devtools discovery.
4. Record command, revision, runtime, counts, elapsed time, skips and blockers in
   the verification record. A missing environment stops only its own gate.

**Acceptance:** HostActivity passes without lost/duplicate identities; PyUtil's
bounded rerun and selected identity comparison pass. The Linux selected-slice
gate is now closed; this is not execution of all 224 cases or full-suite acceptance.

### TC-LNX-02 — Implement an Explicit Read-Only Dataset Smoke Check

**Proposed files in Analytics:**

- `validation/dataset-smoke/smoke_dataset.py` — explicit CLI and small functions.
- `validation/dataset-smoke/test_smoke_dataset.py` — synthetic local controls only.
- `validation/dataset-smoke/README.md` — command, budgets and result meanings.

An opt-in entry point is justified because existing capture validators require
workload manifests/expectations that this historical dataset does not supply.
Do not build a generic validation framework or make default tests discover private
data. Use stdlib plus existing DuckDB 1.5.6; the dependency-only smoke helper can
use HostActivity's ready interpreter without treating it as PyUtil's environment.

Implementation requirements:

1. Require an explicit local dataset root and explicit existing database path.
   Fail before connecting if the database is missing; never create a replacement.
   Restrict input files to that root, reject remote URLs and escaping symlinks.
2. Report raw and database readiness independently: **readable**, **empty**,
   **unavailable/error**, or **budget exceeded**. A readable empty relation is not
   positive event evidence. Emit only sanitized counts/statuses, never row values,
   host/account/address identifiers, stored SQL, or secret configuration.
3. For raw data, select deterministic explicit finalized Parquet files from at
   most one hour, prioritizing process/file/network if present. Inspect schemas
   and read a small row sample; missing families remain explicit, not invented.
   No full-root glob queries, joins, global counts, timestamp sweeps or parity claims.
4. Open the built DB read-only; disable external access and extension auto-load/
   installation. List a bounded catalog, inspect and sample **one base table**.
   Do not execute stored views/macros: they may reference absent/remote raw data.
   If a WAL, lock, version mismatch or permission problem appears, stop and report
   it; no checkpoint, migration, exclusive reopen, upgrade or recovery attempt.
5. Never write under the dataset, including dashboard summary persistence. Use
   in-memory connections for raw reads, disable disk spill, and put any private
   temporary diagnostics under `/tmp/opencode/`. Check selected input size/mtime
   before/after; this detects observed change, not full immutability/provenance.

**Initial budgets:** 120 seconds per command; 15 seconds per query; 256 MiB DuckDB
memory; one thread; no spill; at most 32 catalog objects; at most 3 Parquet files,
each at most 32 MiB; at most 128 sampled rows per input. Bound discovery itself
to 128 directory entries; exceeding a cap means unavailable, not truncated PASS.
Sampling/`LIMIT` does not guarantee an I/O-byte ceiling, so retain the file-size
and wall-clock limits. Do not retry automatically or raise limits to make data pass.

**Synthetic acceptance controls:**

- Tiny known Parquet/database fixtures are read successfully; actual rows are not
  printed and originals remain unchanged.
- Missing DB does not create a file; empty/missing raw roots and empty tables have
  distinct non-quality results.
- An unreadable/corrupt input, external view, WAL and escaping path are refused or
  reported unavailable without repair, view execution or external requests.
- File/catalog/discovery/query limits fail visibly rather than accepting partial
  data; source-diff review confirms read-only operations and no persistence path.
- Default unit discovery uses only synthetic temporary fixtures, never the RHEL
  dataset. Negative expectations are independent of the helper's own output.

Proposed synthetic command, from Analytics after these files exist:

```sh
streamlit/projects/HostActivity/.venv/bin/python -B -m unittest discover \
  -s validation/dataset-smoke -p test_smoke_dataset.py
```

Accepted opt-in command:

```sh
streamlit/projects/HostActivity/.venv/bin/python -B \
  validation/dataset-smoke/smoke_dataset.py \
  --dataset-root ../Wintap-PyUtil/data/wintap-analysis/rhel8 \
  --database duckdb/wintap.duckdb
```

**Acceptance:** synthetic positive/negative controls pass and the bounded CLI
reports the current snapshot honestly. Raw-empty status does not block helper
development. The RHEL path was a one-time existing sample to bootstrap readiness
work; it will not be populated and is not a recurring raw-data gate. No
manifestless sensor-completeness assertion is added.

### TC-LNX-03 — Next Mechanical Cleanup Slice, Without Waiting for Data

After TC-LNX-02, prioritize Analytics SmokeTests query/quality controls needed by
the eventual capture loop. Review imports and side effects; freeze and run the
small selected baseline before moving any file. Relocate one whole-file group
using TC-06's pattern, with only import/path/package adjustments. Keep loopback
HTTP opt-in and UI tests separate; preserve existing synthetic negative controls
and test names. Add a per-suite README and compare normalized discovery identities
before/after. Establish a separate suitable SmokeTests environment before running
its project suite; provisioning is not implicit.

PyUtil SQL relocation is a later slice after its environment gate: update the
known `test_compacted_inputs.py` renderer dependency, then collect the selected
identities and run the representative consumers. Do not start coordination/entity,
compactor, historical, release-CI or Wintap platform-project restructuring here.
Sibling edits require the applicable approved test scope; Wintap retains its
human-approved instruction/audit workflow and shared-sensor ownership boundaries.

**Acceptance:** selected pre/post gates agree; no lost/duplicate cases, changed
assertions, weakened oracle, new dependencies, or default external-data access.
If this selection cannot fit 120 seconds, stop and propose a smaller slice or an
explicit budget change rather than run a full suite.

### TC-LNX-04 — Switch to Fresh-Capture Validation When Ready

Receive TC-03's exact fix/build/configuration, authorized local files, UTC interval,
enabled families and independent workload expectations. Add only the affected
capture check, pair it with synthetic negative controls and the relevant SQL
consumer, then follow TC-04/TC-05. Bind each result to test and sensor revisions.
Existing-data readiness remains a separate round; do not relabel it as proof of
the new fix or repair historical datasets to match new assertions.

**Stop boundaries for this tranche:** no collector/workload, deployment, S3 reads/
writes, DBT rebuild, dataset mutation, dependency installation, commits/pushes,
assertion deletion or broad-suite expansion. Ask only for the blocked prerequisite
when it is actually needed; sensor-capture delay need not idle synthetic test work.

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

## First sensor-fix batch status — 2026-11-22

The selected source candidate now combines the `sfx-01` Linux executable-name
repair with additive process observation timing and UTC-aligned periodic Refresh
on Linux and Windows. It preserves birth `EventTime`, resolver behavior and
`PID_HASH`, and does not infer executable paths from command lines. An authorized
bounded Linux `live-01` run passed **8/8** multi-exec identity/timing/name checks
and demonstrated two periodic inventories, but exposed a direct-Parquet null that
materialized as numeric `0`. The narrow projection/schema repair passes **8/8**
observation tests and the expanded Linux/synthetic suite passes **65/65**. Linux
and Windows-targeted non-incremental Release builds pass with zero errors. The
repaired-binary Linux `live-02` passes 18/18 aggregate acceptance checks, including
null monotonic timing across all 1,312 Refresh rows and 8/8 multi-exec checks.
Native Windows runtime remains required.

This implementation is a separate sensor unit under the iterative workflow. It
does not retroactively expand TC-02's mechanical test-move scope, authorize
historical repair, or make the Linux-hosted broader Windows run an acceptance gate.
See [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].

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
- [x] TC-LNX-01 partial: destination revisions/environment checked; 59 HostActivity
  and 7 stdlib parser controls pass; existing DB readiness inspected read-only.
- [x] TC-LNX-01 remaining: approved isolated compatible PyUtil environment; 17-case
  execution and 224-identity destination comparison pass.
- [x] First sensor-fix source batch: Linux name repair, additive observation timing,
  and periodic Linux/Windows Refresh implemented without changing birth/hash.
- [x] Source qualification: 65/65 focused Linux/synthetic tests, 1/1 new Windows
  periodic synthetic test, and zero-error Linux/Windows-targeted Release builds.
- [x] TC-03 partial: bounded `live-01` handoff recorded with 8/8 multi-exec checks,
  two periodic inventories, and retained direct-Parquet null defect evidence.
- [x] TC-05 first repair: direct projection/schema null handling repaired and
  covered in both first-row orders; focused observation tests pass 8/8.
- [x] TC-LNX-02: opt-in read-only smoke helper and 18 synthetic refusal/budget
  controls pass; the existing database is readable without observed file change.
- [x] TC-LNX-02 sample disposition: the existing RHEL sample was read once, its raw
  directory is empty by design, and no future raw-file arrival is expected or gated.
- [x] TC-LNX-03 first slice: SmokeTests query/quality modules moved whole into
  `tests/contract`; 34/34 pass before/after with identical normalized identities.
- [x] TC-LNX-04: repaired `live-02` capture checked with 18/18 aggregate assertions
  and per-file nullable timing-schema coverage.
- [ ] Wintap extension: native Windows baseline/discovery/filtering and focused
  runtime acceptance. Linux-hosted cross-build and one periodic synthetic case
  pass, but do not close this platform gate.
- [x] TC-03 completion: repaired-binary `live-02` passes 18/18 aggregate checks;
  `live-01` remains retained defect evidence and Refresh monotonic timing stays null.
- [x] TC-04 first sensor round: explicit aggregate Parquet checks and immutable
  capture/validation hashes recorded outside Git.
- [x] TC-05 first sensor round: `live-01` defect, narrow repair, repeat stress and
  repaired `live-02` acceptance recorded.
- [x] TC-06 first SmokeTests slice: query/quality contract inventory and focused
  command documented; durable producer, S3/HTTP and UI modules remain separate.
- [x] TC-06 second SmokeTests slice: the complete synthetic analysis/summary-store
  module moved whole; 22/22 pass before/after and the contract package passes 56/56.
- [x] TC-06 third SmokeTests slice: synthetic S3 configuration/listing/source
  contracts moved whole; 13/13 pass before/after and the package passes 69/69.
- [x] `sfx-03`: bounded Linux procfs command-line provenance/status and child-only
  clone attribution implemented; 6/6 focused, 71/71 combined and 28/28 live
  aggregate assertions pass. Structured argv and deterministic DBT selection remain.
- [x] `sfx-04`: exec syscall attempts and successful scheduler image transitions
  receive distinct additive semantics; 7/7 focused, 78/78 combined and 26/26 live
  aggregate assertions pass. Process-lifetime executable selection remains open.
- [x] `sfx-05`: Linux executable path evidence source retained without changing
  selected path/name; 5/5 focused, 83/83 combined and 37/37 live aggregate
  assertions pass. BPF truncation and downstream lifetime policy remain open.
- [ ] TC-06: remaining organization slices completed with scoped discovery proof.
- [ ] Final: agreed sensor checks and organization boundaries accepted; broader
  gates and unresolved limitations recorded; durable facts promoted to canonical pages.

TC-02 completion is a first-cut milestone only. The overall workflow stays open
through native Windows acceptance, dataset checks, subsequent bounded cleanup
slices and final review.
