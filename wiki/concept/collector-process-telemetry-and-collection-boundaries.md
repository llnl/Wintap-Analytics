---
title: "Collector process telemetry and collection boundaries"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/infrastructure/CollectorEventPolicy.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs
  - ../wintap/wintap/core/etl/extract/ProcessSerializer.cs
  - ../Wintappy/wintap_dbt/models/silver/process.sql
  - ../Wintappy/wintap_dbt/models/gold/process_summary.sql
  - ../wintap/wintap/core/etl/WintapETL.cs
  - ../wintap/wintap/core/infrastructure/WintapSvcCore.cs
  - ../wintap/wintap/core/infrastructure/EtlShutdownBarrier.cs
  - ../wintap/wintap/core/infrastructure/SerializerCallbackAdmission.cs
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/infrastructure; ../wintap/wintap/platform/linux; ../Wintappy/wintap_dbt/models
tags: [collector, self-telemetry, collection-boundaries, lifecycle, attribution]
---

# Ordinary process telemetry for the collector

The user requires the Lintap service process to appear in ordinary datasets for
retrospective validation, not solely in experimental manifests or sidecars.
The candidate implementation in `wintap` admits Linux self-PID **Process** messages
through `EventChannel`; all other self-PID message types remain suppressed.
Windows/macOS self-filter behavior is unchanged. Linux startup inventory includes
the collector as an already-existing process using a genuine **Refresh**, with
its readable `/proc` birth, executable, command line, user and parent context.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/CollectorEventPolicy.cs §ShouldSuppress; ../wintap/wintap/core/infrastructure/EventChannel.cs §SendCore; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §IsUsableProcess; §CreateRefreshMessage -->

The inventory must be enabled and successfully run. Disabled sensors or an
unavailable birth do not establish collector coverage. Inventory now skips
unavailable-birth entries rather than assigning observation time as a birth.
No synthetic Start, Stop, or collection cutoff is added. Including a process
record does **not** require recording the collector's own log/parquet writes,
which can generate telemetry feedback.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §ProcessRundown; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §CreateRefreshMessage; ../wintap/wintap/core/infrastructure/CollectorEventPolicy.cs §ShouldSuppress -->

The existing normal process serializer retains Refresh as Refresh in `raw_process`.
Wintappy's silver `process` includes Refresh birth context; gold `process_summary`
joins from those processes rather than requiring self-generated file/network rows.
Wintap owns collection, Wintappy owns downstream transformations, and
Wintap-Analytics hosts the wiki and independent verification artifacts.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent; ../Wintappy/wintap_dbt/models/silver/process.sql §process_base; ../Wintappy/wintap_dbt/models/gold/process_summary.sql §joins -->

For retrospective discovery, inspect normal process rows using the expected
collector executable **and command line**, then retain hostname/AgentId/PID/PidHash
and ActivityType/EventTime. Process name alone is not proof of collector role;
manual or multiple collector instances need contextual disambiguation. A recorded
Refresh means “already existed,” not “collection began at this EventTime.” Test
`/proc` receipts independently verify those rows but are not required to query them.

## Three boundaries that must not be conflated

**Producer running is not query readiness.** Shared `WintapETL.Start` schedules
background initialization and returns before all serializers exist;TCP/UDP come
late. Service startup uses a fixed5second delay,not a confirmed subscription barrier.
Revision11Linux controls show network startup before TCP initialization and a
complete-trace TCPdeficit at Esper→serializer (54→50per host). Exact registration/
correction proof was open at revision11;this does not explain all historicalTCPabsence or
establish a Windowslive verdict.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/WintapETL.cs §Start/ProcessObjectModelWorker_RunWorkerCompleted; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync -->
<!-- SYNTHESIS: readiness risk from live source plus wiki/work/host-process-identity-patch/delivery_diagnostic_results.md -->
See [[wiki/work/host-process-identity-patch/delivery_diagnostic_results]].

Revision12 observes fourAXON/sixCALDERATCP handoffs completed before query registration.
CALDERA's entire six-event deficit matches those counts;AXON retains six additional
post-registration missing counts. A real production-EPL control proves pre-deployment
inputs are not replayed. The candidate Linux-only/default-off
`WINTAP_EXPERIMENT_ETL_READINESS=true` now waits for successful query attachment and
completed serializer constructors before collector admission,with a30second readiness
wait bound. The existing5second plugin delay is unchanged,not enlarged. Failed query
registration or timeout blocks producers. This is neither a capture-begin receipt,
kernel-hook readiness guarantee,nor a general startup/shutdown cancellation policy.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EtlStartupReadiness.cs; ../wintap/wintap/core/etl/WintapETL.cs §Ready/ProcessObjectModelWorker_RunWorkerCompleted; ../wintap/wintap/core/infrastructure/PluginManager.cs §ETLReady; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync; wiki/work/host-process-identity-patch/delivery_diagnostic_results.md -->

1. **Collector process lifetime:** OS birth through actual exit. The collector
   starts before its sensors and normally cannot observe its own final exit after
   those sensors have stopped.
2. **Actual collection interval:** when particular sensors/producers capture activity.
   Initialization, disabled/failed capabilities and producer shutdown can make
   these intervals different from each other and from the collector's lifetime.
3. **Analysis window:** a filter over recorded data. A missing lifecycle record may
   be present outside the queried slice; examine broader context before diagnosing loss.

Collector visibility supplies a process reference and restart identity, **not exact
per-sensor capture bounds by itself**. Start/cutoff evidence remains separate work.
<!-- SYNTHESIS: user clarification 2026-10-24 and lifecycle/inventory ownership above -->

## Boundary-aware quality interpretation

The user accepts some incomplete data near collection start/end. Report **start
edge, interior and end edge** separately using explicitly declared boundaries and
tolerances. On2026-10-24 the user selected **10-second** start/end edges with
**1/5/20-second sensitivity** reports. Keep raw counts and incomplete
observations visible; do not discard edge events, stretch identity lifetime validity,
or silently rewrite old strict acceptance results. Event time and processing time
are separate: an event processed near shutdown need not have occurred near an edge.

CALDERA shutdown-window experiments stop **`lintap.service` on `caldera-host`**,
not the host/OS or CALDERA application. Teardown stress findings are not automatic
evidence of steady-state failures. Preserve previous measurements while applying
explicit boundary-aware criteria when those criteria and bounds become available.
See [[wiki/work/host-process-identity-patch/package_host_results]].

The implemented conservative overlay requires verified clock alignment and
per-sensor transition brackets. A span must fit the same band for every possible
boundary; otherwise it is uncertain. Missing evidence stays unclassified. Existing
BaseEbpfSensor logs provide operational startup/stop envelopes, not uninterrupted
delivery or exact per-hook cutoffs. Historical revision7 lacks independent clock
receipts, so its formal overlay is unclassified rather than retroactively green.
Missing payloads use separately labelled stimulus intervals, not fabricated event
timestamps. Strict conservation, hash validity and exact DBT birth gates stay intact.
<!-- GROUND_TRUTH: wiki/work/host-process-identity-patch/collection_edges.py; wiki/work/host-process-identity-patch/collection_edge_analysis.py; wiki/work/host-process-identity-patch/collection_edge_results.md -->
Rerun plan: [[wiki/work/host-process-identity-patch/collection_edge_plan]].

## Verification scope

### Terminal query/callback barriers are not native capture cutoffs

Revision14exact traces demonstrate a live finalTCPcontext callback after completed
serializer shutdown:twoCALDERArows/fourcounts accepted after the zero-depth return,
all absent from drain/export. AXONpasses the same round,so disappearance is not
closure. This confirms a shared ordering defect consistent with revision13AXON's
undrained tail,not exact retrospective reconstruction of that earlier boundary.
<!-- GROUND_TRUTH: wiki/work/host-process-identity-patch/shutdown_delivery_results.md -->

Experimental Linux-only/default-off `WINTAP_EXPERIMENT_ETL_SHUTDOWN_BARRIER=true`
freezes Esper's clock and explicitly executes pending timers through current+10,000ms
for the bundled aggregation horizon. It then closes listener admission and joins
already-running callbacks before any serializer drain. The OS clock,raw event time,
process births and identity inputs are unchanged;this is a terminal scheduling
operation,not an11second wall-clock sleep. Runtime/callback stages each have30s wait
bounds;timeout/failure does not declare live callbacks drained,and does not cancel
an in-flight native call. Custom longer-window EPL/full service-deadline guarantees,
kernel cutoff,fsync/upload and production/Windows acceptance are outside this control.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EtlShutdownBarrier.cs; ../wintap/wintap/core/infrastructure/SerializerCallbackAdmission.cs; ../wintap/wintap/core/etl/WintapETL.cs §ShutdownWithBarrierAsync; ../wintap/wintap/core/etl/extract/Serializer.cs §CloseCallbacks -->
Plan/results:[[wiki/work/host-process-identity-patch/shutdown_delivery_plan]].
Revision16 strict controls conserve54AXON/60CALDERAobservedTCPcounts through exact
row-ID/raw joins;samecandidate17 conserves58/58perhost with all file/endpoint stimuli
interior at1/5/10/20s. Callback quiescence before all drains,zero lateacceptance or
cutoffrefusals pass. This verifies scoped observed delivery on disposable Linux,
not native kernel/durable fate,performance,Windows/installed release acceptance or
historical loss closure. Original controls/database remain unchanged.
<!-- GROUND_TRUTH: wiki/work/host-process-identity-patch/shutdown_delivery_results.md; wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §shutdown archive members -->

Candidate regressions cover platform-specific filtering, real Refresh semantics,
canonical birth/hash, invalid/missing birth and reused-PID restart separation.
All eight revision7 captures passed raw collector visibility; all eight DBT builds
retained unique collector rows/metadata, but four exact derived-birth checks failed.
Default conservation/TCP failures remain separate. Four fresh boundary-aware raw
rounds pass,with shutdown uncertainty retained;three fresh exact DBT birth failures
persist. See [[wiki/work/host-process-identity-patch/collection_edge_results]]. No production
rollout, historical migration or universal lifecycle coverage is implied.

Subsequent revision9 **fresh reprocessing** with integer timestamps restores all12
collector exact-birth checks (eight revision7/four revision8captures),without changing
recordings or rewriting old failed verdicts. Full DBT12/12passes;conservation/TCP/
saturation and cutoff uncertainty remain separate. Contract:
[[wiki/concept/filetime-derived-timestamp-precision]]. Bounded attribution tracing is
now a default-off,locally tested candidate,not installed final-fate evidence.
<!-- GROUND_TRUTH: wiki/work/host-process-identity-patch/timestamp_and_trace_results.md; ../wintap/wintap/core/infrastructure/AttributionTrace.cs -->

Related: [[wiki/concept/wintap-ecosystem-glossary]],
[[wiki/concept/telemetry-identity-and-endpoint-orientation]].
