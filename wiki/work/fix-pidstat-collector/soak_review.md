---
title: "Four-hour Go pidstat VM soak review"
type: diagnostic
confidence: high
grounded_by:
  - ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/retained/state.json
  - ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/retained/inspection.json
  - ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/review-summary.json
  - ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/decoded-review.json
  - ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/log-review.json
  - ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/retrieval.json
policy: agent-editable
last_validated: 2026-10-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: mixed
status: draft
source_paths: validation/pidstat-loop; ../Lintap/pidstat-go
tags: [pidstat, go, soak, resource-measurement, smoke-test, ubuntu, arm64]
---

# Outcome

**The scoped four-hour default-cadence Ubuntu arm64 collection check passes.**
This is same-session technical review, not human acceptance of fpc-03 or permission
to package. No collector changes were made for this run.

The current Wintap checkout's Linux sensor build ran throughout collection. Go
pidstat and the independent existing smoke runner used isolated data/evidence.
No package installation, shared service restart, upload or consumer change.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/retained/state.json -->

## Dataset checks

| Check | Observed result |
|---|---|
| Actual collection duration | 14,400.022 seconds |
| UTC interval | 2026-10-31 05:18:50–09:18:50 |
| Local interval, America/Phoenix | Oct30 22:18:50–Oct31 02:18:50 |
| Cadence / rotation / compression | 5 seconds / 300 seconds / ZSTD |
| Closed pidstat files / rows | **49 / 399,312** |
| Distinct sample times | **2,880**, every gap exactly5seconds |
| Per-sample process rows | min136 / median138 / max146 |
| Physical and DuckDB schema | All49files match the actual Python reference, all26columns |
| Partition/window errors | 0; contiguous300-second windows, including midnight |
| Duplicate identity/time groups, including across files | 0 |
| Remaining pidstat active/spool/journal state | None; lock file alone remains |
| Final SIGTERM-sealed file | 6,484rows, local02:15:00–02:18:50 |
| Shutdown | Smoke, Go pidstat and Lintap exit0; no forced kills |

The first partial window has1,788rows; the final partial window has6,484rows.
Container runtime/id are null in every row; all other columns have zero nulls.
This is observed host coverage, **not** container-attribution workload qualification.
Every row was decoded with non-finite metric rejection. Per-file hashes, null counts,
schema results and timestamps remain in `retained/inspection.json`.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/retained/inspection.json -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/decoded-review.json -->

## Resource observations

479 independent, approximately30-second `/proc` observations had no read errors.
CPU below is **percent of one core**, not percent of the4-core host. Peak CPU is an
interval average, not an instantaneous maximum; RSS peaks are sampled observations.

| Process | Median CPU | Peak30s CPU | Median RSS | Peak RSS | Peak threads |
|---|---:|---:|---:|---:|---:|
| Go pidstat | 0.47% | 0.80% | 16.97MiB | 44.86MiB | 10 |
| Lintap | 1.36% | 35.15% | 495.27MiB | 620.23MiB | 50 |

Go's elapsed-hour median RSS was16.70,16.96,17.03,17.03MiB; sampled peak RSS stayed
around44–45MiB. There is no evident sustained RSS ratchet in this run, but four
hours of modest canaries does not prove leak-freedom under other loads. No children
of either collector were seen in the30-second observations; transient children or
sensor thread-event noise were not exhaustively audited.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/retained/inspection.json -->
<!-- SYNTHESIS: bounded memory observation from ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/review-summary.json -->

Decoded pidstat rows independently contain all2,880samples for both collectors.
Go's raw5-second median/max CPU is0.40%/1.96%; Lintap's is1.23%/83.00%. Raw sampled
RSS and the independent30-second measurements have different observation times;
their different maxima are not an equivalence failure or a paired-live tolerance.
There is **no equivalent Python live-resource baseline**, so no improvement claim.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/decoded-review.json -->

## Smoke activity and sensor output

16 rounds of five families: **80/80 exit0 and `recorded`**. Named cross-domain,
process lifecycle, eight-file, native clone and same-host TCP endpoint canaries all
ran every approximately15minutes plus sequential round duration. This proves
stimulus generation and durable local manifests, **not full sensor capture**.

436 retained sensor/manifest Parquet files all read successfully:

| Domain | Files | Rows |
|---|---:|---:|
| raw_host | 5 | 5 |
| raw_macip | 5 | 5 |
| raw_process | 80 | 6,105 |
| raw_process_conn_incr | 66 | 2,619 |
| raw_process_file | 40 | 148,670 |
| raw_smoke_test | 240 | 240 |

Lintap stayed alive throughout. Retained log reports show zero maxima for the
reported serializer `dropped_total`, FileOps `drops` and `summary_enqueue_fail`;
these do not certify uninstrumented kernel loss or every expected smoke event.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/review-summary.json -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/log-review.json -->

### Findings retained, not hidden by the collection pass

- FileOps is partial: legacy open/unlink tracepoints are absent on this arm64
  kernel; available primary/openat and other auxiliary hooks attach.
- SELinux filesystem is absent on Ubuntu; SELinux startup failed as reported.
- Source configuration includes a disabled, unresolved `SignedS3UrlAdapter`;
  startup logs one adapter-resolution error despite the disabled adapter. All
  upload adapters remain disabled; upload delivery was intentionally not tested.
- Startup has disabled-UI/plugin/inference warnings; one best-effort unknown-parent
  warning appears. These are retained sensor findings, not Go collector failures.
- Go log has no error/failure/panic/eviction entries and shows final signal seal.
- Startup readiness-harness failure and incidental shared NuGet restore are
  documented in [[wiki/work/fix-pidstat-collector/verification]]; no repair or
  restoration of an uncaptured pre-existing lockfile diff is claimed.

## Retained evidence and next gate

Local root: `validation/pidstat-loop/evidence/four-hour-20261031T0520/`.
Read `retained/inspection.json`, `review-summary.json`, `decoded-review.json`,
`log-review.json` and `retrieval.json`; raw datasets/logs are private and ignored by
Git. Guest originals remain at `/var/tmp/pidstat-four-hour-20261031T0520`.

Archive SHA256:
`5e324a0fe0f3c8607ae8e04617ba907fc81489c49ba845668f77d0a5d0757ab1`.
Transferred19,773,414bytes; safely extracted969regular files/51,538,189bytes.
Initial SFTP failed to traverse the root-private parent. A separate Ubuntu-owned
0700directory/0600archive copy fixed retrieval; original permissions/data unchanged.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence/four-hour-20261031T0520/retrieval.json -->

**Packaging remains on hold for human review.** Exact identical-input Python
comparisons already have their earlier evidence; this run adds sustained sampling,
rotation, midnight placement, graceful seal and measured resources. Paired-live
Python comparisons, equivalent-load comparative resources, canonical DBT, original
pytest, package/service integration and native RHEL/amd64 remain separate gates.

Related: [[wiki/work/fix-pidstat-collector/verification]],
[[wiki/work/fix-pidstat-collector/implementation_plan]],
[[wiki/work/fix-pidstat-collector/dev_handoff]].
