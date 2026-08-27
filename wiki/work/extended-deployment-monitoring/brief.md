---
title: "Extended Deployment Monitoring: Retention + FileOps Acceptance"
type: concept
confidence: high
grounded_by:
  - wiki/work/optimize-fileops-poller/test_plan.md
  - extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/extended-deployment-monitoring/brief.md
tags: [feature-work, monitoring, acceptance, lintap, retention, file-events]
---

# Extended Deployment Monitoring: Retention + FileOps Acceptance

The long-running acceptance testing for the two 2026-08-27-closed
features ([[wiki/work/fix-unbounded-process-table-growth/brief]],
[[wiki/work/optimize-fileops-poller/brief]]), shifted to a parallel
task by human decision 2026-08-27: the branch ships via PR now (the
Windows developer needs the changes; no production deployments exist),
and confidence finalizes over ~a few weeks of test deployments on many
hosts with varied workloads. Expect short, focused patch cycles out of
each status check — that is the intended cadence, not a failure of the
closeout.

## Cadence

Human status check every 1-2 weeks per test host:

1. Run `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`.
2. Check, from the bundle (details in
   [[wiki/work/optimize-fileops-poller/test_plan]] T3/T5/T6/P2):
   - `process` rows in the ~50k band, open rows small,
     `process_retention_telemetry` bounded (P2);
   - `fileops-parquet-sanity.txt`: `raw_events > rows`,
     `zero_first_seen_rows = 0` (T5);
   - counters: `ring_fail_total=0`, queue `drops=0`,
     `summary_enqueue_fail=0` (T3);
   - `backlog limit reached` count ≈ 0 (T6 / fop-14 watch).
3. Record each check as a dated entry in wiki/log.md (host, bundle
   path, the four checks, any anomaly).

## Exit Criteria (final acceptance)

- ≥3 hosts with distinct workloads, ≥3 weeks total, all four checks
  green on every status pass (or every anomaly root-caused and patched
  with a green re-check).
- Then: record final acceptance in both closed features'
  verification.md and close this task.

## Carried Watch Items

- fop-14 serializer-cap sizing: reopen only if T6 shows sustained
  backlog drops (prior severity number was measured under the EPL bug).
- ~1% open+close capture flake: track that it stays ~1% and
  phase-symmetric; a growth trend is a capture-fidelity regression.
- **ACME dataset check** (one-time): confirm whether any consumed
  dataset contains pre-0e01783 File/Registry parquet (n²-inflated
  eventCount). Likely not a practical problem — no production
  deployment since long before the fix — but verify before anyone
  re-baselines analytics on historical data.
