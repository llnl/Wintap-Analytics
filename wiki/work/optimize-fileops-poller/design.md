---
title: "Feature Design: Optimize FileOps Poller Event Volume"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/shared/ProcessHash.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: mixed
status: draft
source_paths: wiki/work/optimize-fileops-poller/design.md
tags: [feature-work, file-events, ebpf, linux-sensor, ring-buffer, performance, co-re]
---

# Feature Design: Optimize FileOps Poller Event Volume

## Summary

Reduce FileOps event processing with **no information loss** by (a) never
letting guaranteed-discard events enter the ring buffer (Wintap's own PID,
non-regular-file fds), (b) eliminating per-event dead work in userspace
(reflection marshaling, dead PidHash computation, uncached `/proc` readlinks),
(c) shrinking fd-op ring records and batching poller wakeups, and (d) adding
emit/drop counters at every stage so all of it is measurable. Aggregation is
explicitly out of scope for this feature.

## Current Pipeline Anatomy (cost inventory per event)

Kernel (per traced syscall):
`bpf_ringbuf_reserve` 296B → fill (comm copy; pathname copy for open/unlink)
→ `bpf_ringbuf_submit` (default flags → epoll wakeup of the poller).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §emit_file_event -->

Userspace, `FileOps-Poller` thread (per record):

1. `Marshal.PtrToStructure<FileEvent>` — reflection marshal, allocates a
   16-byte and a 256-byte array per event.
2. fd ops: `_fdToPath` lookup; on miss, `new FileInfo("/proc/pid/fd/N")` +
   `Exists` (stat) + `LinkTarget` (readlink) — **result never cached**, so an
   untracked fd pays this on every operation.
3. `NormalizeFilePath` (trim/lowercase allocation), pseudo-path filter,
   data-root prefix filter, `.etl` / `.parquet` suffix filters.
4. `GenPidHash` — two BouncyCastle MD5 digests + `StringBuilder(9999)`s.
5. `new WintapMessage(DateTime.UtcNow, …)` + `EventChannel.Send` → WintapPID
   drop / process resolution / Esper or DirectParquetSink.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent -->

## Where the volume actually comes from

- **Sockets/pipes/ttys**: `t_read_ent`/`t_write_ent`/`t_close` fire for every
  fd. Non-file fds always miss the fd cache (they were never opened via
  open/openat), always pay stat+readlink, and then *are emitted* with paths
  like `socket:[12345]` — these pass every filter (they don't start with
  `/sys`, `/proc`, `/dev`). On a network- or IPC-busy host this plausibly
  dominates both poller CPU and File stream volume, and it duplicates
  NetworkSensor's domain with unusable paths.
  <!-- SYNTHESIS: inferred from FileOpsSensor.cs §GetPathFromFd/§IsPseudoPath and file_ops_tracer.bpf.c §t_read_ent; needs the fop-01 counters to quantify -->
- **Self-feedback**: every Wintap parquet/log/DuckDB write is traced, fully
  processed, then dropped by the data-root/parquet filters or by
  `EventChannel.Send`'s `PID == StateManager.WintapPID` check.
- **Close storm**: every `close` on an untracked fd triggers a fallback
  readlink that is *guaranteed to fail* — the fd is already closed when
  userspace processes the record. Pure wasted stat per close.

## Proposed Changes

### Kernel-side

**K1 — Self-PID filter (both tracer variants).** Add a 1-entry
`BPF_MAP_TYPE_ARRAY` (`filter_pids` or a `.bss` global); userspace writes
Wintap's PID after `bpf_object__load`. Every program returns early when
`tgid == wintap_pid`. Managed data-root/parquet filters stay as a net for
child helper processes. *No loss: these events are all discarded today.*

**K2 — Regular-file filter for fd ops (CO-RE tier only).** In
`t_read_ent`/`t_write_ent`/`t_close`/`t_mmap`, resolve the fd to its inode
via CO-RE: `task = bpf_get_current_task()`, `BPF_CORE_READ(task, files, fdt,
fd)[fd]` → `f_inode`; emit only when `S_ISREG(i_mode)`. In the same lookup,
read `i_sb->s_magic` and drop `PROC_SUPER_MAGIC`/`SYSFS_MAGIC` (and devtmpfs)
— the pseudo-path filter moves into the kernel for fd ops without needing a
pathname. Requires moving `file_ops_tracer.bpf.c` into the Makefile
`CORE_OBJS` tier (vmlinux.h); `file_ops_tracepoint.bpf.c` stays as the
non-CO-RE fallback without this filter, so BTF-less hosts keep today's
behavior. *Loss analysis:* regular-file events are unaffected. Socket/pipe
rows disappear — gated on the sign-off recorded in the brief's Open
Questions. Pseudo-fs fd ops are dropped in userspace today anyway.

**K3 — Wakeup batching (both variants).** Submit with `BPF_RB_NO_WAKEUP`,
plus a forced wakeup (`BPF_RB_FORCE_WAKEUP`) every Nth event or when
`bpf_ringbuf_query(AVAIL_DATA)` crosses a threshold; the existing
`ring_buffer__poll(rb, 100)` timeout bounds delivery latency at ~100ms.
Removes the per-event epoll wakeup / context-switch storm charged to the
poller thread. *No loss: latency-bounded batching only.*

**K4 — Small records for fd ops (both variants).** fd ops never carry a
filename; give them a compact record (~40B: pid, comm, ts, fd, bytes,
op_type) — either a second ring buffer or a tagged variable-size record.
~7× more burst headroom in the same 512KB → fewer overflow drops → *fidelity
improves*. Requires a matching decode change in `FileOpsSensor`.

### Userspace

**U1 — Remove per-event `GenPidHash`.** Dead on the Esper path
(`EventChannel.Send` overwrites PidHash for all non-Process events) and
wrong on the DirectParquetSink path (hash keyed on per-event time → same
process gets a different PidHash every event, unjoinable to the process
table). Set `PidHash = ""` (or resolve via the resolver if DirectParquetSink
needs it — record the choice). Removes 2 MD5s + allocations per event.

**U2 — Memoize the `/proc` fallback; skip it for close.** Store successful
fallback resolutions into `_fdToPath` (evicted on close like traced opens).
For op `close` (type 4), skip the fallback entirely — the fd is gone.
Replace `FileInfo` with `File.ResolveLinkTarget`/direct readlink to avoid
the extra allocation+stat.

**U3 — Zero-alloc decode.** Replace `Marshal.PtrToStructure` +
`[MarshalAs(ByValArray)]` with direct unsafe/`Span` reads from the native
pointer: read `pid`/`op_type`/`fd`/`bytes` first, run all drop logic, and
materialize `comm`/`filename` strings only for events that will be emitted.

**U4 — Evict `_fdToPath` on process exit.** Exit closes fds implicitly (no
close syscalls), so per-PID maps for dead processes live forever: unbounded
growth plus **wrong paths on PID reuse** (a fidelity bug). Evict on
process-exit signal (ExitSensor already exists) or a periodic liveness sweep
of map keys against `/proc`.

**U5 — Use the kernel timestamp.** `evt.TimestampNs`
(`bpf_ktime_get_ns`, monotonic) is currently ignored in favor of
`DateTime.UtcNow` at dequeue — under backlog, event times skew by the queue
depth. Compute the monotonic→wallclock offset once (CLOCK_REALTIME −
CLOCK_MONOTONIC) and convert per event. Fidelity fix + removes a clock call.

**U6 — Counters everywhere.** Kernel: percpu array counting
emitted/dropped-by-filter per op class, plus ringbuf reserve failures
(overflow drops). Userspace: extend the existing pseudo-drop counter pattern
(`CountPseudoDrop`/`MaybeLogPseudoDrops`) to all drop reasons + emit count.
Log every 60s. These are the acceptance evidence for every other change.

## Data Model Or Schema Changes

None to the WintapMessage File schema. Ring-buffer wire format changes (K4)
are internal to the sensor. Stream *content* changes are limited to the
decided removals (self-PID rows; socket/pipe rows if approved).

## Edge Cases

- **BTF absent** → fallback object loads (existing candidate mechanism);
  no K2 filtering; userspace filters still correct. Must be exercised in
  tests by forcing the fallback object.
- **fd reuse**: unchanged semantics — traced open overwrites the cache entry,
  traced close evicts. U2's memoized entries follow the same lifecycle.
- **Missed closes (process exit)**: handled by U4 eviction.
- **dup/dup2/dup3, inherited and pre-existing fds**: not in the fd cache;
  still resolved via the (now memoized) `/proc` fallback — behavior today,
  minus the repeated readlink cost. K2 does not affect them (it inspects the
  fd's inode directly, no state needed).
- **O_DIRECTORY opens** are already dropped at open-exit; unchanged.
- **`fd` field width**: `t_mmap` compares `ctx->fd != -1` on an unsigned
  long; K2's fdt lookup must bounds-check fd against `fdt->max_fds`.
- **Verifier limits**: the fdt array access needs a bounded read
  (`bpf_probe_read_kernel` of one pointer at a computed offset) — standard
  libbpf-tools idiom, but must be validated on the RHEL8 4.18 kernel's
  verifier specifically.

## Error Handling

- If the self-PID map write fails at startup, log Warn and continue (sensor
  still correct, just slower).
- If the CO-RE object fails to load/verify on a given kernel, the existing
  fallback-candidate loop must cleanly fall back to the tracepoint object —
  this is the primary safety valve and must be tested, not assumed.
- Counter reads/logs must never throw into the poll callback.

## Risks

- RHEL8's 4.18 backport verifier may reject the task→fdt traversal pattern;
  mitigation: prototype K2 first on the target host (spike), fall back to
  the tracked-fd map alternative if truly blocked.
- K4's two-record decode is easy to get subtly wrong; mitigation: tag byte +
  size check + unit-tested decode.
- Batched wakeups interact with sensor shutdown (poll timeout bounds it).
- Removing GenPidHash changes DirectParquetSink output (PidHash column) —
  verify no downstream consumer depends on the current (broken) values.
  <!-- REVIEW NEEDED: confirm DirectParquetSink File rows' PidHash is not consumed downstream in its current per-event-time form -->

## Alternatives Considered

- **Tracked-fd eBPF map** (the original 2026-08-24 hypothesis): kernel hash
  map of (tgid, fd) populated at open-exit; fd ops emit only on map hit.
  Rejected as plan-of-record because it silently loses pre-existing fds
  (opened before sensor start), inherited fds, and the dup family — real
  information loss unless mitigated by a `/proc/*/fd` rundown seed plus
  dup/dup2/dup3/fcntl tracing, which is substantial added complexity and
  state. K2 achieves the same volume cut statelessly. Revisit only if K2 is
  verifier-blocked, or if in-kernel data-root filtering for fd ops is later
  wanted (a path-prefix filter needs open-time state; that would be a
  follow-on where the map's fidelity mitigations get designed properly).
- **Op-class disable toggles** (hypothesis item 3): loses information by
  construction; deferred until no-loss options are exhausted.
- **Short-cycle aggregation** of read/write (count/bytes per fd flushed on
  close/timer): deferred by explicit human direction 2026-08-24; revisit
  after this feature's measurements.
- **fentry/LSM + `bpf_d_path`** (kernel-side full path resolution on
  vfs_read/vfs_write): would eliminate the userspace fd cache entirely and
  enable in-kernel path-prefix filtering with no loss, and would also catch
  pread/readv/io_uring-adjacent paths — but it's a program-type migration
  with RHEL8 helper-availability risk. Recorded as the natural *next*
  feature if this one's results warrant it.

## Fidelity-Gap Backlog (out of scope, recorded for follow-on)

Currently invisible to FileOps: `rename`/`renameat2` (file-tampering blind
spot — deletes are covered, renames are not), `pread64`/`pwrite64`,
`readv`/`writev`, `openat2`, `sendfile`/`copy_file_range`/`splice`, io_uring
(bypasses syscall tracepoints entirely), and failed opens (`fd < 0` dropped —
failed access attempts are security-relevant and cheap to keep as an op
class). These are information *gains* to weigh against the volume they add,
after this feature lands its counters.

Added by the 2026-08-25 socket/pipe decision: **pipe/anon_inode I/O** is now
invisible on CO-RE-tier hosts (dropped by the `is_regular_fd` filter, per the
human sign-off recorded in [[wiki/work/optimize-fileops-poller/brief]] §Open
Questions). Unlike sockets, pipe and anon_inode activity is not covered by
NetworkSensor, so this is a real coverage gap — recorded here as a candidate
future op class if IPC visibility is later wanted.

## Open Questions

Tracked in [[wiki/work/optimize-fileops-poller/brief]] §Open Questions
(socket/pipe row decision, fallback-tier filter retention, latency budget).
