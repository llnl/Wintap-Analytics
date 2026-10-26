---
title: "Disposable-host identity and recovery: results summary"
type: diagnostic
confidence: high
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap; wiki/work/host-process-identity-patch
tags: [identity, attribution, experiments, preserved-failures]
---

# Installed disposable-host experiments—meaningful findings

AXON/CALDERA identity,restart,parent and non-loopback endpoint controls passed.
Canonical lifecycle-input and collector-visibility corrections qualified native
tests/installed controls. Normal installed suites and30-minute soaks demonstrated
workload conservation,not universal host coverage or permanent drain acceptance.

Exit-only recovery remains opt-in:authoritative Stop birth evidence supports historical
attribution without synthetic Start or active/durable lifetime insertion. Positive
controls improved attribution;birth-disabled/legacy negative controls retained
unknowns instead of fabricated identities.

## Failures that matter

- Earlier AXON lost252paths/2,067events in a revision7control;default-workload TCP
  absences remain unexplained. Later delivery passes do not reconstruct those losses.
- Revision6CALDERAshutdown retained1,346unknown rows/1,471events across199PIDs,
  matching capacity refusals. Recorded/final resolver identities do not prove they
  were available at earlier admission/lookup attempts.
- Bounded capacity A/B sensitivity supported admission pressure but did not establish
  production sizing. Retry defaults remain1024/ten nominal1s attempts.
- Failed conservation/canonical-birth/deadline controls and the lintap-dev ENOSPC
  incident remain preserved. Its complete service I/O/resource effect is unproved.

Later exact startup/shutdown and pressure proof is summarized in
[[wiki/work/host-process-identity-patch/shutdown_delivery_results]] and
[[wiki/work/host-process-identity-patch/pressure_results]]. Those passes close their
observed controls,not these historical failures.

Full original package/state/host receipts and round tables:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]],archive member
`wiki/work/host-process-identity-patch/package_host_results.md`.
