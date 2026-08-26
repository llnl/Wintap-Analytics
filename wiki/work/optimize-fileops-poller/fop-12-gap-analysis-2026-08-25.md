---
title: "Gap Analysis: fop-12 Relative-Open Identity Floor"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - wiki/work/optimize-fileops-poller/verification.md
  - wiki/work/optimize-fileops-poller/milestone-2026-08-25-phase2-wrapup.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: mixed
status: draft
source_paths: wiki/work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25.md
tags: [feature-work, file-events, ebpf, linux-sensor, path-identity, diagnostic]
---

# Gap Analysis: fop-12 Relative-Open Identity Floor

Deeper analysis of why fop-12's remaining misses persist and how to fix them,
requested after the phase-2 milestone wrap-up. Evidence: recorded summary
statistics in [[wiki/work/optimize-fileops-poller/verification]] plus
read-only source review of the deployed fop-12 implementation.

## Verdict In One Paragraph

The remaining ~8k/min `relative_open_resolve_miss` floor is **structural, not
tunable**: every fop-12 fallback (opened-fd readlink, cwd, dirfd readlink)
reads *current* `/proc/<pid>/...` state at userspace decode time, while the
dominant relative-open producers are millisecond-lived processes whose fds
and `/proc` entries are gone before the record is decoded. No reordering,
caching, or latency-shaving of `/proc` lookups can recover identity that no
longer exists on the host. The fix is to capture base-directory identity
**in the kernel at event time** — and the sensor currently *discards* the
one record class that would make that identity resolvable: `O_DIRECTORY`
opens. A second, complementary fix — the already-approved (s_dev, i_ino)
emission — makes fop-11's aggregation key independent of path resolution
entirely, unblocking it on a separate, shorter path.

## 1. Anatomy Of The Miss (What The Counters Prove)

- The reason-split counters show recovery comes from `resolved_fd`
  (~871–1528/min) and `resolved_dirfd` (~548–958/min); `resolved_cwd` is
  0–1/min — the cwd branch is confirmed dead weight for this workload.
- **`dirfd_lookup_miss` is essentially equal to `relative_open_resolve_miss`
  (~8k/min)**: virtually every remaining miss is a non-`AT_FDCWD` relative
  open that fell through BOTH the opened-fd readlink and the dirfd readlink.
  <!-- SYNTHESIS: verification.md §Root-Run Diagnostics Bundle Review 20260825T234559Z, "dirfd_lookup_miss is essentially the same size as relative_open_resolve_miss" -->
- Both readlinks failing together is the signature of the producer being
  gone (or both fds closed) by decode time. The fop-10 attribution supports
  this: top emitting comms include `sed`, `awk`, `sh`, and `rpm` helpers —
  classic fork-exec-exit-in-milliseconds processes, while ring delivery plus
  wakeup batching alone is up to ~100ms before poller scheduling.
  <!-- SYNTHESIS: comm_top evidence in verification.md §First Deployed fop-10 Build; wakeup batching design in file_ops_tracer.bpf.c §submit_file_event -->
- What the counters cannot yet distinguish: process-dead vs fd-closed-early.
  See F3 below — one cheap counter split settles it.

## 2. The Structural Root Cause In The Tracer

Two kernel-side facts make the miss floor inevitable today:

1. **`O_DIRECTORY` opens are discarded at open-exit** (both open and openat
   exit paths). When `rpm` does `open("/usr/lib/rpm", O_DIRECTORY)` and then
   `openat(dirfd, "rpmrc")`, the sensor throws away the record that says
   what `dirfd` points at — then later tries to rediscover it from `/proc`
   after the process is dead. glibc's `opendir()` also routes through
   `openat(..., O_RDONLY|O_DIRECTORY|O_CLOEXEC)`, so directory-handle opens
   ARE visible at these tracepoints; they are just dropped.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §t_open_exit/§trace_openat (O_DIRECTORY early return, lines ~447/~477) -->
2. **Directory-fd closes are invisible too** — `t_close` drops non-regular
   fds in-kernel via `is_regular_fd` (a directory is not `S_ISREG`), so a
   per-(pid, fd) dirfd cache could never be evicted by observed closes. Any
   userspace directory knowledge must therefore be keyed by something
   stable, not by (pid, fd).
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §t_close (is_regular_fd drop, lines ~500-506) -->

## 3. Ranked Fixes

### F1 — Global directory-identity index, learned in-kernel (the structural fix)

CO-RE tier, two coordinated changes sharing one record-format revision:

1. **Stamp relative-open records with the dirfd's inode identity.** At
   open-enter/exit for non-`AT_FDCWD` relative opens, resolve
   dirfd → `struct file` → `f_inode` → `(s_dev, i_ino)` and carry it in the
   path record. This is the same fdt traversal `is_regular_fd` already runs
   per fd event — the verifier pattern is proven on the RHEL8 kernel.
2. **Stop discarding `O_DIRECTORY` opens; emit them as a new internal
   `DIR_OPEN` record** carrying the opened fd, the directory's
   `(s_dev, i_ino)`, and its pathname. Userspace does NOT emit a
   WintapMessage for these; it maintains a **global bounded LRU index keyed
   by `(s_dev, i_ino) → absolute directory path`**. Identity-keyed, not
   (pid, fd)-keyed: stable across processes and process lifetimes, immune to
   fd close and `/proc` races, and shared — one `rpm` worker teaching the
   index `/usr/lib/rpm` resolves every later worker's relative opens under
   that directory. A `DIR_OPEN` whose own path is relative resolves through
   the same chain (directories outlive their openers far more often, and the
   index bootstraps recursively).

New resolution chain: opened-fd readlink (fast path, producer alive) →
**dir-index lookup by dirfd `(s_dev, i_ino)` + join (race-free, works after
producer exit)** → `/proc` dirfd readlink → cwd → miss.

Expected effect: the ~8k/min floor collapses to dirfds whose `DIR_OPEN` was
never observed (inherited fds, opens predating sensor start, `dup` family) —
a bounded residual that shrinks as the index warms after startup, and which
gets its own `dir_index_miss` counter instead of hiding inside the current
aggregate miss.

Costs and edges to record during implementation:
- Path record grows ~16B (dev+ino+pad); `DIR_OPEN` adds ring volume equal to
  the directory-open rate — previously dropped pre-reserve, so measure it
  (new stat slot) rather than assume; directory opens are far rarer than
  file opens.
- Index staleness on directory rename/move: a known blind spot already
  (rename is in the fidelity-gap backlog); the index makes it no worse than
  today's raw-relative emission and strictly better on identity.
- Fallback (non-CO-RE) tier cannot read inodes: it keeps the current `/proc`
  chain; the tier fidelity difference is already the documented pattern
  (consistent with the fop-05 and socket/pipe decisions).
- Eviction: size-bounded LRU only (thousands of live directories, not
  millions); no close-driven eviction needed or possible (§2 fact 2).

### F2 — File (s_dev, i_ino) as the fop-11 aggregation identity (already approved as A3 — elevate it to the unblocker)

Emit the opened file's `(s_dev, i_ino)` at open-exit and on compact fd
records (the inode pointer is already in hand in `is_regular_fd`). Then
fop-11's aggregation key becomes `(pid, dev:ino, op)` wherever identity is
present — exact and collision-free regardless of path-resolution quality.
Unresolved relative paths stop being a conflation risk and become a
display/enrichment concern. Combined with the milestone's split-contract
idea: rows lacking dev:ino (fallback tier) either stay per-event or
aggregate only on proven-absolute paths. **This unblocks fop-11 without
waiting for perfect path recovery** — F1 then raises path quality on its own
track. F1 and F2 share the same record-format change; implement in one
kernel slice.

### F3 — Miss-cause counter split (do first; hours, not days)

On the miss path only (~133/s), one `stat("/proc/<pid>")` distinguishes
producer-dead from fd-closed-early; split `opened_fd_lookup_miss` and
`dirfd_lookup_miss` accordingly. This validates the §1 diagnosis with field
data before the kernel work lands, and it sizes F1's expected win precisely
(process-dead misses are exactly the class the dir index recovers). Follows
the feature's measurement-first ethos at negligible cost.

### Non-fixes, recorded to prevent re-litigation

- **Shaving delivery latency** (smaller wakeup threshold, tighter poll)
  cannot beat millisecond process lifetimes; it trades context-switch CPU
  for a race it cannot win.
- **More cwd investment** — measured at 0–1 recoveries/min; dead end for
  this workload (already the milestone's position; the counters now prove
  it).
- **Retro-resolution from later events** — fd records carry no path; there
  is nothing to attach a late resolution to.

## 4. Recommended Sequencing (fop-13)

1. **fop-13a**: F3 counter split (immediate; validates and sizes).
2. **fop-13b**: F1 + F2 as one kernel/userspace slice — record format gains
   file dev:ino, dirfd dev:ino on relative opens, and the `DIR_OPEN`
   internal record + global directory index; new counters
   (`resolved_dir_index`, `dir_index_miss`, `dir_open_emitted`).
3. Re-measure against this milestone's baseline: `relative_open_resolve_miss`
   and the `(relative)` prefix bucket should collapse toward the
   inherited-fd residual.
4. **fop-11 unblocks on the F2 track** once dev:ino identity is in the
   stream — with the split contract for identity-less rows — independent of
   how far the F1 path-quality residual has shrunk.

## 5. Acceptance Criteria For The Fix

- `relative_open_resolve_miss` drops by an order of magnitude under the
  standing smoke workload versus the 20260825T234559Z baseline (~8k/min),
  with the residual explained by `dir_index_miss`.
- `(relative)` leaves the top-5 prefix buckets in `prefix_top`.
- Differential harness: regular-file tuples remain equal-or-superset; newly
  resolved paths appear as absolute where the baseline had relative
  (comparator needs a relative→absolute matching mode for the transition).
- `ring_fail_total` stays 0 and queue drops do not regress with the added
  `DIR_OPEN` volume; `dir_open_emitted` is recorded so the added volume is a
  measured number.
- No WintapMessage is emitted for `DIR_OPEN` records (internal only), and
  fallback-tier behavior is unchanged.
