---
title: "Exact shutdown delivery gate"
type: workflow
confidence: medium
grounded_by:
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - ../wintap/wintap/core/etl/WintapETL.cs
  - ../wintap/wintap/core/infrastructure/WintapSvcCore.cs
  - wiki/work/host-process-identity-patch/delivery_diagnostic_results.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: developer
status: draft
source_paths: ../wintap/wintap/core/etl; ../wintap/wintap/core/infrastructure
tags: [shutdown, conservation, bounded, evidence]
---

# Approved milestone continuation

User approved exact cutoff evidence, a correction only after cause proof, and new
trace-off/on controls on AXON/CALDERA. Preserve prior failures, installed controls,
historical DB and unrelated work. No production rollout or broad historical repair.

Hypothesis: a live Esper context emits after the TCP serializer stops its scheduled
drains and returns successful shutdown. `IsEnabled=false` does not guard the callback
or `Save`, and listeners remain attached. Exact boundary/active-callback/depth/accepted
receipts are required to distinguish this from overlapping drain/write failure.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Stop/Shutdown/ProcStatement_Events/Save -->

# Gates

- [x] Qualify bounded shutdown/callback observer and deterministic production-EPL
  queue-before-final-window versus window-before-queue ordering control.
- [x] Reproduce accepted-but-undrained rows with exact completed-shutdown bracket.
  Revision14 CALDERA:two rows/four counts accepted after completed shutdown,all
  undrained. AXONpasses this round;timing-dependent shared defect,not historicalclosure.
- [x] Implement bounded Linux-only/default-off correction after live cause proof.
  Final window completion must precede listener quiescence and serializer drain.
  No longer arbitrary sleep, fabricated lifecycle observation or raw schema change.
- [x] Tests cover real EPL final-window conservation plus callback admission,
  in-flight joins, failures/timeouts and unchanged ordinary behavior.
  Revision16 locked qualification267native tests/Linuxbuild pass. Revision15's
  ambiguousTimer/EventChannel compile failure archived;aliases corrected in fresh16.
- [x] Fresh trace-off/on controls on both hosts: complete observer, exact row IDs,
  producer/projection/accepted/drained/enqueued/finalized TCP counts, finalized/raw
  counters/timestamps, identity/per-path/collector/non-loopback endpoints.
- [x] Retain primary10s and1/5/20s sensitivity, separate uncertain/interior/edges;
  report resource samples without accepting performance equivalence.
- [x] Final source/archive/service/DLL/AgentId/database preservation receipts;
  update verification, checklist, canonical semantics and log.

Qualification/capture driver:`shutdown_delivery_experiment.py`; uses private SDK
on CALDERA with disk preflight, fresh snapshots and create-new evidence roots.
Managed-only derivatives preserve revision11 dependencies/native artifacts; not a
clean native rebuild, installed-package acceptance or Windows runtime qualification.

If exact live reproduction fails, preserve that result and do not infer closure
from the deterministic control or disappearance in a later capture.

# Candidate barrier semantics

`WINTAP_EXPERIMENT_ETL_SHUTDOWN_BARRIER=true` explicitly selects Linux terminal
shutdown behavior. After collector stop returns and attribution final flush:

1. Freeze the Esper internal clock with `ClockExternal`.
2. Execute pending timer boundaries with `AdvanceTimeSpan(current+10000)` for the
   bundled10second aggregation horizon. This changes only terminal runtime scheduling,
   not OS time, raw event times, process births or identity inputs. It is NOT a longer
   wall-clock sleep or a generic drain for arbitrary/customEPL durations.
3. Close callback admission, detach serializer listeners, join already-admitted
   callbacks before draining any serializer; preserve explicit refusal receipts if
   a callback arrives after cutoff. Acceptance requires zero such refusals.
4. Drain existing serializer queues/writers/cache using existing shutdown paths.

Clock operation and callback-quiescence stages each have30s wait bounds; existing
serializer/writer/cache deadlines are unchanged. Timeout/failure returns incomplete
without declaring live callbacks drained. It does NOT cancel an already-running
native clock call; failed observer/process evidence stays failed. No production
deadline guarantee or general shutdown cancellation design is established here.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EtlShutdownBarrier.cs; ../wintap/wintap/core/infrastructure/SerializerCallbackAdmission.cs; ../wintap/wintap/core/etl/WintapETL.cs §ShutdownWithBarrierAsync; ../wintap/wintap/core/etl/extract/Serializer.cs §CloseCallbacks/ProcStatement_Events -->

Evidence:[[wiki/work/host-process-identity-patch/shutdown_delivery_results]],
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
Revision16 passes54AXON/60CALDERATCPcounts. Samecandidate17 passes58/58perhost,
allstimuli interior at1/5/10/20s;final262source matches/archive/preservation pass.
Results:[[wiki/work/host-process-identity-patch/shutdown_delivery_results]].
Trace ETL clock boundaries use `QueueDepth` to carry runtime milliseconds; serializer
boundaries use it for queued rows. Analyzer separates components and checks the
exact10,000ms horizon; this diagnostic field never enters raw schemas.
