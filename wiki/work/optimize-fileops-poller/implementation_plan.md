---
title: "Implementation Plan: Optimize FileOps Poller Event Volume"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: llm-agent
status: draft
source_paths: wiki/work/optimize-fileops-poller/implementation_plan.md
tags: [feature-work, file-events, ebpf, linux-sensor, implementation-plan]
---

# Implementation Plan: Optimize FileOps Poller Event Volume

Branch: `grantj-rhel8-testing` in `../wintap` (code) and in
`Wintap-Analytics` (wiki + validation). Units are `fop-nn`. Sequenced so
measurement lands first and decision-gated work lands last. Design rationale:
[[wiki/work/optimize-fileops-poller/design]].

## Scope

Kernel tracers (`file_ops_tracer.bpf.c` CO-RE tier, `file_ops_tracepoint.bpf.c`
fallback), `FileOpsSensor.cs`, minor `LibBpf.cs`/`BaseEbpfSensor.cs` touches,
Makefile tier move, and a new validation scenario in `Wintap-Analytics`.
No aggregation, no new syscall coverage, no Windows changes.

## Steps

### fop-01 — Counters + baseline (measure first)

- Kernel (both variants): percpu array map `fileops_stats` counting, per op
  class: emitted, dropped-by-filter (one slot per filter as they land), and
  ringbuf reserve failures (overflow drops).
- Userspace: extend the `CountPseudoDrop`/`MaybeLogPseudoDrops` pattern to
  count all drop reasons (no-path, data-root, .etl, parquet) plus emitted,
  per op class; read and log the kernel map on the same 60s cadence.
- Capture a **baseline** on the RHEL8 host with
  `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` plus the
  new counter logs, under (a) idle, (b) the deterministic file workload,
  (c) a network-busy period. Record in verification.md. This quantifies the
  socket/pipe share and is the evidence base for every later slice.

### fop-02 — Userspace dead-work removal (U1, U2, U3)

- Remove per-event `GenPidHash`; record the DirectParquetSink decision.
- Memoize `/proc` fallback resolutions into `_fdToPath`; skip fallback for
  close ops; replace `FileInfo` with a direct readlink.
- Zero-alloc decode: read scalars from the native pointer first, drop early,
  materialize strings only for emitted events.

### fop-03 — Kernel self-PID filter (K1, both variants)

- 1-entry array map; userspace writes `StateManager.WintapPID` after load
  (needs `bpf_map_update_elem` P/Invoke if not present in `LibBpf.cs`).
- Early-return in all 9 programs; count drops in `fileops_stats`.

### fop-04 — Wakeup batching (K3, both variants)

- `BPF_RB_NO_WAKEUP` submits + forced wakeup every Nth event or on
  `bpf_ringbuf_query` occupancy threshold; verify shutdown still drains
  within the 2s `PollingThread.Join` budget.

### fop-05 — CO-RE regular-file filter (K2) — gated on socket/pipe decision

- Move `file_ops_tracer.bpf.o` from `TRACEPOINT_OBJS` to `CORE_OBJS` in the
  Makefile; include vmlinux.h; keep `file_ops_tracepoint.bpf.c` unchanged as
  fallback.
- fd→`f_inode` CO-RE traversal with `max_fds` bounds check; emit fd ops only
  for `S_ISREG`; drop `PROC_SUPER_MAGIC`/`SYSFS_MAGIC`/devtmpfs by
  `s_magic`. Count each drop class.
- **Spike first** on the target RHEL8 kernel: minimal program proving the
  verifier accepts the traversal (record in a `spike.md` if non-trivial).
- Keep userspace pseudo-path/data-root filters (fallback tier + defense in
  depth).

### fop-06 — Small fd-op records (K4)

- Compact record for read/write/close/mmap (second ringbuf or tagged
  variable-size records — dev's choice, record rationale); matching decode;
  both variants if the format is shared, otherwise CO-RE tier only with
  fallback keeping the old format (decode must handle both).

### fop-07 — fd-cache eviction + kernel timestamps (U4, U5)

- Evict `_fdToPath[pid]` on process exit (ExitSensor hook or periodic
  liveness sweep — dev's choice, record rationale).
- Convert `TimestampNs` (monotonic) to wallclock via a once-computed offset;
  use it for `WintapMessage` EventTime.

## Files Likely To Change

- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c`
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile`
- `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`
- `../wintap/wintap/platform/linux/sensor/ebpf/helpers/LibBpf.cs`
- `../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs` (only if
  poll timeout/knobs need touching for fop-04)
- `Wintap-Analytics/validation/` — new file-ops differential + burst scenario
  (see Tests below)

## Tests To Add Or Update

Required per slice; a slice is not done until its tests pass and results are
recorded in [[wiki/work/optimize-fileops-poller/verification]].

1. **Builds (every slice):**
   - `cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make`
     — both tiers build; preflight passes on the RHEL8 host (clang, bpftool,
     BTF detected).
   - `cd ../wintap && dotnet build wintap/Lintap.csproj` — 0 errors.
2. **Deterministic file workload + A/B differential (the no-loss proof;
   built in fop-01, run every slice after):** a script that, in a temp dir
   outside the data root: creates N files, writes, reads, mmaps (e.g. via
   `python -c`), closes, deletes; also touches a `/proc` and `/dev` path and
   generates socket traffic (e.g. `curl` localhost) for the negative cases.
   Run baseline build and slice build against it; extract File events from
   the run's parquet/DuckDB output; assert the slice stream is equal-or-
   superset on regular-file (path, op class, PID) tuples, and that the only
   removals are the enumerated allowed classes. Fold into
   `Wintap-Analytics/validation/` following the process-creation harness
   pattern (uv + pytest where practical).
3. **Counter reconciliation (fop-01+):** kernel emitted ≈ userspace consumed
   + ringbuf drops over a run; assert in the differential harness.
4. **Burst/storm test (fop-06 acceptance, baseline in fop-01):** e.g.
   `find /usr -type f -exec cat {} + > /dev/null` or a tight
   create/write/delete loop; compare ringbuf overflow-drop counters
   before/after fop-06 — must decrease.
5. **fd-cache boundedness (fop-07):** process-churn workload (spawn/exit
   thousands of short-lived file-touching processes); assert `_fdToPath`
   entry count returns to baseline (expose count via the 60s counter log).
6. **Fallback-tier test (fop-05+, every subsequent slice):** force the
   fallback object (temporarily remove/rename `file_ops_tracer.bpf.o` or add
   a config override) and re-run the smoke workload — sensor loads, events
   flow, userspace filters still applied.
7. **Timestamp sanity (fop-07):** under an artificially backlogged poller
   (pause/resume the process with SIGSTOP during the workload), event times
   must track syscall time, not dequeue time.
8. **Unit-style decode tests (fop-02, fop-06):** decode of both record
   formats from crafted byte buffers, including truncated/garbage input —
   via the `../wintap/diagnostics/` console-project pattern (no test project
   exists in the repo) or in-harness; dev's choice, record location.
9. **Field measurement (fop-02, fop-03, fop-05 at minimum):**
   `collect-lintap-diagnostics.sh` on the RHEL8 field host; record total
   Lintap CPUs (perf stat) and `FileOps-Poller` thread share vs. the fop-01
   baseline.

## Migration Or Compatibility Notes

- `.bpf.o` artifacts are committed alongside sources (existing convention) —
  rebuild and commit both objects when their `.c` changes; the CO-RE object
  must be built on a BTF host.
- Hosts without BTF silently keep today's behavior via the fallback object —
  document in the component page at closeout which filters apply per tier.
- DirectParquetSink File rows lose the (broken) per-event PidHash in fop-02;
  confirm no consumer reads it before removal (flagged in design §Risks).
- Config surface: any new knobs (wakeup batch size, fallback force flag)
  go through `ConfigManager` like existing flags; document defaults.

## Rollback Plan

- Each slice is a separate commit on `grantj-rhel8-testing`; revert the
  commit and rebuild both `.bpf.o` objects to roll back.
- fop-05 has a built-in runtime rollback: force the fallback object.
- Keep the fop-01 counters in any rollback — they are diagnostic, not
  behavioral.

## Done Checklist

- [ ] fop-01 counters landed; baseline (idle / workload / network-busy)
      recorded in verification.md, including the measured socket/pipe share.
- [ ] fop-02 dead-work removal landed; A/B differential clean; allocation/CPU
      delta recorded.
- [x] fop-01/fop-02 code slice built locally: kernel/user counters, userspace
      dead-work removal, and differential harness are implemented. Full field
      baseline and deployed A/B run remain pending before these slices are
      accepted.
- [x] Expanded no-loss reduction slice landed in the working branch and was
      deployed to the RHEL8 field host: self-PID filtering, wakeup batching,
      CO-RE regular-file fd filtering, compact tagged records, 16 MiB ring
      buffer, and kernel pseudo-path filtering are all active in the deployed
      build. Full acceptance remains pending because the overnight run still
      showed sustained ring-buffer loss.
- [ ] fop-03 self-PID filter landed in both variants; self rows absent from
      stream; counter shows kernel-side drops.
- [ ] fop-04 wakeup batching landed; context-switch/CPU delta recorded;
      shutdown drain verified.
- [x] Socket/pipe row decision recorded in brief.md (2026-08-25 human
      sign-off: drop ratified; pipe/anon_inode visibility gap recorded in the
      design fidelity-gap backlog; fallback tier left unchanged).
- [ ] fop-05 CO-RE filter landed (spike accepted by RHEL8 verifier); Makefile
      tier move done; fallback path exercised and unchanged.
- [ ] fop-06 small records landed; burst drop counters reduced vs. baseline.
- [ ] fop-07 fd-cache eviction + kernel timestamps landed; churn and
      timestamp tests pass.
- [ ] Field measurement vs. fop-01 baseline shows the CPU win; recorded.
- [x] Deep-analysis handoff completed (2026-08-25): overnight counters
      interpreted, next no-loss reduction ranked, and the follow-on slice
      selected from evidence rather than intuition (fop-08 front-runner) —
      see [[wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25]].
- [x] fop-08/fop-09 code slice built locally: `ProcessResolver` now maintains
      an in-memory active-process cache for File-event pid-hash lookup,
      `FileOpsSensor` now decouples ring-buffer decode/filter from
      resolve/Esper with a bounded in-process queue (`drop_newest`, depth /
      high-water / drop counters logged every ~60s), and `EventChannel.Send`
      now uses startup-cached config flags instead of per-event lookups. Full
      acceptance remains pending the differential rerun and field-host
      measurement/counter reconciliation.
- [x] fop-10 local code slice built: `FileOpsSensor` now logs bounded summary
      measurements in the 60s `FileOps counters` line for top-N emitted
      process-name buckets, top-N emitted path-prefix buckets, and the
      short-window same-`(pid,path)` open duplicate ratio. Deployed and field-
      host measurement are now recorded in verification.
- [x] Milestone — fop-11 review gate reached: `fop-10` now provides both the
      attribution data and the duplicate-open evidence needed to write a
      concrete `fop-11` proposal for design review; see
      [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]].
- [ ] Closeout: promote durable facts — new FileOps sensor component page
      (pipeline stages, per-tier filters, counters, config), file-events
      event_type update if stream content changed, fidelity-gap backlog
      pointer — and update `wiki/log.md`.

## Phase 2 — Deep Analysis (2026-08-25)

The original-scope implementation reached its current deployed state —
implemented with opencode gpt-5.5 and gpt-5.4. The feature continues in a
deep-analysis phase rather than being closed or forked into a new feature.
Analysis artifact:
[[wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25]].

The analysis concluded the sustained overnight ring-buffer loss is a
userspace consumer-throughput ceiling (per-event DuckDB resolution under the
global `_dbLock` plus a synchronous Esper send on the single poller thread),
not kernel emission volume. Phase-2 slices, ranked by the analysis and
**approved by human sign-off 2026-08-25** with the sequence fop-08 (+fop-09)
→ fop-10 → fop-11 go/no-go (fop-11 remains gated on its own conditions;
fop-07 remains open from phase 1):

- [ ] fop-08 — decouple the poller from per-event resolution: bounded
      in-process queue between the ring-buffer callback and resolve/Esper,
      plus an in-memory pid→pid_hash current-process cache that eliminates
      the per-event DuckDB query under `_dbLock`.
- [ ] fop-09 — hoist the five per-event `ConfigManager.GetValue` calls in
      `EventChannel.Send` into cached fields.
- [x] fop-10 — Q2 measurement slice: top-N per-comm / per-path-prefix
      aggregate emit counters in the 60s `FileOps counters` log (summary
      statistics only; no raw event data). Extended 2026-08-25 per human
      direction: also measure the **open/openat duplicate ratio** — repeats of
      the same (pid, path) open within a short window — to quantify the
      redundancy hypothesis behind fop-11. Local code/build, deployment, and
      field-host collection are complete; review data is recorded in
      verification.
- [ ] fop-11 — short-interval aggregation (APPROVED with conditions,
      2026-08-25): gates (a)/(b) are met — fop-10 measured 52.7–83.7%
      duplicate-open ratios and the human accepted the information tradeoff,
      amending the 2026-08-24 direction to: **aggregation to the
      (pid, path, op) level with grouped totals (bytes etc.) and min/max
      timestamps over short intervals is acceptable**, for all op classes,
      not just open/openat (open-first remains sensible sequencing, not a
      boundary). Emit-first semantics stand. Hard conditions from the
      designer review recorded in
      [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]]
      §Designer Review: absolute-path identity (see fop-12, a precondition),
      and summary-record identity stamped at first occurrence. Layer choice
      per that review: userspace pre-enqueue dedup first (reusing the fop-10
      measurement dictionary; no verifier spike needed), kernel promotion
      later only if ring pressure or poller CPU returns. Revised differential
      contract: op-scoped distinct-tuple equality + count conservation +
      byte-total conservation, decidable only on drop-free runs.
- [ ] fop-12 — absolute-path ground truth (precondition for fop-11 keys,
      human-directed 2026-08-25): resolve relative/`openat` paths to absolute
      at open time so File telemetry records accurate ground truth and
      aggregation keys cannot conflate distinct files. Recommended mechanism:
      readlink `/proc/<pid>/fd/<fd>` at open-exit for non-absolute paths
      (pre-enqueue, while the producer is alive — the fd handle yields the
      absolute path directly); `bpf_d_path` is not available on RHEL8 4.18
      tracepoints. Also improves fd-cache attribution for subsequent
      read/write events. Dev chooses the exact resolution point; record
      rationale.

### Phase-2 future tasks (not slices yet)

- [ ] Mmap as a first-class File activity type (approved 2026-08-25 as a
      future feature enhancement, deliberately NOT in fop-12/fop-11): stop
      collapsing op 5 → `Read` at decode; introduce a distinct `Mmap`
      ActivityType so code-loading is distinguishable from data reads in the
      recorded stream (`file.epl` groups by activityType, so today
      mmap+read of the same file merge into one "Read" row, and mmap's
      mapped-length bytes pollute read byte sums). Stream-content change:
      ship with a downstream note for Wintappy models and analytics keying
      on activityType, and update the differential comparator's op mapping
      in the same slice.

- [ ] OSS sensor survey (requested 2026-08-25; deliberately deferred by human
      direction later that day — "wait a bit longer, improvements still
      coming"): review how other open-source eBPF/host sensors handle
      file-event volume and ring-buffer drop pressure — candidates:
      Falco/Sysdig (drop accounting, consumer design), Cilium Tetragon
      (in-kernel filtering/rate-limiting policies), Aqua Tracee, Elastic
      ebpf/Agent, Sysmon for Linux, osquery. Deliverable: a wiki concept page
      comparing their kernel-side reduction, aggregation, and userspace
      consumption architectures against Lintap's, with adoptable patterns
      ranked. Natural trigger: after fop-11/fop-12 land and are measured,
      when comparing aggregation designs answers concrete questions.
