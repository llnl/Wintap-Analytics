---
title: "Deep Analysis: FileOps Ring Loss Root Cause (Phase 2)"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/etl/load/DirectParquetSink.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: mixed
status: draft
source_paths: wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25.md
tags: [feature-work, file-events, ebpf, linux-sensor, ring-buffer, performance, diagnostic, duckdb, esper]
---

# Deep Analysis: FileOps Ring Loss Root Cause (Phase 2)

This is the deep-analysis pass requested by
[[wiki/work/optimize-fileops-poller/dev_handoff]] after the expanded
optimization slice was deployed and the 2026-08-25 overnight run still showed
sustained ring-buffer loss. It answers the four handoff questions from two
evidence sources only: the summary statistics recorded in
[[wiki/work/optimize-fileops-poller/verification]], and read-only source
inspection of `../wintap`. No raw runtime data was read for this analysis
(per explicit human direction, 2026-08-25); every claim that needs field
confirmation names the summary statistic that would confirm it.

## Verdict In One Paragraph

The overnight ring-buffer loss is a **userspace consumer-throughput problem,
not a kernel-emission or ring-sizing problem**. A single poller thread drains
the ring with a synchronous per-record callback, and every surviving event
pays a synchronous DuckDB process-lookup query under a process-global lock
plus a synchronous Esper submit, with no queue decoupling the ring from that
work. The measured shortfall (~778 lost events/s sustained) is orders of
magnitude above the plausible per-thread drain ceiling implied by previously
recorded lookup timings (~40–80 events/s). Additional kernel-side filtering
cannot fix this; the next slice must raise the consumer ceiling.
<!-- SYNTHESIS: inferred from ../wintap/wintap/core/infrastructure/EventChannel.cs, ../wintap/wintap/core/infrastructure/ProcessResolver.cs, and the overnight counter summaries in verification.md; confirm via consumed/s vs emitted/s from the 60s FileOps counter log -->

## 1. Rate Arithmetic From The Recorded Overnight Snapshots

Inputs are the two representative counter snapshots recorded in
[[wiki/work/optimize-fileops-poller/verification]] §Overnight Field Run —
2026-08-25, taken at `4:06:53 AM` and `6:38:54 AM` host-local time.
Window length: 2h 32m 01s = **9,121 s**.

| Counter | 4:06:53 | 6:38:54 | Delta | Rate |
|---|---|---|---|---|
| `open ring_fail_total` | 8,991,202 | 11,999,369 | 3,008,167 | 329.8/s |
| `read ring_fail_total` | 7,121,895 | 9,342,135 | 2,220,240 | 243.4/s |
| `close ring_fail_total` | 2,547,197 | 3,392,084 | 844,887 | 92.6/s |
| `mmap ring_fail_total` | 2,303,884 | 3,068,775 | 764,891 | 83.9/s |
| `write ring_fail_total` | 31,360 | 292,744 | 261,384 | 28.7/s |
| **ring_fail total** | 20,995,538 | 28,095,107 | **7,099,569** | **~778/s** |
| `open pseudo_drop_total` | 22,959,589 | 30,345,515 | 7,385,926 | ~810/s |

Observations:

- **~778 events/s were lost to ring-buffer reserve failures, sustained across
  the whole 2.5-hour window** — the loss rate is roughly constant, not bursty
  (the deltas accumulate smoothly between the two snapshots as far as the
  recorded evidence shows).
- The kernel pseudo-path filter alone was discarding ~810 opens/s **before**
  the ring, on top of the non-regular-fd filter volumes (cumulative
  `read nonregular_drop_total=69,576,912`, `close nonregular_drop_total=87,966,528`
  at the later snapshot). The already-landed filters are doing enormous work;
  what survives them is still far more than userspace consumes.
- Op-class loss shares: open 42%, read 31%, close 12%, mmap 11%, write 4%.
  Loss is broad-based across op classes, which is what saturation of a shared
  ring predicts — once the ring is full, *every* op class fails reserve at its
  own offered rate, so these shares approximate the post-filter emission mix
  rather than identifying a single hot op.
  <!-- SYNTHESIS: share arithmetic from the table above; the "shares ≈ emission mix" reading assumes a persistently full ring -->

## 2. Ring Capacity Arithmetic

Record sizes from the tracer source:
`FILEOPS_RINGBUF_SIZE = 16 MiB`; compact fd record (`file_fd_event`) is 48 B,
path record (`file_path_event`) is 304 B; the BPF ring buffer adds an 8-byte
header per record, so effective footprints are **56 B** and **312 B**.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §FILEOPS_RINGBUF_SIZE/§file_fd_event/§file_path_event -->

- All-fd-record capacity: 16,777,216 / 56 ≈ **~299,600 queued events**.
- All-path-record capacity: 16,777,216 / 312 ≈ **~53,800 queued events**.

At a net shortfall of ~778 events/s, a 16 MiB ring's worth of headroom is
consumed in **roughly 1–6 minutes** (path-heavy to fd-heavy mix), after which
the ring runs permanently full and every subsequent reserve failure is a lost
event. Growing the ring buys minutes, not a fix.
<!-- SYNTHESIS: capacity arithmetic above combined with the measured shortfall rate -->

## 3. The Consumer Ceiling (Root-Cause Mechanism)

Source inspection of the drain path shows why userspace cannot keep up:

1. **One thread, synchronous callback.** Each eBPF sensor runs a single
   dedicated poller thread looping `ring_buffer__poll(RingBuffer, 100)`;
   libbpf invokes the event callback synchronously once per record, so drain
   rate = 1 / (mean per-event handling time), single-threaded. Only
   `ring_buffer__poll` is bound; there is no multi-consumer or batch handoff.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §PollingThread (poll loop, lines ~218-237) -->
2. **Per-event DuckDB query under a global lock.** For every surviving File
   event, `EventChannel.Send` calls
   `ProcessResolver.ResolveProcessAtTime(pid, …)`, which takes the
   process-wide `_dbLock` (shared with every other sensor, process
   registration, and maintenance sweeps) and executes a synchronous DuckDB
   `SELECT` per event; on a resolver miss a **second** query runs via
   `GetPidHash` under the same lock.
   <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send (~line 266); ../wintap/wintap/core/infrastructure/ProcessResolver.cs §ResolveProcessAtTime (~lines 128-184) and §GetPidHash (~lines 813-853) -->
3. **Synchronous Esper submit.** The event then goes to
   `EsperRuntime.EventService.SendEventBean(...)` inline on the same thread.
   <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send (~line 391) -->
4. **No intermediate queue.** Nothing decouples the ring callback from the
   resolve+Esper work. (The only queued sink in the codebase is
   `DirectParquetSink` — a bounded `ConcurrentQueue` with a flush timer and
   drop policy — which is disabled by default and bypasses resolver+Esper
   entirely when enabled.)
   <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/DirectParquetSink.cs §queues/§IsEnabled -->

The implied ceiling: the 2026-08-24 field diagnostic (recorded in the
fix-unbounded-process-table-growth thread) measured representative process
lookups at **~12–25 ms each** on a copied field DB with sequential scans over
~48k process rows. At one such query per event, serially, one thread drains
**~40–80 events/s** — orders of magnitude below the post-filter kernel
emission rate, and consistent with both the ~778/s sustained loss and the
poller pegged at ~95% CPU.
<!-- SYNTHESIS: inferred from the 2026-08-24 lookup timings in work/fix-unbounded-process-table-growth/verification.md and the send-path source above. CONFIRM VIA: per-60s userspace consumed/emitted counts from the FileOps counters log vs. kernel emitted totals from fileops_stats — the consumed/s figure directly measures the drain ceiling; request it as summary lines only -->

Secondary per-event costs (real, but not the ceiling):

- 3–4 heap allocations per event (`WintapMessage`, `FileActivityObject`,
  lowercased path string, comm string) plus five `ConfigManager.GetValue`
  lookups per event inside `EventChannel.Send` (direct-parquet check + four
  skip-flag checks).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent; ../wintap/wintap/core/infrastructure/EventChannel.cs §Send/§IsEnvEnabled -->
- `_fdToPath` is an unbounded nested `ConcurrentDictionary` with **no eviction
  except on observed close** — missed/dropped closes and dead PIDs leak
  entries (the known fop-07 item), and every cache miss on read/write/mmap
  pays a `/proc/<pid>/fd` readlink with a 4 KiB buffer allocation.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §_fdToPath/§GetPathFromFd/§ReadLinkTarget -->
- The kernel `timestamp_ns` is still discarded in favor of `DateTime.UtcNow`
  at decode time (fop-07 U5) — under the current permanent backlog, emitted
  File event times skew by the queue depth, so this fidelity fix has become
  more important, not less.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent (WintapMessage construction) -->

Existing levers worth knowing about (diagnostic, not the recommendation):
`WINTAP_SKIP_PROCESS_RESOLVE` / `WINTAP_SKIP_ESPER_SEND` env gates bypass the
expensive steps per event, and `WINTAP_ENABLE_DIRECT_PARQUET` routes events to
the bounded queued sink, skipping resolver+Esper entirely. A short field
experiment with `WINTAP_SKIP_PROCESS_RESOLVE=true` would cleanly isolate the
DB-query share of the ceiling (watch `ring_fail_total` growth rate before/after
— summary counters only).
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send/§IsEnvEnabled; ../wintap/wintap/core/etl/load/DirectParquetSink.cs §IsEnabled -->

## 4. Answers To The Four Handoff Questions

### Q1 — Why was the first-minute smoke clean while overnight lost millions?

Because this is **steady-state saturation, not burst loss**. The 16 MiB ring
holds ~54k–300k queued events (§2); at startup it is empty and absorbs the
first minute entirely, so the smoke snapshot legitimately showed
`ring_fail_total=0`. Once sustained post-filter emission exceeds the
consumer's per-event-query ceiling (§3), the ring fills within minutes and
then *stays* full; from that point every event beyond the drain rate fails
reserve. The overnight counters are exactly this signature: large,
smoothly-growing `ring_fail_total` across all op classes at a near-constant
combined rate (~778/s). The smoke test and the overnight run do not
contradict each other — they sample the two phases of the same fill curve.

### Q2 — Which surviving regular-file classes dominate the remaining pressure?

**The recorded evidence cannot attribute loss below op-class granularity.**
`fileops_stats` counts per op class only; ring saturation additionally means
op-class loss shares mirror the offered mix rather than isolating a culprit
workload (§1). What is knowable now: open (42%) and read (31%) dominate the
lost volume, and the kernel still emits *every* surviving regular-file
read/write/close/mmap with no open-tracking gate and no repeat suppression —
a process reading one file in a loop emits one record per syscall.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §t_read_ent/§t_write_ent/§t_close/§t_mmap -->

**Next measurement (summary statistics only, no raw events):** extend the 60s
`FileOps counters` log with top-N aggregate attribution — per-`comm` (and/or
per-path-prefix bucket) emitted counts per op class, held in a small bounded
kernel map or aggregated in userspace at decode time, logged as e.g.
`FileOps top-emitters: comm=X open=N read=M …` lines. That gives path-class
attribution inside the existing no-raw-data diagnostic envelope and decides
whether any further kernel-side filter is even worth building.

### Q3 — Next minimal no-loss change with the highest expected return

Ranked; all preserve the no-loss contract (aggregation/sampling remains
excluded by standing human direction 2026-08-24; op-class toggles remain last
resort since they lose information by construction):

1. **fop-08 — Raise the consumer ceiling (recommended next slice).** Two
   halves, one goal: make per-event cost independent of DuckDB and Esper
   latency.
   - **In-memory pid→process-identity cache for the File path:** resolve
     PidHash/process identity from an in-memory current-process map maintained
     by the resolver (populated at registration, evicted at exit), falling
     back to the DB only on miss. This eliminates the per-event
     `SELECT`-under-`_dbLock` and directly implements the "in-memory
     current-process map" already recommended at the close of
     [[wiki/work/fix-unbounded-process-table-growth/brief]].
   - **Bounded in-process queue between the ring callback and resolve/Esper:**
     the callback does decode+filter only, enqueues, and returns; a worker
     drains into resolve+Esper. Backpressure moves from a 16 MiB kernel ring
     losing events silently-but-counted into a large, cheap userspace queue
     whose depth and any drops are explicitly counted and logged. Loss
     accounting gets *better*, not worse.
2. **fop-09 — Hoist per-event config lookups.** Cache the five
   `ConfigManager.GetValue` results in `EventChannel` fields (they are
   env/config constants for the process lifetime). Trivial, safe, measurable.
3. **fop-07 (already planned) — fd-cache eviction + kernel timestamps.**
   Fidelity fixes whose urgency rose: PID-reuse misattribution grows with
   uptime, and timestamp skew grows with backlog depth (§3).
4. **Further kernel-side reduction — only after the Q2 measurement.** If the
   top-emitter data shows a dominant filterable class (e.g. a data-root-like
   prefix reachable for fd ops via open-state, or a small set of noisy comms),
   design the specific filter then. Building more kernel filters before fixing
   the consumer ceiling cannot stop the loss (§3) and risks optimizing the
   wrong stage.

### Q4 — Incremental, or structural fentry/`bpf_d_path` move?

**Stay incremental.** The fentry/`bpf_d_path` redesign replaces the fd→path
resolution mechanism and enables in-kernel path-prefix filtering — but the
diagnosed bottleneck is userspace consumption downstream of decode, which that
migration does not touch. It carries RHEL8 helper/verifier risk for no leverage
against the actual loss. Reopen it if (a) after fop-08 lands, sustained
`ring_fail_total` growth persists with the consumer no longer CPU-bound, or
(b) the Q2 measurement shows in-kernel path-prefix filtering for fd ops is the
only remaining meaningful reduction (that is the one thing `bpf_d_path`
uniquely enables without open-state tracking).

## 5. Fallback-Tier Caveat And The Socket/Pipe Decision (2026-08-25)

The non-CO-RE fallback tracer (`file_ops_tracepoint.bpf.c`) has **no
`is_regular_fd` filter**, so BTF-less hosts emit socket/pipe/tty fd ops that
the CO-RE tier drops. The 2026-08-25 smoke test confirmed the CO-RE object was
the live tier on spk16, so this does not explain the overnight loss.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c §t_read_ent/§t_close (no regular-file gate) -->

Human decision recorded 2026-08-25 (see
[[wiki/work/optimize-fileops-poller/brief]] §Open Questions):

- **Non-regular-file fd rows (`socket:[N]`, `pipe:[N]`, `anon_inode:[N]`,
  ttys) are permanently dropped from the File stream** — the already-deployed
  CO-RE filter is ratified as the documented stream contract.
- **Recorded fidelity gap:** pipe/`anon_inode` I/O is not covered by
  NetworkSensor, so it becomes invisible; logged in the fidelity-gap backlog
  in [[wiki/work/optimize-fileops-poller/design]] as a candidate future op
  class.
- **Fallback tier stays as-is:** BTF-less hosts keep emitting these rows; the
  per-tier stream-content difference is documented rather than patched.

## 6. What Would Change This Analysis

- If the 60s counter logs show userspace consumed/s **well above** ~100/s
  while ring_fail still grows, the DB-query ceiling estimate is wrong and the
  bottleneck sits elsewhere on the poller thread (readlink misses,
  allocations, Esper) — the fop-08 queue half still applies, the cache half
  changes shape.
- If a `WINTAP_SKIP_PROCESS_RESOLVE=true` field experiment does **not**
  collapse the ring_fail growth rate, the resolver query is not the dominant
  term and fop-08 should be re-scoped before implementation.
- Both checks are summary-statistic requests (counter-log lines and
  before/after rates only), compatible with the no-raw-data constraint.
