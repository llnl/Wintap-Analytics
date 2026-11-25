---
title: "Feature Brief: Implement sensor fixes and cleanup test code"
type: concept
confidence: medium
grounded_by:
  - wiki/overview/test-suite-organization-and-classification.md
  - wiki/todo/test-suite-reorganization.md
  - wiki/concept/llm-assisted-feature-workflow.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan.md
  - streamlit/projects/SmokeTests/tests/README.md
policy: agent-editable
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief.md; wiki/overview/test-suite-organization-and-classification.md
tags: [feature-work, testing, test-organization, sensor-fixes, cross-repo]
---

# Feature Brief: Implement sensor fixes and cleanup test code

## Status

The test-development session has implemented and checked an iterative first cut.
The sensor workstream has completed bounded Linux process units through `sfx-07`
and connection-identity work through `sfx-09`; native Windows acceptance and later
test-organization slices remain open. The feature now
also includes investigation of the latest `process_name` finding: multiple names
associated with the same OS PID. That scope must distinguish repeated exec within
one `PidHash`, PID reuse across distinct process lifetimes, and downstream arbitrary
name selection before choosing a fix. The bounded Linux repeated-exec producer,
evidence, and paired-row PyUtil projection are now complete for this tranche. An
explicit as-of relation is noted for future follow-up, and native Windows validation
remains deferred. The original stub request is retained below
as history.
<!-- HUMAN-DECISION: conversation 2026-11-22 — create a stub only; another session will update the workflow. -->
<!-- HUMAN-DECISION: conversation 2026-11-23 — include the latest multiple-process-name/same-PID issue in the current feature scope. -->

## Problem

Organize tests in bounded slices and validate selected sensor/model fixes with
independent fresh captures. Implemented scope and remaining gates are below.

## Original Phase 1 and Scope Expansion

The initial scope followed [[wiki/overview/test-suite-organization-and-classification]]
for Analytics and Wintappy/PyUtil only, excluding Wintap .NET restructuring from
that first cut. Those implemented changes and their verification remain unchanged.
<!-- HUMAN-DECISION: conversation 2026-11-22 — Phase 1 uses the approved Analytics/PyUtil plan only. -->

- Freeze a fresh inventory and record purpose, platform, discovery commands,
  opt-in requirements, and evidence boundaries before changing the filesystem.
- Use the approved staged classification, command, and mechanical-move sequence.
- Preserve historical qualification evidence. Review coverage and provenance
  before any merge, archive, or deletion decision.
- Explain collection-count changes and verify the affected discovery/import paths.
<!-- GROUND_TRUTH: wiki/overview/test-suite-organization-and-classification.md §Refactor sequence; §Staleness and duplication rules; §Required verification after filesystem changes -->

Related maintenance item: [[wiki/todo/test-suite-reorganization]].

The human subsequently added Wintap repository tests to the workflow and requested
**initial analysis and planning**. The static inventory and execution boundaries
are in [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis]];
the approved first managed slice and later capture loop are in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]]. The
human then authorized implementation and explicitly deferred the Windows baseline
for a static-checked draft on the shared feature checkout. Additive traits and five
test moves are implemented; no sensor source was changed or managed runtime gate
run here.
<!-- HUMAN-DECISION: conversation 2026-11-22 — include Wintap repo tests; prepare initial analysis and plan. -->
<!-- HUMAN-DECISION: conversation 2026-11-22 — proceed with the first slice; authorize a static draft with Windows acceptance pending and share the feature checkout with the sensor worker. -->

## Branches

Matching local branch: `feature/implement-sensor-fixes-and-cleanup-test-code`.

| Repository | Starting revision | Checkout at workflow creation |
|---|---|---|
| Wintap-Analytics | `a63e1d4` — local `main` | Switched to the feature branch. |
| Wintap-PyUtil | `bab304c` — local `main` | Branch created; existing checkout left unchanged. |
| Wintap | `a418aa4` — cached `origin/develop` | Branch created; existing checkout left unchanged. |

These are historical creation checkpoints, not current tips. Feature work has
since been committed/pushed, including Lintap packaging. Preserve newer work.

At TC-02 implementation start, the test session also switched PyUtil to its feature
branch. At Wintap draft start, the human authorized sharing its feature checkout
with the sensor worker; this session switched the clean Wintap checkout from
`develop` at `06849b4` to the existing feature branch at `a418aa4`. No fetch,
branch-ref update, commit, or push was performed.

## Later Sensor-Fix Phase

The selected bounded Linux sensor units and connection-identity work are recorded
in the implementation plan and verification page. The newly included
`process_name` multiplicity issue continues
[[wiki/todo/linux-process-executable-attribution]] inside this feature. Inclusion
authorizes investigation, design, fixtures, and affected producer/downstream tests;
the later approved paired-row selector prefers latest valid Refresh, otherwise
latest successful exec, otherwise eligible fallback. Historical repair and broad
producer rewrites remain separate.

The first question is whether the reported rows share only an OS PID or also one
birth-scoped `PidHash`. Multiple names can be valid raw observations when one
process lifetime successfully execs more than once; the defect risk is silently
collapsing those observations into an arbitrary or mismatched canonical name/path.
<!-- HUMAN-DECISION: conversation 2026-11-23 — add same-PID process-name multiplicity to the active scope without preselecting its remedy. -->

## Iterative Development

The human authorizes first-draft test changes with lightweight affected checks,
followed by testing against fresh small datasets from the separate sensor session,
repairing/cleaning/refining tests, and repeating. Finishing the entire suite
refactor is not a prerequisite for sensor work to begin.
<!-- HUMAN-DECISION: conversation 2026-11-22 — start first-cut test implementation and iterate alongside the separate sensor session. -->

See [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan]]
for the detailed slices, capture handoff, and validation loop, and
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]] for results.

## Open Questions

- Remaining ambiguity/non-image ANY_VALUE contracts beyond the completed Linux repair.
- Whether a separate historical/as-of relation and ordered image history should be
  added; this is deferred after the current full-input paired-row projection.
- Exact remaining sensor fixes, affected platforms, compatibility boundaries, and ordering.
- Sensor-specific dataset checks, verification commands, and acceptance criteria.
- Final workflow completion criteria.
- Windows runtime baseline/acceptance for the authorized Wintap draft;
  platform-project ownership remains a later decision.

## Next Step

Use [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]] for
current closeout gates: native Windows, uploader endpoint/fault qualification,
selected remaining organization and final review. macOS/Linux testing, bounded
process capture/DBT repair and SmokeTests organization (100 cases) are complete.
The empty one-time RHEL readiness sample is not a future data gate.
<!-- HUMAN-DECISION: conversation 2026-11-22 — do not retain the one-time RHEL sample as a raw-data gate. -->
