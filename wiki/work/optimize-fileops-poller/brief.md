---
title: "Feature Brief: Optimize FileOps Poller Event Volume"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: mixed
status: draft
source_paths: wiki/work/optimize-fileops-poller/brief.md
tags: [feature-work, file-events, ebpf, linux-sensor, ring-buffer, performance, lintap]
---

# Feature Brief: Optimize FileOps Poller Event Volume

> **STATUS: CLOSED — accepted 2026-08-27.** All fop slices landed and
> field-verified; fop-11 count+byte conservation proven by the kill-switch
> A/B (see [[wiki/work/optimize-fileops-poller/verification]]); the
> regression surface is [[wiki/work/optimize-fileops-poller/test_plan]].
> Watch items: fop-14 serializer caps (long-term, re-measure post-EPL-fix),
> the ~1% open+close capture flake, and the ACME dataset historical
> eventCount-inflation check.

Spun off from the initial review recorded 2026-08-24 in
[[wiki/work/fix-unbounded-process-table-growth/verification]] ("Initial
FileOps Review"). Development happens on the `grantj-rhel8-testing` branch in
both `../wintap` (code) and `Wintap-Analytics` (wiki + validation artifacts).

## Problem

Field diagnostics after the pidstat and process-retention fixes show
`FileOps-Poller` as the dominant hot thread in Lintap. Source analysis found
that most of that cost is spent on events that are guaranteed to be discarded
or that carry no real file information:

1. **Non-file fds dominate the fd-op stream.** The eBPF tracer emits every
   `read`/`write`/`close` syscall regardless of what the fd refers to.
   Sockets, pipes, and ttys are never opened via `open`/`openat`, so they
   always miss the userspace fd→path cache and pay an uncached
   `FileInfo` + `stat` + `readlink /proc/<pid>/fd/<fd>` **per syscall**. The
   readlink result (`socket:[N]`, `pipe:[N]`) then passes all path filters and
   is emitted as a File event with a garbage path, duplicating NetworkSensor
   coverage.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §GetPathFromFd -->
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §t_read_ent/t_write_ent/t_close -->

2. **Wintap traces its own I/O.** Parquet, log, and DuckDB writes from
   Wintap's own PID ride the full ring-buffer → marshal → path-resolve →
   filter pipeline and are then dropped by the data-root/parquet filters or by
   `EventChannel.Send`'s `PID == WintapPID` check.
   <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send (WintapPID check) -->

3. **Per-event userspace dead work.** Every event pays reflection-based
   `Marshal.PtrToStructure` with two array allocations, and a `GenPidHash`
   (two BouncyCastle MD5 digests plus `StringBuilder(9999)` allocations) whose
   result is unconditionally overwritten in `EventChannel.Send` for the Esper
   path and is semantically wrong (hashed on event time, not process start)
   in the DirectParquetSink path.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent -->
   <!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ProcessHash.cs §GenPidHash -->

4. **Oversized ring-buffer records and per-event wakeups.** Every event is a
   fixed 296-byte record (256 bytes of mostly-empty `filename` for fd ops)
   into a 512KB ring buffer (~1,700 events of burst headroom), and every
   submit can wake the poller thread.

## Goals

- Materially reduce `FileOps-Poller` CPU (and total Lintap CPU) by dropping
  work **before** it enters the ring buffer or as early as possible in
  userspace.
- **Zero information loss** in emitted file telemetry: every File event
  emitted today for a regular file must still be emitted, with the same or
  better path/op/PID fidelity. The only stream-content changes allowed are
  the explicitly decided items in Open Questions.
- Improve burst fidelity: smaller records and batched wakeups reduce
  ring-buffer overflow drops during I/O storms.
- Make the pipeline measurable: per-stage emit/drop counters in kernel and
  userspace so tuning is evidence-based, not inferred from thread CPU.
- Fix latent fidelity bugs found during review: `_fdToPath` never evicted on
  process exit (unbounded growth + wrong paths on PID reuse), and kernel
  timestamps discarded in favor of dequeue-time `DateTime.UtcNow`.

## Non-Goals

- ~~**Aggregation or sampling of read/write events**~~ — the 2026-08-24
  deferral was amended by human direction on 2026-08-25 after fop-10 measured
  52.7–83.7% duplicate-open ratios: **aggregation to the (pid, path, op)
  level with grouped totals (bytes etc.) and min/max timestamps over short
  intervals is now acceptable**, for all op classes, with emit-first
  semantics for distinct activity. Sampling remains out. See
  [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]].
- New syscall coverage (`rename`, `pread64`/`pwrite64`, `readv`/`writev`,
  `openat2`, `sendfile`, io_uring). Recorded as a fidelity-gap backlog in
  [[wiki/work/optimize-fileops-poller/design]] for a follow-on feature.
- Windows file sensor changes.
- Changes to Esper/EventChannel enrichment or DirectParquetSink beyond what
  the FileOps path requires.
- The tracked-fd eBPF map from the original 2026-08-24 hypothesis is treated
  as an alternative, not the plan of record (see design Alternatives).

## User-Facing Behavior

No new user-visible features. Operators should observe lower Lintap CPU
(especially the `FileOps-Poller` thread), unchanged File event content for
regular files, fewer ring-buffer overflow drops under bursts, and new
periodic counter log lines (emitted/dropped per stage and op class).
Per the 2026-08-25 socket/pipe decision (see Open Questions),
`socket:[N]`/`pipe:[N]`/`anon_inode:[N]` path rows disappear from the File
stream on CO-RE-tier hosts; BTF-less fallback-tier hosts still emit them.

## Acceptance Criteria

- **No-loss differential:** an A/B run of baseline vs. modified build against
  the same deterministic file workload shows the modified File event stream
  is equal-or-superset on regular-file events (path, op class, PID). The only
  allowed removals are: events from Wintap's own PID, and (if decided)
  non-regular-file rows (`socket:[N]`, `pipe:[N]`, `anon_inode:[N]`) and
  pseudo-filesystem rows already dropped in userspace today.
- **CPU:** `FileOps-Poller` thread CPU share and total Lintap CPU measurably
  reduced on the RHEL8 field host under comparable workload, measured with
  `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` before
  and after.
- **Counters:** kernel and userspace emit/drop counters exist, are logged
  periodically, and reconcile (kernel emits ≈ userspace consumed + ring drops).
- **Burst behavior:** under a file-storm workload, ring-buffer reserve
  failures (drops) are counted and are lower than baseline after the
  record-size change.
- **Fallback intact:** on a host without BTF, the sensor loads the
  tracepoint fallback object and behaves as today (kernel-side regular-file
  filtering is CO-RE-tier only).
- **No regressions:** existing process/file/network smoke checks and the
  validation harness pytest suite pass at parity; `dotnet build
  wintap/Lintap.csproj` and the tracers `make` build clean.
- `_fdToPath` size is bounded across process churn (no growth from exited
  PIDs), verified by a churn workload.

## Affected Areas

- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`
  — kernel filters, counters, record split; moves to the CO-RE build tier.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c`
  — fallback tier: receives the non-CO-RE-safe subset (self-PID filter,
  wakeup batching, counters).
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile` — tier move.
- `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs` — decode,
  fd-cache memoization/eviction, dead-work removal, counters.
- `../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs` — poll
  loop (only if wakeup batching needs a shorter poll timeout knob).
- `../wintap/wintap/platform/linux/sensor/ebpf/helpers/LibBpf.cs` — possible
  P/Invoke additions (`bpf_map_update_elem` for the self-PID map, ring-buffer
  query).
- `Wintap-Analytics/validation/` — new file-ops A/B differential scenario and
  burst workload script.

## References

See [[wiki/work/optimize-fileops-poller/references]].

## Open Questions

- **Socket/pipe rows — DECIDED 2026-08-25 (human sign-off): drop them.**
  Non-regular-file fd rows (`socket:[N]`, `pipe:[N]`, `anon_inode:[N]`, ttys)
  are permanently dropped from the File event stream, ratifying the CO-RE
  `is_regular_fd` filter already deployed in the expanded slice. Analytics
  does not consume these rows; socket visibility remains NetworkSensor's
  domain. Two accompanying decisions:
  - **Recorded gap:** pipe/anon_inode I/O (not covered by NetworkSensor)
    becomes invisible — added to the fidelity-gap backlog in
    [[wiki/work/optimize-fileops-poller/design]] as a possible future op
    class.
  - **Fallback tier stays as-is:** the non-CO-RE (BTF-less) tracepoint tier
    keeps emitting these rows; the tier content difference is accepted and
    documented rather than patched with a userspace filter.
- Should the userspace pseudo-path (`/sys`, `/proc`, `/dev`) filter remain
  after the kernel-side superblock-magic filter lands, as a belt-and-braces
  check on the fallback tracer path? (Design says yes; cheap.)
- Wakeup batching latency budget: is up to ~100ms added File event latency
  acceptable? (It is bounded by the existing poll timeout; design says yes.)
- Op-class config toggles (disable `read`/`close`/`mmap` emission) from the
  original hypothesis list: deferred — only revisit if the no-loss changes
  are insufficient, since toggles do lose information.

## Test Plan

Summarized here; full requirements in
[[wiki/work/optimize-fileops-poller/implementation_plan]] and
[[wiki/work/optimize-fileops-poller/dev_handoff]].

- Builds: tracers `make` (CO-RE + fallback tiers) and `dotnet build
  wintap/Lintap.csproj`.
- Unit-style checks for pure userspace logic (fd-cache memoization/eviction,
  decode, filters) via the `diagnostics/` console-project pattern or an
  isolated test harness, at the dev agent's discretion.
- Deterministic file workload + A/B differential comparison of emitted File
  events (the no-loss proof).
- Burst/storm workload with drop counters before/after.
- Process-churn workload for `_fdToPath` boundedness.
- Field measurement with `collect-lintap-diagnostics.sh` on the RHEL8 host.
- BTF-absent path: force-load the fallback object and re-run the smoke
  workload.

## Done When

- Acceptance criteria pass on the RHEL8 test host; A/B differential is clean.
- The socket/pipe decision is recorded (here and in design) with its
  rationale.
- Counters are documented and their baseline values captured in
  [[wiki/work/optimize-fileops-poller/verification]].
- If aggregation is reconsidered, a review-ready concrete proposal exists and is
  explicitly accepted before coding. That proposal now exists as
  [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]].
- Durable facts promoted to canonical pages: a FileOps sensor component page
  (pipeline stages, filters, counters, config), and updates to the
  file-events event_type page if stream semantics changed.
- `wiki/log.md` updated at each substantial slice.
