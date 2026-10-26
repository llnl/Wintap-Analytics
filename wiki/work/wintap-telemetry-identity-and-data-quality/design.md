---
title: "Design: evidence-led telemetry identity and data quality"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/ProcessIdentity.cs
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - ../wintap/wintap/core/infrastructure/EtlShutdownBarrier.cs
  - ../wintap/wintap/core/etl/esper/tcp.epl
  - ../Wintappy/wintap_dbt/macros/time.sql
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap/wintap/core; ../Wintappy/wintap_dbt
tags: [feature-work, retrospective, design, evidence, identity]
---

# Design distilled from implementation

| Concern | Decision and durable meaning |
|---|---|
| Host identity | Persist a host-bound AgentId with locked/atomic writes. Preserve legacy state; a cloned binding mismatch gets a distinct identity. |
| Process identity | One production formula uses normalized hostname,PID and canonical UTC FILETIME birth. Agent UUID and callback/exit timestamps are not alternate hash inputs. Unknown remains unresolved. |
| Lifecycle | Acquire authoritative birth evidence; keep Stop/Refresh distinct from Start. Exit-only recovery can support historical attribution without inventing birth or inserting an active lifetime. |
| Networking | Preserve directed source/destination provenance and host-relative local/remote endpoints. Directionless five-tuple connection identity is a different concept. Accept enum/legacy activity vocabulary explicitly. |
| Downstream SQL | Group summaries by lifetime,conserve event counts and prevent fanout. Use integer epoch subtraction/floor-to-microseconds for FILETIME timestamps; raw100ns values do not change. |
| Attribution | Keep bounded retry policy unchanged. Admission,lookup,registration and final-fate receipts diagnose causes; larger queues are not a substitute for proof. |
| Startup | Experimental Linux readiness admits collectors only after successful EPL registration and completed serializer construction. Pre-registration events are not replayed. |
| Shutdown | Experimental Linux barrier stops collectors,flushes attribution,freezes Esper,advances pending bundled10s windows,closes/joins callbacks,then drains. Runtime-clock advancement does not change event time or identity. |
| Evidence | Independent workload manifests plus complete bounded observer histories and exact output joins. Trace refusal/truncation invalidates absence claims. Final rename is not fsync/upload proof. |
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ProcessIdentity.cs; ../wintap/wintap/core/etl/WintapETL.cs; ../wintap/wintap/core/infrastructure/EtlShutdownBarrier.cs; ../Wintappy/wintap_dbt/macros/time.sql -->

## Verification principles learned

- Separate stimulus generation,kernel observation,normalized output and downstream
  annotation; each has its own completeness boundary.
- Preserve first failures; isolate a cause,correct only that cause,and repeat fresh
  controls. Later passes do not retroactively explain older losses.
- Compare protected identities,counters and multiplicities separately from unordered
  metadata. Never blanket-accept executable file-ID/display stability.
- Use10-second collection edges with1/5/20-second sensitivity,without softening
  identity or conservation gates or relabeling uncertain intervals.
- TCP EPL `FirstSeen` aggregates callback `ReceiveTime`,not kernel `EventTime`.
  Validate pressure endpoints inside exact capture bounds plus PID/ports/identity;
  keep stimulus-edge classification separate.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/tcp.epl; wiki/work/wintap-telemetry-identity-and-data-quality/verification.md -->

## Explicitly not selected

DuckDB2.0/unofficial .NET wrappers; production queue resizing; grouped-retry
implementation; historical repair; default-enabling experimental controls; generic
custom-EPL drain guarantees or production rollout. These require separate decisions.
