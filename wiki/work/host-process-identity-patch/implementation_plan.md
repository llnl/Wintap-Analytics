---
title: "Host/process identity: compact implementation record"
type: workflow
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/ProcessIdentity.cs
  - wiki/work/wintap-telemetry-identity-and-data-quality/implementation_plan.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap/wintap/core; ../Wintappy/wintap_dbt
tags: [identity, implementation, retrospective]
---

# Implemented and scoped verification complete

- [x] Single hostname/PID/canonical-birth formula;versioned stores and explicit unknowns.
- [x] Host-bound locked/atomic AgentId persistence with restart/clone/legacy controls.
- [x] Authoritative Linux lifecycle inputs and bounded opt-in exit-only recovery.
- [x] Collector Process/Refresh telemetry without self-I/O feedback or invented Start.
- [x] Correct lifetime summary grouping/counters and integer timestamp conversion.
- [x]10scollection-edge reporting with1/5/20ssensitivity,strict gates unchanged.
- [x] Bounded exact admission/registration/projection/output diagnostics.
- [x] Demonstrated startup/shutdown causes and experimental ordering corrections.
- [x] Fresh normal/interior/shutdown-tail controls and pressure envelope through256children.

These checkboxes describe implementation/scoped proof,not historical-loss closure
or installed-release acceptance. Earlier failed controls stay failed in the archive.

## Still separate

- [ ] Clean native/package qualification and multi-day real-host collection.
- [ ] Windows live runtime,resource/service deadlines and production-control policy.
- [ ] Actual saturation,earlier unexplained losses and complete kernel/durable fate.
- [ ] Historical migration,metadata/OS-label defects and rollout if separately approved.

Umbrella workflow:[[wiki/work/wintap-telemetry-identity-and-data-quality/implementation_plan]].
Results:[[wiki/work/host-process-identity-patch/verification]]. Original evolving plans,
commands and per-round checklists:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
