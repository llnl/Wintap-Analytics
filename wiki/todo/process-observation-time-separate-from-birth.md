---
title: "To-Do: Preserve Process Observation Time Separately from Canonical Birth"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs
  - ../wintap/wintap/core/etl/extract/ProcessSerializer.cs
  - ../wintap/wintap/core/etl/model/ProcessObjectModel.cs
  - ../wintap/wintap/core/etl/load/ParquetWriter.cs
  - ../wintap/wintap/core/etl/load/DirectParquetSink.cs
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../wintap/tests/Lintap.Tests/ProcessObservationTimingTests.cs
  - ../wintap/developer_docs/audits/sfx-02-process-observation-refresh.md
policy: agent-editable
last_validated: 2026-11-22
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/shared/WintapAPI; ../wintap/wintap/platform/linux/sensor; ../wintap/wintap/core/etl; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
tags: [todo, priority, process-events, timestamps, precision, identity, exec, refresh]
---

# To-Do: Preserve Process Observation Time Separately from Canonical Birth

**Priority:** P1 — High (human-requested research/data-fidelity requirement).
**State:** Promoted — the bounded additive slice is implemented in an uncommitted
source candidate. Linux `live-01` validated 8/8 multi-exec timing cases and exposed
a direct-Parquet null defect; the repair passes 8/8 focused observation tests and
65/65 expanded Linux/synthetic tests. Repaired-binary Linux `live-02` passes all
18/18 aggregate acceptance checks. Full migration and native Windows acceptance
remain open.

## Requirement

Keep the coarse, canonical process birth used for `PID_HASH` unchanged. Preserve
the finest available event-occurrence timestamp independently, particularly for
closely spaced exec attempts and successful image changes during shell/script
execution. A later Refresh must also retain its actual observation time without
creating a new process identity. Receipt and serialization time are different facts.
<!-- HUMAN-REQUESTED: conversation 2026-11-22 — assess inclusion in the first name-repair/periodic-Refresh batch; otherwise retain explicitly in the backlog. -->

This makes the timing follow-up in
[[wiki/todo/linux-process-executable-attribution]] independently discoverable;
it does not select that item's eventual process/image model.

## Source findings

- Both Linux exec objects and both clone objects already capture
  `timestamp_ns = bpf_ktime_get_ns()` and expose it to managed callbacks. No new
  kernel hook is needed to retain these existing occurrence observations. The
  candidate copies both values into additive observation metadata while still
  using canonical birth for `EventTime`.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §HandleEvent -->
- `WintapMessage.ProcessObject` now has separate nullable UTC FILETIME and raw
  monotonic nanoseconds plus clock-domain and capture-run fields. Normal process
  ETL propagates them and envelope `ReceiveTime`; birth remains persisted as
  `StartTime`/`EventTime`.
  <!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent; ../wintap/wintap/core/etl/model/ProcessObjectModel.cs §ProcessStartData -->
- `RegisterProcess` derives creation time from envelope `EventTime`, and the
  channel uses it for parent lifetime lookup. PyUtil's silver process model
  derives `process_started` from minimum Start/Refresh `eventtime`, not `StartTime`.
  Changing the producer assignment alone is therefore unsafe.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §RegisterProcess; ../wintap/wintap/core/infrastructure/EventChannel.cs §Send; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §process_base -->
- The additive conversion divides nanoseconds by 100 for FILETIME while retaining
  the exact raw integer separately. Failed conversion leaves UTC absent rather
  than substituting callback time.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs §TryToUtcFileTimeUtc/ApplyKernelProcessObservation -->

## Implemented first-batch candidate

**The bounded additive preservation slice is implemented; a full `EventTime`
semantic migration remains a separate coordinated unit.** The candidate:

1. Leaves canonical birth selection, `PID_HASH`, resolver registration, and legacy
   Start/Refresh `EventTime`/`StartTime` semantics unchanged. This is transitional
   compatibility, not the final separation of the envelope's semantics.
2. Adds explicitly named process observation metadata through WintapAPI and normal
   process ETL: UTC occurrence/observation FILETIME, exact integer kernel
   nanoseconds where available, explicit clock domain, and capture-run scope. It
   reuses the existing receipt's capture-run UUID rather than inventing a process
   identity or host identifier.
3. Populates exec/clone timing from the existing kernel value, not `/proc` birth
   or callback time. Preserve raw nanoseconds even if UTC conversion is unavailable;
   report unavailable UTC distinctly. Conversion must not quantize to `CLK_TCK`.
4. Gives Refresh the userspace UTC scan-start timestamp and propagates the existing
   `ReceiveTime`; it never claims a `/proc` inventory has kernel exec timing.
5. Preserves source provenance and raw row multiplicity. Unsupported/legacy timing
   stays absent/null, not fabricated. Windows live ETW acquisition stays unchanged;
   native additive schema/runtime compatibility still needs its own runner.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs; ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs -->

This is more than one producer assignment: Wintap owns the API, producers,
conversion helper, capture-run access and ETL projection. The Parquet writer now
explicitly types both optional numeric fields as nullable `long` regardless of
first-row population. Focused tests cover null-first/populated-first normal ETL
and direct scalar projection. Finalized merging/compaction and downstream consumer
behavior remain unqualified.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/ParquetWriter.cs §DetermineSchemaFromExpando; ../wintap/wintap/core/etl/load/DirectParquetSink.cs §DirectParquetProjection -->

Keeping legacy `eventtime` unchanged avoids changing PyUtil's birth-time input in
this slice, but does not fix arbitrary executable selection or automatically
expose nanosecond ordering in silver models. Schema-reader compatibility remains
a qualification gate, not an assumed consequence of adding columns.

## Qualification and later migration

Focused synthetic qualification now covers sub-FILETIME raw ordering, conversion
failure, repeated Refresh identity/timing, normal/direct projection and stable
nullable schema. A Windows-targeted cross-build and one Linux-hosted Windows
periodic test pass; neither is native Windows acceptance.

Bounded Linux `live-01` showed all eight multi-exec cases retaining one birth/hash
and run scope, complete UTC/raw-monotonic timing, and strict clone → first exec →
second exec ordering. It also showed one absent Refresh monotonic value serialized
as numeric `0` in a kernel-led direct batch. The repaired projection retains null
timing keys and the schema recognizes prefixed direct fields in either first-row
order. Repaired-binary `live-02` confirms null monotonic timing for all 1,312
Refresh rows, complete nonzero kernel timing for all 4,988 Start rows, and optional
timing fields in all 124 Parquet files.

- Synthetic closely spaced observations share identical birth/hash while retaining
  distinct raw occurrence times, including differences below one FILETIME tick.
- Out-of-order callback delivery does not rewrite the retained kernel timestamp;
  conversion failures, equal timestamps, missing data and restart scope stay explicit.
- Producer-to-serializer-to-Parquet propagation, null-first/populated-first
  batches, Refresh without kernel time and direct projection pass synthetically;
  native Windows/legacy-reader and finalized merge/compaction gates remain.
- Multi-exec live ordering is established in both captures, and `live-02` closes
  bounded Linux acceptance by proving absent Refresh monotonic timing remains null
  after the direct-Parquet repair.
- Raw monotonic nanoseconds are comparable only within their documented capture-run
  and clock domain. Nanosecond units do not guarantee nanosecond accuracy or a total causal
  order; equal timestamps remain ties. Do not order using rounded downstream times.
- Later full migration must explicitly separate canonical birth in WintapAPI,
  hash inputs, resolver registration/parent lookup and normal ETL, and update the
  PyUtil process-birth consumer with backward-compatible handling. No historical
  repair, argv/lifecycle rewrite, or sibling PyUtil code change is authorized here.

Related: [[wiki/todo/periodic-process-refresh-listing]],
[[wiki/concept/filetime-derived-timestamp-precision]],
[[wiki/tension/linux-process-lifecycle-vs-exec-attempt-observations]], and
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief]].
