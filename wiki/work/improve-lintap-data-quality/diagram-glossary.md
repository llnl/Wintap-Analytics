---
title: "Diagram Glossary: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - ../wintap/wintap/core/etl/esper/tcp.epl
  - ../wintap/wintap/core/etl/esper/udp.epl
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - ../wintap/wintap/core/etl/extract/SerializerFlushWorker.cs
  - ../wintap/wintap/core/etl/load/ParquetWriter.cs
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/infrastructure/WintapSvcCore.cs
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: stable
source_paths: wiki/work/improve-lintap-data-quality/ebpf-quality-flow.drawio; ../wintap/wintap/platform/linux/sensor; ../wintap/wintap/core/etl
tags: [feature-work, lintap, ebpf, file-events, attribution, esper, parquet, glossary]
---

# Diagram Glossary: Improve Lintap Data Quality

Use this page with the two-page
[`ebpf-quality-flow.drawio`](ebpf-quality-flow.drawio) diagram. The diagram's
stable labels are `[A1–A13]`, `[Q1–Q5]`, and `[S1–S18]`. The quality labels are
`Q`, not `QA`; for example, the transit gate is `[Q1]`.

- `A` identifies an architecture component or boundary.
- `Q` identifies a quality or performance gate.
- `S` identifies one ordered action in normal delivery or shutdown.

The diagram is a flow explanation, not a guarantee that every event family
uses identical tracer hooks or EPL. FileOps is the most detailed path because
it drove the loss remediation; process and network streams share the lifecycle,
attribution, serialization, and durable-output contracts where noted.

## Architecture labels

### `[A1]` Host activity

The operating-system activity that creates telemetry: process lifecycle events,
file syscalls, and TCP/UDP operations. This is the measured workload or ambient
host behavior, not a Lintap queue. Acceptance workloads should record their
expected paths, operations, and connections independently so downstream counts
can be compared with the source stimulus at `[Q5]`.

**Further detail:** [[wiki/work/improve-lintap-data-quality/verification]]
describes the controlled source and packaged workloads.

### `[A2]` eBPF hooks

Kernel tracepoints and kprobes capture event-time fields such as PID, command
name, operation, and `bpf_ktime_get_ns()` monotonic timestamp. FileOps has a
CO-RE tier and a tracepoint fallback; package builds always validate fallback
objects and validate CO-RE objects when a native host BTF is available. Sensor
configuration determines which process, file, and network producers start.

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §Start -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §emit_file_fd_event; §emit_file_event_saved -->

**Further detail:** [[wiki/component/fileops-event-pipeline]] and the canonical
package guide at `../Lintap/packaging/README.md`.

### `[A3]` BPF ring buffer

The kernel reserves a fixed event record, populates it, and submits it to the
libbpf ring buffer. A failed reserve increments an operation-specific
`ring_fail_total` counter. FileOps submits with flags `0`, allowing the kernel's
adaptive notification policy; the former no-wakeup behavior delayed low-rate
records and released sustained traffic in large bursts.

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §submit_file_event; §emit_file_fd_event -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c §submit_file_event -->

**Operational check:** inspect `FileOps counters` for per-operation
`emitted_total` and `ring_fail_total`. See `[Q1]`.

### `[A4]` libbpf poll and callback

Each eBPF sensor owns a polling thread that calls `ring_buffer__poll` with a
100 ms timeout and invokes the sensor callback for each record. FileOps compares
the event's kernel monotonic time with callback time and records delivery
latency buckets. On shutdown, the polling thread must exit before native ring
buffer memory is freed.

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §PollRingBuffer; §Stop -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent; §RecordDeliveryLatency -->

### `[A5]` Sensor handling

Userspace decodes the native record and applies event-family logic. FileOps
resolves relative and FD-based paths, filters pseudo-filesystem and sensor
self-feedback paths, maps operations, stamps live process identity when
possible, folds repeats through emit-first aggregation, and enqueues output to a
bounded sender queue. Queue depth, high-water mark, and drop-newest counts are
reported in the periodic FileOps counter line.

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent; §MaybeLogCounters -->

**Further detail:** [[wiki/component/fileops-event-pipeline]].

### `[A6]` EventChannel attribution

`EventChannel` enriches non-process events with the owning process. The Linux
fast path accepts identity stamped synchronously from the active-process cache
or live `/proc` while a short-lived producer still exists. If identity is not
yet available, file/TCP/UDP events use a bounded ten-attempt, one-second retry
window before an `Unknown` fallback is emitted. The original event time is
preserved across retries.

<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §SendCore; §TryPopulateCurrentProcessIdentity -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventOwnerSelection.cs §ResolveOwner -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs §MaxAttempts; §TrySchedule -->

**Further detail:** [[wiki/component/process-table-retention]] and `[Q2]`.

### `[A7]` Esper / NEsper

The enriched `WintapMessage` enters the Esper runtime. EPL selects the event
family, applies windows or contexts, aggregates fields, and invokes a serializer
listener. The normal configuration evaluates ingress synchronously on the
sender thread; Esper windows describe stream processing and are not persistent
storage.

This includes network aggregation. `tcp.epl` and `udp.epl` summarize activity
in terminating 10-second contexts, grouping by source/destination address and
port, process identity, activity type, and agent. Both produce packet-byte
sums, event counts, and first/last receive times; TCP additionally computes
minimum/maximum packet size, squared-size sum, and initial sequence number.
Consequently, serialized TCP/UDP rows represent ten-second grouped activity,
not one row per kernel network event.

FileOps is likewise aggregated: `file.epl` uses a 10-second `time_batch`, groups
by path and process identity fields, and sums event and byte counts.

<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §SendCore -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/tcp.epl §tcp-activity -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/udp.epl §udp-activity -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/file.epl §query -->

**Further detail:** [[wiki/pipeline/nesper-esper-event-stream-processing]].

### `[A8]` FileSerializer queue

The serializer listener converts EPL output to normalized rows and calls
`Serializer.Save`. Accepted rows enter an in-memory concurrent queue with a
configured capacity. Counters distinguish accepted rows, dropped rows, current
depth, and peak depth; reaching capacity applies the configured drop policy.
A clean DBT relationship cannot recover or detect every event dropped here.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Save; §initSensor -->

**Operational check:** use `serializer_flush` and `serializer_shutdown` log
records; see `[Q3]`.

### `[A9]` Dedicated drain worker

FileSerializer and RegistrySerializer use a process-lifetime dedicated thread
instead of competing for a shared ThreadPool slot. A high-water signal wakes
the worker early; the serialization interval is the fallback wake-up. A guard
prevents overlapping drains, and the worker continues while the queue remains
above the threshold.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/SerializerSchedule.cs §ResolveOptions -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/SerializerFlushWorker.cs §Run -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §FlushToDisk -->

### `[A10]` ParquetWriter

Serializer drains become asynchronous Parquet batches. The writer processes
batches on one background worker, records write failures and dropped batches,
and exposes a completion wait. Shutdown is successful only when all pending
batches complete and both failure counters remain zero.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/ParquetWriter.cs §BatchWorker_DoWork; §WaitForCompletion; §Add -->

### `[A11]` Runtime staging

ParquetWriter first writes `*.parquet.active` in the runtime
`esper_staging/<serializer>/` tree and renames successful files to
`*.parquet`. The `.active` suffix prevents merge/upload consumers from treating
an incomplete file as finalized. Leftover active or finalized staging files
after a clean final merge are a shutdown-quality failure.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/ParquetWriter.cs §Write; §BatchWorker_DoWork -->

**Further detail:** `../Lintap/packaging/PATHS_AND_CONFIGURATION.md`.

### `[A12]` CacheManager merge

CacheManager periodically merges finalized serializer files and, during
shutdown, first stops and joins its worker and then runs one final cross-stream
merge. `RawSensorWriter` materializes through a destination `.active` file and
renames it only after DuckDB completes. A failed merge retains source Parquet
for a later retry rather than deleting it.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §Stop -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/RawSensorWriter.cs §WriteParquetWithDuckDB -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/Merge.cs §Start -->

### `[A13]` `raw_sensor` Parquet

The durable output is partitioned under
`WINTAP_DATA_ROOT/raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/`. File rows map to
`raw_process_file`; TCP and UDP increments share `raw_process_conn_incr` with a
protocol partition. Wintappy DBT builds process/file/network relations and
quality summaries from these finalized files.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/RawSensorWriter.cs §MapEventType; §WriteParquetWithDuckDB -->

**Further detail:** [[wiki/repo/wintappy-pipeline-repo]] and
[[wiki/work/improve-lintap-data-quality/verification]].

## Quality-gate labels

### `[Q1]` Transit

Measures whether the kernel-to-userspace boundary is timely and loss-free.
Use FileOps delivery-latency samples, weighted average/max/tail buckets, and BPF
ring-reservation failures together. A low ring-failure count alone does not
prove timely delivery; the matched A/B found zero ring failures in both arms
while latency differed materially.

**Acceptance evidence:** `[A3–A4]`, `[S2–S3]`, and the matched two-hour A/B in
[[wiki/work/improve-lintap-data-quality/verification]].

### `[Q2]` Attribution

Measures whether file and network children join to a lifecycle process with a
stable PID hash and usable process name. Count orphan rows/hashes and
`Unknown`-name rows/hashes separately. Claims must remain capture- and
workload-scoped; observed Start-user success does not imply Stop-only user
enrichment.

**Acceptance evidence:** `[A6]`, `[S6]`, Wintappy's
`attribution_quality_summary`, and the isolated DBT runs in
[[wiki/work/improve-lintap-data-quality/verification]].

### `[Q3]` Serializer pressure

Measures the queue where the observed FileOps loss occurred. Review current and
peak depth, accepted total, dropped total, flush trigger and duration, skipped
overlap count, and downstream writer backlog. The passing contract is zero new
serializer and writer drops while retaining every expected workload path.

**Acceptance evidence:** `[A8–A10]`, `[S9–S10]`, and the remediated burst,
two-hour, and packaged gates in
[[wiki/work/improve-lintap-data-quality/verification]].

### `[Q4]` Durable shutdown

Checks that stop does not turn accepted in-memory work into silent data loss.
Required evidence is producer/poller joins, complete sender drain, serializer
`remaining=0`, Parquet backlog/failures/drops all zero, successful final merge,
and no leftover staging or `.active` files. Logger closure occurs only after
these outcomes are reported.

**Acceptance evidence:** `[A4–A12]`, `[S13–S18]`, and the graceful-shutdown
records in [[wiki/work/improve-lintap-data-quality/verification]].

### `[Q5]` End-to-end QA

Compares an independently recorded workload with durable output and downstream
relations. Check distinct expected paths, operation counts or minimums, TCP/UDP
coverage, DBT test results, process joins, and Unknown identities. Passing DBT
relationships alone are insufficient when upstream loss removed rows before
DBT could see them.

**Acceptance evidence:** `[A13]` and the source/package result tables in
[[wiki/work/improve-lintap-data-quality/verification]].

## Sequence labels

### Normal delivery: `[S1–S12]`

#### `[S1]` Syscall or lifecycle event

Host activity reaches an enabled process, file, or network hook. This is the
sequence form of `[A1] → [A2]`.

#### `[S2]` Reserve, populate, and adaptive submit

The tracer reserves a ring record, writes event-time fields, and submits with
the adaptive notification policy. Reserve failures increment kernel counters;
see `[A3]` and `[Q1]`.

#### `[S3]` Poll callback and latency sample

The sensor's libbpf poller receives the record. FileOps samples elapsed transit
time from the kernel monotonic timestamp before doing path or attribution work;
see `[A4]`.

#### `[S4]` Decode, resolve, aggregate, and enqueue

The FileOps callback decodes fields, resolves the path, applies filters and
emit-first aggregation, then puts surviving events on the bounded sender queue;
see `[A5]`.

#### `[S5]` Sender worker calls `Send(message)`

The sensor's dedicated sender dequeues messages and invokes EventChannel. This
keeps expensive process resolution and synchronous Esper work out of the native
ring callback while preserving bounded queue accounting.

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §TryEnqueueMessage; §SenderLoop -->

#### `[S6]` Active cache, live `/proc`, then bounded retry

EventChannel uses the identity stamped by the callback or resolves against the
active cache and durable process history. A miss for configured streams is
retried for at most ten one-second attempts; see `[A6]` and `[Q2]`.

#### `[S7]` Enriched event enters EPL

After attribution and health inspection, EventChannel synchronously sends the
`WintapMessage` bean to Esper unless Esper output is explicitly disabled; see
`[A7]`.

#### `[S8]` EPL aggregates/routes to serializer callback

The event matches its EPL statement. Window/context expiry emits a normalized
aggregate to the registered serializer listener. FileOps uses a 10-second
batch; TCP and UDP use terminating 10-second contexts that aggregate each
network tuple/process/activity group before serialization.

#### `[S9]` Save normalized row to bounded queue

The listener calls `Serializer.Save`; accepted rows increment depth and total
counters, while a capacity breach follows the configured drop policy. This is
the start of `[Q3]`.

#### `[S10]` Dedicated high-water or timer drain

The FileSerializer drain thread wakes at high water or on its fallback interval,
dequeues one non-overlapping batch, normalizes it, and passes it to
ParquetWriter; see `[A9–A10]`.

#### `[S11]` Write active file and finalize

ParquetWriter writes `*.parquet.active`, then renames a successful write to
`*.parquet`. Completion/failure/drop accounting remains associated with the
queued batch; see `[A10–A11]`.

#### `[S12]` Periodic merge to partitioned `raw_sensor`

CacheManager merges finalized staging files into durable, partitioned output.
Only after a successful destination write does merge cleanup remove the source
files; see `[A12–A13]`.

### Coordinated shutdown: `[S13–S18]`

#### `[S13]` Flush pending attribution retries

Shutdown stops the attribution retry timer and makes one final best-effort send
for each pending event without requeueing it. This happens while downstream
components and logging remain available.

<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StopAsync -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs §Shutdown -->

#### `[S14]` Stop producers and join pollers before native free

The subscription manager stops sensors. Every eBPF polling thread exits fully
before its ring buffer, links, or object are freed, preventing the observed
callback/use-after-free segmentation fault.

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §Stop; §WaitForThreadExit -->

#### `[S15]` Complete and drain the sensor sender queue

FileOps stops accepting new callback work, flushes aggregation state, marks the
bounded sender queue complete, and joins the sender. No producer-owned message
may remain when serializer shutdown starts.

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §OnStopping -->

#### `[S16]` Stop schedules and drain serializer queues

ETL disables serializers, disposes periodic/dedicated scheduling workers, and
repeatedly flushes every accepted row until each serializer queue reaches zero
or its shutdown timeout expires.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/WintapETL.cs §Shutdown -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Shutdown -->

#### `[S17]` Wait for Parquet completion

Each serializer waits until pending Parquet batches reach zero. A nonzero write
failure or dropped-batch count makes the serializer shutdown result fail even
if the queue is empty.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/ParquetWriter.cs §WaitForCompletion -->

#### `[S18]` Stop cache worker and perform final merge

After all serializers and writers finish, CacheManager stops its periodic
worker and performs a final cross-stream merge. The service then reports ETL
and shutdown status and closes logging last.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §Stop -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StopAsync -->

## Common citation ranges

| Topic | Diagram citation |
| --- | --- |
| Adaptive ring notification and latency | `[A3–A4]`, `[Q1]`, `[S2–S3]` |
| Live and delayed process attribution | `[A6]`, `[Q2]`, `[S6]` |
| Dedicated FileSerializer draining | `[A8–A10]`, `[Q3]`, `[S9–S10]` |
| Native poll-thread shutdown safety | `[A4–A5]`, `[S14–S15]` |
| Serializer, Parquet, and final-merge shutdown | `[A8–A12]`, `[Q4]`, `[S16–S18]` |
| Durable output and DBT completeness | `[A13]`, `[Q5]`, `[S12]` |

## Related documentation

- [[wiki/component/fileops-event-pipeline]] — detailed FileOps implementation,
  counters, aggregation, and known caveats.
- [[wiki/pipeline/nesper-esper-event-stream-processing]] — EPL and serializer
  behavior, including the shutdown durability contract.
- [[wiki/component/process-table-retention]] — active and historical process
  identity caches.
- [[wiki/repo/wintappy-pipeline-repo]] — downstream DBT/DuckDB ownership.
- [[wiki/work/improve-lintap-data-quality/verification]] — measured evidence
  associated with the `Q` gates.
