---
title: "Clone lifecycle validation results"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/devtools/validate_clone_trace.py
  - ../wintap/devtools/validate_clone_pipeline.py
  - ../wintap/devtools/clone_lifecycle_workload.c
  - ../wintap/tests/Wintap.Tests/ProcessResolverTests.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: reviewed
source_paths: ../wintap/devtools; ../wintap/tests/Wintap.Tests
tags: [clone, clone3, process-events, validation]
---

# Clone lifecycle validation results

Cross-domain capability and interpretation reference:
[[wiki/diagnostic/linux-capability-data-quality-matrix]].

Follow-up to [[wiki/work/improve-lintap-data-quality/clone-validation-plan]],
authorized on the current feature branches. Wintap owns implementation/harnesses;
Analytics owns these records. Lintap packaging and enable defaults are unchanged.

## Evidence

Disposable Multipass `lintap-clone-validation`: Ubuntu 24.04, aarch64,
kernel `6.8.0-147-generic`, libbpf 1.3.0, clang 18. Generated binaries, copied
build tree and reports remain in VM-native `/home/ubuntu/clone-validation`.
The mounted checkout was not used for build output. No field hosts modified.

Each workload has 80 process births (20 each fork-only, fork+exec,
worker-thread fork, clone3 process) and 60 threads (20 each pthread, legacy
clone thread, clone3 thread). **No clone3 skips on this host.**

| Run | Missing processes | False thread births | Wrong worker parent |
|---|---:|---:|---:|
| baseline2, original object | 0 | 40 (pthread + clone3) | 20 |
| core, new CO-RE object | 0 | 0 | 0 |
| fallback, updated tracepoint + optional hooks | 0 | 0 | 0 |
| fallback-no-hooks, primary only | 0 | 60 | 0 |

The baseline runner initially failed because arm64 has no `sys_enter_vfork`;
it was corrected to match the sensor's optional-hook policy. Logs preserve that
failure. The CO-RE object filters child pid != tgid before publishing and uses
parent tgid. The fallback now captures clone3 user flags and parent TGID, but
missing auxiliary hooks still mean ambiguous flags, not reliable process births.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c §trace_process_fork -->

`pipeline4` and the rebuilt final `pipeline-final` used the compiled Linux app and both sensors, then inspected
direct-parquet writer staging. All 80 births appeared, no thread starts appeared,
and all 20 fork+exec children shared one PidHash across **three** Start records:
fork, exec syscall entry, successful sched exec. Raw observations are preserved;
distinct-process analysis must not count raw Start rows as distinct processes.
Registration and Esper were deliberately bypassed; normal ETL/package acceptance
is not established by this run.

Test-harness corrections retained in earlier reports: `pipeline` looked only
in published data although ETL-disabled output stays in runtime staging;
`pipeline2` compared a whole Arguments string rather than its source token and
incorrectly expected two records; `pipeline3`'s fixed delay missed the first
seven iterations before sensor registration. The corrected harness waits for
both registration log entries and checks fork/sched-exec coverage without
throwing away exec-entry observations. This startup result is not sensor loss.

## Resolver behavior

Five new xUnit cases: an unmarked duplicate characterizes the old metadata
overwrite, then four Clone/Exec order × stopped/not-stopped cases verify one row,
exec name/path/command/hash retained, Stop time retained, and no late-clone
active-cache resurrection. Clone now marks `PROC_START_SRC=sched_fork`; an
existing identity rejects that provisional upsert. Other sources retain their
previous update behavior. Raw event publication/serialization is not deduplicated.
<!-- GROUND_TRUTH: ../wintap/tests/Wintap.Tests/ProcessResolverTests.cs §CloneAndExec_KeepOneIdentityAndExecMetadata -->

## Commands and outcomes

From Wintap root:

```bash
dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter FullyQualifiedName~ProcessResolver --no-restore -v quiet
dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --no-build --no-restore -v quiet
git diff --check
```

Focused: **88 passed**, zero failures/skips. Broad macOS run: **603 passed,
16 failures, then test-host aborted** in `ETWTraceEventSource.Finalize`.
Failures include Windows SID/path/ETW tests and the state-template agent-ID
test against a pre-existing modified state file. Do not claim a green full suite
or discard that state file. The unrelated failures were not repaired here.

VM-native build:

```bash
dotnet build /home/ubuntu/clone-validation/source/wintap/Lintap.csproj -v quiet
make -C /home/ubuntu/clone-validation/source/wintap/platform/linux/sensor/ebpf/tracers all
make -B -C /home/ubuntu/clone-validation/source/wintap/platform/linux/sensor/ebpf/tracers clone_tracer.bpf.o clone_core_tracer.bpf.o
```

Linux build: zero errors, 589 warnings initially and 560 in the final incremental
build. Final build plus `pipeline-final` passed after the ERR_PTR safety fix.
Initial tracer build exposed
missing multiarch headers (`asm/types.h`); Makefile now supplies compiler-selected
multiarch include search through CPATH. Forced rebuild of both clone objects
passes without a manual CPATH override; all tracer objects built with the override
before that build-system correction.

Repeatable live commands (VM paths; each output directory must be fresh):

```bash
cc -O2 -pthread -o /home/ubuntu/clone-validation/workload /home/ubuntu/wintap/devtools/clone_lifecycle_workload.c
cc -O2 -o /home/ubuntu/clone-validation/runner /home/ubuntu/wintap/devtools/clone_trace_runner.c -lbpf
sudo python3 /home/ubuntu/wintap/devtools/validate_clone_trace.py --object /home/ubuntu/clone-validation/core.bpf.o --runner /home/ubuntu/clone-validation/runner --workload /home/ubuntu/clone-validation/workload --output /home/ubuntu/clone-validation/core-repeat
sudo /home/ubuntu/clone-validation/venv/bin/python /home/ubuntu/wintap/devtools/validate_clone_pipeline.py --dll /home/ubuntu/clone-validation/source/wintap/bin/Debug/net8.0/Lintap.dll --workload /home/ubuntu/clone-validation/workload --output /home/ubuntu/clone-validation/pipeline-repeat
```

## Limits / next deployment gates

- This confirms Ubuntu arm64 behavior only; Fedora attach root cause, RHEL,
  x86_64, namespaces, performance/fork storms and long-running PID reuse untested.
- BTF absence/load/attach failure selects the existing tracepoint fallback;
  libbpf ERR_PTR attach results are now rejected without destroying invalid links.
- Packaging builds glob tracer payloads, but explicit package validation lists
  do not yet require the new CO-RE clone object. No fresh package build was run.
- Missing `/proc` can still produce identity/enrichment approximation for very
  short-lived processes. Same-PidHash results here do not prove universal parity.
- Standard ProcessSerializer does not persist Arguments breadcrumbs, although
  direct parquet does. No shared output schema was changed in this follow-up.
