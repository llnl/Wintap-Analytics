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
last_validated: 2026-11-23
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
Another session owns the small sensor changes and fresh captures; its exact fix scope
remains to be supplied. The original stub request is retained below as history.
<!-- HUMAN-DECISION: conversation 2026-11-22 — create a stub only; another session will update the workflow. -->

## Problem

Begin a phased workflow with the approved test-suite reorganization, followed by
sensor fixes whose scope is still to be supplied.

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

These are local branch references only; no push was performed. Existing untracked
work was left untouched. Lintap's supporting packaging repo has no new branch;
add one only if later scope requires it.

At TC-02 implementation start, the test session also switched PyUtil to its feature
branch. At Wintap draft start, the human authorized sharing its feature checkout
with the sensor worker; this session switched the clean Wintap checkout from
`develop` at `06849b4` to the existing feature branch at `a418aa4`. No fetch,
branch-ref update, commit, or push was performed.

## Later Sensor-Fix Phase

To be populated by the other session. No existing sensor or pipeline TODO is
automatically selected. This test-development session makes no sensor behavior or
schema changes.

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

- Exact sensor fixes, affected platforms, compatibility boundaries, and ordering.
- Sensor-specific dataset checks, verification commands, and acceptance criteria.
- Final workflow completion criteria.
- Windows runtime baseline/acceptance for the authorized Wintap draft;
  platform-project ownership remains a later decision.

## Next Step

The Analytics/PyUtil first draft is checked, bounded Linux sensor acceptance is
complete, and Windows acceptance remains separate. HostActivity passes 59
destination tests; an approved isolated uv environment passes 17 PyUtil cases and
preserves 224 selected identities. The read-only dataset helper passes its
synthetic controls, and the first SmokeTests query/quality move preserves 34 cases.
The second whole-file move adds 22 synthetic analysis/store cases, bringing the
classified contract package to 56 passing cases. A third whole-file move adds 13
mocked, transport-free S3 source contracts, bringing the package to 69 passing
cases. A fourth whole-file move adds 11 durable producer/Parquet contracts,
bringing the package to 80 passing cases. A fifth adds 5 unchanged page-query
contracts, bringing the package to 85. The synthetic localhost HTTP case is now
default-on with explicit environment opt-out. The final SmokeTests organization
places that one case under `tests/transport` and all 12 AppTest cases under
`tests/ui`; the 85 contracts remain under `tests/contract`, and full discovery
passes 98/98. Continue TC-06 with a separate validation/PyUtil/coordination slice.
The existing RHEL path was only a one-time sample and will not receive raw files;
its empty raw directory is not a gate. Continue later bounded cleanup slices under
the implementation plan without inventing a replacement data requirement.
<!-- HUMAN-DECISION: conversation 2026-11-22 — do not retain the one-time RHEL sample as a raw-data gate. -->
