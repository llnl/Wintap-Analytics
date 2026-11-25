---
title: "Implementation Plan: Sensor Fixes and Test Cleanup"
type: concept
confidence: medium
grounded_by:
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/any-value-audit.md
  - wiki/overview/test-suite-organization-and-classification.md
  - ../wintap/tests/Wintap.Tests/README.md
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - streamlit/projects/SmokeTests/tests/README.md
policy: agent-editable
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/implement-sensor-fixes-and-cleanup-test-code; streamlit/projects; validation; ../wintap/tests; ../Wintap-PyUtil/tests
tags: [feature-work, testing, sensor-fixes, iterative-development]
---

# Implementation Plan: Sensor Fixes and Test Cleanup

## Current status and ownership

The bounded Linux process tranche, paired-row DBT repair, connection-ID cutover,
SmokeTests organization and stable .NET 10 policy are implemented. macOS/Linux
feature testing is complete; native Windows acceptance remains separate.
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]] gives current
next gates; [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]]
records results and retained failures. Original transfer/static-only instructions
are historical, not current prerequisites.

Wintap owns sensor/shared API/ETL changes and instruction/audit records; PyUtil owns
DBT; Analytics owns analysis/tests/wiki. Lintap packaging and Go pidstat qualification
use their separate feature plan. Confirm current revisions, permissions and file
ownership before continuation; never reset a shared checkout.

## Operating model

Work in small approved slices: freeze the contract and identities, implement one
change, run affected checks, obtain independent fresh capture evidence when producer
behavior changes, then repair/refine without weakening the oracle. Synthetic passes
are code contracts, not capture or delivery acceptance. Preserve historical evidence
and report unsupported/missing observations separately from failures.

## TC-01 / TC-02 — Inventory and mechanical organization

Completed first cut:

- HostActivity: three whole-module moves and path/discovery corrections; 59 affected
  cases and normalized identities preserved.
- PyUtil: configuration moved; unit/contract markers added to selected modules;
  17 representative passes and 224 preserved collected identities (4 / 220).
- Wintap: five whole-class moves plus additive `TestKind=unit` /
  `Execution=synthetic` traits. Existing Category, namespace, fixtures and bodies
  preserved; Windows emission neighbor remains part of the focused gate.

For any later move, compare before/after identities and bodies, change only
location-dependent imports/paths and approved markers, and avoid forwarding modules
that collect duplicates. Hold production sources constant for organization comparisons.

## Current Linux Tranche

Destination baseline and opt-in readiness helper are complete: HostActivity 59,
stdlib parser 7, PyUtil representative 17, and readiness controls 18 pass. The
old PyUtil environment was unusable; a separately approved isolated locked
environment closed the selected destination gate. The old RHEL database was a
one-time readable sample with empty raw input, not a future capture requirement.

SmokeTests organization is complete (86 contract / 1 transport / 13 UI cases).
Loopback HTTP defaults on, with case-insensitive `0`, `false`, `no`, or `off`
as explicit `SMOKE_S3_HTTP_TEST` opt-outs. This is not external S3 qualification.

## Included process-name multiplicity scope — 2026-11-23

The completed investigation distinguishes reusable PID from birth-scoped `PidHash`,
raw repeated exec from multiple births, requested paths from successful image
installation, and raw evidence from arbitrary downstream projection.

Accepted bounded process-image selection:

1. Eligible rows are Start/Refresh, excluding `exec_attempt`.
2. Prefer latest valid Refresh; otherwise latest `exec_success`; otherwise explicit
   eligible fallback.
3. Rank by observation UTC, monotonic observation time, receipt time, event time
   and a stable value tie-breaker; project name/path/arguments from the same row.
4. Preserve birth/lifetime aggregation and raw transition/failed-attempt evidence.
   Nullable staging defaults support older raw schemas.

Refresh is sampled current-state evidence, not an exec outcome or a new birth;
procfs enumeration/reads are not atomic. Raw monotonic time is comparable only
within its run/clock domain. The current model consumes full input; an explicit
as-of relation, freshness/ambiguity contract and broader non-image ANY_VALUE audit
are separate follow-ups, not unfinished requirements for this bounded repair.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql -->

## TC-03 — Capture handoff

The Linux capture cycle has completed. For a new approved slice, obtain:

| Item | Required boundary |
|---|---|
| Implementation | Fix ID, exact source/build/configuration |
| Platform | OS/architecture and enabled sensor capabilities |
| Data | Explicit isolated local snapshot or authorized remote scope |
| Workload | UTC interval, event families, independent expected actions |
| Limitations | Losses, unsupported cases and semantic compatibility |

Keep normal ETL output distinct from diagnostic direct-Parquet output. Do not
inherit private S3/data/runtime roots or launch collectors without agreed scope.
Keep actual host/account/IP identifiers and detailed capture output outside wiki.

## TC-04 / TC-05 — Validate and repair

Use the smallest relevant validator and explicit read budgets. Check fields,
identities, timing and workload correspondence, not merely nonempty tables. Separate
producer, oracle/test, downstream, environment and insufficient-evidence failures.
Retain failed output; make a narrow repair; rerun affected/neighbor checks and obtain
a fresh capture after producer changes. Do not relax thresholds to conceal defects.

The Linux direct timing null-to-zero defect and absent-resolver Stop failure were
repaired and validated with fresh output. The independent DBT selection defect
was repaired without rewriting raw or historical data.

## TC-06 — Remaining organization

Select one validation/PyUtil/coordination family at a time. Preserve platform skips,
retained-history controls and independent verifiers. Split mixed HostActivity cases
or extract shared fixtures only after mapping coverage. Isolated compactor and
historical suites need explicit qualification boundaries; age/name/size alone never
authorizes deletion. No wholesale project/default-suite rewrite is implied.

## Done checklist

- [x] TC-01/02: initial inventories, markers, mechanical moves and identity gates.
- [x] Linux destination baseline and bounded read-only readiness controls.
- [x] SmokeTests contract/transport/UI organization; full recorded run 100/100.
- [x] Linux executable-name evidence, additive timing and periodic Refresh.
- [x] Command-line provenance, exec kind, path source, exit status and Stop timing.
- [x] Fresh repaired process captures and independent workload validation.
- [x] .NET connection-ID authority, loopback/public context and PyUtil passthrough.
- [x] Repeated-exec/failed-attempt capture and deterministic paired-row DBT repair.
- [x] Legacy raw-schema compatibility and scoped DBT build qualification.
- [x] Stable .NET 10 SDK selection; macOS/Linux feature testing complete.
- [x] Align Lintap Debian/RPM SDK preflight with stable .NET 10 roll-forward;
  record resolved version and retain pre-cleanup rejection/runtime checks.
- [x] Add pinned Go build prerequisites to both Multipass launchers, existing-VM
  setup guidance and fake-download installer regressions; live installation separate.
- [x] S3 UTC upload-partition/attempt binding implementation and focused tests.
- [ ] Native Windows build/discovery/filtering/runtime acceptance.
- [ ] Authorized uploader endpoint/ambiguous PUT/HEAD fault qualification.
- [ ] Remaining validation/PyUtil/coordination organization, if selected.
- [ ] Final human review, explicit deferrals and release acceptance.

Separate future scope: structured/eBPF argv, syscall-result correlation, BPF
truncation, historical repair, as-of image relation, broader ANY_VALUE audit and
symmetric private-network namespace. These are not implementation authorization.
