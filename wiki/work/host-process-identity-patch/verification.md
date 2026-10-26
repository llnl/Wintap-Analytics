---
title: "Host/process identity and delivery: verification summary"
type: diagnostic
confidence: high
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/verification.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap; ../Wintappy; wiki/work/host-process-identity-patch
tags: [identity, delivery, verification, retrospective]
---

# Compact verification

The completed umbrella scope and proof are now in
[[wiki/work/wintap-telemetry-identity-and-data-quality/verification]]. Read that
summary rather than the historical round-by-round audit.

- Shared canonical process identity and host-bound AgentId persistence qualify
  independently;missing birth remains unknown,not a timestamp-derived identity.
- Collector Process/Refresh visibility and bidirectional TCP endpoint/identity
  checks pass without self-I/O feedback or synthetic lifecycle observations.
- Integer timestamp correction restores exact downstream birth representation;
  lifetime grouping and protected counters/multiplicities pass fresh DBT controls.
- Exact startup subscription and late post-drain callback defects are demonstrated;
  experimental readiness/terminal-window callback ordering conserves observed output.
- Accepted pressure controls conserve13,312paths/93,184file events and3,328child
  lifetimes/TCPendpoint pairs;24fresh DBT builds and complete observed delivery joins pass.
- Final work-folder suite103passed;28archives/262source matches and installed
  service/DLL/AgentId/historical DB preservation pass.

## Limits kept visible

Recovery/readiness/shutdown controls remain Linux/default-off experiments. Sampled
pending max348/1024 is not saturation. Clean native/package installation,Windows
live runtime,resource/deadline and complete kernel/durable fate are not accepted.
Earlier AXONloss/TCP and CALDERAsaturation failures remain unresolved. Historical
repair,queue resizing,deterministic metadata/OS-label fixes and rollout were not done.

Detailed commands,receipts and original failed audits remain locally available but
uncommitted,and are included in the verified pre-condensation archive:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]]. Harnesses/tests
remain here for selective reproduction;restore archived JSON for historical replay.
