---
title: "Lintap eBPF Path, Diagnostics, and Validation Audit"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/etl/esper/file.epl
  - ../wintap/devtools/file_capture_smoke_test.py
  - validation/perf-collection/scripts/capture_lintap_perf_for_user.sh
  - validation/perf-collection/scripts/run_lintap_perf_batch.sh
policy: agent-editable
last_validated: 2026-08-30
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/improve-etl-and-qa/ebpf-path-audit-2026-08-30.md
tags: [feature-work, lintap, ebpf, diagnostics, validation, fileops, network]
---

# Lintap eBPF Path, Diagnostics, and Validation Audit

## Scope

Read-only audit of the Lintap Linux eBPF producers, user-space sensors,
EventChannel/Esper boundary, diagnostics, validation assets, and Analytics-side
performance collector wrappers. This is the source note for later canonical
developer, architect, and reviewer documentation.

## Execution Map

1. `LinuxSubscriptionManager` selects Execve, Clone, Exit, Network, FileOps,
   and ProcessRundown from the corresponding config properties. Each eBPF
   sensor derives from `BaseEbpfSensor`, loads a primary or fallback object,
   attaches its primary program, and runs a 100 ms ring-buffer poller.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §Start; ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §Start; §PollRingBuffer -->

2. Process semantics are intentionally layered rather than duplicated: Clone
   observes fork-like creation, Execve observes executable transition, Exit
   closes lifecycle state, and ProcessRundown fills the startup blind spot.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs -->

3. FileOps is the main high-volume path: kernel records enter `FileOpsSensor`,
   paths are resolved and filtered, process identity is stamped while live,
   emit-first repeat aggregation runs, then a bounded sensor queue feeds one
   sender thread. `EventChannel` respects prepopulated FileOps identity before
   sending the event to Esper. File EPL performs ten-second count/byte
   aggregation and `FileSerializer` writes Parquet.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent; §ProcessSendQueue; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs; ../wintap/wintap/core/infrastructure/EventChannel.cs §Send; ../wintap/wintap/core/etl/esper/file.epl -->

4. Direct Parquet is a sensor-path bring-up mode, not normal ETL proof: it
   returns before process resolution, registration, and Esper.
   <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->

## Intentional Layers

These overlaps are useful and should be documented as separate diagnostic
scopes, not consolidated blindly:

| Layer | Purpose |
|---|---|
| Kernel FileOps counters | Producer emission, ring failures, and kernel-side filtering. |
| FileOps user counters | Path resolution, queue state, aggregation, sender cost, and cache state. |
| Serializer diagnostics | Downstream queue drain count, duration, overlap, and Parquet backlog. |
| External perf collector | Process CPU, memory, FD/maps, and .NET runtime symptoms. |
| Network in-band diagnostics | Socket attribution STORE/HIT/MISS from the loaded tracer. |
| Process lifecycle sensors plus rundown | Distinct lifecycle truths and startup coverage. |

The FileOps aggregator is also intentional: it emits first occurrences and
only folds repeat `(PID, path, operation)` activity inside its window, preserving
count/byte semantics while avoiding delayed first-event visibility.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs §TryAbsorb; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §EmitAggregateSummary -->

## Cleanup Findings

### P0: Correct documented Linux sensor toggles

The subscription manager reads properties named `Execve`, `Clone`, `Exit`,
`Network`, `FileOps`, and `ProcessRundown`. Existing deployment documentation
uses `WINTAP_ENABLE_*_SENSOR` names that are not consumed by this path. This
makes claimed isolated-sensor runs unreliable. Align the docs/templates to the
actual config names or add supported aliases, then log the effective sensor set
at startup.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §Start; ../wintap/wintap/core/shared/ConfigManager.cs §GetValue; ../wintap/BUILD_AND_TEST.md §Linux sensor commands -->

### P1: Make fallback semantic degradation explicit

Primary CO-RE and tracepoint fallback objects do not provide equivalent data.
Examples include exit-code/thread-leader filtering, exec parent/start-time
context, FileOps inode/mount-namespace directory identity, and network
attribution/send-receive coverage. Log only the selected object today; add a
capability manifest and teach smoke tests which assertions are valid per tier.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §FindBpfObject; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/*_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/*_tracepoint.bpf.c -->

### P1: Fix Network extra-attach cleanup consistency

`NetworkSensor.Start()` can return failure after `BaseEbpfSensor.Start()` has
already loaded the object and started polling, without calling `Stop()`. FileOps
cleans up on analogous startup failure. Adopt one explicit policy for required
extra attachments and always clean up when startup is reported as failed.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §Start; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §Start -->

### P1: Repair EventChannel throughput accounting

The inline `EventsPerSecond` calculation compares a wall-clock second to an
event-count field, while a separate worker also performs rate calculation.
Treat current rate fields as untrustworthy for performance diagnosis until one
synchronized sampler replaces both paths.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send; §EventsPerSecond worker -->

### P1: Continue the bounded FileOps FD-cache work

The cache is removed by observed close and cleared at shutdown, but has no
process-exit, age, or capacity eviction. Live cardinality growth confirms this
is a long-run risk. Preserve its new metrics and add explicit bounded cleanup
with short-lived-process validation rather than silently pruning state.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §StoreFdPath; §RemoveFdPath; wiki/work/improve-etl-and-qa/verification.md §Manual Checks -->

### P2: Retire ambiguous generic BPF map polling

`BaseEbpfSensor`'s optional diagnostics discover the first globally named
`diag_counters` map with `bpftool`, which may not belong to the active sensor
object. Network's in-band diagnostic events are closer to producer truth. Keep
the map path only as a labeled cross-check, or inspect the map through the
loaded object/map FD instead.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §StartDiagMonitor; ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §diagnostics -->

### P2: Add a fidelity snapshot to the external perf collector

The perf collector captures process symptoms but not active BPF object hashes,
effective sensor/capability state, FileOps counters, serializer diagnostics,
or EventChannel drops. A performance result without these signals cannot prove
unchanged telemetry quality. Make `LINTAP_DIAG_COMMAND` a concrete periodic
diagnostic-bundle capture, or add a structured service diagnostic endpoint.
<!-- GROUND_TRUTH: validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py §main; validation/perf-collection/README.md §Current collectors -->

### P3: Remove or isolate stale `OpenAtSensor`

`OpenAtSensor` states it was moved into FileOps and is not started by the Linux
subscription manager, yet its source and tracer remain. Delete after packaging
reference verification or move it to an explicitly diagnostics-only tool path.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/OpenAtSensor.cs §header; ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §Start -->

## Perf Wrapper Review

The two scripts are intentionally distinct entry points, but currently share
similar elevation/default logic without a common implementation:

| Script | Intended use | Distinct behavior |
|---|---|---|
| `capture_lintap_perf_for_user.sh` | Root-owned systemd service | Root-side PID discovery, explicit PID, default .NET counters, ownership handoff. |
| `run_lintap_perf_batch.sh` | General/manual process capture | CLI PID discovery, optional counters, no ownership handoff. |

The focused wrapper is the right installed-service choice. The divergence is
currently operationally risky: PID discovery is duplicated, only the focused
wrapper honors `PID`, counters have different defaults, and its recursive
`chown` covers the entire supplied data root rather than only run outputs.
Consolidate PID discovery in the Python CLI, make both wrappers honor explicit
PID and a shared `ENABLE_DOTNET_COUNTERS` contract, and scope ownership changes
to files produced by the current invocation.
<!-- GROUND_TRUTH: validation/perf-collection/scripts/capture_lintap_perf_for_user.sh; validation/perf-collection/scripts/run_lintap_perf_batch.sh; validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py §discover_pid_by_substring -->

## Documentation Plan

### Developer Guide

1. Startup/effective configuration and sensor selection.
2. Kernel-to-user ABI and field provenance per sensor.
3. CO-RE versus fallback capability matrix.
4. EventChannel, resolver, Esper, serializer, and direct-Parquet boundaries.
5. FileOps operations/counter handbook.
6. Network attribution and IPv4 coverage limits.
7. Diagnostic commands and fidelity acceptance gates.

### Architect Guide

1. End-to-end architecture diagram and producer overlap policy.
2. Process identity, count/byte conservation, and fallback invariants.
3. Backpressure and loss-accounting points from ring buffer through Parquet.
4. Evidence requirements for performance changes.

### Reviewer Checklist

1. Primary/fallback tracer ABI and attachment parity.
2. Queue/filter/aggregation conservation proof.
3. EventChannel attribution and direct-mode scope.
4. Diagnostics scope, periodicity, and source identity.
5. Deployment configuration names, wrapper PID selection, and ownership safety.
