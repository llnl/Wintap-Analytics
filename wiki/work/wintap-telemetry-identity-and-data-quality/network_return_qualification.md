---
title: "Network return corrections and bounded VM qualification"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/developer_docs/instructions/telemetry-quality-network-return.md
  - ../wintap/developer_docs/audits/telemetry-quality-network-return.md
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/devtools/network_trace_runner.c
  - ../wintap/devtools/network_trace_smoke_test.py
  - ../wintap/devtools/test_network_trace_smoke.py
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/wintap/core/etl/extract/ProcessSerializer.cs
  - ../wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs
  - ../wintap/tests/Wintap.Tests/TelemetryProjectionQualityTests.cs
  - ../wintap/wintap/core/etl/model/ProcessObjectModel.cs
  - ../Wintappy/wintap_dbt/models/silver/process_file.sql
  - streamlit/projects/SmokeTests/test_quality.py
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: mixed
status: draft
source_paths: ../wintap/devtools; ../wintap/wintap/platform/linux/sensor/ebpf; streamlit/projects/SmokeTests
tags: [telemetry-quality, linux, network-events, qualification, canary]
---

# Authorized follow-up, not field rollout

Latest advisory corrective bundle is complete in Ubuntu: strict legacy provenance
and partial-endpoint checks, event-time relative/cwd unlink attribution and a live
case-only pair. All29 focused receipt/hash/projection gates pass, with two TCP
provenance checks still incomplete. Rapid24-lifetime UDP qualification passes48
checks; pointer reuse remains unforced. Actual collector shutdown exits0. Full
results and broader test limitations:
[[wiki/work/wintap-telemetry-identity-and-data-quality/verification]]. Prepared later
deployment: [[wiki/work/wintap-telemetry-identity-and-data-quality/rhel9_validation]].

User authorized recommended-order implementation and iterative local VM work.
Analytics first added source-aware per-path/lifecycle/socket regressions; Wintap owns
the corrected CO-RE tracer, managed capability facts and stimulus/actual-object tools.
Supporting Lintap packaging and Wintappy remain unchanged. Private evidence is VM-local.

## Producer meaning

Accept emits at successful IPv4 accept return with accepting TGID, remote→local
orientation, and host-relative connection cache. UDP kernel `msghdr`/socket context
has one successful-return owner per operation; `msg_name` is kernel memory and the
user buffer is not read before copy-out. Failed returns do not emit, zero bytes does.
Explicit `int` sign-extension handles arm64 errno returns. Receive `msg_namelen` is
filled by the socket wrapper after the hook, so it is not a valid bound at that point;
the helper reads the kernel-supplied sockaddr_storage and checks family/read outcome.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §kretprobe__inet_csk_accept, kprobe__udp_sendmsg, kretprobe__udp_sendmsg, kretprobe__udp_recvmsg -->

UDP bytes now mean successful **protocol-function return**, not requested bytes,
packet counts, final syscall success or conservation. Core syscall-entry Send no
longer adds a duplicate partial row. Existing one-second TCP Send/Recv and UDP Send /
connected-Receive sampling remains; peer-buffer UDP receives remain unsampled. Local
socket address is best-effort, with the existing loopback wildcard interpretation.
No historical rows are rewritten/deleted and no global sampling disablement occurred.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §trace_sendto, kretprobe__udp_sendmsg, kretprobe__udp_recvmsg -->

Network startup receipts expose additive PID-restriction booleans, operation return
hook facts, sampling intervals and byte/address contracts. Version2 requires the new
core context-map marker; an older same-name object does not inherit source claims.
Hook attachment remains capability evidence, not proof of capture.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §Start -->

## Verification so far

- Idle Ubuntu arm64/kernel6.8 actual-object comparison: original object fails the
  same strict matrix that corrected object passes (**15 checks**). Accept and UDP
  send/receive modes include recvfrom, recvmsg, connected recv, zero-length,
  truncation, sendmsg and recvmmsg; nonblocking failure and oversize-send negatives,
  no duplicate successful rows, and all context maps empty. Observer hard-bound20s,
  no service/configuration management. This is not a recurring field canary.
- All12 eBPF objects compile; exact SDK10.0.402 managed build has zero errors.
  Expanded network/receipt/identity/resolver/root unit selection:159 passed, zero skips.
- Runtime normal-ETL VM startup receipt matches the exact copied rebuilt tracer and
  reports Network running/contract2. First qualification harness mistakes (wrong
  receipt phase predicate and evidence directory ownership) were exposed, not
  suppressed; five-family JSON generation succeeded but first evidence export failed.
- Corrected fresh180-second normal-ETL VM pilot delivers all five manifest families,
  zero evidence/analysis errors; local summary saved. Accept and all four independent
  UDP cases observed; exact UDP tuple/identity assertions and both dedicated TCP
  endpoint scenarios have zero missing checks/violations. All triage remains yellow
  due stimulus-only scope and outstanding limitations. No Garage upload or field-host
  operations. Timeout SIGINT wrapper returns124, not collector exit-status proof.
- Final dashboard:93 synthetic tests pass, including HTTP/S3/Streamlit persistence/
  stale behavior and18 quality regressions. Runner/adapters:17 mocked tests pass;
  Wintap source/actual-object assertion/manifest/workload tests:12 pass. Final idle-VM
  actual-object repeat also passes15 checks. Local summary integrity/read-back/latest
  verifies after final evaluator rescan; raw file size/mtime snapshot is unchanged.
<!-- GROUND_TRUTH: ../wintap/developer_docs/audits/telemetry-quality-network-return.md; wiki/work/smoke-test-dashboard/verification.md -->

## Original projection findings (before approved follow-up)

The new checks expose projection limits, not absent file activity: every one of eight
paths has all five required activities, but the prior FileSerializer lowercased non-Windows
paths; exact mixed-case identity no longer matches. Preserve uncertainty and review
[[wiki/tension/linux-file-path-case-projection]] before changing historical conventions.
The prior normal ProcessSerializer omitted `Process.Arguments`, so repeated raw Starts could not be
source-classified downstream even though Clone/Exec producers include breadcrumbs.
An additive explicit provenance column needs separate schema review; never rewrite
CommandLine or pretend each repeated Start is a new birth. TCP EOF/close still yields
partial socket tuples, which the broader candidate checks leave incomplete.
<!-- GROUND_TRUTH: ../wintap/developer_docs/audits/telemetry-quality-network-return.md §Verified (original pilot) -->

## Approved greenfield projection follow-up

On 2026-10-25 the user approved both changes, explicitly stating greenfield
development with no existing deployment/data-preservation requirement. Wintap adds
nullable `ProcessStartSource` to normal Start/Refresh parquet, from one distinct
recognized `PROC_START_SRC=` producer Arguments value. Allowed values are `sched_fork`,
`sched_exec`, `execve_or_execveat`; missing/unknown/conflicting tokens remain null.
CommandLine, process hashes, timestamps and Stop projection are unchanged. Analytics
prefers this column, retaining actual Arguments fallback for other output schemas.
No birth/exec-success claim or row suppression follows from source classification.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §ApplyStartProvenance; ../wintap/wintap/core/etl/model/ProcessObjectModel.cs §ProcessStartSource; streamlit/projects/SmokeTests/queries.py §prepare_data -->

FileSerializer now preserves producer path case, including Linux case-only names
in File_Path and sensor file-key preimages. Windows producer normalization and
pass-through remain unchanged. Locale/case-distinct key tests and production-schema
null/mixed-source parquet roundtrips guard the changes. Wintappy still folds paths
in its separate `file_id`, so downstream ID collision risk remains outside this
authorized sensor/dashboard slice; no Wintappy or historical-data edits occurred.
The sensor projection decision is resolved in
[[wiki/tension/linux-file-path-case-projection]].
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/FileSerializer.cs §SelectPath; ../wintap/tests/Wintap.Tests/TelemetryProjectionQualityTests.cs; ../Wintappy/wintap_dbt/models/silver/process_file.sql -->

### Follow-up qualification

- SDK10.0.402 managed Linux build: zero errors,177 warnings. Expanded shared
  test selection: **180 passed, zero failures/skips**. Includes recognized/missing/
  conflicting provenance, duplicate same-source tokens, unchanged identity/CommandLine,
  case-distinct Linux sensor file keys under en-US/tr-TR and actual production-schema
  parquet roundtrips with first-row null/known provenance. Initial new roundtrip test
  incorrectly indexed a null dictionary key; untyped Parquet deserialization omits
  null entries. Corrected test asserts schema presence plus TryGetValue-null; no writer
  change was necessary and mixed-row non-null source roundtrips successfully.
- Dashboard **94 tests pass**, including synthetic real HTTP/S3 and explicit-column
  precedence; legacy no-breadcrumb/CommandLine-only behavior remains unknown.
- Fresh bounded180-second normal-ETL VM pilot: all five families generate/deliver,
  zero evidence/analysis errors and violations. Eight-file, process, native clone,
  and dedicated TCP endpoint families each have **zero missing checks**. All selected
  repeated-Start groups source-classify (clone3, process13, cross-domain6 groups),
  never counted as extra births. Persisted process output contains all three allowed
  source values and nulls. Exact mixed-case eight-file observations now match.
- Cross-domain retains **three missing checks**: one expected file Delete activity
  and the two TCP Send/Recv complete-provenance checks. Do not treat these as full
  coverage or fix them by suppressing rows/relaxing expectations. All family triage
  stays yellow because these are stimulus-only canaries and other limitations remain.
- Passive Network startup is running/contract2 and copied rebuilt tracer hash matches
  receipt. Local summary/latest integrity and reload pass; raw size/mtime snapshot is
  unchanged. VM collector/actual-object observer are inactive after the bounded run.
  Timeout wrapper returns124, not collector exit-status proof. No Garage writes,
  installation/rollout or Lintap/Wintappy modifications in this follow-up.
<!-- GROUND_TRUTH: ../wintap/developer_docs/audits/telemetry-quality-network-return.md §Approved projection follow-up; wiki/work/smoke-test-dashboard/verification.md §Greenfield projection follow-up -->

## Boundaries and next gate

Actual-object checks do not establish managed identity/normal-ETL acceptance. Even a
successful VM pipeline pilot would not prove the deployed RHEL object shares this
source: trusted installed-package provenance and operator-approved review/install
remain separate. Field collectors are left running unchanged. TCP Disconnect listener
tuples, IPv6, non-loopback wildcard IP, pointer-reuse/sampling, final-syscall failures,
historical-loss closure and exact count/resource/deadline equivalence remain open.

Related: [[wiki/work/wintap-telemetry-identity-and-data-quality/quality_followup_analysis]],
[[wiki/tool/smoke-test-results-dashboard]], [[wiki/schema/runtime-capability-receipt]],
[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]].
