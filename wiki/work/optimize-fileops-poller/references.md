---
title: "Feature References: Optimize FileOps Poller Event Volume"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile
policy: agent-editable
last_validated: 2026-08-24
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: llm-agent
status: draft
source_paths: wiki/work/optimize-fileops-poller/references.md
tags: [feature-work, file-events, ebpf, linux-sensor, references]
---

# Feature References: Optimize FileOps Poller Event Volume

## Live Repo Sources

All on branch `grantj-rhel8-testing` in `../wintap` unless noted.

- `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`
  - §HandleEvent — per-event pipeline: marshal, fd→path, filters, GenPidHash, Send.
  - §GetPathFromFd — `_fdToPath` lookup + uncached `/proc/<pid>/fd/<fd>`
    stat/readlink fallback; result is NOT memoized back into the map.
  - §StoreFdPath/§RemoveFdPath — map populated only by traced opens, evicted
    only by traced closes; no process-exit eviction (leak + PID-reuse hazard).
  - §IsPseudoPath/§CountPseudoDrop — existing userspace pseudo-path filter
    and 60s drop-count logging (the pattern to extend for new counters).
  - §FileEvent struct — `[MarshalAs(ByValArray)]` decode; 296-byte layout.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`
  — primary object. 9 programs; stateful open/openat (enter saves
  pathname+flags in `openat_state_map`, exit emits with fd); unconditional
  emit for read/write/close/file-backed mmap; single 512KB `events` ringbuf;
  fixed 296-byte `file_event`. Currently built in the tracepoint (non-CO-RE)
  Makefile tier despite the name.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c`
  — fallback object, functionally identical today. Changes must be mirrored
  here where they don't require CO-RE, or the divergence documented.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile` — two-tier
  build: `CORE_OBJS` (need BTF/vmlinux.h; execve/exit/network already there)
  vs `TRACEPOINT_OBJS` (portability fallback). Both file_ops objects are in
  `TRACEPOINT_OBJS` today; the CO-RE regular-file filter requires moving
  `file_ops_tracer.bpf.o` into `CORE_OBJS`.
- `../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs`
  — §PollRingBuffer (the `FileOps-Poller` thread, `ring_buffer__poll(rb, 100)`),
  §LoadBpfProgram (fallback-object candidate loading, ring buffer setup),
  §LogEbpfEnvironment (BTF presence check already logged at startup).
- `../wintap/wintap/platform/linux/sensor/ebpf/helpers/LibBpf.cs` — P/Invoke
  surface; likely needs `bpf_map_update_elem`/`bpf_object__find_map_by_name`
  usage for the self-PID map and counter map reads.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` — §Send: WintapPID
  self-drop, PidHash overwrite for non-Process events (proof that
  sensor-side GenPidHash is dead work on the Esper path), DirectParquetSink
  early-return path (where sensor-set fields survive).
- `../wintap/wintap/core/etl/load/DirectParquetSink.cs` — §IsEnabled/§Save:
  the alternate sink where sensor-set PidHash/ProcessName survive.
- `../wintap/wintap/core/shared/ProcessHash.cs` — §GenPidHash/§GetHash: two
  MD5 digests + StringBuilder(9999) per call; hash keyed on the passed
  event time (wrong identity basis when called per file event).
- `../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs`
  — FileOps enable flag (`FileOps=true/false`) and sensor startup.
- `Wintap-Analytics/extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`
  — field measurement tool (perf stat, hot threads, DuckDB snapshot).
- `Wintap-Analytics/validation/process-creation/` — harness pattern (uv +
  pytest, workload manifests, run scripts) to extend with a file-ops
  differential scenario.

## External Sources

- libbpf ring buffer API: `bpf_ringbuf_reserve/submit` flags
  (`BPF_RB_NO_WAKEUP`, `BPF_RB_FORCE_WAKEUP`), `bpf_ringbuf_query`
  (`BPF_RB_AVAIL_DATA`) — basis for wakeup batching. Kernel docs/libbpf
  headers on the RHEL8 target are authoritative for what's available there.
- CO-RE task→fd traversal pattern: `bpf_get_current_task()` +
  `BPF_CORE_READ(task, files, fdt, fd)` then `f_inode->i_mode` (S_ISREG) and
  `i_sb->s_magic` — standard BCC/libbpf-tools idiom (e.g., filetop/opensnoop
  lineage). RHEL 8.2+ ships kernel BTF on 4.18 with backports; the target
  branch name (`grantj-rhel8-testing`) implies ringbuf support is already
  present on the fleet since the current tracers use it.
- Superblock magics: `PROC_SUPER_MAGIC` (0x9fa0), `SYSFS_MAGIC` (0x62656572),
  `TMPFS_MAGIC` (0x01021994, devtmpfs reports as tmpfs on some kernels),
  `SOCKFS_MAGIC`, `PIPEFS_MAGIC` — from `include/uapi/linux/magic.h`.

## Related Wiki Pages

- [[wiki/work/fix-unbounded-process-table-growth/verification]] — "Initial
  FileOps Review (2026-08-24)" section this feature supersedes; field
  diagnostics showing FileOps-Poller as dominant hot thread.
- [[wiki/work/fix-unbounded-process-table-growth/implementation_plan]] — the
  original future-todo checklist item, now pointing here.
- [[wiki/work/lintap-process-creation-validation/validation-harness-design]]
  — harness design the differential test should follow.
- [[wiki/work/improve-pidstat-collector/brief]] — per-thread CPU measurement
  data path used for before/after evidence.

## Libraries And APIs

- libbpf via P/Invoke (`LibBpf.cs`) — no managed BPF framework in use.
- clang + bpftool required by the tracers Makefile preflight; vmlinux.h is
  generated from `/sys/kernel/btf/vmlinux` for the CO-RE tier.
- BouncyCastle MD5 (ProcessHash) — being removed from this hot path, not added.

## Notes

- The naming is misleading: `file_ops_tracer.bpf.c` is *not* currently CO-RE
  despite the `_tracer` name other CO-RE objects use; both file_ops objects
  are near-identical tracepoint programs. After this feature, the `_tracer`
  object becomes genuinely CO-RE and the `_tracepoint` object is the real
  fallback — matching the pattern of execve/exit/network.
- `FileOpsSensor.Start()` attaches 9 additional programs by short name
  (15-char libbpf name limit noted in code); any new program names must
  respect that limit and be added to the attach list.
- The 296-byte figure: 4 (pid) + 16 (comm) + 256 (filename) + 8 (ts) + 4 (fd)
  + 4 (bytes) + 4 (op_type) = 296; ringbuf adds a header per record.
