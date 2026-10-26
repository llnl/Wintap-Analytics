---
title: "Wintap ecosystem glossary"
type: concept
confidence: medium
grounded_by:
  - wiki/concept/telemetry-identity-and-endpoint-orientation.md
  - wiki/component/wintap-api-shared-data-model.md
  - wiki/pipeline/nesper-esper-event-stream-processing.md
  - wiki/repo/wintappy-pipeline-repo.md
  - wiki/work/improve-lintap-data-quality/diagram-glossary.md
  - wiki/work/host-process-identity-patch/package_host_results.md
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/BoundedEventTimeCache.cs
  - ../wintap/wintap/core/infrastructure/AttributionTrace.cs
  - ../wintap/wintap/core/infrastructure/EtlStartupReadiness.cs
  - ../wintap/wintap/core/infrastructure/EtlShutdownBarrier.cs
  - ../wintap/wintap/core/infrastructure/SerializerCallbackAdmission.cs
  - ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs
  - ../Wintappy/wintap_dbt/macros/time.sql
  - ../wintap/BUILD_AND_TEST.md
  - ../Lintap/packaging/lintap-deb/build-deb.sh
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/concept; wiki/component; wiki/pipeline; wiki/repo; ../wintap/wintap/core/infrastructure
tags: [glossary, telemetry-semantics, identity, attribution, data-quality, cross-repo]
---

# Wintap ecosystem glossary

Living, plain-language reference; started 2026-10-24 at the user's request.
Definitions describe meaning, not universal implementation or release acceptance.
Add unfamiliar terms as they arise, with links to their owning source/page.
Experimental ideas are explicitly labeled. Historical datasets may use older schemas.

## Ecosystem and collection

| Term | Definition |
|---|---|
| **Wintap** | Research-oriented host telemetry platform; the `wintap` repo owns the Windows sensor, shared model and current cross-platform collection code. |
| **Lintap** | Linux collection name/build within the Wintap implementation. The separate `Lintap` repo mainly supplies packaging and development infrastructure in this wiki. |
| **Wintap-Analytics** | Repository hosting this wiki and exploratory analysis; not the owner of canonical sensor or DBT transformations. |
| **Wintappy / Wintap-PyUtil** | Canonical Python/DBT/DuckDB post-processing pipeline for recorded Wintap/Lintap data. |
| **Telemetry** | Observations about host activity, such as process creation, file operations and network traffic; not a complete account of everything the host did. |
| **Sensor / producer** | Component that observes a particular activity and emits telemetry. |
| **ETW** | Event Tracing for Windows: Windows instrumentation used by Wintap sensors. |
| **eBPF** | Linux kernel instrumentation used by Lintap to observe activity and send records to userspace. |
| **Ring buffer / poller / callback** | Kernel-to-userspace record buffer; a poller retrieves records and a callback handles each one. Distinct sensors can deliver related records in different orders. |
| **WintapAPI / WintapMessage** | Shared normalized event model/envelope carrying event type, times, PID, identity and domain-specific data. |

Sources: [[wiki/component/wintap-api-shared-data-model]],
[[wiki/work/improve-lintap-data-quality/diagram-glossary]],
[[wiki/repo/wintappy-pipeline-repo]], and repository roles in `AGENTS.md`.

## Identity and process lifecycle

| Term | Definition |
|---|---|
| **PID** | Operating-system process number. It can be reused after a process exits, so it is not a process-instance identity. |
| **Process instance / lifetime** | One execution of a process, from its birth to its exit; a reused PID refers to another instance. |
| **Canonical start / authoritative birth** | The process's actual start time from accepted OS/kernel evidence, not the time a callback happens to observe it. |
| **`pid_hash` / `PidHash`** | Process-instance key. The `pid-v2` contract uses normalized hostname, PID and canonical start time; agent UUID is not an input. Older recordings are not silently rekeyed. |
| **`agent_id` / `AgentId`** | Persisted collector UUID, bound to the host in the candidate identity implementation; distinct from process identity. |
| **Attribution** | Associating an event with its owning process instance; correct identity does not guarantee complete metadata or recorded lifecycle coverage. |
| **Process resolver** | Runtime component that finds process information using PID and the event's time, through caches and a process-history database. |
| **Active cache / historical identity cache** | Fast lookups for current processes / bounded retained identities with lifetime time bounds. Neither is the recorded telemetry itself. |
| **Start / Stop / Refresh (Rundown)** | Birth observation / exit observation / snapshot observation of an already-existing process. A Refresh is not evidence that the process was just created. |
| **Lifecycle coverage** | Which lifecycle observations were actually captured, such as birth and exit; separate from whether an event can be attributed. |
| **Exit-only evidence** | Experimental recovery of canonical identity from authoritative start information carried by a Stop. It does not invent a Start or imply complete lifecycle coverage. |
| **Unknown sentinel** | Explicit placeholder for unresolved identity. Many unknown observations sharing it are not one real process. |
| **Orphan row** | An event whose process key has no matching process record in the dataset being checked. Known-key orphans and explicit unknowns are separate defects. |

Sources: [[wiki/concept/telemetry-identity-and-endpoint-orientation]],
[[wiki/work/host-process-identity-patch/package_host_results]].
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §BuildResolveProcessAtTimeQuery; §ResolveProcessIdentityAtTime; §RetainExitIdentityEvidence; ../wintap/wintap/core/infrastructure/BoundedEventTimeCache.cs §TryGet -->

## Time and evidence

| Term | Definition |
|---|---|
| **Event time** | Time the observed activity happened, distinct from when it was delivered or processed. |
| **Receive time / processing time** | Receipt timestamp / time work is performed. Actual field meaning depends on the producer and stage; zero or missing receive times cannot establish delivery order. |
| **TCP `FirstSeen` receipt-time scope** | Production TCP EPL uses min/max `ReceiveTime`, not kernel `EventTime`. Under callback backlog, valid observations can fall outside a completed stimulus interval. Pressure validation uses exact capture bounds plus PID/ports/identity; stimulus-edge classification remains separate. |
| **FILETIME** | UTC timestamp encoding in 100-nanosecond units since 1601-01-01, used by the process identity contract. |
| **Derived microsecond timestamp / representability** | Analysis timestamp floored from raw100ns ticks. Integer DBT conversion preserves exact raw births only when divisible by10;other remainders are intentionally discarded,not used for identity. See [[wiki/concept/filetime-derived-timestamp-precision]]. |
| **Monotonic time / boottime** | Elapsed-time clocks rather than calendar time. On Linux the distinction includes whether suspend time is counted; clock type must be preserved when deriving start time or duration. |
| **Recorded telemetry** | Data actually saved to capture files; evidence of exported observations, not proof that every host event was collected. |
| **Final resolver** | Shorthand for the resolver database snapshot after collection stopped, including its matching WAL when needed. It shows eventual identity knowledge, not when that knowledge became available. |
| **WAL** | Write-ahead log containing database updates not yet incorporated into the main database file. A database snapshot without its matching WAL can omit evidence. |
| **Sidecar / receipt** | Auxiliary evidence file / diagnostic record documenting configuration, observations or stage outcomes alongside telemetry. Missing or truncated evidence is not a zero count. |
| **Manifest / independent oracle** | Independently recorded expected workload / separate calculation checking captured data against that expectation. |
| **Event conservation** | Expected observations/counts survive the pipeline. Aggregated row counts alone cannot prove conservation. |
| **Quality gate / acceptance** | Explicit check and its pass/fail decision for a stated scope. Passing identity does not automatically pass coverage, conservation, shutdown or release. |
| **Collection boundary / boundary tolerance** | Beginning or end of actual collection / explicitly declared edge interval where incomplete observations are expected and reported separately from interior quality. The tolerance is not permission to fabricate identity or erase events. |
| **Conservative capture band / uncertain transition** | Event interval classified only when every possible sensor boundary agrees; otherwise uncertain. Approved10-second edges have1/5/20-second sensitivity. Operational Start/Stop brackets do not guarantee delivery; missing clock/bound evidence stays unclassified. |
| **Analysis-window boundary** | Edge of a time-filtered query or dataset slice. A lifecycle record outside that slice may exist in the broader collection; this is not necessarily sensor data loss. |

Boundary implementation/proof: [[wiki/work/host-process-identity-patch/collection_edge_results]].
Pressure scope proof:[[wiki/work/host-process-identity-patch/pressure_results]].
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/tcp.epl §firstSeen/lastSeen; ../wintap/shared/WintapAPI/WintapMessage.cs §constructor; wiki/work/host-process-identity-patch/pressure_results.md -->
<!-- GROUND_TRUTH: wiki/work/host-process-identity-patch/collection_edges.py; wiki/work/host-process-identity-patch/collection_edge_results.md -->

Sources: [[wiki/work/host-process-identity-patch/package_host_results]],
[[wiki/work/improve-lintap-data-quality/diagram-glossary]].

## Queues, retries and shutdown

| Term | Definition |
|---|---|
| **Retry queue** | Bounded waiting area for events whose owners are not yet resolved, allowing another attribution attempt later. |
| **Admission / capacity refusal** | Acceptance into a queue / rejection of that scheduling request because the queue is full. A retry-capacity refusal need not drop the event; it may proceed with unknown attribution. |
| **Exhausted retries** | Attribution still failed after the allowed attempt count. Distinct from being denied queue space or from shutdown preventing requeueing. |
| **Admission pressure / saturation** | Demand for waiting space exceeds what the queue can accommodate / the queue reaches its limit. |
| **Backpressure / backlog** | Downstream slowness constrains upstream progress / accumulated unfinished work. Backlog is not itself evidence of deadlock. |
| **High-water mark** | Highest observed queue occupancy within the counter's stated scope. Per-stream high water need not equal the shared queue's total. |
| **Final fate** | What ultimately happened to a particular event: attributed, exported unknown, dropped, or incomplete. Entering Esper or invoking a callback does not prove durable output. |
| **Admission/final-fate evidence** | Tracking an event's admission through output rather than inferring outcomes from counters. Revision11complete scoped traces match finalized rows to archived raw output;broaderTCPdelivery/readiness fails,and native/durable/rollout acceptance remains open. |
| **Bounded attribution trace / diagnostic event ID** | Optional create-new Linux JSONL with capped queue/rows/bytes/strings,explicit refusal/error/truncation counts and weak per-object retry correlation. Its ID is not `pid_hash` or a raw-schema field;Esper return does not prove durable export. |
| **Diagnostic row ID / finalized-output join** | Weak per-object serializer/parquet correlation without a raw-schema ID. A final rename receipt is checked against archived raw row multisets;it is not filesystem fsync,remote upload or complete kernel-event delivery. |
| **Trace budget versus retry capacity** | Separate bounded observer and attribution queues. Experimental trace budgets may increase diagnostic buffering without changing retry admission capacity;refused histories remain incomplete. |
| **Subscription readiness / readiness barrier** | Queries and consumers are ready before producers send. A startup label or fixed sleep is not this guarantee;revision11traces localize a startup-overlapping TCPdeficit before serializer acceptance. |
| **Query deployment / listener attachment / callback initialization** | The stream query exists / its result handler is attached / that handler's required state is initialized. These are separate startup boundaries; TCP's base constructor attaches before its watchdog/NIC initialization. New bounded receipts distinguish them; candidate Linux readiness waits for successful queries and completed constructors, not an enlarged sleep. |
| **Projection / diagnostic projection ID** | An aggregate emitted by EPL / a weak per-object diagnostic key linking that exact aggregate to its saved row. An aggregate can represent multiple inputs; matching owner/endpoint keys alone cannot identify a particular missing input. Projection IDs are not exported telemetry identities. |
| **Accepted but undrained row** | A row with serializer acceptance evidence but no matching drain receipt. Revision13 AXON has two exact TCP row IDs/six counts in this state; finalized-to-raw equality does not excuse them or prove a shutdown fix. |
| **Terminal window barrier / callback quiescence** | Execute pending bundled 10-second Esper windows after producers stop, then close listener admission and join in-flight callbacks before queue draining. The experimental Linux control freezes/advances runtime scheduling—not OS/event time—and is neither an arbitrary longer sleep nor proof of native/durable cutoffs. |
| **Drain / producer cutoff** | Complete accepted pending work / boundary after which a producer no longer captures activity. A fixed sleep is not proof of a completed drain. |
| **SIGTERM / graceful shutdown** | Request to terminate / orderly completion of shutdown without forced termination. A graceful process exit alone does not prove data completeness. |
| **Sensor-service shutdown** | Stopping the collector service and its producer/queue/output components. In the CALDERA tests this means stopping `lintap.service` on `caldera-host`, not powering off that host or stopping the CALDERA application. |
| **Collector self-telemetry** | Ordinary process telemetry identifying the collector itself, so normal datasets can support retrospective validation. Candidate Linux implementation includes its startup Refresh, not its own file writes. Collector lifetime is not necessarily the exact collection interval. See [[wiki/concept/collector-process-telemetry-and-collection-boundaries]]. |
| **Grouped retries (proposed)** | Share a lookup/scheduling operation among events waiting for the same process lifetime, while retaining every event's time, payload and final outcome. |

Current retry implementation holds individual messages, normally schedules one-second
delays, and allows ten retries with default shared capacity 1,024. These are nominal
attempt/delay settings, not a guaranteed ten-second wall-clock completion budget.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs §MaxAttempts; §DefaultCapacity; §TrySchedule; §Pump; §Shutdown -->
See [[wiki/work/host-process-identity-patch/grouped-retry-design-notes]] for the proposal.
Trace limits/proof:[[wiki/work/host-process-identity-patch/timestamp_and_trace_results]].
Live controls/limits:[[wiki/work/host-process-identity-patch/delivery_diagnostic_results]].
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/AttributionTrace.cs; ../wintap/tests/Wintap.Tests/AttributionTraceTests.cs -->

## Networking

| Term | Definition |
|---|---|
| **Five-tuple / `conn_id`** | Two IP/port endpoints plus transport protocol / key for canonical tuple equivalence. It does not identify a unique socket lifetime or process owner. |
| **Endpoint orientation** | Correctly identifying source/destination and host-relative local/remote endpoints for an observation. A correct connection hash does not prove orientation. |
| **Socket role / bidirectional traffic** | Client/server or socket-end perspective / traffic observed in both directions. One process can own both ends. |
| **TCP / UDP** | Connection-oriented transport / datagram transport; recorded activity and byte meanings must be interpreted using the specific sensor's semantics. |
| **Loopback / non-loopback** | Traffic through the host's loopback interface / traffic using another interface address. Same-host traffic can be non-loopback. |

Source: [[wiki/concept/telemetry-identity-and-endpoint-orientation]].

## Stream processing and downstream analysis

| Term | Definition |
|---|---|
| **Esper / NEsper / EPL** | Event-stream processor / its .NET implementation / SQL-like event processing language. Stream windows are not persistent database tables. |
| **Window / aggregation** | Group of observations selected by a time/count rule / combining observations into summaries. One saved row may represent many events. |
| **Serializer / Parquet** | Component converting stream results into stored rows / column-oriented file format used for captures. |
| **`raw_sensor`** | Collector's durable dataset input for downstream analysis. Despite “raw,” rows can already be normalized, enriched and aggregated; not necessarily raw kernel records. |
| **ETL / DBT / DuckDB** | Extract-transform-load processing / SQL transformation-and-test tooling / embedded analytical database used for runtime history and offline analysis in separate contexts. |
| **Bronze / silver / gold** | Wintappy layers for source/schema compatibility / normalized detail / analyst-facing summaries. These are modeling layers, not quality verdicts. |
| **Join / fanout** | Relating rows using matching keys / accidental multiplication when a key matches multiple rows. Valid joins do not prove no upstream events were lost. |
| **Annotation / label / shadow classification** | Analysis added to observations / category assigned for analysis / experimental classification recorded without suppression or a definitive benign verdict. |

Sources: [[wiki/pipeline/nesper-esper-event-stream-processing]],
[[wiki/repo/wintappy-pipeline-repo]],
[[wiki/work/improve-lintap-data-quality/diagram-glossary]],
[[wiki/work/host-process-identity-patch/investigation_mitigation_plan]].

## Builds, installation and verification

| Term | Definition |
|---|---|
| **Candidate / baseline / same-binary control** | Proposed version under test / reference version or configuration / comparison that changes a declared setting while keeping the executable identical. A candidate pass is not a production release. |
| **Self-contained / framework-dependent** | Package includes its .NET runtime / package relies on a compatible installed .NET runtime. Other native-library dependencies can remain in either case. |
| **Runtime root / capture data root** | Directory for collector state, resolver databases and logs / directory for recorded datasets. They can differ; moving output does not necessarily move identity state. |
| **Native filesystem / shared mount** | VM-local storage / filesystem shared from the Mac. Build/runtime behavior can differ; native build outputs avoid known shared-mount issues. |
| **Installed-service test / isolated executable test** | Exercises the package through its service manager / launches a separate test executable. Success in one does not automatically establish success in the other. |
| **Test fixture / snapshot** | Controlled setup for a test / preserved state at a stated point. A final snapshot shows final state, not the complete sequence that produced it. |
| **Effective configuration** | Settings the actual running process received, not merely what an edited config file or launcher intended. |
| **SHA256 / artifact checksum** | Cryptographic content fingerprint / recorded fingerprint used to confirm compared packages, binaries or archives contain the same bytes. It does not prove correctness by itself. |

Sources: `../wintap/BUILD_AND_TEST.md`,
`../Lintap/packaging/lintap-deb/build-deb.sh`,
[[wiki/work/host-process-identity-patch/verification]].
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/build-deb.sh §SELF_CONTAINED; §PUBLISH_DIR; ../wintap/BUILD_AND_TEST.md §Working Directory; wiki/work/host-process-identity-patch/verification.md §Collector-process visibility -->

## Expansion queue

Next source-grounded additions: CO-RE/BTF, kernel hook families, UID/SID and parent
lineage, namespaces/containers, byte-counter semantics,
collection capability receipts, research labels and feature-work terminology.
Keep the existing diagram-specific glossary rather than duplicating its A/Q/S labels.
