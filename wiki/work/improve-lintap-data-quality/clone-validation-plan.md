---
title: "Post-closeout plan: Clone lifecycle validation"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: draft
source_paths: ../wintap/devtools; ../wintap/tests/Wintap.Tests
tags: [lintap, process-events, clone, validation]
---

# Clone lifecycle validation

User-authorized follow-up on the existing branches, not a reopening of the
completed data-quality acceptance criteria. No packaging default change.

## Test contract

1. Characterize fork+exec as multiple observations of one process identity, not
   independent processes. Live validation found three: fork, exec entry, and
   sched exec. Preserve raw observations; do not discard exec
   metadata merely to reduce row counts.
2. Replay Clone→Exec, Exec→late Clone, and Stop→late Clone into the real resolver.
   Require one identity row, exec metadata not overwritten by inherited clone
   metadata, and durable exit time retained.
3. A manifest-producing Linux workload records getpid/gettid, parent IDs and
   outcomes for fork without exec, fork+exec, pthreads, legacy clone threads,
   clone3 threads/processes, and forks initiated by a non-leader thread.
   Unsupported clone3 is an explicit skip, never a pass.
4. Attach the actual compiled clone objects with a small libbpf runner. Compare
   kernel event child IDs against manifest TGIDs/TIDs; require every successful
   process birth and zero thread-only births. Exercise ordinary and intentionally
   absent auxiliary syscall hooks separately.
5. Prefer authoritative kernel child pid/tgid classification on BTF hosts;
   maintain tracepoint-only fallback compatibility. No shared schema/identity
   algorithm changes. Capture fallback limitations rather than assert parity.
6. Build the Linux application and run focused xUnit regressions. Record exact
   host/kernel, objects, commands, skips, and negative baseline before claiming
   live validation. Existing production/field hosts are not used for experiments.

## Checklist

- [x] Baseline live thread/clone3 capture
- [x] Duplicate observation and resolver ordering regressions
- [x] Evidence-supported classification/metadata fixes
- [x] Rebuilt-object live comparison and Linux build
- [x] Document durable semantics and remaining platform gaps

Results and repeatable commands: [[wiki/work/improve-lintap-data-quality/clone-validation-results]].

## Environment

A new disposable Ubuntu 24.04 arm64 Multipass instance,
`lintap-clone-validation`, was created because the prior `lintap-quality`
instance no longer exists. The Wintap checkout is mounted read/write at
`/home/ubuntu/wintap`; generated test binaries/results stay in native VM storage.
Existing modified state files and unrelated untracked files are preserved.
