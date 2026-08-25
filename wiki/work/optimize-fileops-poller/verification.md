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
