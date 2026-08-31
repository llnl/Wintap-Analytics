---
title: "Tenable Scan Storm: FileOps Production Response Options"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - wiki/work/improve-etl-and-qa/verification.md
  - wiki/work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30.md
policy: agent-editable
last_validated: 2026-08-31
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: file
audience: developer
status: draft
source_paths: wiki/work/improve-etl-and-qa/tenable-scan-storm-response-2026-08-30.md
tags: [feature-work, lintap, fileops, tenable, backpressure, telemetry-fidelity]
---

# Tenable Scan Storm: FileOps Production Response Options

## Observed Run

The mutable host log is retained below only as an artifact locator. Durable
evidence is the dated verification record and the hash-identified follow-up
analysis. The initial run ID was `lintap-perf-20260830`, with exact UTC window
`2026-08-30T16:17:46Z` through `17:17:45Z`. The later policy and sustainability
windows, commands, and counts are recorded in [[verification]] and
[[no-tenable-run-analysis-2026-08-30]].

The unique `lintap-perf-20260830` capture ran from `2026-08-30T16:17:46Z` to
`17:17:45Z`. FileSerializer backlog warnings did not occur, but FileOps sender
backpressure did: the bounded sender queue grew from roughly `419k` entries to
its `524288` cap, then reported continuous queue drops. At saturation, logs
also show aggregation cap bypass and summary enqueue failures. This invalidates
the run as a no-loss performance baseline.
<!-- SYNTHESIS: exact-window host evidence recorded in wiki/work/improve-etl-and-qa/verification.md and wiki/work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30.md -->

This establishes that the current storm bottleneck is upstream of the serializer:
the single FileOps sender invokes synchronous `EventChannel.Send`, whose normal
path performs attribution and Esper dispatch before returning.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §ProcessSendQueue; ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->

The operator identifies the workload as a weekly Tenable filesystem scan. Local
FileOps `comm_top` output includes scanner-like helper activity but does not
prove that one specific raw Linux `comm` value represents all scan work. Do not
hard-code a product name or infer child suppression from a parent process name
without local process-name evidence.

## Production Objective

Allow an operator to intentionally suppress a known high-volume FileOps source
before it consumes ring-buffer, user-space path-resolution, sender-queue,
resolver, Esper, and serializer capacity, while recording the exact number of
sensor-policy suppressions by configured rule and operation.

The suppression count means: covered FileOps tracepoint attempts that reached
the policy gate, matched the current configured rule, incremented that rule/op
counter, and did not create a ring-buffer record. It is not a claim about all
filesystem activity performed by a vendor product.

## Recommended Design

Implement an opt-in generic kernel-side FileOps exact-`comm` deny policy.

- Default state is disabled and an empty rule list.
- Rules match exact, case-sensitive Linux `comm` values only; reject names that
  exceed the 15 visible-byte `TASK_COMM_LEN` limit rather than truncating.
- A bounded BPF map maps each configured raw `comm` to a stable rule ID.
- A policy match occurs after intrinsic kernel filters, increments exactly one
  `policy_suppressed_attempts[rule_id, operation]` counter, and returns before
  ring-buffer reservation.
- Both CO-RE and tracepoint fallback FileOps tracers implement the same policy
  and accounting contract.
- Startup logs record policy mode, rule IDs/names, selected tracer tier, and
  policy generation. Interval logs report counter deltas alongside existing
  FileOps counters.

This uses the existing self-PID BPF-map and per-operation-statistics pattern,
but does not overload its single-PID map or counters.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §fileops_filter_pids; §fileops_stats; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §InitializeSelfPidFilter; §BuildKernelCounterSummary -->

## Rejected As Primary Policy

| Option | Reason |
|---|---|
| User-space `comm` filter | Useful as a canary, but cannot prevent ring reservation, ring loss, or sender pressure. |
| Static PID filter | Breaks on restart, misses worker children, and risks PID reuse. |
| Dynamic PID/process-tree filter | Lifecycle races, PID reuse, child exec semantics, and map cleanup make it more fragile than an exact worker-name policy. |
| Tenable-specific hard code | No source-grounded local identity contract; would hide a generic policy mechanism behind a vendor exception. |

## Required Evidence Before Enabling A Rule

1. Capture raw `comm_top` and process-lifecycle evidence during a scan.
2. Identify exact independent worker `comm` values to suppress; do not assume a
   parent name includes its children.
3. Run a user-space raw-`comm` canary first if needed, with counters but no
   kernel policy, to verify candidate scope.
4. Enable the kernel policy on a controlled host and prove:
   - policy counter deltas match a deterministic helper workload;
   - matching processes produce no FileOps parquet rows;
   - nonmatching processes retain expected rows;
   - queue drops, ring failures, and serializer drops decline;
   - FileOps count/byte conservation remains valid for the non-policy workload.

## First Host Candidate

The active `spk16` scan provides the first source-grounded candidate. Its
process tree shows `nessus-agent-module` launching multiple
`/opt/nessus_agent/lib/nessus/plugins/tenable-utils-LINUX-x86_64.bin find / ...`
workers. Their exact kernel-visible `comm` is `tenable-utils-L`, exactly 15
bytes. This is a suitable first policy rule because it names the scanner utility
itself, not a generic helper such as `find`, `rpm`, `sed`, or `sh`.

First controlled rollout value:

```text
WINTAP_FILEOPS_DENY_COMMS=tenable-utils-L
```

After restart, validate for 10 minutes while the scan remains active:

- startup logs `deny policy enabled rules=[tenable-utils-L]`;
- FileOps policy deltas for rule 1 are positive;
- sender queue depth remains materially below 524288;
- sender queue drops, aggregation cap bypass, and summary enqueue failures stay
  zero;
- non-policy FileOps paths remain visible.

If policy counters remain zero or queue pressure persists, remove the variable
and treat the result as an incomplete worker-name inventory, not as a reason to
deny generic helpers.
<!-- SYNTHESIS: exact worker identity and rollout command recorded in this durable evidence page and wiki/work/improve-etl-and-qa/verification.md -->

## First Live Policy Result

The first `spk16` rollout passed its 10-minute in-scan gate. The policy
suppressed `dir_open` attempts for `tenable-utils-L` at approximately `114102`
then `117327` per 60-second interval. The FileOps sender stayed at depths `853`
then `192`, compared with the prior run's sustained saturation at `524288`; its
drop count, aggregation `cap_bypass`, and summary enqueue failures were all
zero. The result shows that scanner directory-open identity traffic was a
dominant pressure source and that pre-ring suppression restores headroom while
non-policy FileOps events continue flowing.
<!-- SYNTHESIS: exact-window policy counters recorded in this page and wiki/work/improve-etl-and-qa/verification.md -->

The filtered one-hour capture later confirmed no FileOps sender drops,
aggregation cap bypass, summary enqueue failures, or serializer backlog
warnings while the rule was active. Its CPU/memory shape is not a policy
performance baseline because a local Wintappy DBT build overlapped the latter
half and created additional FileOps load. Preserve it as a no-loss stress
artifact; the requested repeat is analyzed below and did not produce a valid
baseline.

## Post-Capture Sustainability Result

The filtered run was loss-free only inside its exact capture window. Sender
depth rose from `7860` to `338592` during that hour, continued rising afterward,
and produced its first nonzero drop summary at `13:36:36 PDT`, about 23 minutes
after capture ended.

The subsequent `lintap-perf-20260830-no-tenable` hour had zero policy hits in
all 60 FileOps summaries, but began with sender depth `524148` and recorded
`601126` drops plus `192774` summary enqueue failures. This does not invalidate
the exact-`comm` policy's successful suppression of the observed Tenable worker.
It does show that suppressing that worker alone does not make the entire
non-policy FileOps workload sustainable through the current synchronous sender
path. Do not promote the filtered capture from controlled policy validation to
long-run deployment acceptance.
<!-- SYNTHESIS: hash-identified run and exact log window recorded in wiki/work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30.md -->

## Immediate Operational State

The current Tenable-period perf run is a valuable failure artifact, not a
deployment acceptance result. Do not use it to establish stable CPU or memory
behavior because FileOps telemetry was dropped. Preserve its parquet and log
for before/after comparison once a policy or upstream throughput change exists.

## Implementation Status

The first generic policy slice is implemented but disabled by default:

```json
"FileOpsDenyComms": ""
```

Set `WINTAP_FILEOPS_DENY_COMMS` or the JSON property only after local evidence
identifies exact worker names. The parser rejects names longer than 15 UTF-8
bytes and supports at most 15 distinct rules. Startup logs the enabled list;
60-second FileOps summaries emit `policy=[...]` with per-rule/per-operation
suppressed-attempt deltas.

Both FileOps BPF tiers contain the policy map and pre-ring gate. A configured
policy that cannot be installed fails FileOps startup, avoiding silent policy
failure.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsDenyPolicy.cs; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §InitializeDenyCommPolicy; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §fileops_deny_comms -->
