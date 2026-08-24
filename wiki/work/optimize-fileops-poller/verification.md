---
title: "Verification: Optimize FileOps Poller Event Volume"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-08-24
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: llm-agent
status: stub
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

## Known Gaps

- No results yet; feature created 2026-08-24, handed off for fop-01+fop-02.

## Follow-Ups

- Fidelity-gap backlog (rename, pread/pwrite, io_uring, failed opens) —
  see design §Fidelity-Gap Backlog; candidate next feature after closeout.
- fentry/`bpf_d_path` migration if this feature's results warrant it
  (design §Alternatives).
