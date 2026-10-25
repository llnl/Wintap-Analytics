---
title: "Pressure and shutdown-tail: verified burst-envelope summary"
type: diagnostic
confidence: high
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
  - ../wintap/wintap/core/etl/esper/tcp.epl
  - wiki/work/host-process-identity-patch/pressure_workload.py
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/host-process-identity-patch; ../wintap/wintap/core
tags: [pressure, conservation, attribution, proof]
---

# Outcome

Same qualified revision16private package,retry1024unchanged:32/128/256-child
interior and immediate post-workload shutdown-tail tests pass on AXON/CALDERA.
Each child independently records birth,PID,fourfile write/read pairs and a32-byte
non-loopback TCP echo. Socket syscalls are not predicted kernel event counts.

Six accepted experiments/24off-on controls conserve **13,312paths/93,184file events**
and **3,328child lifetimes/TCPendpoint pairs**.24fresh full canonical DBT builds pass
births,collector retention and raw→silver/gold protected counters.12complete traces
contain1,013,739receipts with zero refusals/errors/discards/truncation and exact
observed-stage/raw joins. Whole-file unknown/orphan gates pass.

Sampled pending peak348/1024,zero pressure-child capacity refusal/exhaustion:
**tested burst envelope,not saturation or production sizing**. Short-run peak RSS
1,192,704–1,542,156KiB is an observation,not resource equivalence acceptance.
10sprimary/1,5,20s sensitivity stays separate;tail uncertainty is not relabeled interior.

## Preserved failed oracle and cause proof

Revision20CALDERAtrace-off failed44endpoint pairs/152observations. Every supposedly
missing observation was present in raw,later than the stimulus+2s predicate but
inside capture bounds. Production TCP `FirstSeen` aggregates callback `ReceiveTime`,
not kernel `EventTime`. This was an oracle error,not demonstrated sensor loss.

Bounded correction selects exact capture time/PID/ports/roles/canonical identity;
deterministic delayed-receipt tests and fresh128/256repeats pass. Original20failure
and stopped escalation are preserved;no sensor timestamp/schema change or extra
arbitrary grace. Historical losses remain unresolved.

## Preservation and scope

28archives hash-verified,262source matches;installed DLL/AgentIds/historical DB
size/mtime unchanged. AXON/CALDERAinactive/PID0/restarts0;lintap-devactive/PID701.
No commands remain running. No installed release,Windows live,performance/deadline,
kernel/fsync/upload or historical migration acceptance;DuckDB2.0 held.

Original full results,per-stage counters,edge bands,exact cause receipts and hashes:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
