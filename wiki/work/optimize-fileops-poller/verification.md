---
title: "Verification: Optimize FileOps Poller Event Volume"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: llm-agent
status: draft
source_paths: wiki/work/optimize-fileops-poller/verification.md
tags: [feature-work, file-events, ebpf, linux-sensor, verification]
---

# Verification: Optimize FileOps Poller Event Volume

Record commands and results per slice (fop-nn). The A/B differential is the
standing no-loss gate: it must be re-run and recorded for every slice after
fop-01. Baselines captured in fop-01 are the comparison point for all CPU,
drop-rate, and volume claims.

## Test Commands

Standing commands (fill in results per slice below):

```bash
# Builds
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj

# Field measurement (RHEL8 host)
bash extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh

# Differential + workload harness (created in fop-01; exact invocation TBD)
# cd validation/<file-ops-scenario> && ...
```

## Baseline (fop-01) — TO BE CAPTURED

- [ ] Idle: total Lintap CPUs, FileOps-Poller thread share, counter snapshot.
- [ ] Deterministic file workload: emitted/dropped per op class and stage.
- [ ] Network-busy period: socket/pipe share of fd-op volume (feeds the
      fop-05 human decision).
- [ ] Ring-buffer overflow drops under the burst workload.
- [ ] `_fdToPath` entry count under process churn.

## Manual Checks

- [ ] Fallback object force-load smoke run (fop-05 onward).
- [ ] Shutdown drains within the 2s Join budget with wakeup batching (fop-04).
- [ ] DirectParquetSink File rows inspected before/after GenPidHash removal
      (fop-02).

## Results

(append per slice: `## fop-nn — <date>` with commands, output summaries, and
differential verdict)

## fop-01/fop-02 Code Slice — 2026-08-24

Implemented the first code slice for counters and userspace dead-work removal.
This is not yet a full field acceptance: the RHEL8 live A/B run and counter
baseline still need to be captured after deploying the build.

Pre-update baseline captured immediately before deploying this code slice:

- Diagnostics bundle: `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260824T190007Z`.
- Running Lintap PID `2066843`, elapsed `54346s` (~15.1h).
- `perf stat`: `2.804` CPUs over ten seconds; `ps` reported `222%` cumulative CPU.
- Fork rate: `12` process creations over ten seconds (~1/sec).
- Hot thread snapshot: `FileOps-Poller` sampled `18.8-25.4%` in top output, but had accumulated `686:42` CPU time, far above other pollers.
- Event store: `process=49,470` rows, `open_rows=1,377`, `process_retention_telemetry=42,752` aggregate rows, copied DB size `77.5 MiB`.
- No `FileOps counters` / `fileops_stats` / `self_drop` / `fallback_miss` strings were present in that diagnostics bundle, as expected for the old build.

Code changes in `../wintap`:

- Added a `fileops_stats` BPF array map to both `file_ops_tracer.bpf.c` and
  `file_ops_tracepoint.bpf.c`.
- Kernel counters now track emitted events and ring-buffer reserve failures by
  op class (`open`, `read`, `write`, `close`, `mmap`, `unlink`).
- Added `bpf_map_lookup_elem` P/Invoke to `LibBpf.cs` so userspace can read the
  FileOps stats map.
- Extended `FileOpsSensor.cs` userspace counters for consumed/emitted events,
  no-path drops, pseudo-path drops, data-root drops, `.etl` drops, parquet
  drops, and `/proc/<pid>/fd` fallback hits/misses by op class.
- Added periodic `FileOps counters` log output on the existing ~60s cadence.
- Removed the dead per-event `GenPidHash` call in FileOps. `EventChannel.Send`
  resolves/overwrites non-Process event PidHash on the Esper path; the prior
  DirectParquetSink value was event-time-derived and not process-identity-safe.
- Changed fd fallback behavior: successful `/proc/<pid>/fd/<fd>` readlink
  results are memoized into `_fdToPath`; close events use only the fd cache and
  do not perform a guaranteed-late `/proc` fallback.
- Replaced the per-event full `Marshal.PtrToStructure<FileEvent>` decode with
  scalar reads first and string materialization only after early drop checks.

Validation harness added in `Wintap-Analytics`:

- `validation/fileops-differential/fileops_workload.py` creates deterministic
  regular-file activity plus negative noise (`/proc`, `/dev`, socketpair).
- `validation/fileops-differential/compare_fileops.py` compares baseline and
  candidate `raw_process_file` parquet outputs and fails if any regular-file
  `(pid, normalized_path, op)` tuple is missing from the candidate.

Commands run:

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
cd Wintap-Analytics && python3 -m py_compile validation/fileops-differential/compare_fileops.py validation/fileops-differential/fileops_workload.py
cd Wintap-Analytics && python3 validation/fileops-differential/fileops_workload.py --work-dir "$tmp/work" --manifest "$tmp/manifest.json" --files 2 --rounds 1
cd Wintap-Analytics && python3 validation/fileops-differential/compare_fileops.py --baseline "$tmp/baseline.parquet" --candidate "$tmp/candidate.parquet" --json-out "$tmp/summary.json"
cd Wintap-Analytics && python3 validation/fileops-differential/compare_fileops.py --baseline "$tmp/baseline.parquet" --candidate "$tmp/candidate.parquet"
```

Results:

- eBPF tracer build passed on the RHEL8 host (`make clean && make`), compiling
  both tracepoint fallback objects and CO-RE objects.
- `dotnet build wintap/Lintap.csproj` passed with existing warnings and `0`
  errors.
- Python harness syntax check passed.
- Workload smoke run produced a manifest successfully.
- Comparator smoke test with identical synthetic parquet passed and reported
  `missing_regular_tuples=0` while classifying socket/proc rows as noise.
- Comparator negative smoke test with one omitted regular-file tuple exited
  non-zero and reported the missing tuple in JSON.

Pending field validation:

- Deploy this build, run baseline/candidate A/B captures with the deterministic
  workload, and archive the comparator JSON.
- Capture the new `FileOps counters` log lines during idle, file workload, and
  network-busy periods.
- Check whether userspace no-path/fallback-miss counters confirm the expected
  socket/pipe/non-file-fd share.

### CO-RE/compact-record follow-up (2026-08-24)

After the first deployment, `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260824T212523Z` showed the new FileOps objects failed verifier on `t_unlinkat` before counters started. The verifier rejected using the saved-buffer helper with a raw user pointer (`R8 invalid mem access 'inv'`) in the unlink path. This meant FileOps did not load in that run, so the extremely low CPU sample was not a valid FileOps optimization result.

Fix applied:

- Split pathname event emission into two helpers in both tracer variants:
  `emit_file_event_saved()` for already-copied kernel/local buffers from
  open/openat state, and `emit_file_event_user()` for raw syscall user pointers
  from unlink/unlinkat using `bpf_probe_read_user_str()`.
- Completed the intended compact record format: fd ops emit a small tagged
  record; pathname ops emit a full tagged path record.
- Moved `file_ops_tracer.bpf.o` into the CO-RE Makefile tier so the fd regular-file filter can use `vmlinux.h` and BTF, while `file_ops_tracepoint.bpf.o` remains the fallback tier.

Validation after the fix:

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
```

Results: tracer build passed, including CO-RE `file_ops_tracer.bpf.o`; Lintap build passed with existing warnings and `0` errors.

## Known Gaps

- Full live A/B differential against a deployed baseline and fop-02 build is
  still pending.
- fop-01 field baseline with the new counters is pending deployment.
- Counter reconciliation is approximate in this first slice because kernel
  counters are cumulative while userspace counters are logged/reset per 60s
  interval.

## Follow-Ups

- Fidelity-gap backlog (rename, pread/pwrite, io_uring, failed opens) —
  see design §Fidelity-Gap Backlog; candidate next feature after closeout.
- fentry/`bpf_d_path` migration if this feature's results warrant it
  (design §Alternatives).

## Expanded Deployment Summary — 2026-08-25

The feature moved beyond the original fop-01/fop-02 handoff during live RHEL8
iteration. In addition to the first counters/dead-work slice, the current
branch and deployed host now include:

- kernel self-PID filtering and `self_drop_total`
- CO-RE regular-file fd filtering for `read`/`write`/`close`/`mmap`
- `nonregular_drop_total`
- compact tagged fd-vs-path records
- wakeup batching plus `force_wakeup_total`
- `FILEOPS_RINGBUF_SIZE = 16 MiB`
- kernel pseudo-path filtering for `open`/`openat`/`unlink`/`unlinkat`
- `pseudo_drop_total`
- verifier-safe unlink pathname emission split into saved-buffer vs user-pointer helpers
- diagnostics-bundle capture of deployed hashes and live `bpftool` state

Validation/build commands rerun during that expansion:

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
bash -n extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh
```

Results:

- Repeated tracer rebuilds passed after each FileOps tracer change.
- `dotnet build wintap/Lintap.csproj` repeatedly passed with existing warnings
  and `0` errors.
- Diagnostics script syntax validation passed.

## Deployed Smoke Test — 2026-08-25

Diagnostics bundle:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T033307Z`

Deployment proof:

- `manifest.txt` recorded `lintap_pid=2805261` and `install_root=/usr/lib/lintap`.
- `journal/lintap-file-log-fileops.txt` showed:
  - `FileOps loaded eBPF object: ./tracers/file_ops_tracer.bpf.o`
  - `FileOps sensor started`
  - `FileOps kernel self PID filter set to 2805261`
- Installed object hashes:
  - `Lintap.dll`: `7b7b077ec6bc471592cfd62739fc720c458c25421b62c85a34b7b627b8d187ee`
  - `file_ops_tracer.bpf.o`: `7b7f058bb4d67336a44a43404be667c41f7c7a9dad53b9c34aed3cd57b368099`
  - `file_ops_tracepoint.bpf.o`: `3a0fe4c9772f15153a3bfbcb4f72838a30f7bb76fef6b7f3e71a1db3e80222e9`

Live-kernel proof from `bpftool`:

- FileOps tracepoints attached: `t_openat_ent`, `t_open_ent`, `t_open_exit`,
  `trace_openat`, `t_read_ent`, `t_write_ent`, `t_close`, `t_mmap`,
  `t_unlinkat`, `t_unlink`.
- FileOps maps present: `openat_state_map`, `fileops_stats`,
  `fileops_filter_pids`.
- FileOps ring buffer size confirmed live at `16777216` bytes (16 MiB).

First-minute counter snapshot:

- `ring_fail_total=0` across all FileOps op classes.
- `open pseudo_drop_total=50348` in the first minute.
- `read nonregular_drop_total=104515` in the first minute.
- `close nonregular_drop_total=207460` in the first minute.
- `close:fallback_miss=0` remained true.
- `force_wakeup_total=80470` confirmed batched wakeups were active.

Interpretation:

- The redeployed build was definitely live.
- The kernel self-filter, kernel pseudo-path filter, CO-RE non-regular-fd
  filter, compact records, wakeup batching, and 16 MiB ring buffer were all
  active.
- The startup/smoke picture was materially better than the original state:
  large classes of useless events were now being dropped before userspace, and
  the first minute showed no ring-buffer loss.

## Overnight Field Run — 2026-08-25

Diagnostics bundle:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T142601Z`

Deployed-build consistency:

- Same install root as the smoke test: `/usr/lib/lintap`.
- Same `Lintap.dll` hash as the smoke test.
- Same `file_ops_tracer.bpf.o` and `file_ops_tracepoint.bpf.o` hashes as the
  smoke test.

Runtime CPU snapshot:

- `ps` showed `Lintap` at about `220%` CPU.
- `perf stat` over 10 seconds showed `2.818 CPUs utilized`.
- `FileOps-Poller` remained the dominant named hot thread:
  - `81.4%` cumulative in `ps -L`
  - `94.71%` average in `pidstat`

Representative overnight FileOps counters:

- Early in the window (`4:06:53 AM`):
  - `open ring_fail_total=8991202`
  - `read ring_fail_total=7121895`
  - `close ring_fail_total=2547197`
  - `mmap ring_fail_total=2303884`
  - `write ring_fail_total=31360`
  - `open pseudo_drop_total=22959589`
- Later in the window (`6:38:54 AM`):
  - `open ring_fail_total=11999369`
  - `read ring_fail_total=9342135`
  - `close ring_fail_total=3392084`
  - `mmap ring_fail_total=3068775`
  - `write ring_fail_total=292744`
  - `open pseudo_drop_total=30345515`
  - `read nonregular_drop_total=69576912`
  - `close nonregular_drop_total=87966528`

Observed trend over the overnight interval:

- The new kernel-side filters were doing large amounts of work.
- The 16 MiB ring buffer and compact records improved the early burst case, but
  sustained-loss behavior remained: ring-buffer reserve failures continued to
  climb materially for `open`, `read`, `close`, and `mmap`.
- Userspace still showed some `read`/`write` `no_path` and `fallback_miss`
  counts, but these are secondary relative to the kernel-side ring-fail totals.
- `close:fallback_miss=0` remained true, confirming that the explicit close
  fallback removal held under long-running conditions.

Current interpretation:

- Compared with the original pre-feature state, this feature has made a large
  practical improvement:
  - there is now strong per-stage observability,
  - Wintap's own PID is filtered in-kernel,
  - huge non-regular-fd volume is dropped before submit,
  - huge pseudo-path open volume is dropped before userspace,
  - close-path dead work is gone,
  - the deployed build can be fingerprinted and verified from diagnostics.
- However, the overnight data also shows that the system is not yet at a
  no-loss steady state on this host. The remaining bottleneck is still the
  sustained volume of regular-file `open`/`read`/`close`/`mmap` traffic that
  survives those earlier filters.

## Handoff Summary For Deep Analysis

What is complete and grounded:

- fop-01 measurement/counter scaffolding exists in kernel and userspace.
- fop-02 userspace dead-work removal exists and is deployed.
- fop-03 self-PID filter exists and is deployed.
- fop-04 wakeup batching exists and is deployed.
- Much of fop-05/fop-06 effectively landed in code and deployment:
  CO-RE regular-file fd filtering, compact tagged records, CO-RE tier move,
  larger ring buffer, and kernel pseudo-path filtering.
- The differential harness exists and works as a standing no-loss gate for
  regular-file tuples, but a full baseline-vs-current live capture pair has not
  yet been archived and compared end-to-end.

What remains open for the next deep-analysis task:

- Determine the next highest-yield no-loss reduction after the currently landed
  filters, using the overnight counter data as the evidence base.
- Quantify which surviving regular-file classes dominate the remaining
  `open`/`read`/`close`/`mmap` ring-fail totals.
- Decide whether the next slice should focus on additional pre-submit filtering,
  path/state reuse, or a larger architectural step such as an fentry/
  `bpf_d_path`-style redesign.
- Preserve the no-loss contract for regular-file telemetry while avoiding a
  premature jump to aggregation/sampling.

Recommended starting artifacts for that next analysis pass:

- `wiki/work/optimize-fileops-poller/brief.md`
- `wiki/work/optimize-fileops-poller/design.md`
- `wiki/work/optimize-fileops-poller/implementation_plan.md`
- `wiki/work/optimize-fileops-poller/dev_handoff.md`
- `wiki/work/optimize-fileops-poller/verification.md`
- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T033307Z`
- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T142601Z`

## Phase 2 Deep Analysis — 2026-08-25

The deep-analysis pass was performed from recorded summary statistics only:
the raw runtime diagnostics bundles are not readable in this environment by
security constraint, so the evidence base is the counter summaries above plus
read-only source review of `../wintap`.

Key numbers (deltas over the ~9,121s overnight window between the recorded
4:06:53 AM and 6:38:54 AM counter snapshots):

- `ring_fail_total` rates: `open` ≈ 330/s, `read` ≈ 243/s, `close` ≈ 93/s,
  `mmap` ≈ 84/s, `write` ≈ 29/s — ≈ 778/s total sustained loss.
- `open pseudo_drop_total` ≈ 810/s dropped in-kernel before the ring.

Conclusion: the loss is a steady-state userspace consumer shortfall, not a
burst problem. Every surviving event pays a synchronous DuckDB query under
the process-global `_dbLock` plus a synchronous Esper send on the single
poller thread; the 2026-08-24 diagnostic's ~0.012–0.025s per process lookup
implies a consumption ceiling of roughly 40–80 events/s. The 16 MiB ring
buffer (~300k compact-record capacity) absorbs the first minutes — hence the
clean smoke test — then fills and stays saturated overnight.

Next-slice ranking and the full reasoning are recorded in
[[wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25]] (fop-08
front-runner: decouple the poller from per-event resolution plus an
in-memory pid→pid_hash cache).

The socket/pipe stream-content question was decided 2026-08-25 (human
sign-off): the drop of non-regular-file fd rows is ratified; the resulting
pipe/anon_inode visibility gap is recorded in the design fidelity-gap
backlog; the BTF-less fallback tier is left unchanged and the tier content
difference is documented rather than patched.

## fop-08/fop-09 Local Code Slice — 2026-08-25

Implemented the approved phase-2 consumer-ceiling slice in `../wintap`.

Code changes:

- `ProcessResolver` now maintains an in-memory active-process cache keyed by
  PID and populated on process registration. The cache is evicted on stop,
  stale-open reconciliation, and retention pruning, and is updated if the
  resolver repairs a live PID hash.
- `EventChannel.Send` now consults that current-process cache for File events
  before falling back to the per-event DuckDB lookup under `_dbLock`.
- `EventChannel.Send` now hoists the per-event config/env gates into startup-
  cached fields for `WINTAP_ENABLE_DIRECT_PARQUET`,
  `WINTAP_SKIP_PROCESS_RESOLVE`, `WINTAP_SKIP_PARENT_PROCESS_RESOLVE`,
  `WINTAP_SKIP_PROCESS_REGISTER`, and `WINTAP_SKIP_ESPER_SEND`.
- `FileOpsSensor` now decodes/filters on the poller thread and enqueues into a
  bounded in-process queue drained by a dedicated sender thread that performs
  `EventChannel.Send`.
- Queue observability added to the existing 60s `FileOps counters` log:
  current depth, high-water mark, drop count, configured capacity, and fixed
  `drop_newest` policy. File-event process-cache hit/miss counters are also
  surfaced in that log.
- New queue capacity knob: `WINTAP_FILEOPS_MAX_QUEUE_EVENTS` (default
  `131072`).

Commands run:

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
cd ../wintap && dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests
```

Results:

- eBPF tracer rebuild passed.
- `dotnet build wintap/Lintap.csproj` passed with existing warnings and `0`
  errors.
- Targeted resolver tests passed: `4 passed`.

Known limitations / follow-up for acceptance:

- The standing no-loss differential harness was not rerun in this local slice.
- No field-host deployment or overnight measurement has been performed yet, so
  there is not yet evidence that `ring_fail_total` growth collapsed versus the
  ~778/s overnight baseline.
- Shutdown drain budget is now effectively revised for FileOps from the prior
  single 2s poller join to a two-stage stop path: up to 2s for the poller join
  in `BaseEbpfSensor.Stop()` plus up to 2s for the FileOps sender-thread join
  during `OnStopping()`. This needs field confirmation under backlog.

## Field-Host Non-Root Smoke Workload Session — 2026-08-25

Context: after deployment, this environment was confirmed to be the deployed
field host itself, but without root access. That means the existing parquet-
based `devtools/file_capture_smoke_test.py` cannot read the deployed default
data root under `/var/log/lintap` and fails at path discovery with
`PermissionError` before it can validate output. For this host/user context,
the reliable non-root stimulus path is the deterministic workload generator,
with root-side diagnostics collection used later to observe sensor response.

Diagnostics collector improvement:

- `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` now copies
  `/tmp/fileops-phase2-smoke` into the diagnostics bundle when present, so the
  next root-run collection captures the exact stimulus session timestamps and
  workload manifests.

Workload session run locally:

- Session directory: `/tmp/fileops-phase2-smoke/session-20260825T165200Z`
- Host: `spk16.llnl.gov`
- Session window: `2026-08-25T16:52:00Z` to `2026-08-25T16:59:22Z`
- Pattern: 5 repeated deterministic FileOps workload runs, spaced across the
  session.
- Per run parameters: `--files 24 --rounds 4`
- Per-run status: all 5 runs exited `0`

Representative commands:

```bash
python3 validation/fileops-differential/fileops_workload.py \
  --work-dir "/tmp/fileops-phase2-smoke/session-20260825T165200Z/run-1/workload" \
  --manifest "/tmp/fileops-phase2-smoke/session-20260825T165200Z/run-1/workload-manifest.json" \
  --files 24 \
  --rounds 4

python3 devtools/file_capture_smoke_test.py --timeout 90 --poll-interval 5 \
  --file-dir "/tmp/fileops-phase2-smoke/trial/file-dir"
```

Results:

- Deterministic workload generation succeeded for all 5 runs.
- The parquet-based smoke validator is not usable as this non-root user on the
  deployed host because `/var/log/lintap` is permission-restricted; the script
  currently raises `PermissionError` while probing the default data root.
- The next root-run diagnostics bundle should include the workload session
  under `runtime/fileops-phase2-smoke/`, allowing direct correlation between
  the stimulus window above and the `FileOps counters` / thread-CPU evidence.

## Root-Run Diagnostics Bundle Review — 2026-08-25

Bundle reviewed:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T172341Z`

Deployment/runtime proof:

- `manifest.txt` shows `lintap_pid=3202938`, `install_root=/usr/lib/lintap`,
  and a root-run collection on the deployed host.
- The copied smoke artifact session is present under
  `runtime/fileops-phase2-smoke/session-20260825T165200Z`, matching the
  non-root workload session recorded above.

Key findings:

1. **Kernel ring-buffer loss collapsed to zero in this capture.**
   Every recorded `FileOps counters` line in the bundle shows
   `ring_fail_total=0` for `open`, `read`, `write`, `close`, `mmap`, and
   `unlink`.
2. **The bottleneck moved from the poller/ring to the new userspace sender
   queue.**
   - Early intervals looked healthy: at `9:35:01 AM`, queue
     `depth=4170,high_water=48782,drops=0`.
   - By `9:52:39 AM`, the queue was effectively full:
     `depth=130479,high_water=131072,drops=21567`.
   - Subsequent one-minute intervals continued to show queue saturation and
     non-zero drop counts, including:
     - `9:55:39 AM`: `drops=47564`
     - `9:59:39 AM`: `drops=78368`
     - `10:04:39 AM`: `drops=50144`
   - Queue depth repeatedly sat near capacity (`~128k-131k`).
3. **CPU shifted off `FileOps-Poller` and onto `FileOps-Sender`, exactly as the
   decoupling design intended.**
   - `runtime/ps-lintap-threads.txt` shows `FileOps-Poller` at only `0.1%`
     while `FileOps-Sender` is the dominant thread at `67.1%`.
   - `runtime/pidstat-lintap-thread.txt` shows the same pattern over samples:
     `FileOps-Sender` at roughly `66%`, `93%`, `98%`, `95%` CPU while
     `FileOps-Poller` remains `0%`.
4. **The process cache helps, but under backlog it is not sufficient to prevent
   sender saturation.**
   - Healthy intervals show large cache wins, e.g. `9:49:39 AM`
     `process_cache:hit=103906,miss=3717`.
   - Under saturated backlog the miss share rises sharply, e.g. `9:59:39 AM`
     `process_cache:hit=139,miss=8388`, which is consistent with queued File
     events being processed after many short-lived producer processes have
     already exited and been evicted from the active-process cache.

Interpretation:

- `fop-08` succeeded at its first goal: the ring no longer overflows in this
  measurement window, and the poller thread is no longer the hot thread.
- But the current configuration does **not** yet satisfy the no-loss goal for
  regular-file telemetry, because the replacement bounded queue now drops in
  userspace once it fills.
- The sender thread remains the consumer ceiling. The queue is acting as a
  shock absorber and as explicit loss accounting, but not yet as a full fix.
- The cache-miss behavior under deep backlog suggests that sender-side process
  resolution still becomes expensive once queued events outlive the active
  process cache entries.

Updated phase-2 reading from this bundle:

- `fop-08` materially improved failure mode and observability:
  ring loss -> queue loss, and poller hot thread -> sender hot thread.
- The next pass should treat queue drops, not ring drops, as the active loss
  signal for this design.
- `fop-10`-style attribution remains useful, but there is also a fresh
  consumer-path question to answer: whether the next minimal win is more queue
  headroom, less sender-side work per event, or both.

## Queue-Follow-On Local Code Slice — 2026-08-25

Based on the deployed-bundle review above, implemented the next minimal
consumer-path improvement in `../wintap`:

- `FileOpsSensor` now tries to stamp File events with current-process identity
  from the active-process cache before enqueue.
- `EventChannel.Send` now trusts pre-populated File-event identity and skips
  re-resolving that event on the sender thread when `PidHash` and
  `ProcessName` are already present.

Rationale:

- In the deployed bundle, queue saturation coincided with sharply worse
  File-event process-cache hit rates on the sender thread, consistent with
  short-lived producer processes exiting before their queued File events were
  finally drained.
- Pre-enqueue stamping targets exactly that failure mode: resolve while the
  producer is still active, then carry the identity through backlog instead of
  paying a later miss.

Commands run:

```bash
cd ../wintap && dotnet build wintap/Lintap.csproj
cd ../wintap && dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests
```

Results:

- `dotnet build wintap/Lintap.csproj` passed with `0` errors.
- Targeted resolver tests passed again: `4 passed`.

Pending validation:

- Redeploy and collect another short root-run diagnostics bundle.
- Compare queue depth / high-water / drops and `process_cache:hit/miss` against
  bundle `20260825T172341Z`.
- Success signal for this slice: materially fewer sender-side cache misses and
  reduced queue-drop accumulation under comparable load, while `ring_fail_total`
  remains `0`.

## Field-Host Non-Root Smoke Workload Session (Post Identity-Stamping Deploy) — 2026-08-25

Ran a second repeated deterministic FileOps workload session after deploying the
 pre-enqueue File-event identity-stamping change.

- Session directory: `/tmp/fileops-phase2-smoke/session-20260825T184056Z`
- Host: `spk16.llnl.gov`
- Session window: `2026-08-25T18:40:56Z` to `2026-08-25T18:48:17Z`
- Build note recorded in session artifact:
  `post-pre-enqueue-identity-stamping-deploy`
- Pattern: 5 repeated deterministic FileOps workload runs
- Per run parameters: `--files 24 --rounds 4`
- Per-run status: all 5 runs exited `0`

Use this session as the next diagnostics-correlation anchor when reviewing the
 next root-run bundle against `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T172341Z`.

## Root-Run Diagnostics Bundle Review (Post Identity-Stamping Deploy) — 2026-08-25

Bundle reviewed:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T184934Z`

Deployment/runtime proof:

- `manifest.txt` shows `lintap_pid=3271282`, `install_root=/usr/lib/lintap`.
- The copied smoke artifact session is present under
  `runtime/fileops-phase2-smoke/session-20260825T184056Z`, matching the
  post-deploy non-root workload session above.

Comparison target:

- Prior bundle with queue-saturation behavior:
  `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T172341Z`

Key findings versus the prior bundle:

1. **Kernel ring-buffer remains healthy.**
   - As in the prior bundle, every recorded interval still shows
     `ring_fail_total=0` for all FileOps op classes.
   - The ring fix held while testing the follow-on improvement.

2. **The userspace queue no longer drops in this capture window.**
   - In the prior bundle, the queue repeatedly saturated and dropped, including:
     - `9:52:39 AM`: `drops=21567`
     - `9:55:39 AM`: `drops=47564`
     - `9:59:39 AM`: `drops=78368`
     - `10:04:39 AM`: `drops=50144`
   - In the new bundle, every recorded interval shows `drops=0`.
   - Queue depth still rises substantially under load, but stays below the hard
     failure mode seen before. Highest recorded depth/high-water in this bundle:
     `depth=102547,high_water=103187` at `11:49:30 AM`.

3. **Backlog-time process attribution is materially healthier.**
   - In the prior saturated bundle, a deep-backlog interval showed sender-side
     cache collapse, e.g. `9:59:39 AM`:
     `process_cache:hit=139,miss=8388`.
   - In the new bundle, even the deepest recorded backlog interval (`11:49:30 AM`)
     still shows strong cache usage:
     `process_cache:hit=54026,miss=4834`.
   - Other intervals are similarly healthy, e.g.:
     - `11:44:30 AM`: `hit=80515,miss=5100`
     - `11:46:30 AM`: `hit=53005,miss=2578`
   - This is consistent with the intended effect of pre-enqueue File-event
     identity stamping: resolve while the producer is still live, then carry
     that identity through backlog instead of rediscovering it later.

4. **`FileOps-Sender` is still the dominant thread, but the loss mode improved.**
   - `runtime/ps-lintap-threads.txt` shows `FileOps-Sender` at `56.8%` and
     `FileOps-Poller` at `0.2%`.
   - `runtime/pidstat-lintap-thread.txt` still shows `FileOps-Sender` as the
     hot thread in the sample window (examples: `49.02%`, `63.00%`, `71.00%`,
     `99.00%`).
   - Even so, the crucial operational difference from the prior bundle is that
     sender saturation no longer translated into queue drops during this
     collection window.

Interpretation:

- The pre-enqueue identity-stamping follow-on appears to have produced a real
  improvement.
- Relative to bundle `20260825T172341Z`, this new bundle shows:
  - same `ring_fail_total=0` success,
  - zero queue drops instead of repeated queue-drop bursts,
  - much healthier File-event process-cache hit behavior under backlog.
- The sender thread remains the main consumer hotspot, so the feature is not at
  final closeout yet, but this slice moved the system materially closer to a
  no-loss steady state.

Current verdict for this follow-on slice:

- **Accepted as an improvement in the active failure mode.**
- Remaining question before closeout: whether longer-duration comparable load
  reintroduces queue drops, or whether this queue/no-drop behavior is stable
  enough to proceed to the next measurement slice (`fop-10`) without another
  immediate sender-path optimization.

## Root-Run Diagnostics Bundle Review (Later Same Build) — 2026-08-25

Additional same-build bundle reviewed:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T203648Z`

Key finding:

- The zero-queue-drop behavior seen in bundle `20260825T184934Z` was **not**
  stable over a later observation window. Kernel ring loss still stayed at `0`,
  but userspace queue saturation returned hard.

Representative evidence from `journal/lintap-file-log-fileops-counters.txt`:

- `12:17:31 PM`: `depth=119439`, `drops=30591`
- `12:19:31 PM`: `depth=131053`, `drops=91570`
- `12:41:33 PM`: `depth=84287`, `drops=385435`
- `12:42:33 PM`: `depth=131071`, `drops=448425`
- `12:43:36 PM`: `depth=30129`, `drops=1960545`

Important nuance:

- Even in this worse snapshot, `ring_fail_total` remained `0` for all recorded
  FileOps op classes. The active loss signal stayed in the bounded userspace
  queue, not in the kernel ring.
- `FileOps-Poller` remained cold while `FileOps-Sender` remained the dominant
  hot thread (`56.6%` in `ps-lintap-threads.txt`; `28-34%` in the sampled
  `pidstat` window, with Clone/Exit also hot there).
- The worst queue-drop spikes coincided with extreme userspace consumption
  bursts, especially for `read` and `write`. The largest example is the
  `12:43:36 PM` interval with `write:consumed=1820145` and
  `process_cache:hit=2034769,miss=7746`.

Interpretation update:

- The pre-enqueue identity-stamping change helped, but it did **not** make the
  queue-loss problem disappear under all observed host conditions.
- The `184934Z` bundle should therefore be read as a better short-window sample,
  not as proof of stable no-loss steady state.
- This strengthens the value of `fop-10`: we need attribution data and the
  duplicate-open measurement before deciding whether the next move should be
  another sender-path optimization, more queue headroom, or the gated
  aggregation candidate.

## fop-10 Local Code Slice — 2026-08-25

Implemented the approved measurement slice in `../wintap`.

Code changes:

- `FileOpsSensor` now records bounded summary emit measurements for the 60s
  `FileOps counters` log.
- Added top-N emitted process-name (`comm`) buckets.
- Added top-N emitted path-prefix buckets using coarse normalized prefixes
  (`/tmp`, `/var`, `/usr`, `/home/*`, etc.) rather than raw full paths.
- Added same-`(pid,path)` short-window open duplicate measurement, reported as
  total opens, repeat count, repeat percent, and window size.
- The measurement state is bounded: aggregate buckets are capped, duplicate
  tracking uses a bounded recent-open map with pruning, and only summary
  statistics are logged.

Commands run:

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
cd ../wintap && dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests
```

Results:

- Tracer rebuild passed.
- `dotnet build wintap/Lintap.csproj` passed with `0` errors.
- Targeted resolver tests passed: `4 passed`.

Pending validation:

- Deploy this slice.
- Capture a short root-run diagnostics bundle and confirm the new
  `measure=[...]` section appears in the `FileOps counters` log.
- Review the resulting top-comm / top-prefix / duplicate-open numbers to decide
  whether the gated `fop-11` aggregation candidate is justified.

## fop-12 Local Code Slice — 2026-08-25

Implemented the approved precondition slice in `../wintap` plus the naturally
paired accuracy fixes already approved in the handoff.

Code changes:

- `FileOpsSensor` now resolves relative/openat `open` paths to absolute paths
  pre-enqueue via `readlink /proc/<pid>/fd/<fd>` when the raw open path is not
  absolute and the returned fd is available.
- Successful relative-path resolution is now counted separately from resolution
  misses in the 60s `FileOps counters` log (`resolve=[...]`).
- Linux File paths are no longer lowercased during normalization; Windows-only
  lowercasing remains the policy. This avoids conflating distinct Linux files
  that differ only by case.
- File event time now uses the kernel monotonic timestamp (`TimestampNs`)
  converted to wallclock rather than `DateTime.UtcNow` at dequeue.
- The differential comparator in
  `validation/fileops-differential/compare_fileops.py` was aligned to preserve
  Linux path case as well.

Not yet folded into this slice:

- A3 `s_dev` / `i_ino` emission
- P3 sampled sender cost-split timing

Commands run:

```bash
cd ../wintap && dotnet build wintap/Lintap.csproj
cd ../wintap && dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests
cd Wintap-Analytics && python3 -m py_compile validation/fileops-differential/compare_fileops.py
```

Results:

- `dotnet build wintap/Lintap.csproj` passed with `0` errors.
- Targeted resolver tests passed: `4 passed`.
- Comparator syntax check passed.

Pending validation:

- Deploy this slice.
- Confirm that `resolve=[relative_open_resolved=...,relative_open_resolve_miss=...]`
  appears in the FileOps 60s log.
- Measure whether the `(relative)` top-prefix bucket collapses in the deployed
  `fop-10` measurement output.
- Re-run the differential harness against Linux-case-preserving output before
  treating fop-12 as accepted.

## Field-Host Non-Root Smoke Workload Session (Deployed fop-12 Build) — 2026-08-25

Ran another repeated deterministic FileOps workload session after deploying the
 `fop-12` absolute-path precondition slice.

- Session directory: `/tmp/fileops-phase2-smoke/session-20260825T224052Z`
- Host: `spk16.llnl.gov`
- Session window: `2026-08-25T22:40:52Z` to `2026-08-25T22:48:14Z`
- Build note recorded in session artifact:
  `deployed-fop-12-absolute-path-precondition`
- Correlation note recorded in session artifact:
  `FileOps-counters,pidstat-collector`
- Pattern: 5 repeated deterministic FileOps workload runs
- Per run parameters: `--files 24 --rounds 4`
- Per-run status: all 5 runs exited `0`

Use this session as the next diagnostics-correlation anchor when reviewing the
 first root-run bundle from the deployed `fop-12` build.

## Root-Run Diagnostics Bundle Review (First Deployed fop-12 Build) — 2026-08-25

Bundle reviewed:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T225502Z`

Deployment/runtime proof:

- `manifest.txt` shows `lintap_pid=3405711`, `install_root=/usr/lib/lintap`.
- The copied smoke artifact session is present under
  `runtime/fileops-phase2-smoke/session-20260825T224052Z`, matching the
  post-`fop-12` workload session above.

What improved:

1. **The new `resolve=[...]` section is present in the FileOps counters log.**
   The deployment is definitely running the `fop-12` code.
2. **Kernel ring loss stayed at `0`.**
   All reviewed FileOps counter lines continue to show `ring_fail_total=0`.
3. **Queue drops stayed at `0` throughout the sampled window.**
   Even with substantial queue depth/high-water in some intervals, no drop was
   recorded in this bundle.

Representative queue/cpu picture:

- `3:49:31 PM`: `depth=96932`, `high_water=96978`, `drops=0`
- `3:50:31 PM`: `depth=19271`, `high_water=115640`, `drops=0`
- `3:55:16 PM` sampled `pidstat`: `FileOps-Sender` about `91%`,
  `FileOps-Poller` about `0%`
- `ps-lintap-threads.txt`: `FileOps-Sender` `33.2%`, `FileOps-Poller` `0.4%`

What did **not** improve enough yet:

1. **Relative-path resolution is only partially successful.**
   The new counters show many relative-open resolution misses still remain.
   Examples:
   - `3:40:30 PM`: `relative_open_resolved=1734`,
     `relative_open_resolve_miss=9012`
   - `3:45:31 PM`: `relative_open_resolved=1261`,
     `relative_open_resolve_miss=9185`
   - `3:55:31 PM`: `relative_open_resolved=1357`,
     `relative_open_resolve_miss=9841`
2. **`(relative)` remains a top prefix bucket.**
   The expectation for `fop-12` was that this bucket would shrink materially.
   It did not. Examples:
   - `3:40:30 PM`: `(relative):total=9152,open=9013`
   - `3:45:31 PM`: `(relative):total=9205,open=8960`
   - `3:55:31 PM`: `(relative):total=10291,open=9843`

Interpretation:

- The deployed `fop-12` slice successfully added the necessary observability
  and did not regress queue/ring behavior in this sampled window.
- But it did **not** yet achieve the intended absolute-path precondition for a
  large portion of relative opens. The misses are too numerous for us to claim
  aggregation keys are reliably absolute today.
- The most likely reading is that many relative/openat cases do not have a
  still-open fd target at the time userspace resolves, or are otherwise not
  represented by the current open-exit/fd path we assumed.

Pidstat collector correlation:

- The workload session window was `22:40:52Z` to `22:48:14Z`.
- In local service timestamps, the pidstat collector wrote parquet at:
  - `15:40:02`
  - `15:45:02`
  - `15:50:02`
- So this workload window overlaps the `15:45` collector flush directly and is
  bounded by the `15:40` and `15:50` pidstat parquet writes.

Current verdict for `fop-12`:

- **Partially successful / not yet accepted.**
- Accepted aspects: path-case policy, kernel timestamps, new resolution
  counters, and no observed queue/ring regression in this bundle.
- Not accepted yet: the absolute-path precondition itself, because the
  remaining relative-path miss volume is still high and the `(relative)` bucket
  remains a major top-prefix class.

## Field-Host Non-Root Smoke Workload Session (Deployed fd=0 Fix, Short) — 2026-08-25

Ran a shortened repeated deterministic FileOps workload session after deploying
 the `fd=0` resolution/caching fix.

- Session directory: `/tmp/fileops-phase2-smoke/session-20260825T231857Z`
- Host: `spk16.llnl.gov`
- Session window: `2026-08-25T23:18:57Z` to `2026-08-25T23:22:38Z`
- Build note recorded in session artifact:
  `deployed-fd0-fix-short-smoke`
- Correlation note recorded in session artifact:
  `FileOps-counters,pidstat-collector`
- Pattern: 3 repeated deterministic FileOps workload runs
- Per run parameters: `--files 24 --rounds 4`
- Per-run status: all 3 runs exited `0`

Use this short session as the next diagnostics-correlation anchor to evaluate
 whether the `fd=0` bug fix materially increases `relative_open_resolved` and
 reduces the `(relative)` top-prefix bucket.

## Root-Run Diagnostics Bundle Review (Post `fd=0` Fix, Short Smoke) — 2026-08-25

Bundle reviewed:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T232323Z`

Deployment/runtime proof:

- `manifest.txt` shows `lintap_pid=3432760`, `install_root=/usr/lib/lintap`.
- The copied smoke artifact session is present under
  `runtime/fileops-phase2-smoke/session-20260825T231857Z`, matching the short
  post-`fd=0` workload session above.

What improved:

1. **The `fd=0` fix appears to have increased relative-path resolution in at
   least some intervals.**
   Compared with the first `fop-12` bundle, the strongest sampled interval now
   shows much larger absolute resolution counts:
   - prior `fop-12` example: `relative_open_resolved=1734`,
     `relative_open_resolve_miss=9012`
   - post-`fd=0` example (`4:18:57 PM`): `relative_open_resolved=10654`,
     `relative_open_resolve_miss=23424`
2. **Queue/ring behavior remained healthy in this short sample.**
   - `ring_fail_total` stayed `0`.
   - queue `drops=0` throughout the reviewed intervals.
3. **The deployed build still carries the new `resolve=[...]` and
   `measure=[...]` sections, so both `fop-10` and `fop-12` observability are
   intact.**

What did not improve enough yet:

1. **`(relative)` is still a major top-prefix bucket.**
   Examples from this bundle:
   - `4:18:57 PM`: `(relative):total=23743,open=23424`
   - `4:19:57 PM`: `(relative):total=15277,open=15118`
   - `4:22:30 PM`: `(relative):total=8340,open=8195`
   - `4:23:30 PM`: `(relative):total=14838,open=11839`
2. **Resolution misses remain very high even after the bug fix.**
   Examples:
   - `4:19:57 PM`: `relative_open_resolve_miss=15118`
   - `4:21:30 PM`: `relative_open_resolve_miss=8597`
   - `4:22:30 PM`: `relative_open_resolve_miss=8195`
   - `4:23:30 PM`: `relative_open_resolve_miss=11835`

Interpretation:

- The `fd=0` fix was worth doing and likely recovered a real slice of missed
  resolution opportunity.
- But it is **not** sufficient by itself to make relative/openat paths reliably
  absolute before aggregation.
- The remaining miss volume is still too large for us to declare `fop-12`
  accepted as the absolute-path precondition for `fop-11`.
- That points back to the next likely follow-on: carry more open-time context
  such as `dirfd` so userspace can fall back to `cwd` / `dirfd`-base joins when
  the newly opened fd is already gone.

Pidstat collector correlation:

- The short workload session window was `23:18:57Z` to `23:22:38Z`.
- In local service timestamps, the pidstat collector wrote parquet at:
  - `16:20:02`
- The diagnostics bundle does not include a later pidstat write inside the
  exact short window, so this bundle is more useful for FileOps counter
  correlation than for direct pidstat time-bucket comparison.

Current verdict for the `fd=0` follow-up:

- **Improvement confirmed, but not enough.**
- Keep the `fd=0` fix, but continue with a richer `fop-12` follow-on if the
  goal remains “absolute-path ground truth before aggregation.”

## fop-12 Follow-On Local Code Slice (dirfd / cwd fallback) — 2026-08-25

Implemented the next `fop-12` follow-on in `../wintap` to recover more
absolute paths when the newly opened fd is already gone by userspace decode.

Code changes:

- `file_ops_tracer.bpf.c` and `file_ops_tracepoint.bpf.c` now carry `dirfd` in
  open/openat path records.
- `FileOpsSensor` now resolves relative/openat paths pre-enqueue with this
  branch order:
  1. `readlink /proc/<pid>/fd/<opened-fd>`
  2. if that fails and `dirfd == AT_FDCWD`, resolve `/proc/<pid>/cwd` and join
     the raw relative path
  3. if that fails and `dirfd >= 0`, resolve `/proc/<pid>/fd/<dirfd>` and join
     the raw relative path
- Added reason-split resolution counters to the 60s FileOps log:
  - `resolved_fd`
  - `resolved_dirfd`
  - `resolved_cwd`
  - `opened_fd_lookup_miss`
  - `dirfd_lookup_miss`
  - `cwd_lookup_miss`
  - `unsupported_dirfd`

Commands run:

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
cd ../wintap && dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests
```

Results:

- Tracer rebuild passed.
- `dotnet build wintap/Lintap.csproj` passed with `0` errors.
- Targeted resolver tests passed: `4 passed`.

Pending validation:

- Deploy this slice.
- Compare `resolved_dirfd` / `resolved_cwd` against prior bundles to see which
  fallback branch contributes real recovery.
- Re-check whether `(relative)` materially collapses in `prefix_top` after this
  richer fallback is live.

## Field-Host Non-Root Smoke Workload Session (Deployed dirfd/cwd Fallback Build, Short) — 2026-08-25

Ran a shortened repeated deterministic FileOps workload session after deploying
 the `dirfd` / `cwd` fallback follow-on.

- Session directory: `/tmp/fileops-phase2-smoke/session-20260825T234052Z`
- Host: `spk16.llnl.gov`
- Session window: `2026-08-25T23:40:52Z` to `2026-08-25T23:44:33Z`
- Build note recorded in session artifact:
  `deployed-dirfd-cwd-fallback-short-smoke`
- Correlation note recorded in session artifact:
  `FileOps-counters,pidstat-collector`
- Pattern: 3 repeated deterministic FileOps workload runs
- Per run parameters: `--files 24 --rounds 4`
- Per-run status: all 3 runs exited `0`

Use this short session as the next diagnostics-correlation anchor to evaluate
 whether `resolved_dirfd` / `resolved_cwd` materially reduce
 `relative_open_resolve_miss` and shrink `(relative)` in `prefix_top`.

## Root-Run Diagnostics Bundle Review (Deployed dirfd/cwd Fallback Build, Short Smoke) — 2026-08-25

Bundle reviewed:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T234559Z`

Deployment/runtime proof:

- `manifest.txt` shows `lintap_pid=3451743`, `install_root=/usr/lib/lintap`.
- The copied smoke artifact session is present under
  `runtime/fileops-phase2-smoke/session-20260825T234052Z`, matching the short
  post-`dirfd`/`cwd` workload session above.

What improved:

1. **The new reason-split resolution counters are present and clearly show a
   real `dirfd` contribution.**
   The deployed build is definitely running the new follow-on code, and the
   recovery is coming primarily from `dirfd`, not `cwd`:
   - `4:40:59 PM`: `resolved_fd=1362`, `resolved_dirfd=958`, `resolved_cwd=0`
   - `4:41:59 PM`: `resolved_fd=1528`, `resolved_dirfd=918`, `resolved_cwd=0`
   - `4:42:59 PM`: `resolved_fd=1368`, `resolved_dirfd=807`, `resolved_cwd=0`
   - `4:44:31 PM`: `resolved_fd=871`, `resolved_dirfd=548`, `resolved_cwd=0`
   - `4:46:31 PM`: `resolved_fd=1486`, `resolved_dirfd=931`, `resolved_cwd=1`
2. **Relative-open recovery is better than the earlier `fd=0`-only short-smoke
   bundle.**
   In the low-backlog intervals aligned with this short smoke window, resolved
   counts moved up while misses came down:
   - post-`fd=0` short-smoke examples:
     - `4:19:57 PM`: `relative_open_resolved=1371`,
       `relative_open_resolve_miss=15118`
     - `4:21:30 PM`: `relative_open_resolved=1300`,
       `relative_open_resolve_miss=8597`
     - `4:22:30 PM`: `relative_open_resolved=1468`,
       `relative_open_resolve_miss=8195`
   - post-`dirfd`/`cwd` short-smoke examples:
     - `4:41:59 PM`: `relative_open_resolved=2446`,
       `relative_open_resolve_miss=7997`
     - `4:42:59 PM`: `relative_open_resolved=2175`,
       `relative_open_resolve_miss=8268`
     - `4:44:31 PM`: `relative_open_resolved=1419`,
       `relative_open_resolve_miss=8814`
3. **Queue/ring behavior remained healthy during the correlated smoke window.**
   - `ring_fail_total=0` throughout the reviewed counter lines.
   - queue `drops=0` throughout the reviewed counter lines.
   - Queue depth still fell back to `0` by `4:44:31 PM`, so this bundle does
     not show a regression in no-loss-ish behavior.

What did not improve enough yet:

1. **`resolved_cwd` is effectively negligible.**
   The new counters show almost all additional recovery comes from the `dirfd`
   branch; `cwd` contributes `0` in the smoke-window lines and only `1` in the
   later `4:46:31 PM` line.
2. **`(relative)` is still a major top-prefix bucket.**
   Representative examples:
   - `4:40:59 PM`: `(relative):total=10727,open=8081`
   - `4:41:59 PM`: `(relative):total=8162,open=7998`
   - `4:42:59 PM`: `(relative):total=8439,open=8269`
   - `4:44:31 PM`: `(relative):total=8966,open=8814`
3. **Resolution misses remain too high to treat path identity as reliably
   absolute.**
   Representative examples:
   - `4:40:59 PM`: `relative_open_resolve_miss=8081`
   - `4:41:59 PM`: `relative_open_resolve_miss=7997`
   - `4:42:59 PM`: `relative_open_resolve_miss=8268`
   - `4:44:31 PM`: `relative_open_resolve_miss=8814`
4. **The miss-side reason counters show the remaining gap is now mostly
   `dirfd` lookup failure.**
   In the smoke-window lines, `dirfd_lookup_miss` is essentially the same size
   as `relative_open_resolve_miss`, while `cwd_lookup_miss` stays near zero.
   That means the follow-on improved recovery, but the dominant unresolved class
   is still “we have a non-`AT_FDCWD` relative open and cannot recover the base
   directory fd path in userspace at decode time.”

Interpretation:

- This follow-on was worth doing. The bundle confirms that carrying `dirfd`
  recovers a meaningful additional slice of absolute paths.
- The new evidence also narrows the remaining problem: `cwd` fallback is not a
  significant contributor in this workload, while `dirfd`-base recovery helps
  but still leaves a large unresolved floor.
- The path-quality picture is better than the first `fop-12` deployment and
  better than the `fd=0`-only short-smoke bundle, but it is still not strong
  enough to call `fop-12` accepted as the hard precondition for `fop-11`
  aggregation.

Pidstat collector correlation:

- The short workload session window was `23:40:52Z` to `23:44:33Z`.
- In local service timestamps, the reviewed FileOps counter lines overlapping
  that window are `4:40:59 PM`, `4:41:59 PM`, `4:42:59 PM`, and `4:44:31 PM`.
- The bundle's thread pidstat sample starts later at `4:46:11 PM`, so it is
  useful for the post-window hot-thread picture rather than exact within-window
  matching.
- That later pidstat still shows the same steady-state hotspot pattern:
  `FileOps-Sender` around `66-98%` while `FileOps-Poller` remains near `0%`.

Current verdict for the `dirfd` / `cwd` follow-on:

- **Improvement confirmed, but still not enough to accept `fop-12`.**
- Keep this change, because `resolved_dirfd` is materially helping.
- But the remaining `relative_open_resolve_miss` floor and persistent
  `(relative)` prefix bucket still block declaring path identity good enough for
  the gated `fop-11` aggregation step.

## Field-Host Non-Root Smoke Workload Session (Deployed fop-10 Build) — 2026-08-25

Ran another repeated deterministic FileOps workload session after deploying the
 `fop-10` measurement slice.

- Session directory: `/tmp/fileops-phase2-smoke/session-20260825T205219Z`
- Host: `spk16.llnl.gov`
- Session window: `2026-08-25T20:52:19Z` to `2026-08-25T20:59:41Z`
- Build note recorded in session artifact:
  `deployed-fop-10-measurement-slice`
- Correlation note recorded in session artifact:
  `FileOps-counters,pidstat-collector`
- Pattern: 5 repeated deterministic FileOps workload runs
- Per run parameters: `--files 24 --rounds 4`
- Per-run status: all 5 runs exited `0`

Use this session as the next diagnostics-correlation anchor when reviewing the
 first root-run bundle from the deployed `fop-10` build.

## Root-Run Diagnostics Bundle Review (First Deployed fop-10 Build) — 2026-08-25

Bundle reviewed:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T210710Z`

Deployment/runtime proof:

- `manifest.txt` shows `lintap_pid=3341237`, `install_root=/usr/lib/lintap`.
- The copied smoke artifact session is present under
  `runtime/fileops-phase2-smoke/session-20260825T205219Z`, matching the
  `fop-10` workload session above.

Measurement visibility:

- The new `measure=[...]` section is present in the `FileOps counters` log as
  intended.
- It includes all three requested `fop-10` outputs:
  - top emitted process-name buckets (`comm_top`)
  - top emitted path-prefix buckets (`prefix_top`)
  - short-window open duplicate ratio (`open_dup`)

Representative measurement readout:

1. `1:43:49 PM` interval:
   - `comm_top`: `rpm` dominates (`total=17562`), then `systemd`, `splunkd`,
     `awk`, `sed`.
   - `prefix_top`: `/lib64` and `/usr` dominate, followed by `(relative)`,
     `/opt`, `/var`.
   - `open_dup`: `total=15229`, `repeat=8030`, `repeat_pct=52.7`.
2. `1:45:30 PM` interval:
   - `comm_top`: `systemd` dominates (`total=20188`), then `splunkd`, `sed`,
     `awk`, `sh`.
   - `prefix_top`: `(relative)` dominates, then `/usr`, `/lib64`, `/`, `/opt`.
   - `open_dup`: `total=24714`, `repeat=20377`, `repeat_pct=82.5`.
3. `1:48:31 PM` interval:
   - `comm_top`: `rpm`, `systemd`, `setroubleshootd`, `splunkd`,
     `setroubleshootprivileged.py` dominate.
   - `prefix_top`: `/lib64`, `/usr`, `(relative)`, `/`, `/opt` dominate.
   - `open_dup`: `total=30143`, `repeat=18200`, `repeat_pct=60.4`.
4. `1:58:32 PM` interval:
   - `comm_top`: `rpm`, `systemd`, `setroubleshootd`, `splunkd`,
     `setroubleshootprivileged.py` dominate.
   - `prefix_top`: `/usr`, `/lib64`, `(relative)`, `/`, `/opt` dominate.
   - `open_dup`: `total=25194`, `repeat=15576`, `repeat_pct=61.8`.

What the new measurements say:

- The surviving File stream is not dominated by one single long-lived research
  workload. It is shared across package-management / system-maintenance style
  activity (`rpm`, `systemd`, `setroubleshoot*`) and application/service reads
  (`splunkd`, `git`, Falcon sensor helpers).
- The hottest path-prefixes are consistently library and system-tree paths:
  `/lib64`, `/usr`, plus substantial `(relative)` opens.
- The duplicate-open ratio is persistently high, not marginal. Across the
  sampled intervals it ranges roughly from `52.7%` up to `83.7%`, with many
  intervals in the `60-80%` band.

Queue/ring state in the same bundle:

- Kernel ring loss remained `0` throughout the reviewed lines.
- Queue drops were `0` for most of the sampled deployment window, but not all:
  the `2:07:32 PM` interval shows renewed queue saturation with
  `depth=130909`, `high_water=131072`, `drops=39731`.
- This means `fop-10` succeeded as a measurement slice, but the current
  userspace queue-loss problem still exists under at least some later load
  phases.

Pidstat collector correlation:

- The workload session window was `20:52:19Z` to `20:59:41Z`.
- In local service timestamps, the pidstat collector wrote parquet at:
  - `13:50:02`
  - `13:55:02`
  - `14:00:02`
- So the workload window overlaps the `13:55` collector flush directly and sits
  between the `13:50` and `14:00` flush boundaries. That gives a practical
  anchor for future correlation with pidstat-derived CPU/process activity, even
  though this diagnostics bundle does not itself summarize those parquet rows.

Interpretation for the next decision:

- `fop-10` produced real gating evidence for `fop-11`.
- The duplicate-open ratio is high enough to justify serious consideration of
  short-interval duplicate suppression/aggregation as the next candidate.
- The path-prefix and comm attribution also suggest that much of the surviving
  load is library/system-tree churn rather than a single bespoke workload,
  which makes targeted one-off filters less attractive than a more structural
  duplicate-reduction step.

Milestone reached:

- `fop-10` moved `fop-11` from “candidate” to “review-ready proposal.” The
  concrete designer-review artifact is
  [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]].

## fop-13a/fop-13b Local Code Slice — 2026-08-25

Implemented the gap-analysis fix ([[wiki/work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25]])
in `../wintap` plus the harness updates in this repo.

Code changes in `../wintap`:

- `file_ops_tracer.bpf.c` (CO-RE tier):
  - New `FILE_OP_DIR_OPEN=7` internal record class: `O_DIRECTORY` opens are no
    longer discarded at open-exit; un-flagged opens of directories are also
    detected via `i_mode` and rerouted to `DIR_OPEN`.
  - Path records now carry the opened object's `(s_dev, i_ino)` and, for
    non-`AT_FDCWD` relative opens, the dirfd base directory's `(s_dev, i_ino)`
    captured at event time.
  - Compact fd records (read/write/close/mmap) now carry the file's
    `(s_dev, i_ino)` — `is_regular_fd` was refactored to `fd_to_inode` +
    `is_regular_fd_info` so identity comes from the traversal the filter
    already performs (no second fd-table walk).
  - Open-exit handlers no longer copy the 264-byte `openat_state` to the BPF
    stack (stack-limit fix found at build time): they read the map value
    directly and delete the entry after emission (same-thread key ownership).
- `file_ops_tracepoint.bpf.c` (fallback tier): identity fields added zeroed so
  the wire format stays identical across tiers; behavior unchanged
  (`O_DIRECTORY` opens still dropped, no inode reads — documented tier
  difference).
- `FileOpsSensor.cs`:
  - fop-13a: final relative-open misses are now split by cause via one
    `/proc/<pid>` existence check — `miss_producer_dead` vs
    `miss_producer_alive`.
  - fop-13b: global bounded dir-identity index
    (`(s_dev, i_ino) → absolute dir path`, FIFO-bounded at 16,384 entries,
    eviction counted) learned from `DIR_OPEN` records; relative `DIR_OPEN`
    paths resolve through their own fd readlink then the base-dir index.
    `DIR_OPEN` records never become WintapMessages.
  - Resolution chain gains the race-free dir-index step between the opened-fd
    readlink and the `/proc` dirfd fallback:
    fd readlink → **dir-index by kernel-captured (s_dev, i_ino)** → dirfd
    readlink → cwd → miss.
  - New 60s `resolve=[...]` counters: `resolved_dir_index`, `dir_index_miss`,
    `miss_producer_dead`, `miss_producer_alive`, `dir_open_consumed`,
    `dir_open_indexed`, `dir_open_unresolved`, `dir_index_size`,
    `dir_index_evictions`; kernel summary now includes the `dir_open` op class.

Changes in `Wintap-Analytics`:

- `validation/fileops-differential/compare_fileops.py`: relative→absolute
  upgrade matching. Relative-path tuples (previously invisible noise) are now
  tracked; a baseline relative tuple matches when the candidate has the same
  relative tuple or an absolute tuple (same pid+op) ending in `/<relative>`.
  New summary fields `baseline/candidate/matched/unmatched_relative_tuples`
  plus samples; `--fail-on-unmatched-relative` opt-in gate (strict
  absolute-tuple failure behavior unchanged by default).
- `validation/fileops-differential/fileops_workload.py`: new deterministic
  dirfd-relative scenario — opens an `O_DIRECTORY` handle and reads a file by
  relative name through it; manifest records the expected absolute path.

Commands run (lintap-dev VM, arm64; `.bpf.o` artifacts are gitignored and the
field host rebuilds its own):

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
cd ../wintap && dotnet test tests/Wintap.Tests/Wintap.Tests.csproj \
  --filter "FullyQualifiedName~ProcessResolverTests|FullyQualifiedName~WintapMessageTests|FullyQualifiedName~ProcessTreeRecoveryGapTests"
python3 -m py_compile validation/fileops-differential/compare_fileops.py validation/fileops-differential/fileops_workload.py
uv run --with duckdb python <synthetic comparator scenarios>
python3 validation/fileops-differential/fileops_workload.py --files 2 --rounds 2 ...
```

Results:

- Tracer `make clean && make` passed for both tiers after the stack-limit fix
  (first build attempt failed with "BPF stack limit exceeded" in the open-exit
  handlers; resolved by eliminating the on-stack `openat_state` copy).
- `dotnet build wintap/Lintap.csproj` passed with existing warnings, `0` errors.
- Linux-relevant test classes passed `10/10`. Known pre-existing failures on
  this Linux/arm64 host (verified present without this change via stash):
  `WindowsProcessSidExtractionTests` and Windows-path-expectation cases in
  `WindowsProcessSensorTests`/`RuntimeDataRootTests`.
- Comparator synthetic scenarios passed: upgrade-matched rc=0, lost-relative
  report-only rc=0 with `unmatched_relative_tuples=1`, lost-relative gated
  rc=1, missing-regular still rc=1.
- Workload smoke run produced the `dirfd_relative` manifest section.

Pending field validation (acceptance per the gap analysis):

- Rebuild tracers on the RHEL8 field host, deploy, and capture bundles.
- `relative_open_resolve_miss` drops by an order of magnitude vs. the
  20260825T234559Z baseline (~8k/min), with the residual explained by
  `dir_index_miss`; `(relative)` leaves the top-5 prefix buckets.
- `miss_producer_dead` share confirms (or corrects) the producer-lifetime
  diagnosis from fop-13a data.
- `ring_fail_total` stays 0 and queue drops do not regress with `dir_open`
  volume measured via the new `dir_open` kernel/user counters.
- A/B differential rerun including the dirfd-relative workload scenario.

## fop-13 Field Runs — 2026-08-25 (recorded from implementor review summaries)

The deployed-build bundle reviews below were performed on the field-side
system; the numbers are transcribed from the implementor's review summaries
so this clone carries the complete acceptance record. If the field-side clone
holds its own richer copies of these reviews, prefer those on merge.

### First deployed fop-13 bundle

- `relative_open_resolve_miss` fell from the ~7997-8814/min post-dirfd floor
  to 0-945/min (samples: 46, 853, 945, 200, 14, 33, 133, 4, 0, 68).
- DIR_OPEN/dir-index live: `dir_open_consumed` ~11.9k-19.8k,
  `dir_open_indexed` ~11.6k-19.3k, `dir_index_size` → 1055, evictions 0.
- Miss-cause split supports the producer-lifetime diagnosis: heavy windows
  mostly `miss_producer_dead` (819/34, 945/0, 180/20 dead/alive).
- `(relative)` no longer in top-prefix examples; `ring_fail_total=0`.
- Queue drops still recurred under load (e.g. 6:14:19 PM `drops=47404` at
  `depth=107238`).
- Smoke: session-20260826T011005Z complete; session-20260826T011806Z partial
  in that bundle (collected mid-run).

### Follow-up bundle, same running instance (lintap_pid=3502838)

- Key line 6:19:29 PM: `relative_open_resolved=29152`, `miss=6`,
  `resolved_fd=9442`, `resolved_dir_index=19709`, `resolved_cwd=1`,
  `resolved_dirfd=0` — first at-scale proof that the dir-index branch does
  the bulk of the recovery.
- Later window misses: 31, 0, 21, 5, 15, 131, 62, 66, 27, 0, 10.
- Index healthy: size → 2029, evictions 0.
- Queue drops remained the active problem across 6:21-6:30 PM
  (1617 → 61671/min peaks) — assigned to fop-11, not a fop-13 gap.
- Smoke session-20260826T011806Z runs 1-2 present, run 3 not yet copied.

### 4x queue-capacity experiment (WINTAP_FILEOPS_MAX_QUEUE_EVENTS=524288)

- Bundle 023152: sampled windows showed `drops=0` at 4x capacity; the
  10-minute spaced smoke session fully copied; path identity strong.
- Bundle 024019 (later, same execution): `drops=0` persisted with backlog
  depth reaching `393320` and `437633` (`high_water=437692`) — the drops were
  burst-shaped, not a sustained deficit. Misses stayed 0-124/min under that
  backlog (resolution is pre-enqueue, unaffected by sender lag); index size
  → 2108, evictions 0. `FileOps-Sender` remained the hot thread,
  `FileOps-Poller` cold.
- RSS accounting deferred to the longer execution cycle; the
  pidstat-collector parquet series already records memory over time.

## fop-13 Closeout — 2026-08-25 (human acceptance)

Human decision: fop-13 is closed as the successful fix for the fop-12
path-identity floor, on the field evidence recorded above:

- `relative_open_resolve_miss` collapsed from the ~7997-8814/min pre-fop-13
  floor to 0-945/min (first bundle) and 0-131/min in later windows, with the
  6:19:29 PM line as the at-scale proof: `relative_open_resolved=29152`,
  `miss=6`, and `resolved_dir_index=19709` as the dominant recovery branch.
- `miss_producer_dead` dominance confirmed the gap-analysis diagnosis.
- `(relative)` left the top prefix buckets; dir index healthy
  (size ~2.1k of 16,384 cap, evictions 0); `ring_fail_total=0` throughout.
- The 4x queue experiment (`WINTAP_FILEOPS_MAX_QUEUE_EVENTS=524288`) was
  robustly positive: `drops=0` sustained later in the same execution with
  backlog depth reaching ~437k, while path identity held under that backlog
  (resolution is pre-enqueue, unaffected by sender lag). Decision: the code
  default is raised to 524288 in the fop-11 slice.
- RSS accounting for the deeper queue is deferred to the upcoming longer
  execution cycle; the pidstat-collector parquet already records process/
  thread memory over time, so the number is retrievable without a dedicated
  capture.
- Accepted behavior note (for the component page at closeout): under burst
  backlog, File events reach live Esper consumers late; recorded output stays
  truthful because EventTime/firstSeen/lastSeen use kernel timestamps.
- The updated differential rerun folds into fop-11's standing A/B gate (the
  harness runs for every slice; fop-11's run covers both).

Deferred (tracked in the plan): fop-13c namespace-aware index keying; F2/F4
test-harness hardening.

## fop-11 Local Code Slice — 2026-08-25

Implemented the approved emit-first short-interval aggregation, with P3
cost-split sampling and the validated queue default riding along.

Schema decision (recorded before coding, per acceptance): `FileActivityObject`
in `shared/WintapAPI/WintapMessage.cs` gains `EventCount` (int, **default 1**
via initializer so Windows senders are safe), `FirstSeenEventTime` and
`LastSeenEventTime` (FileTime-UTC longs, 0 = unset). **Parquet columns are
unchanged** — `file.epl` already output `eventCount`/`firstSeen`/`lastSeen`;
only their sources change (`count(*)` → `sum(file.eventCount)`; min/max over
the new fields with a `case`-fallback to `eventTime` for rows that never set
them). Downstream note for Wintappy/analytics: `eventCount` now counts raw
events rather than pre-Esper rows — a semantic improvement, same column.

Code changes in `../wintap`:

- New `FileOpsAggregator` (dependency-free, internal, unit-testable):
  (pid, path, op)-keyed table, emit-first — first occurrence in a window is
  never absorbed; repeats fold into count/byte-sum/first-last-kernel-ts;
  summary emitted on window expiry, rollover, timer flush, or shutdown
  FlushAll. Identity captured at first occurrence, never at flush. Bounded
  (default 32,768 keys) with per-event bypass at cap — never loses data.
- `FileOpsSensor`: absorb hook after identity stamping and before enqueue;
  summary rows built from entry state (EventCount = repeats; first-emit rows
  carry EventCount=1 and First/Last = EventTime, so SUM conserves); byte sums
  clamped to int.MaxValue with a counter; flush timer at max(250, window/2);
  shutdown drains the aggregator before the queue closes. Config:
  `WINTAP_FILEOPS_AGG_ENABLED` (default true — the A/B kill switch),
  `WINTAP_FILEOPS_AGG_WINDOW_MS` (default 1000, matching the fop-10
  measurement window), `WINTAP_FILEOPS_AGG_MAX_KEYS` (default 32768).
- P3: every 64th `EventChannel.Send` on the sender thread is Stopwatch-timed;
  60s log gains `sender=[send_sample_avg_us=,samples=,interval=]`.
- Queue default raised 131072 → 524288 (field-validated 4x setting).
- 60s log gains `agg=[enabled,window_ms,first_emits,repeats_folded,summaries,
  cap_bypass,entries,summary_enqueue_fail,bytes_clamped]`.
- `file.epl` updated per the composition rules (cross-platform safe).

Changes in `Wintap-Analytics`:

- `compare_fileops.py`: tuple counts now weighted by the `eventCount` column
  when present (COALESCE to 1), making the standing missing-tuple gate
  count-conserving across pre/post-aggregation streams; absent column keeps
  weight 1 (backward compatible).

Tests:

- New `FileOpsAggregatorTests` (9 tests): emit-first, absorption, count
  conservation (first + repeats == raw), distinct-key isolation, window
  rollover, zero-repeat suppression, cap bypass, FlushAll drain,
  identity-from-first-occurrence. The dependency-free class is compiled
  directly into the test project (linux platform sources are excluded from
  the Wintap assembly the tests reference).
- Comparator synthetic scenarios: aggregated candidate (1+4 vs 5 raw)
  conserves → rc=0; count shortfall (1+3 vs 5) detected → rc=1.

Commands/results:

- `dotnet build wintap/Lintap.csproj` — 0 errors.
- Targeted test classes: `19/19 passed` (resolver, message, process-tree,
  aggregator).
- `python3 -m py_compile` + uv/duckdb synthetic comparator runs passed.
- Tracers unchanged this slice (no kernel edits in fop-11).

Pending field validation (acceptance):

- Deploy; A/B differential (the fop-13 rerun folds in here) with
  `--fail-on-unmatched-relative`; counter reconciliation now includes
  aggregation: kernel emitted ≈ consumed; first_emits + repeats_folded ≈
  consumed-after-filters; sum(EventCount) in output ≈ raw event count.
- Queue drops vs the fop-13-era bundles under comparable load — expected to
  collapse with 50-80% of opens (and read/write repeats) no longer enqueued.
- `send_sample_avg_us` recorded — the P3 number that decides any post-fop-11
  sender work.
- `agg=[...]` health: entries bounded, cap_bypass ~0, summary_enqueue_fail 0.

## fop-11 Field Bundle 041718 — 2026-08-25 (recorded from implementor review summary)

Same running sensor as the first two fop-11 bundles (`lintap_pid=3584692`);
includes both 5-minute smoke sessions (20260826T033507Z, 20260826T034337Z).
Reviewed against the handoff acceptance criteria:

- **Item 1 (queue-drop collapse): good.** `drops=0` throughout sampled
  lines; depth/high-water modest vs capacity=524288.
- **Item 3 (aggregation health): good in sampled windows.**
  `summary_enqueue_fail=0`, `cap_bypass=0`, `bytes_clamped` 0 (occasionally
  1-2), `repeats_folded` substantial.
- **Item 4 (ring/resolve health): mixed.** `ring_fail_total=0` holds.
  Resolve health holds in the smoke windows (misses 0-44/min). **New
  finding: late-run dir-index saturation/churn** — around 9:02:34 PM:
  `dir_index_size=16384` (the cap), `dir_index_evictions=133126`,
  `relative_open_resolve_miss=357` with `dir_index_miss=357`; at 9:17:37 PM
  evictions 144525, miss 322 (cwd_lookup_miss 316).
- **Item 5 (P3 send timing): captured.** `send_sample_avg_us` ~356-2202.
- **Items 2/6 (A/B differential, parquet sanity): not assessable from this
  bundle** (pre-collector-update capture; kill-switch run still pending).

### Designer disposition (2026-08-25)

The churn is a fop-13 structural limit exposed by runtime, not a fop-11
defect: ~133-144k evictions/interval at a pinned cap is the signature of a
filesystem walk (updatedb/backup/rpm-verify class) flooding the index with
one-shot directory identities, and the index's FIFO eviction (implemented as
a simplicity shortcut; the gap analysis specified LRU) evicts the hot
long-lived base dirs the steady-state workload depends on —
`dir_index_miss ≈ relative_open_resolve_miss` is exactly that signature.
Even degraded, misses (322-357/min) are ~4% of the pre-fop-13 floor.

Decision path: **does not block fop-11 acceptance** (queue/composition/A-B
criteria are independent and the smoke anchors stay clean); fixed instead by
a new hardening slice **fop-13d** — LRU (touch-on-hit) eviction replacing
FIFO, cap raised 16384 → 65536 with an env knob, ~10 MB worst case within
the approved memory tradeoff. Confirmation to pull from the existing bundle:
`dir_open_consumed` and `dir_open_unresolved` during the 9:02-9:17 window.

## fop-13c/fop-13d + F2/F4 Hardening Local Code Slice — 2026-08-25

Implemented all deferred hardening in one dev pass (human-directed).

Code changes in `../wintap`:

- **fop-13c (namespace keying):** the CO-RE tracer reads the opener's
  mount-namespace inum (`task->nsproxy->mnt_ns->ns.inum`, one CO-RE chain)
  and stamps it on path records (`mnt_ns` at offset 328; record grows to
  336B). The dir-identity index is now keyed `(mnt_ns, s_dev, i_ino)` — a
  bind-mount/container alias in another namespace can never satisfy a
  lookup. Fallback tier mirrors the field zeroed (its records group under
  ns 0).
- **fop-13d (LRU + capacity):** the index is extracted into a new
  dependency-free `DirIdentityIndex` class (also the F4 fix) with
  touch-on-hit LRU eviction replacing the FIFO shortcut, capacity raised
  16384 → 65536 via `WINTAP_FILEOPS_DIR_INDEX_MAX` (~10 MB worst case).
  Hot base directories now survive filesystem-walk floods; one-shot scan
  identities age out. Eviction counting moved into the class.
- **F4:** `DirIdentityIndexTests` (7 tests) — ns key isolation, LRU
  scan-flood survival of a hot entry (the exact field failure mode from
  bundle 041718), cold-entry eviction, get-refreshes-LRU, capacity/eviction
  counting, update-in-place.

Changes in `Wintap-Analytics`:

- **F2:** `compare_fileops.py` relative→absolute matcher is now
  count-consuming: exact relative matches consume candidate relative
  counts; upgrade matches consume from the candidate's absolute SURPLUS
  (candidate − baseline, so rows satisfying the strict absolute gate are
  never double-credited); longest suffix matches first ("b/c" claims
  "/a/b/c" ahead of "c").
- **Stretch — fop-13d field validation scenario:** `fileops_workload.py
  --dir-churn N` opens N distinct O_DIRECTORY handles (synthetic filesystem
  walk) while interleaving relative opens through one hot base dir;
  manifest records the expected absolute. Under LRU the hot dir's relative
  opens keep resolving during the flood; under FIFO they would miss.

Commands/results:

- Both tracer tiers rebuilt clean (mnt_ns CO-RE read accepted by clang/BTF
  locally; RHEL8 verifier check happens at deploy as usual).
- `dotnet build wintap/Lintap.csproj` — 0 errors.
- Targeted tests: 26/26 (resolver/message/process-tree 10, aggregator 9,
  dir-index 7).
- Comparator F2 scenarios: over-credit fixed (longest-suffix wins, second
  claimant unmatched), count-bounded matching (5 vs 3 → matched 3,
  unmatched 2), no-double-dip into gate-satisfying rows, prior scenarios
  regression-free.
- Workload `--dir-churn 200` smoke run produced the manifest section.

Deploy note: **this slice changes the ring record format (path record +8B).
Tracers MUST be rebuilt on the field host together with the Lintap
rebuild** — a mixed deploy (old .bpf.o + new decoder, or vice versa)
misreads the mnt_ns field.

Pending field validation:

- Post-deploy bundle: during a scan window, `dir_index_evictions` no longer
  correlates with `relative_open_resolve_miss`; miss floor returns to the
  0-131/min range; `dir_index_size` may sit at the new 65536 cap without
  miss impact.
- `--dir-churn` A/B scenario: hot-base relative opens resolve to absolute
  throughout the flood.
