---
title: "Identity and attribution experiments: results summary"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/LinuxLifecycleEvidence.cs
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/devtools; ../wintap/wintap/platform/linux; ../Wintappy
tags: [experiment, attribution, identity, preserved-failures]
---

# What the early experiments established

Thirteen isolated rounds reproduced timestamp-derived identity substitution and
final-batch delivery loss. Candidate normal/burst/restart controls passed their
measured identity/count gates;missing-birth controls remained incomplete rather
than fabricating canonical identities. This reproduced a mathematical failure
mechanism,not the historical host's exact trigger.

Authoritative Exit/Clone birth evidence feeds the shared process formula. Legacy
records remain supported with explicit unknown when canonical birth is unavailable.
Bounded exit-only shadow classification is experimental evidence,not a general
Linux role classifier,benign verdict or capture-suppression policy.

Same-binary batch-barrier A/B demonstrated final-window ordering:barrier-off lost
113paths/1,247events;barrier-on preserved2,088paths/14,616events. Early deadline
failures were retained. This motivated—not substituted for—the later exact
shutdown/callback cause proof.

Read-only historical SQL projections corrected file/network summary grouping,
spelling/Open counters and elapsed duration. Historical database bytes were not
rewritten;metadata precedence and broader event-domain fanout remained separate.

Later proof:[[wiki/work/host-process-identity-patch/shutdown_delivery_results]].
Missing-birth/historical-loss limits:[[wiki/work/host-process-identity-patch/package_host_results]].
Original round matrices,raw vectors and projections:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
