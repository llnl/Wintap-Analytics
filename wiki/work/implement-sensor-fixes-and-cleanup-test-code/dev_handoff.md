---
title: "Dev Handoff: Sensor Fixes and Test Cleanup Closeout"
type: concept
confidence: medium
grounded_by:
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan.md
  - ../wintap/tests/Wintap.Tests/README.md
  - ../wintap/global.json
  - ../Wintap-PyUtil/tests/README.md
  - streamlit/projects/SmokeTests/tests/README.md
policy: agent-editable
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: wiki/work/implement-sensor-fixes-and-cleanup-test-code; ../wintap/tests; ../Wintap-PyUtil/tests
tags: [feature-work, dev-handoff, sensor-fixes, testing, cross-repo]
---

# Dev Handoff: Sensor Fixes and Test Cleanup Closeout

## Current checkpoint

Use the latest `feature/implement-sensor-fixes-and-cleanup-test-code` tips, not
the original transfer commits. Feature work is committed/pushed in the related
repositories; this documentation review is not a new commit/push authorization.
Check each destination's instructions, revisions and dirty state; preserve newer work.

- **Test organization:** HostActivity's 59 affected cases pass; PyUtil's initial
  representative gate passes 17 cases and preserves 224 collected identities
  (4 unit / 220 contract). SmokeTests is organized into contract, transport and UI
  packages, with 100 passing cases (86 / 1 / 13), no forwarding copies.
- **Process telemetry:** Linux name evidence, observation/receipt timing, periodic
  Refresh, command-line quality, exec attempt/success distinction, executable-path
  source, exit-code status and Stop timing are implemented and bounded-live tested.
  Birth-based `PidHash` and birth `EventTime` remain unchanged.
- **Repeated exec / DBT:** the fresh Linux capture and deterministic paired-row
  selector are complete. Select latest valid Refresh, otherwise latest successful
  exec, otherwise eligible fallback; take name/path/arguments from one row and
  exclude failed attempts. Focused contracts pass 32 with one existing skip;
  isolated DBT passes 139/139 and legacy-schema checks 13/13.
- **Connections:** .NET owns canonical tuple IDs; DBT and legacy PyUtil preserve
  producer IDs. Loopback is host-scoped, non-loopback uses public context, and
  gateways remain metadata. Release assumes a clean new-data cutover.
- **Publication:** shared S3 upload-time UTC partitions and durable ambiguous-attempt
  bindings are implemented; 8/8 focused tests pass. Dashboard read-only source and
  selected-run validation have executed, but yellow quality results and uploader
  fault/endpoint qualification are not full publication acceptance.
- **SDK/platforms:** stable .NET 10 policy is implemented (minimum 10.0.100,
  `latestMinor`, no prereleases). macOS/Linux feature testing is complete; native
  Windows acceptance remains separate. `Lintap.Tests` now supplies a Linux-focused
  assembly. Historical static-only guidance is superseded.

See [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]] for
scoped passes, failed rounds and evidence limits. Counts are recorded results,
not claims of a fresh rerun during this review.

## Next gates

1. Run native Windows build/discovery/filtering and focused execution using
   `../wintap/tests/Wintap.Tests/README.md`; record actual stable SDK and platform.
   Do not equate a Linux cross-build or synthetic case with Windows acceptance.
2. Complete separately authorized S3-compatible endpoint and ambiguous PUT/HEAD
   fault scenarios. Keep dashboard reads distinct from uploader mutation tests.
3. If continuing organization, select one remaining validation/PyUtil/coordination
   slice. Freeze identities, move mechanically, compare discovery and run affected
   checks. Do not delete historical qualification evidence based on age or size.
4. Record final human review and any explicit platform deferrals before release.

Separate follow-ups: structured/eBPF argv, syscall-result correlation, BPF
truncation, historical repair, explicit as-of image relation, non-image ANY_VALUE
audit, symmetric private-network namespace, and host OS-family labeling.
Unselected NFS attribution, interactive-session and listening-socket TODOs are
still intake, not an approved implementation queue.

## Ownership and evidence rules

Wintap owns sensor/shared API/ETL code and its `developer_docs` instructions/audits.
PyUtil owns canonical DBT; Lintap owns supporting packaging; Analytics owns tests,
analysis and this wiki. Cross-repo dependencies do not grant write permission.
Go pidstat packaging has its own [[wiki/work/fix-pidstat-collector/dev_handoff]].

For a new capture, agree platform, sensors, privileges, duration, isolated roots,
source revisions and independent workload expectations before launch. Keep normal
ETL separate from direct-Parquet diagnostic output. Classify producer, oracle,
downstream, environment and insufficient-evidence failures; retain failing evidence
and obtain a fresh capture after producer repairs. The old empty RHEL readiness
sample is not a future raw-data gate.

Apply `AGENTS.md` privacy rules to all persisted results. Keep raw telemetry,
identifiers, private configuration and detailed capture reports outside the wiki.
