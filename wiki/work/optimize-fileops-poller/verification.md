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
