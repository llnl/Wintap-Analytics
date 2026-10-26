---
title: "Senior review: telemetry-quality round and next package plan"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/core/etl/extract/ProcessSerializer.cs
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/devtools/network_trace_smoke_test.py
  - ../wintap/devtools/network_trace_runner.c
  - ../wintap/devtools/telemetry_smoke_workload.py
  - streamlit/projects/SmokeTests/queries.py
  - streamlit/projects/SmokeTests/analysis.py
  - streamlit/projects/SmokeTests/batch_views.py
  - streamlit/projects/SmokeTests/result_store.py
  - ../Wintappy/wintap_dbt/models/silver/process_file.sql
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap; ../wintap/devtools; streamlit/projects/SmokeTests; ../Wintappy/wintap_dbt
tags: [review, telemetry-quality, package-plan, validation]
---

# Assessment

Follow-up: the user approved implementation/testing on the Ubuntu VM and preparation
for later RHEL9 RPM deployment. The bounded corrective bundle is implemented; results
and limitations are in [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]].
The recommendations below preserve the review-time findings. Deployment procedure:
[[wiki/work/wintap-telemetry-identity-and-data-quality/rhel9_validation]].

User requested a fair, critical advisory review before closing the round. Reviewed
current Wintap c0b6774 (including bba2e7c network changes) and Analytics 00dda2d,
including generators, validators, receipts, summary persistence and qualification
records. This is this round's review, not a fresh audit of every historical identity,
runtime-upgrade or pressure experiment. No production source changes or new collector
run were performed. Recommendations below are a plan, not implementation authorization.

The fixes are directionally sound: single-owner Accept/UDP protocol-return emission,
kernel-memory peer reads, arm64 errno handling, explicit process provenance, and
producer-case-preserving file projection. Original-object negative control and real
normal-ETL pilot are stronger evidence than test totals alone. The 180 managed/94
dashboard passes remain scoped; they do not establish native RHEL/x64 acceptance,
full network semantics, or exact loss/count closure.

## Findings

### 1. Confirmed relative-unlink attribution defect — bundle before package rebuild

Read-only examination of the existing final VM pilot identifies the missing expected
Delete as the fixed workload's `relative.bin`. A broader **same-host/PID/time** query
finds one Delete stored as the bare basename. This is incomplete path attribution,
not evidence that the event was never captured. The CO-RE `t_unlinkat` passes zero
instead of its `dfd`; the user-path emitter also clears namespace/base identity.
Managed relative-path resolution is applied to Open, not Delete. Absolute renamed
file deletion is not the missing case in this pilot.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §t_unlinkat, emit_file_event_user; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent; ../wintap/devtools/telemetry_smoke_workload.py §files -->

Plan: preserve event-time dirfd/base identity for unlinkat and AT_FDCWD for unlink;
reuse the directory-identity machinery conservatively. A late /proc lookup alone is
insufficient when the directory FD closes or the process exits. Test relative and
absolute names, closed/reused dirfds, short-lived workers and unresolved bases. Keep
unknown base provenance explicit. Delete currently represents syscall-entry intent;
this path fix must not silently claim successful unlink semantics.

### 2. Confirmed validator contradiction suppression — fix before acceptance

Synthetic current-code reproduction: a socket row bound by correct local/remote
ports, but with wrong directed source port and null local address, yields **zero
violations**, only incomplete-provenance warning. `evaluate_endpoint_candidates`
continues at any null before checking other known endpoint fields. Missing information
should not erase an independently provable contradiction.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §evaluate_endpoint_candidates (null-field early continue); §evaluate_case (complete-tuple predicate) -->

Plan: check each known field against consistently bound candidate roles; keep missing
fields separately incomplete. Add mixed wrong-plus-null negatives, including multiple
possible roles, without making genuinely unbound candidates falsely red.

### 3. Confirmed source-parser mismatch — fix before acceptance

Synthetic parquet normalization accepts `xPROC_START_SRC=sched_exec`, truncates
`PROC_START_SRC=sched_exec123` to sched_exec, and classifies conflicting fork/exec
tokens by the first match. Managed `ApplyStartProvenance` rejects these. Explicit
normal-process source fixes remain valid; the dashboard's Arguments fallback is too
permissive. A null explicit column can also fall back to conflicting Arguments.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §prepare_data; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §ApplyStartProvenance -->

Plan: align exact token boundaries, allowed values and ambiguity rejection; explicitly
define precedence when the column exists but is null. Prefer schema-aware fallback
only when the explicit column is absent. Preserve same-source repeat counts rather
than interpreting source-classified rows as deduplicated births.

### 4. Sampling/lifetime evidence is narrower than everyday operation

Both actual-object UDP tests and connected/unconnected canary separation deliberately
wait1.1seconds. This avoids retained one-second sampling/socket-pointer reuse effects.
`udp_rate_map` is keyed only by socket pointer, with no deletion on socket destruction
in this tracer. A rapidly reused pointer can suppress a new socket's first sample.
This is an inherited source-level risk, not newly proven live loss from this review.
<!-- GROUND_TRUTH: ../wintap/devtools/network_trace_smoke_test.py §stimulus; ../wintap/devtools/telemetry_smoke_workload.py §network_pair; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §udp_rate_map, UDP return probes -->

Plan: qualify rapid socket churn separately from intentional within-socket sampling;
test failures before success, repeated receives, concurrent callers and map cleanup.
Review the dev observer's claimed hard bound: it uses wall-clock time, and installs
signal handlers/deadline after attachment. Add an outer process deadline and monotonic
elapsed timing before treating it as a strict runtime bound.
<!-- GROUND_TRUTH: ../wintap/devtools/network_trace_runner.c §main -->

### 5. Case preservation stops short of canonical downstream identity

Wintappy retains filename but derives file_id from lower(file_path). Case-only Linux
names therefore share its derived ID despite distinct sensor paths/keys. Fix the
shared downstream formula and all dependent joins together, with Windows-specific
normalization grounded in real platform provenance. This needs Wintappy authorization.
It is a pipeline-acceptance prerequisite, not a sensor package-build prerequisite.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/silver/process_file.sql -->

### 6. Good conservative summaries need operational qualification

Summary integrity/read-back, explicit validation and fail-closed budgets are useful.
However fingerprints include the full selected object snapshot/all run manifests,
so unrelated arrivals can invalidate an old round. The row/memory limits do not cap
network bytes or elapsed scans, and max-receipt handling bounds returned receipts,
not scanned parquet bytes. Qualify summary reuse during ongoing uploads before
optimizing round-specific discovery. Keep yellow canary scope while exposing changes
in missing/contradictory checks so recurring regressions are not buried in constant yellow.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/analysis.py §input_fingerprint, read_receipts; streamlit/projects/SmokeTests/batch_views.py §canary_batch_page; streamlit/projects/SmokeTests/result_store.py §save_result -->

## Recommended sequence and stopping rule

1. Fix the two reproduced validator issues with adversarial regressions.
2. Bundle relative-unlink attribution; run an actual case-only pair through normal
   ETL (current live eight-file proof is mixed-case, while case-only key distinction
   was tested synthetically). Require exact paths, activities and distinct sensor keys.
3. Add a bounded rapid-socket qualification. Diagnose the remaining partial TCP
   EOF/close tuples separately; do not rewrite TCP byte semantics in this small bundle.
4. Freeze sensor scope after these concrete findings. Rebuild managed and all eBPF
   payloads natively for the target RHEL9 architecture, with SDK10.0.402 and existing
   DuckDB pins. Record source/package/object hashes and verify receipt operation hooks.
5. Operator-approved disposable install and independent round; require corrected
   observations, no contradictory findings, explicit skipped/unknown cases and actual
   process shutdown evidence. Then proceed to longer multi-host runs.
6. Align Wintappy IDs before claiming end-to-end case-sensitive pipeline acceptance;
   schedule broader TCP return semantics, IPv6 and resource/loss work separately.

Revise the earlier unqualified "ready for rebuild" to **small corrective bundle,
then one trusted package qualification**. Do not indefinitely postpone the package
for every known research question. If rapid-socket qualification exposes a defect
outside the bounded bundle, document the limited sampling contract and explicitly
decide whether it is compatible with the intended first package's use.

Related: [[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]],
[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]],
[[wiki/tension/linux-file-path-case-projection]].
