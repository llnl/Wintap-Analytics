---
title: "Closeout Test Plan: grantj-rhel8-testing Branch (fop + process-table retention)"
type: concept
confidence: high
grounded_by:
  - Wintap-Analytics/validation/fileops-differential/run_fop11_ab.sh
  - Wintap-Analytics/validation/fileops-differential/compare_fileops.py
  - Wintap-Analytics/extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh
  - ../wintap/tests/Wintap.Tests
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: mixed
status: reviewed
source_paths: wiki/work/optimize-fileops-poller/test_plan.md
tags: [feature-work, file-events, ebpf, linux-sensor, test-plan, closeout]
---

# Closeout Test Plan: grantj-rhel8-testing Branch

The critical milestone tests for everything the branch changed, across
both features: [[wiki/work/fix-unbounded-process-table-growth/brief]]
(P-tests below: resolver retention/reconciliation, telemetry bounding,
CloneSensor thread-clone filter) and its FileOps subtask (T-tests):
kernel tracers + filters (fop-01..07), the decoupled poller/sender
(fop-08/09), runtime measurement (fop-10), emit-first aggregation with
count/byte conservation (fop-11), relative-path ground truth + the LRU
dir-identity index (fop-12/13), and the Esper EPL grouped-output fix
(`file.epl`/`registry.epl` AgentId, `../wintap` 0e01783).

**Supersedes** the per-slice tests in
[[wiki/work/optimize-fileops-poller/implementation_plan]] §Tests: the
counter-reconciliation, burst, fd-cache-boundedness, fallback-tier, and
timestamp-sanity items were one-time slice proofs, recorded in
[[wiki/work/optimize-fileops-poller/verification]]; their regression
surface is covered by T2/T4/T5 below. If a T-test fails, dig into the
superseded material then.

## T1 — Build + unit smoke (dev box or field host, ~2 min)

```bash
cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make
cd ../wintap && dotnet build wintap/Lintap.csproj
dotnet test tests/Wintap.Tests/Wintap.Tests.csproj \
  --filter "FileOpsAggregatorTests|DirIdentityIndexTests|ProcessResolverTests"
```

Expected: both tracer tiers build (CO-RE + tracepoint fallback), 0 build
errors, all filtered tests pass. Covers: aggregator conservation
semantics, LRU dir-index behavior, resolver identity.

## T2 — Harness self-test, no sensor needed (any machine with uv, ~3 min)

```bash
validation/fileops-differential/run_fop11_ab.sh --simulate /tmp/fop11-sim
```

Expected: `VERDICT: PASS`, exit 0. Proves the A/B harness plumbing and
all three comparator invariants (distinct tuples, count conservation
weighted by eventCount, byte conservation) against synthetic fixtures —
run this after ANY harness/comparator change before trusting a field run.

## T3 — Field deploy smoke (spk16-class host, ~5 min)

After deploy + `systemctl restart lintap`, wait ~2 min, then:

```bash
sudo grep 'FileOps counters' /var/log/lintap/Logs/Lintap.log | tail -1
```

Checklist on that one line: `agg=[enabled=true, ...]` present;
`ring_fail_total=0` for every op; `queue=[... drops=0 ...]`;
`summary_enqueue_fail=0`, `cap_bypass=0`; and no
`ERROR`/`backlog`/`dropped=` lines elsewhere in the log
(`sudo grep -cE 'dropped=|ERROR' .../Lintap.log`). NB: the log is
truncated on every service restart (LogType.Overwrite) — capture
evidence before restarting.

## T4 — fop-11 kill-switch A/B differential (field host, ~15 min) — THE milestone test

```bash
sudo validation/fileops-differential/run_fop11_ab.sh
```

Expected: `VERDICT: PASS`, exit 0. One command runs both phases
(aggregation OFF baseline via the kill switch, ON candidate), a
deterministic workload (per-file open/write/read/mmap/delete rounds,
dirfd-relative opens, dir-churn flood of the identity index), harvests
by firstSeen window + prefix, and verifies the full contract:

- count conservation, eventCount-weighted, with a documented 1%
  missing tolerance for the known phase-symmetric open+close capture
  flake (see log 2026-08-27) — anything above 1% is a real failure;
- byte-total conservation (strict, zero deficit);
- relative-path tuples upgrade-matched (strict);
- vacuous-run and serializer-backlog guards (exit 2/3 are not passes).

It self-quiesces the S3 upload cycle and restores production config
(aggregation ON, env clean) on any exit. Exit codes: 0 PASS, 1 FAIL,
2 vacuous/no data, 3 backlog-invalidated. On failure, the results dir
(`/var/tmp/fop11-ab-results-<ts>/`) holds everything: `summary.txt`,
`result.json` (missing/added/byte-deficit samples), per-phase parquet,
per-phase `*-lintap.log` + `*-counters.log` snapshots (taken before the
restarts that would truncate them). This test also carries the fop-08
and fop-13 differential obligations.

## T5 — Collector parquet sanity (field host, ~5 min)

```bash
sudo extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh
cat <bundle>/duckdb/fileops-parquet-sanity.txt
```

Expected in the composition check: `raw_events > rows`,
`aggregated_rows > 0`, `max_event_count > 1` (aggregation composed
through Esper into parquet), and `zero_first_seen_rows = 0`
(timestamp sanity). If `rows == raw_events` on a loaded host, suspect
the EPL grouped-output fix is missing from the deployed build
(pre-0e01783 symptom is the reverse: eventCount inflated n² per group).

## T6 — Long-term watch (extended test deployments; fop-14)

Not a gate — the standing observation during longer deployments:

```bash
sudo grep -c 'backlog limit reached' /var/log/lintap/Logs/Lintap.log
```

Zero or near-zero expected in normal operation post-EPL-fix. Sustained
nonzero during heavy windows reopens fop-14 (serializer/parquet-writer
cap sizing; env knobs `WINTAP_ETL_MAX_QUEUE_EVENTS_*` exist). Also
worth a periodic glance: `open: no_path` in the counters — the residual
~1% open/close capture flake documented in the 2026-08-27 log entry.

## P1 — Process-creation harness (dev box or VM, ~5 min)

```bash
cd validation/process-creation && uv run pytest
```

Expected: all tests pass (workload, evaluator, schema, lintap
normalizer). Covers: process event correctness end to end — the
regression surface for resolver retention, rundown reconciliation, and
the CloneSensor thread-clone filter.

## P2 — Process-table boundedness (field host; free with the T5 bundle)

In the diagnostics bundle, read `duckdb/event-table-counts.out`:

- `process` rows in the ~50k band (2026-08-16 baseline: 47,648 rows,
  1,977 open / 45,671 closed) — NOT millions (the pre-feature failure
  was 8M rows/10 days);
- open rows a small fraction of total (thousands, not tens of
  thousands) — stale-open reconciliation working;
- `process_retention_telemetry` bounded (the aggregation/retention fix),
  not growing per-sweep.

Order-of-magnitude growth in any of these on a long-running host reopens
the retention feature.

## P3 — Deep-dive long run (VM; only when P1/P2 flag something, ~hours)

```bash
validation/process-creation/scripts/run_lintap_currentish_long_run.sh
python3 validation/process-creation/scripts/summarize_currentish_long_run.py --run-dir /tmp/validation-runs/<run-id>
```

Expected: `live_pids_missing_open_row == 0`, low `stale_open_rows`, no
surprising `reconciled_closed` jump. This is the diagnostic tool, not a
routine gate — spk16's continuous operation is the standing long run.

## Run cadence

- Every sensor or harness change: T1 + T2; P1 when the process path is
  touched.
- Every field deploy: T3, then T4 when the change touches the FileOps
  path (events, aggregation, serialization, EPL).
- Per diagnostics bundle: T5 and P2 come free with the collector.
- T6 continuously during long-running test deployments; P3 on demand.
