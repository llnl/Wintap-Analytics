---
title: "Verification: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - ../Lintap/multipass-lintap.sh
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../Wintappy/wintap_dbt/qa/pid_hash_orphan_checks.sql
policy: agent-editable
last_validated: 2026-10-21
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/improve-lintap-data-quality/verification.md
tags: [feature-work, verification, lintap, file-events, attribution]
---

# Verification: Improve Lintap Data Quality

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
