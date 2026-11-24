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
  - ../wintap/developer_docs/audits/sfx-06-linux-exit-code-status.md
  - ../wintap/developer_docs/audits/sfx-07-linux-stop-observation-timing.md
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/tests/test_network_activity_sql.py
  - ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md
  - ../wintap/developer_docs/audits/sfx-09-loopback-connection-context.md
  - validation/dataset-smoke/README.md
  - streamlit/projects/SmokeTests/tests/README.md
policy: agent-editable
last_validated: 2026-11-23
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

## Included process-name multiplicity scope — 2026-11-23

The human added the latest `process_name` issue—multiple names associated with the
same OS PID—to this feature. It continues the open deterministic executable-
attribution work in [[wiki/todo/linux-process-executable-attribution]]. This is an
investigation and affected producer/model-test scope, not a conclusion that every
multi-name PID is invalid or authorization for historical repair.
<!-- HUMAN-DECISION: conversation 2026-11-23 — include the latest multiple-name/same-PID issue in the current feature scope. -->

Use a bounded slice:

1. Bind the observation to its source layer and exact producer/PyUtil revisions.
   Group first by normalized host, OS PID and `PidHash`, not PID alone.
2. Classify each multi-name case as PID reuse across distinct hashes, multiple raw
   observations within one process lifetime, a valid successful exec transition,
   a failed exec attempt, or a downstream projection/aggregation artifact.
3. For one-lifetime cases, order rows with the additive observation fields and use
   `ExecutionObservationKind` plus `ExecutablePathSource`; keep name and path from
   the same observation. Birth `EventTime` alone is not sufficient ordering.
4. Measure current silver `any_value` behavior, including whether independently
   selected `process_name` and `process_path` can mismatch or select an attempted
   executable. Do not treat raw Start-row multiplicity as multiple process births.
5. Prepare fixtures for repeated successful exec, failed attempts, wrapper/
   interpreter transitions, PID reuse, Refresh, and Stop after the final image.
6. Present an explicit initial-versus-latest representative-image policy and an
   ordered-history shape for human review before changing DBT/schema semantics.

**Acceptance for the investigation/design slice:** the frequency and layer of the
reported behavior are measured; same-lifetime exec is separated from PID reuse;
failed attempts cannot become the representative successful executable; selected
name/path stay paired; and unresolved policy choices remain visible. Native Windows,
historical rebuilding, and migration compatibility remain separate gates.

### Refresh as point-in-time image evidence — design input, not a decision

The human's proposal is plausible for a narrower question: a valid Refresh can be
the best evidence of the process image that was observable **at that scan time**.
Linux Refresh reads the current `/proc` process listing and records the process birth
in `EventTime` plus the scan instant in `ObservationTimeFileTimeUtc`; Windows periodic
Refresh similarly reads a live snapshot and records the scan observation time. Both
recompute the birth-scoped `PidHash`, so a Refresh can be joined to the lifetime
without treating the reusable PID as identity.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §RunSnapshot; §CreateRefreshMessage; ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §RunPeriodicRefreshSnapshot; §CreateRefreshMessage -->

This does **not** make Refresh universally more accurate. Apply the following
semantic separation during investigation:

| Question | Preferred evidence candidate | Reason / limitation |
|---|---|---|
| When was the process born? | Birth `EventTime` and `PidHash` | Refresh observes an existing process; its observation time is not birth. |
| What image was live at a scan instant? | Latest valid Refresh at or before the query time | It samples current state, but `/proc`/snapshot enumeration and field reads are not atomic and the process may change or exit during the scan. |
| Did an exec request occur? | `exec_attempt` row | Refresh cannot prove a syscall attempt or its outcome. |
| Which image installation succeeded? | `exec_success` row, ordered by observation time | Refresh can corroborate later state but does not identify the transition that produced it. |
| What was current at process termination? | Last valid observation before Stop, with explicit freshness bounds | A Refresh can be stale; Stop and later observations must not be rewritten from it. |
| What should the lifetime summary report? | Unselected until policy review | “Initial,” “latest successful,” and “latest observed” answer different analytical questions. |

Therefore the initial plan is to expose Refresh as a separate **current-state
evidence role**, not to let it overwrite the canonical lifetime `process_name`.
For a current-state view, a candidate precedence is: matching valid Refresh at the
requested as-of time; otherwise the latest ordered `exec_success`; otherwise the
birth/start observation with explicit quality. This is a proposal for measurement
and fixture evaluation, not an accepted DBT contract. A Refresh must lose authority
when its identity is missing/mismatched, its executable evidence is unavailable, or
the query asks about a historical transition rather than current state.

### Detailed implementation sequence

#### Phase A — Freeze contracts and inspect evidence

1. Record the exact Wintap and PyUtil revisions, raw/normal-ETL/direct-Parquet
   source layer, platform, enabled process sensors, and schema version.
2. Inventory which rows carry `ActivityType`, `ProcessStartSource`,
   `ExecutionObservationKind`, `ExecutablePathSource`, `ObservationTimeFileTimeUtc`,
   `ObservationTimeMonotonicNanoseconds`, `ObservationRunId`, `ProcessName`, and
   `ProcessPath` on Linux and Windows.
3. Verify that Refresh rows use birth `EventTime` plus observation time and that
   repeated Refresh rows retain one `PidHash`; do not infer this from a row count.
4. Document missing comparability: Windows Refresh currently has live snapshot name
   and path but does not carry the Linux exec-kind/path-source vocabulary. Do not
   silently equate platform-specific evidence strength.
5. Inventory every `any_value` use across the PyUtil SQL/DBT tree, then trace the
   affected model uses to reachable downstream consumers. The current textual
   inventory is a baseline (73 matches across SQL files) and must be regenerated at
   the pinned revision. This is a column/feature audit, not a blanket ban: the
   existing compaction decision treats the debt as non-blocking for compaction, but
   this feature must resolve semantic uses that can misrepresent process identity or
   image state.
   The first read-only inventory is recorded in
   [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/any-value-audit]].

#### Phase A2 — Classify `any_value` by column contract

For each use, record the relation, grouping key, expression, null behavior, expected
invariance, whether row ordering has meaning, downstream consumers, and the proposed
replacement or retained justification. Include process, network, file, registry,
image-load, host, SELinux, and legacy-model uses rather than assuming the process
finding generalizes. Use three outcomes:

1. **Invariant-safe shortcut:** within the grouping key, all non-null values are
   proven equal, or there is at most one non-null value and null is intentionally
   ignored. `any_value` may remain as a performance/readability shortcut, but the
   invariant must have a regression test and an explicit comment or contract.
2. **Conflict-visible metadata:** values are normally stable but disagreement is
   meaningful. Keep a deterministic representative only if consumers need one, and
   expose a distinct-count/conflict flag rather than hiding the disagreement.
3. **Ordering-sensitive feature:** values can legitimately change across rows or
   must be paired with another value. `any_value` is not acceptable as the semantic
   selector; use a deterministic ordered row or a separately defined aggregate.

DuckDB's `any_value` ignores nulls and, absent an explicit ordering contract, does
not establish which non-null row supplied the result. Therefore do not document it
as “first non-null” unless the SQL explicitly defines that ordering. The safe claim
is instead “all eligible non-null candidates are equivalent, so whichever eligible
candidate is returned has the same meaning.” If there are multiple distinct
candidates, order and provenance must be addressed.

Initial process-model audit targets:

| Field/feature | Initial risk hypothesis | Required treatment |
|---|---|---|
| `process_name` | Can change across fork/exec/Refresh and can select an attempted image | Ordering- and evidence-sensitive; paired with path. |
| `process_path` | Can change and can disagree independently with name | Ordering- and evidence-sensitive; select the same row as name. |
| `args` / command line | Can vary by observation and has explicit quality states | Preserve observation/source semantics; do not arbitrary-select for canonical image. |
| `os_pid` | Usually invariant within `PidHash`, but PID reuse is outside the group contract | Prove invariant in each grouping model; retain QA conflict count. |
| `hostname` / `agent_id` | Expected stable for a scoped identity, but conflicts indicate data quality | Prove invariance and expose conflicts; do not use arbitrary selection to hide them. |
| parent identity fields | May differ under late linkage, missing history, or race | Measure conflicts and document whether representative or temporal parent is required. |
| file hashes and user fields | May be invariant, absent, or observation-dependent | Test per model; do not generalize from process rows. |
| downstream `os_pid` summaries | Often a display shortcut after grouping by a stronger key | Retain only after group-specific invariance tests pass. |

This matrix is a starting hypothesis, not a pre-approved classification. The same
SQL function can be safe for one column and wrong for another.

#### Phase B — Measure the reported multi-name population

1. Group raw observations by normalized host, OS PID, and `PidHash`; separately list
   PID groups that contain more than one hash to identify reuse.
2. Within each hash, count distinct names and paired `(name, path)` values by
   activity/source: fork/start, `exec_attempt`, `exec_success`, Refresh, and Stop.
3. For each multi-name lifetime, order observations by the best available evidence:
   observation UTC, same-run monotonic time where comparable, source kind, and a
   stable file/row tie-breaker. Mark ordering confidence instead of fabricating it.
4. Measure whether the current silver `any_value` result selects an attempt, a
   successful image, a Refresh value, or a name/path pair that never co-occurred.
5. Produce aggregate-only results for counts/rates and sanitized fixture labels;
   retain raw identifiers outside the wiki and do not repair historical data.
6. For every affected `any_value` field, compare `count(distinct non-null value)`
   and null/non-null patterns within the actual grouping key. Separate harmless
   repeated values from conflicting candidates; do not count duplicate identical
   rows as semantic disagreement.

#### Phase B2 — Measure prevalence, recurrence, and concentration

Do not answer “how common is the problem?” from raw row volume alone. A frequently
run wrapper can create many observations from one recurring cause, while a rare
one-off defect can affect many independent process lifetimes. Report the population
at several levels:

| Level | Example measure | What it answers |
|---|---|---|
| Observation | Multi-name rows / all process rows | How much telemetry is affected or noisy? |
| Lifetime | Affected `PidHash` lifetimes / all lifetimes | How many process instances experience it? |
| PID reuse group | Affected PID groups / PID groups | Is reusable PID ambiguity contributing? |
| Host-day | Host-days with at least one affected lifetime / observed host-days | How broadly does it occur operationally? |
| Host | Hosts with affected lifetimes / observed hosts | Is it isolated to one machine or environment? |
| Cause cluster | Independent recurring signatures with affected lifetimes | How many distinguishable causes appear? |

For every numerator and denominator, retain the source layer, time window, platform,
and evidence-quality restrictions. Report both count and rate, plus the number of
hosts and host-days contributing. A large observation count from one repeatedly
invoked script must not be presented as broad host prevalence.

Cluster recurring cases before estimating generality. Candidate aggregate-only
signature components include the ordered source-kind pattern, successful-image
transition shape, paired executable/path category, parent/launcher category,
Refresh confirmation pattern, and coarse time cadence. Keep exact hostnames,
accounts, addresses, command lines, and raw paths out of persistent artifacts.
Use a stable signature version so a later algorithm change does not silently merge
or split historical clusters.

For concentration, report at least:

1. largest-cluster share of affected lifetimes and observations;
2. top-`K` cluster share and the smallest `K` covering 50%, 90%, and 95% of
   affected lifetimes (with `K` reported, not only a percentage);
3. per-host and per-host-day maximum share;
4. leave-one-host-out and leave-one-day-out rates; and
5. whether the finding persists after capping each cause cluster to one lifetime
   per host-day.

These measures distinguish a common generic producer/model problem from a narrow
but highly recurring workload signature. Do not call a cluster a root cause until
the source evidence and an independent workload or temporal pattern support that
interpretation; otherwise label it a recurrence/signature cluster.

#### Phase B3 — Feedback loop for algorithm tuning

Use the data as a controlled feedback loop rather than allowing the current
algorithm to train on or validate itself:

1. **Baseline:** run the current detector/projection unchanged and persist only a
   versioned aggregate report plus bounded, sanitized exemplars outside the wiki.
2. **Review labels:** humans classify a stratified sample of clusters and cases as
   valid repeated exec, PID reuse, failed-attempt contamination, Refresh/current-
   state disagreement, producer evidence loss, downstream selection error, or
   unknown. Stratify by host, day, platform, cluster size, and evidence quality so
   the dominant wrapper cannot consume the entire sample.
3. **Candidate rule:** change one ranking, eligibility, pairing, or clustering rule
   at a time. Record the policy version and the expected semantic effect.
4. **Shadow evaluation:** run candidate and baseline side by side on the same
   immutable data. Compare affected lifetimes, false selections, name/path pairing,
   Refresh freshness, cluster concentration, and unknown/ambiguous rates.
5. **Holdout:** validate on a later time window and, when possible, a held-out host
   or workload family. Do not accept a rule because it only fixes the recurring
   known wrapper.
6. **Promotion:** require human review of changed cases and retain the baseline,
   candidate, labels, policy version, and limitations. Promote only a rule whose
   improvement holds across independent strata without hiding unresolved cases.
7. **Drift monitoring:** rerun aggregate prevalence/concentration checks after
   each meaningful producer, DBT, or workload change. Alert on new clusters,
   sudden host concentration, rising ambiguous rates, or evidence-source changes.

The feedback artifact should answer: what changed, which labeled cases motivated
it, which cases improved or regressed, whether the result generalized beyond the
dominant recurring cause, and what remains unknown. Automatic production retuning,
historical rewriting, and self-labeling from `any_value` output are out of scope.

#### Phase C — Build the semantic fixture matrix

Create synthetic and, only when separately authorized, fresh bounded captures for:

- fork/start followed by no exec;
- failed exec attempts followed by a different successful image;
- wrapper/interpreter followed by `exec` into a final image under the same PID;
- multiple successful image transitions under one `PidHash`;
- Refresh before and after an image transition;
- repeated Refresh with unchanged and changed current image;
- PID reuse with distinct birth times and hashes;
- process exit during enumeration or field lookup;
- Stop after the final image; and
- missing, unavailable, or conflicting name/path evidence.

Each fixture must assert identity, paired name/path, source kind, observation time,
Refresh freshness, and whether the row is eligible for current-state versus
lifetime selection. Raw Start/Refresh counts must not stand in for process counts.

#### Phase D — Prototype views before producer changes

1. Add a read-only analysis query/view in the test fixture environment, not yet a
   production model, that returns one row per `(PidHash, observation)` with paired
   image fields and an evidence classification.
2. Add a current-state candidate view that selects the latest valid Refresh as of a
   requested observation time, with deterministic fallback to ordered successful
   exec and then qualified start evidence.
3. Add a lifetime candidate view that reports separate initial, latest-successful,
   latest-Refresh, and selected-policy fields rather than hiding disagreement.
4. Add a column-contract QA relation for each audited `any_value`: group key,
   non-null distinct count, null-only flag, conflict flag, chosen value, source
   evidence, and whether the field was invariant-safe, conflict-visible, or
   ordering-sensitive.
5. Add process-specific QA columns/counts for `num_process_name`, distinct paired
   images, selected evidence kind, ordering confidence, and name/path disagreement.
   Preserve current model names until compatibility and query costs are reviewed.
6. Compare the candidate views against current `process.sql` output and classify
   every difference as expected policy change, arbitrary-selection correction,
   missing evidence, or fixture/model defect.

#### Phase E — Human policy review and bounded implementation

Present the measured results and choose, explicitly:

1. whether `process_name` in the existing lifetime model means initial image,
   latest successful image, latest observed image, or remains a compatibility field;
2. whether Refresh is authoritative only for a new current-state relation or also
   for the lifetime summary;
3. whether ordered image history is a view, separate relation, nested attribute,
   or raw-only evidence; and
4. how Linux/Windows evidence differences and old Parquet missing columns are
   represented.

Only after approval should the smallest implementation be selected. Prefer a
deterministic paired-row DBT change plus regression fixtures if raw fields suffice;
retain `any_value` where the column-contract evidence proves equivalence; replace it
only where conflict or ordering semantics require it. Add producer fields only when
ordering or evidence provenance is demonstrably insufficient. Historical repair,
mixed-version migration, and a broad schema rewrite require separate authorization.

#### Phase F — Acceptance and closeout

- Unit/synthetic tests cover all fixture cases and preserve existing process counts.
- DBT tests prove failed attempts cannot be selected as successful canonical images.
- Name and path always come from one observation row.
- Every retained `any_value` has an invariance/eligibility contract and regression
  evidence; every removed use has a documented semantic reason and replacement.
- Duplicate identical values are not misreported as conflicts, while distinct
  non-null candidates and null-only groups remain visible.
- Current-state queries select a matching, fresh Refresh and expose its observation
  time; stale or mismatched Refresh rows are not silently promoted.
- PID reuse remains distinct from repeated exec under one `PidHash`.
- Linux and Windows behavior is tested within each platform's evidence contract.
- A bounded fresh capture validates the approved semantics independently of the
  model's own output; native Windows acceptance remains a separate gate.
- Verification records row counts, selected evidence, limitations, revisions and
  compatibility decisions; durable semantics are then promoted to canonical pages.

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

### Prepared Linux capture cycle — awaiting collector launch

The named workload is now prepared for a bounded Linux executable-attribution cycle.
Its default one-round behavior remains compatible with existing smoke checks. The
new optional cases preserve independent stimulus evidence for repeated successful
execs in one PID (`wt_reexec`), a failed exec attempt followed by a successful exec
(`wt_execfail`), changing argument tokens, and a long-lived Refresh candidate
(`wt_refresh`). `--rounds`/`--interval` repeat the complete named set and the portable
manifest records same-PID execution stages rather than treating names as identity.
<!-- GROUND_TRUTH: ../wintap/devtools/telemetry_smoke_workload.py §exec_worker; §main; ../wintap/devtools/test_telemetry_smoke_workload.py -->

The recommended first cycle is approximately ten minutes: nine rounds at 60-second
spacing, `--hold 0.25`, and one `--refresh-hold 600` candidate. Lintap must be
launched first with process, exec, clone, exit, and rundown sensors enabled, normal
Parquet/ETL output enabled, and a one-minute Refresh interval (`ProcessRefreshEnabled`,
`ProcessRefreshIntervalMinutes=1`, `ProcessRefreshOffsetMinutes=0`). The operator
must confirm the actual data root and retain the workload manifest, collector build/
configuration, UTC interval, runtime capability receipt, raw process output, and
smoke-parquet oracle. No capture has started yet.

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
- [x] TC-06 fourth SmokeTests slice: the 11-case durable producer/Parquet contract
  moved whole with path-only import updates; 11/11 pass before/after, the package
  passes 80/80, and project-root discovery finds each moved case exactly once.
- [x] TC-06 fifth SmokeTests slice: the 5-case page-query/materialization contract
  moved whole without content changes; 5/5 pass before/after, the package passes
  85/85, and project-root discovery finds each moved case exactly once.
- [x] SmokeTests loopback HTTP policy: enabled when `SMOKE_S3_HTTP_TEST` is unset,
  with case-insensitive `0`, `false`, `no`, or `off` as explicit opt-outs. The
  default localhost case passes and the project-wide default run passes 98/98.
- [x] TC-06 sixth SmokeTests slice: the byte-identical 1-case localhost transport
  module moved into `tests/transport`; default and explicit opt-out behavior pass,
  and project discovery remains 98/98 with the identity present exactly once.
- [x] TC-06 seventh SmokeTests slice: the 12-case Streamlit AppTest module moved
  into `tests/ui` with only three project-main path-depth adjustments; 12/12 pass
  before/after, contracts remain 85/85, and project discovery remains 98/98.
- [x] SmokeTests remote diagnostics: replace the generic remote-source catch-all
  with sanitized connection/listing/evidence/dashboard stage codes; the UI package
  passes 13/13 and full project discovery/execution passes 99/99. Target-system
  diagnosis remains an operator follow-up, not a local acceptance claim.
- [x] `sfx-03`: bounded Linux procfs command-line provenance/status and child-only
  clone attribution implemented; 6/6 focused, 71/71 combined and 28/28 live
  aggregate assertions pass. Structured argv remains a separate deferred producer
  follow-up; deterministic DBT image selection is complete.
- [x] `sfx-04`: exec syscall attempts and successful scheduler image transitions
  receive distinct additive semantics; 7/7 focused, 78/78 combined and 26/26 live
  aggregate assertions pass. Process-lifetime executable selection remains open.
- [x] `sfx-05`: Linux executable path evidence source retained without changing
  selected path/name; 5/5 focused, 83/83 combined and 37/37 live aggregate
  assertions pass. BPF truncation and downstream lifetime policy remain separate
  future follow-ups, not blockers for the bounded repeated-exec repair.
- [x] `sfx-06`: Linux Stop rows distinguish CO-RE kernel wait status from fallback
  placeholder zero without decoding or changing `ExitCode`; 5/5 focused, 88/88
  combined and 43/43 final live assertions pass.
- [x] `sfx-07`: Linux Stop retains kernel occurrence and receipt timing without
  changing EventTime or identity; 4/4 focused, 92/92 combined and 50/50 live
  aggregate assertions pass.
- [x] Five-tuple current-source investigation: no duplicate-port call exists in
  available v7 history; current Wintap and canonical DBT semantics/exact IDs were
  compared with bounded offline vectors. The absent ACME4 build remains unresolved.
- [x] Five-tuple single-authority source migration: qualify .NET endpoint reversal,
  opposite-host, same-host client/server, field sensitivity and context vectors;
  retain ordinary gateways as metadata and loopback host scoping; remove DBT and
  legacy PyUtil hash generation. Source-linked Wintap cases pass 32/32 and PyUtil
  contracts pass 222/222. Native Windows acceptance remains deferred; exact DBT
  JSON is not an acceptance requirement.
- [x] `sfx-09`: move loopback host scoping into connection context for the full
  RFC 1122 loopback block, use `public` for non-loopback connections, and leave
  both gateway identity slots empty. Source-linked checks pass 33/33; focused
  PyUtil passthrough contracts pass 78/78 and all 11 selected real-DBT nodes pass.
  Release is a clean new-data cutover with no legacy or mixed-data requirement.
- [x] Included process-name multiplicity: the finalized Linux capture measures same-
   PID cases by `PidHash` and source layer, and the human-reviewed representative-
  image/current-state semantics are recorded in verification. The deterministic DBT
  implementation is complete; an explicit as-of relation is deferred.
- [x] ANY_VALUE audit baseline: inventory 73 source-SQL text matches at pinned PyUtil
   revision `4085747` (71 calls and 2 comments), identify preliminary field
   contracts, and define equivalence/conflict/order-sensitive regression fixtures in
   [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/any-value-audit]].
- [x] ANY_VALUE synthetic contract slice: add six in-memory DuckDB cases for
   invariant fields, duplicate/null handling, visible conflicts, paired name/path,
   failed-attempt exclusion, and Refresh as-of selection. Focused combined suite
   passes 31/31 with one pre-existing skip; Black and compilation pass.
- [x] Linux capture preparation: extend the named workload with repeated rounds,
   same-PID successful exec/argument stages, failed-attempt coverage, and a long-lived
   Refresh candidate; Python 3.12 regression passes 2/2.
- [x] Linux real capture: the operator completed the one-minute-Refresh,
   approximately ten-minute nine-round workload; all 19 targeted PIDs matched,
   manifest/raw process output and clean-shutdown evidence were retained externally,
   and the isolated DBT analysis completed 139/139 nodes. See verification for
   sanitized counts and the unresolved deterministic projection finding.
- [x] Deterministic process projection: replace changing image-field `any_value`
   usage with paired-row selection for latest valid Refresh/current state and latest
   successful-exec fallback; preserve failed-attempt/history evidence. PyUtil focused
   contracts pass 32/32 with one existing skip and the isolated DBT build passes
   139/139; native Windows qualification remains open.
- [x] Linux tranche disposition: bounded repeated-exec capture, producer evidence,
   paired-row DBT selection, legacy-schema compatibility and focused validation are
   complete. Structured argv/eBPF argv, syscall-result correlation, BPF truncation,
   historical repair, and the explicit as-of relation are recorded as separate
   future follow-ups; Windows validation remains deferred.
- [ ] TC-06: SmokeTests organization is complete with scoped discovery proof;
  remaining validation/PyUtil/coordination organization slices are still open.
- [ ] Final: agreed sensor checks and organization boundaries accepted; broader
  gates and unresolved limitations recorded; durable facts promoted to canonical pages.

TC-02 completion is a first-cut milestone only. The overall workflow stays open
through native Windows acceptance, dataset checks, subsequent bounded cleanup
slices and final review.
