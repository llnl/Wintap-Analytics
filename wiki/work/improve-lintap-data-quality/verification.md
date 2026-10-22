---
title: "Verification: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - ../Lintap/multipass-lintap.sh
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs
  - ../Wintappy/wintap_dbt/qa/pid_hash_orphan_checks.sql
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: stable
source_paths: wiki/work/improve-lintap-data-quality/verification.md
tags: [feature-work, verification, lintap, file-events, attribution]
---

# Verification: Improve Lintap Data Quality

## Diagram references

The two-page diagrams.net source at
[`ebpf-quality-flow.drawio`](ebpf-quality-flow.drawio) provides stable anchors
for connecting evidence to the implementation flow:

- architecture page `[A1–A13]`: event source through `raw_sensor` parquet;
- architecture quality gates `[Q1–Q5]`: transit, attribution, serializer
  pressure, durable shutdown, and end-to-end QA;
- sequence page `[S1–S12]`: normal event delivery;
- sequence page `[S13–S18]`: coordinated shutdown and final merge.

For example, dedicated FileSerializer draining is `[A8–A9]` / `[S9–S10]`,
while coordinated serializer, parquet, and cache shutdown is `[A8–A12]` /
`[S16–S18]`.

| Validation evidence | Diagram anchors | What is measured |
| --- | --- | --- |
| Matched ring-notification A/B | `[A3–A4]`, `[Q1]`, `[S2–S3]` | delivery-latency buckets and BPF ring failures |
| File burst and serializer drain | `[A5]`, `[A8–A10]`, `[Q3]`, `[S4–S10]` | sender drops, queue peak/drops, accepted rows, writer backlog |
| Process attribution QA | `[A6]`, `[Q2]`, `[S6]` | unresolved owners and orphan/`Unknown` PID hashes |
| Graceful-shutdown smoke | `[A4–A12]`, `[Q4]`, `[S13–S18]` | worker completion, write/merge status, staging/`.active` leftovers |
| DBT and workload completeness | `[A13]`, `[Q5]` | expected paths/operations and file/network relationships |

## ldq-00 — fresh source-build host

- Replaced the prior disposable `lintap-dev` instance with arm64 Ubuntu 24.04
  Multipass instance `lintap-quality`.
- The shared checkout is mounted at `/home/ubuntu/git`; the feature-isolated
  macOS directory `../Wintappy/data/improve-lintap-data-quality` is mounted at
  `/home/ubuntu/data/quality`. Sensor output is directly queryable by the Mac
  DBT/DuckDB workflow.
- Verified BTF, Clang, bpftool, .NET 8, DuckDB, and uv, then built the mounted
  feature source as Lintap.

## ldq-01 — source-build baseline

Two 6,000-unique-file runs used the hardened no-new-FileSerializer-drop gate.

| Run | Result | Distinct paths | FileSerializer drops | Key observation |
| --- | --- | ---: | ---: | --- |
| Initial clean run | fail | 5,693 / 6,000 (94.9%) | 0 | All five file operations stopped at index 5,693. Kernel ring failures and FileOps sender-queue drops were zero. |
| Rebuild/restart, 45 s warm-up | pass | 6,000 / 6,000 (100%) | 0 | 30,000 rows with open/read/write/close/delete; serializer peak depth 5,282 of 10,000. |

The failed run's FileSerializer accepted 34,540 events with `dropped_total=0`.
Its FileOps sender queue reached 29,486 of 524,288 with no drops and its BPF
ring-failure count was zero. Neither run supports increasing a serializer or
sender queue. The fixed tail loss in the first run requires a controlled
warm-up/attach-state experiment before assigning a kernel-tracer cause.

The live process RSS after the successful run was about 525 MiB. Source output
passed `WINTAP_DATA_ROOT=data/improve-lintap-data-quality/data
WINTAP_DBT_START_DAY=20261021 WINTAP_DBT_END_DAY=20261021 make dbt-build` with
**79 PASS, 0 WARN, 0 ERROR**.

Focused xUnit execution could not run because existing NuGet caches lack
restored packages (`AWSSDK.S3` on macOS; `xunit.analyzers` on the VM). This is
an environment prerequisite failure, not a test failure.

## ldq-03 — hostname and attribution baseline

- Before the hostname change, `process` and network relations recorded
  `LINTAP-QUALITY`, while `process_file` recorded `lintap-quality`. The cause
  was the FileSerializer-only `Environment.MachineName.ToLower()` assignment.
- File serialization now uses `HostSerializer.Instance.HostId.Hostname`, as
  process and network serializers do. The fresh capture confirms
  `LINTAP-QUALITY` across all three families.
- Post-capture DBT baseline: `process_file` has 33,398 rows, 162 orphan rows
  across 151 hashes, and 162 `unknown` process names; summary rows have 151
  orphan hashes. Network relation orphan counts are zero. `process` has 40
  empty/unknown user names. This is a baseline, not an acceptance threshold.

### Lifecycle diagnosis — Clone disabled

- The active source-build log records `CloneSensor disabled by config
  (Clone=false)`, although the Execve, Exit, FileOps, and ProcessRundown
  sensors started.
- Every PID contributing a file orphan that was examined has either only a
  process `Stop` row or no process row; PID 14176 is representative. It
  generated 150 `Unknown` file hashes during cron/PAM setup and has a later
  `cron` Stop record, but no Start/Refresh record for that process instance.
  The log emits `Could not resolve owner process for PID 14176 (File)` at the
  same time.
- This is expected coverage behavior when Clone is disabled: a forked child
  can perform file activity before it execs, so Execve cannot establish an
  owner for that interval. Clone's Start event uses the child PID and its
  `/proc` start time, the identity basis used by the Linux lifecycle path.

**Next controlled remediation:** enable `Clone` in the source-build runtime
configuration, restart into a clean output root, and repeat the cron/workload
capture. Compare `process_file` orphan rows/hashes and the `Unknown` name
composition with this baseline. Do not claim the 40 empty/unknown process-user
values are fixed by this lifecycle coverage change.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/runtime/Logs/Lintap.log §2026-10-21 09:54:26 and 09:55:13 -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §HandleEvent -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §TryConvertBootNsToFileTimeUtc -->
<!-- SYNTHESIS: orphan composition from ../Wintappy/data/improve-lintap-data-quality/data/raw_sensor and lifecycle logs -->

### Controlled Clone-enabled remediation

- The runtime override was changed from `WINTAP_ENABLE_CLONE_SENSOR=false` to
  `true`; the fresh log confirms that `CloneProcess` registered.
- A fork-before-exec file/network probe initially showed a network ownership
  race: the process hash matched the Clone-created process record while the
  network name was `Unknown`. Owner selection now checks the active process
  cache for network as well as file events.
- File and network attribution retries are enabled by default. A rapid
  200-child `/bin/cat /etc/hostname` workload proved that the prior three
  one-second retries were too short (90 Unknown file rows); a bounded ten
  one-second retry window, plus consistent clock-tick conversion for Clone,
  Execve, and `/proc` start times, produced **10,769 file rows with zero
  Unknown names/hashes**. The same run produced 32 network rows with zero
  Unknown names/hashes and no owner-resolution warnings.
- This validates the controlled lifecycle remediation for this workload. It
  does not establish that process-user fallback values are fixed, nor does it
  replace the pending full DBT orphan comparison against the baseline.

<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventOwnerSelection.cs §ResolveOwner -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs §MaxAttempts -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/runtime/esper_staging/fileserializer §2026-10-21 controlled rapid-child rerun -->

## ldq-04 — DBT attribution-quality contract

- Added Wintappy's `attribution_quality_summary` monitoring view. It reports
  child rows, distinct child hashes, orphan rows/hashes, `Unknown` process-name
  rows/hashes, and both rates for file increments, network increments, and
  aggregated network connections. `build_summary` now exposes the view.
- `make dbt-build` against the mounted data root passed **80/80**. The existing
  `qa-pid-hash` orphan check intentionally remains a failing diagnostic rather
  than a passing quality gate: the shared raw root contains the Clone-disabled
  baseline and intermediate captures as well as the clean retry-10 capture.
  Its aggregate results therefore cannot measure the final controlled capture
  alone.
- Aggregate mixed-capture diagnostics: `process_file` has 7,855/71,640 orphan
  rows (299 hashes, 10.96%) and 200 Unknown-name rows (189 hashes, 0.28%);
  `process_conn_incr` has 7/559 orphan rows (1.25%) and 8 Unknown-name rows;
  `process_net_conn` has 7/102 orphan rows (6.86%) and 8 Unknown-name rows.
  These are retained as baseline/intermediate evidence, not acceptance results.
- The controlled retry-10 staged capture remains the acceptance evidence for
  the rapid-child workload: 10,769 file and 32 network rows, zero Unknown
  identities. A capture-isolated raw root is still required for an end-to-end
  DBT orphan-rate acceptance gate.

<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/monitoring/attribution_quality_summary.sql -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/qa/pid_hash_orphan_checks.sql -->

### Capture-isolated acceptance rerun — not accepted

- A new runtime/data root at
  `../Wintappy/data/improve-lintap-data-quality/acceptance/` was started with
  Clone enabled and the same retry-10 build. It is isolated from the historic
  raw capture, but its merge into `data/raw_sensor` had not completed at
  observation time, so DBT must not yet be run against it.
- The same 200-child workload plus TCP probe produced 13,097 staged file rows,
  including 20 `Unknown` identities, and 64 staged network rows, including one
  `Unknown` identity. The log records the matching failed-owner warnings.
- Therefore the earlier zero-Unknown staged result is a successful pilot, not
  repeatable acceptance evidence. Preserve the DBT quality view, but keep
  ldq-03/ldq-05 open until this race is reproduced and the isolated raw output
  reaches a zero-Unknown or explicitly accepted threshold outcome.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance/runtime/Logs/Lintap.log §2026-10-21 15:02:21 -->

### Live producer-identity fallback — implementation and partial rerun

- The residuals were not transformed by DBT: the earliest loader-file `Open`
  events were queued before lifecycle registration, then retried only after the
  short-lived child had exited. The retry could no longer obtain the live
  `/proc` start time used to form the stable PID hash.
- `EventChannel.TryPopulateCurrentProcessIdentity` now supports file, TCP, and
  UDP callbacks. It first uses the active process cache, then—only for a
  non-Unknown producer name—asks the resolver for the live/stored stable PID
  hash while the producer remains alive. File/TCP/UDP messages with that
  complete producer identity bypass a second lookup. Network callbacks no
  longer generate a hash from callback time, which was not a process identity.
- `make build_dotnet` succeeded locally and on the arm64 source-build VM (both
  with existing warnings). Unit tests remain blocked by the pre-existing local
  NuGet `AWSSDK.S3` restore failure.
- The fresh `acceptance2` isolated rerun has 24 staged TCP rows with zero
  Unknown names and zero owner-resolution warnings. It does **not** validate
  file attribution: FileOps kernel `emitted_total` counters increased but its
  userspace `total`, queue, and first-emission counters remained zero, leaving
  no staged file rows. This is an upstream FileOps callback/data-path condition,
  not evidence of zero file Unknowns. DBT acceptance remains blocked pending a
  capture that emits file rows.

<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §TryPopulateCurrentProcessIdentity -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventOwnerSelection.cs §ResolveOwner -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §HandleEvent -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance2/runtime/Logs/Lintap.log §2026-10-21 15:14:18 -->

### acceptance3 — file attribution passes; final network skew identified

- A fresh arm64 source build using the live attribution fallback restored the
  FileOps userspace path and completed the same 200-child workload plus TCP
  probe. Staged output contained 10,000 file rows and 42 TCP rows with zero
  Unknown names, zero empty PID hashes, zero owner-resolution warnings, and
  zero FileOps queue drops.
- Clone/Exec lifecycle starts contained no same-timestamp multi-hash groups and
  no one-100-ns-tick split hashes. This validates nearest-clock-tick
  canonicalization against the defect observed in the mixed historical root.
- The isolated raw merge completed and DBT passed **80/80**. DBT relationship
  checks matched all 10,000 `process_file` rows. One of 27
  `process_conn_incr` rows remained orphaned: PID 22505 (`python3`) had a
  producer hash different from its lifecycle hash despite a valid process row.
- Root cause was a second timestamp conversion in
  `ProcessResolver.TryGetLinuxProcStartFileTimeUtc`: `TimeSpan.FromSeconds` used
  a `double`, allowing the live `/proc` fallback to land one 100-ns tick below
  the integer ProcReader/lifecycle value. It now converts Linux clock ticks to
  DateTime ticks using integer arithmetic. A regression test covers the exact
  conversion. This final network fix is built locally but requires the next
  isolated long-run validation.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance3/runtime/Logs/Lintap.log §2026-10-21 16:21:04 -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance3/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §ConvertLinuxProcStartTicksToUtc -->
<!-- GROUND_TRUTH: ../wintap/tests/Wintap.Tests/ProcessResolverLinuxTimestampTests.cs -->

### acceptance4 and acceptance5 — clean recorded DBT snapshots

Three independently started, approximately 30-minute source-build captures
(`acceptance4`, `acceptance5`, and `acceptance6`) exercised file activity,
fork/exec, TCP, UDP, and a secondary-user workload. The DBT databases retained
for the first two captures report no PID-hash relationship or `Unknown`
process-name failures:

| Capture | `process_file` | `process_conn_incr` | `process_net_conn` | Orphans / Unknown names |
| --- | ---: | ---: | ---: | --- |
| acceptance4 | 205,031 | 943 | 795 | 0 / 0 in every relation |
| acceptance5 | 212,182 | 946 | 774 | 0 / 0 in every relation |

The explicit file workloads also have zero PID-hash or `Unknown`-name failures:
7,000 rows across 2,800 paths for acceptance4, and 7,650 rows across 3,030
paths for acceptance5. The acceptance4 secondary-user command was malformed by
shell interpolation, so only acceptance5 and acceptance6 are process-user
evidence.

### acceptance6 — controlled workload passes; frozen available output fails QA

The first acceptance6 DBT snapshot was clean (216,113 file rows, 946 network
increments, and 771 network connections, each with zero relationship or
`Unknown`-name failures). It was taken before the source-build service was
stopped and its final output was rebuilt. It is therefore an interim snapshot,
not the final acceptance result.

After stopping the service and rebuilding DBT from the available isolated raw
output, the final database has the following results:

| Relation | Rows | Orphan rows / hashes | `Unknown`-name rows / hashes |
| --- | ---: | ---: | ---: |
| `process_file` | 241,662 | 21,571 / 349 | 10 / 10 |
| `process_conn_incr` | 1,003 | 12 / 3 | 0 / 0 |
| `process_net_conn` | 806 | 12 / 3 | 0 / 0 |

- The file orphans are concentrated between 18:22:24 and 18:22:44 local VM
  time, during system package-maintenance activity. They carry stable producer
  hashes and names but lack matching lifecycle rows in `process`; this is a
  process-lifecycle coverage gap, not a claim that DBT altered the identities.
  No Clone/Execve/Exit poll or callback-handler error is recorded. The capture
  does not identify the kernel/userspace cause, so it must not be attributed to
  a ring-buffer failure without further instrumentation.
- The explicit `/tmp/lintap-quality-acceptance6/` workload remains clean: 7,650
  rows across 3,030 paths, with zero orphans and zero `Unknown` names. Its Start
  rows include `cat` as `ubuntu` and secondary-user `python3` as `nobody`.
  This is bounded workload evidence for the UID fallback, not a general
  process-user acceptance claim.
- There are 755 Stop-only process rows (715 named `cat`). `ProcessStopSerializer`
  has no user-name field, so their empty user values remain a serializer/model
  limitation distinct from Start owner attribution.
- The final log has two failed File owner-resolution warnings. FileOps itself
  reports zero sender-queue drops and zero BPF ring-reservation failures, but
  `FileSerializer` reports `dropped_total=32,496` at its in-memory limit. That
  is confirmed file-output loss and keeps ldq-02 open independently of the
  PID-hash relationships.

`make build_dotnet` passed on the arm64 source-build host. After restoring the
local test project, the focused xUnit command for `ProcReaderTimestampTests`,
`ProcessResolverLinuxTimestampTests`, `AttributionRetryQueueTests`, and
`EventOwnerSelectionTests` passed **348/348**. Restore/build retain existing
NuGet compatibility/version warnings.

The final `qa-pid-hash` relationship diagnostic is therefore not accepted for
acceptance6. The clean acceptance4/acceptance5 databases and the controlled
acceptance6 workload prove the targeted timing and UID improvements; the frozen
acceptance6 output disproves a general zero-orphan claim.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance4/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance5/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance6/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/acceptance6/runtime/Logs/Lintap.log §2026-10-21 18:22:24–18:24:08 -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/ProcessStopSerializer.cs §createProcessTerminate -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Save/FlushToDisk -->
<!-- GROUND_TRUTH: ../wintap/tests/Wintap.Tests/ProcReaderTimestampTests.cs §RootUidResolvesFromTheLocalPasswdDatabase -->

## ldq-01 — matched two-hour FileOps A/B

Matched source-build runs each completed 120 one-minute rounds and 124,800
unique workload paths without workload failures. Both arms used the same
delivery-latency instrumentation; only the BPF ring submission flag differed.

| Measure | Suppressed notifications | Adaptive notifications |
| --- | ---: | ---: |
| Delivery samples | 1,555,567 | 1,506,846 |
| Weighted average delivery latency | 27.9 s | 4.6 s |
| Maximum delivery latency | 117.3 s | 25.0 s |
| Delivery samples over 60 s | 484,546 | 0 |
| FileSerializer drops | 32,489 | 46,705 |
| Workload paths retained | 120,252 (96.4%) | 117,462 (94.1%) |
| FileOps sender-queue / BPF ring failures | 0 / 0 | 0 / 0 |

Adaptive ring notifications materially reduce delivery delay and eliminate the
observed over-60-second tail, but do not by themselves prevent FileSerializer
loss. The adaptive arm therefore remains selected only in combination with the
serializer-drain remediation below. Both isolated DBT builds passed 80/80; file
relationships were clean, while network orphan/`Unknown` rows fell from 780 to
437. Clean relationships did not imply complete capture: each arm still lost
workload paths.

The baseline `pidstat` accidentally sampled the `sudo` launcher and is unusable
for CPU/RSS comparison. The adaptive service had 716 valid samples: 14.94%
average CPU, 160.2% peak CPU, 730,474 KiB average RSS, and 1,142,192 KiB peak
RSS. The final remediated run uses the service PID and will provide the valid
post-change resource point; no baseline resource delta is claimed.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/long-ab-results.json -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/long-ab-baseline/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/long-ab-adaptive/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../wintap/devtools/lintap_long_ab_report.py -->

## ldq-02 — dedicated drain and coordinated shutdown

The A/B logs localized loss to the bounded 10,000-event FileSerializer queue:
high-water requests competed for a ThreadPool slot after the queue reached half
capacity. FileSerializer now uses the existing dedicated flush worker, as the
registry serializer already did. Adaptive ring notification remains enabled in
both the CO-RE and tracepoint FileOps tiers.

Shutdown now follows an ordered producer-stop, serializer-drain, parquet-write,
and final-merge sequence. Linux skips the prior Windows registry write that
could abort this sequence. The logger drains accepted entries before closing,
and failed final merges retain source parquet instead of deleting it.

A 5,000-file, 40-worker burst completed in 0.292 seconds with all 5,000 paths
and 25,000 expected operation rows retained. FileSerializer accepted 33,767
rows, reported zero drops, and peaked at 5,617 queued events. Graceful shutdown
drained every serializer, left no staged or `.active` files, and materialized
all seven observed raw streams. Its isolated DBT build passed 80/80 with zero
file/network orphan or `Unknown` rows. This was the first passing burst gate;
the final long and packaged gates are recorded below.

The first final-code repetition exposed a native shutdown race: the two-second
poll-thread join could expire under burst load and free the libbpf ring buffer
while its callback was still active, causing a segmentation fault. Poll and
FileOps sender workers are now fully joined before native cleanup and ETL drain.
After rebuild, a second 5,000-file/40-worker burst shut down normally. It
retained all 5,000 paths and the exact 40,000 operations implied by the
workload: 10,000 each for Open, Read, and Close plus 5,000 each for Write and
Delete. FileSerializer accepted 46,608 rows with zero serializer/parquet drops;
the final merge completed and left zero staged or `.active` files. The short
capture did not emit every optional network stream, so its DBT build correctly
failed the missing-input assumption and is not represented as an 80/80 gate.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/SerializerSchedule.cs §ResolveOptions -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Shutdown -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §Stop -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/remediation-smoke/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §Stop -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/final-shutdown-smoke-v2/runtime/Logs/Lintap.log §2026-10-22 08:45:45 -->

### Final two-hour source-build remediation

The final-code source run completed all 120 one-minute rounds and generated
124,800 unique workload files with zero workload failures. It retained all
124,800 `.dat` paths. DBT counted 998,421 file operations against the workload's
998,400 minimum (21 additional Open/Read/Close observations), so no exact-count
claim is made for this long capture.

FileSerializer accepted 972,172 events, dropped zero, and peaked at 5,728 of
10,000 queued events. FileOps sender drops, BPF ring failures, parquet failures,
and parquet dropped batches were all zero. Delivery latency averaged 6.1 s,
peaked at 36.1 s, and had zero samples over 60 s. Shutdown fully drained the
serializer and writer, completed the final merge, returned status 0, and left
zero staging or `.active` files. The isolated DBT build passed **80/80** and the
workload's file rows had zero `Unknown` process names.

The valid post-change resource point is 717 samples: 21.30% average CPU,
156.6% peak CPU, 639,419 KiB average RSS, and 2,106,660 KiB peak RSS. The
baseline sampled `sudo`, not the sensor, so no CPU/RSS improvement or regression
delta is claimed.

This run still had 904 network orphan/`Unknown` identities. Each affected rapid
process could produce multiple fallback hashes milliseconds after its recorded
Stop because NetworkSensor used delayed callback time as event time. The tracer
already supplied `bpf_ktime_get_ns()`; the final remediation converts that
kernel monotonic timestamp to UTC using integer nanoseconds, shared with
FileOps, rather than substituting callback time.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/long-ab-remediated/acceptance-status.txt -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/long-ab-remediated/data/duckdb/wintap.duckdb §process_file and attribution_quality_summary -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/long-ab-results.json -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §HandleEvent -->

## ldq-03 — final network event-time validation

A fresh source-build rapid-child run exercised 200 children, 2,000 files, TCP,
and UDP after the kernel event-time change. It retained all 2,000 paths and the
exact 16,000 workload operations. DBT passed **80/80**. Across 45,567
`process_file`, 892 `process_conn_incr`, and 888 `process_net_conn` rows, all
three relationships had zero orphan rows/hashes and zero `Unknown` process
names. TCP contributed 610 increments and UDP 282. All 661 observed Start rows
had known users. FileSerializer accepted 46,356 events with zero drops; shutdown
and final merge completed with no staging or `.active` files.

This closes the observed rapid-exit network skew without broadening the claim:
the evidence applies to observed Start rows and the controlled workload.
Stop-only rows do not gain a user field from `ProcessStopSerializer`.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/network-kernel-time/data/duckdb/wintap.duckdb §attribution_quality_summary -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/network-kernel-time/dbt-summary.txt -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs -->

## ldq-05 — fresh packaged arm64 acceptance

Debian arm64 package `lintap_0.1.0-102_arm64.deb` was built from the final source
later committed as `1c048a8`. Its SHA-256 is
`0b2e7cc3842c394fc6caab678f843f22f693ad317b685d93f330b54d95ada46c`.
It was installed on newly created Ubuntu 24.04 arm64 Multipass instance
`lintap-ldq-package`; BTF and architecture checks passed. The acceptance config
explicitly enabled Clone and used the feature-isolated mounted data root.

The 200-child burst generated 5,000 files with zero workload failures. DBT
passed **80/80** and retained all 5,000 distinct paths and exactly 40,000
operations: 10,000 each for Open, Read, and Close, and 5,000 each for Write and
Delete. All 25,000 workload aggregate rows had known process names.

The full isolated database reports zero orphan and `Unknown` rows across
103,266 `process_file`, 877 `process_conn_incr`, and 875 `process_net_conn`
rows. The network workload included 609 TCP and 268 UDP increments. All 923
observed Start rows had known users. The 189 Stop-only rows had blank users,
consistent with the separately documented Stop serializer/model limitation.

FileSerializer accepted 106,155 events, dropped zero, peaked at 5,522, and
drained its final 3,592 rows during shutdown. Parquet failures/dropped batches,
FileOps sender drops, and BPF ring failures were zero. Systemd reported a
successful exit; final merge completed, and zero staging/`.active` files
remained.

The final focused arm64 suite passed **383/383** and `make build_dotnet` passed
with zero errors and 567 existing warnings. The package build, source rapid-run,
two-hour source run, and package acceptance together satisfy the frozen feature
criteria. Commit `1c048a8` was created locally and was not pushed.

<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/packaged-102/data/duckdb/wintap.duckdb §attribution_quality_summary and process_file -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/packaged-102/Lintap.log §2026-10-22 11:26:06–11:26:07 -->
<!-- GROUND_TRUTH: ../Wintappy/data/improve-lintap-data-quality/packaged-102/dbt-summary.txt -->
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/build-deb.sh -->

## Acceptance result

**PASS — feature closed 2026-10-22.** The selected design is adaptive ring
notification plus a dedicated FileSerializer drain and coordinated shutdown.
It meets the source and packaged path-coverage/zero-new-drop gates and the
capture-isolated DBT attribution contract. The evidence does not claim a valid
baseline CPU/RSS delta, universal zero-orphan behavior, or Stop-user enrichment.
