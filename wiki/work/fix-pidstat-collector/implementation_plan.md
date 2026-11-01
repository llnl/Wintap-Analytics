---
title: "Implementation Plan: Fix pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../Lintap/tests/test_pidstat_collector.py
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: developer
status: draft
source_paths: wiki/work/fix-pidstat-collector/implementation_plan.md
tags: [feature-work, pidstat, go, engineering-loop, verification]
---

# Implementation Plan: Fix pidstat Collector

## Scope

Implement [[wiki/work/fix-pidstat-collector/brief]] in bounded units `fpc-01` through
`fpc-05`. First live environment: existing Multipass `lintap-dev` (Ubuntu arm64).
Do not recreate the VM, stop existing services or change shared data without approval.
This document is a plan, not current implementation authorization.

## fpc-01 — Freeze compatibility and prove binary/Parquet feasibility

1. Read Lintap's applicable AGENTS.md and current source/test/package files; inventory
   local changes and guest state. Read canonical Wintappy sources in `../Wintap-PyUtil`.
2. Select a small Go module location consistent with Lintap's layout, pure-Go Parquet
   writer with ZSTD, and pinned supported Go version. Record license and dependency
   choices. No DuckDB Go binding or cgo in the collector.
3. Preserve the current Python version/revision as the reference through final review.
   Generate authoritative golden output from its actual execution in `lintap-dev`,
   including real `/proc` samples and resulting TSV/Parquet. Hand-built expected rows
   supplement this baseline but cannot replace it. Python/DuckDB are allowed for
   testing, not installed runtime needs.
4. Encode the same rows in Go, inspect both with DuckDB, and compare types and values.
   Build arm64 and amd64 using `CGO_ENABLED=0`; inspect ELF linkage and execute arm64
   in the guest. Stop and revisit design if compatibility/static output fails.

**2026-10-30 checkpoint:** technical spike complete and human-approved.
Go1.27.3/parquet-go0.32.0 initial writer-only implementation in `../Lintap/pidstat-go` passed
exact comparison of captured Python TSV (266,705,1640 live rows), supplemental writer
fixtures, both static builds and arm64 guest execution. The Go raw-input sampler replay
and paired-live requirements below belong to later units; they are not satisfied by
TSV encoding. See [[wiki/work/fix-pidstat-collector/verification]].

### Required Python-versus-Go differential evidence

- Capture multiple real `/proc` snapshots and sample times from controlled live
  workloads in `lintap-dev`: idle, CPU (including multicore), memory, I/O and process
  churn, with cgroup/namespace observations where available. Preserve raw inputs,
  clock tick/page-size/memory context and the Python-produced results. Replay the
  **same inputs and elapsed times** through both samplers/writers. Exercise the real
  Python implementation, not a Go reimplementation of its formulas as the oracle.
- Compare decoded output row-for-row, all 26 columns, row multiplicity, local times,
  types, rounding/nulls, partition placement and window membership. Exact equality
  is the replay gate; file bytes/compression layout and process-specific collision
  suffixes need not match. Any numeric tolerance beyond the existing REAL encoding
  must be justified and approved, never added after a failure just to pass.
- Also run Python and Go alongside the same real workloads with separate data/spool
  roots and matching configuration. Compare stable common process identities using
  PID/starttime evidence kept in the test harness (do not add raw schema columns).
  Declare time-alignment and absolute/relative rate tolerances **before** the run;
  live reads cannot be expected to observe identical counters at identical instants.
- Report unmatched/missing/duplicate rows, baseline/new-PID behavior, every field's
  mismatch count and maximum error, plus classified timing/churn differences. Never
  drop unmatched rows or broadly whitelist fields to manufacture parity. Escalate
  unexplained differences; synthetic tests or mere readability are insufficient.
- Review must inspect actual Python and Go datasets and the comparison report, not
  just a test pass count. Retain hashes, revisions, commands and evidence paths.

### Compatibility facts to capture

Current output has 26 columns: `time`; `uid`, `pid`; CPU/rate/memory metrics;
`command`, `hostname`, `cgroup_path`; nullable `pid_ns_inode`, `container_runtime`,
`container_id`. The spool has 27 fields because date and sample time are separate.
The writer casts rates to REAL, UID/PID/core/iodelay to INTEGER, VSZ/RSS/namespace
inode to BIGINT, text to VARCHAR, and combined local date/time to TIMESTAMP.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector.py §TSV_COLUMNS, convert_spool_to_parquet -->

Do not substitute DOUBLE, UTC-normalized timestamps or empty strings for nulls
without a deliberate scope amendment. Test timestamp logical annotation and reader
behavior, not just names. Current TSV rates round to two decimal places before
REAL conversion. Match observable rounding with fixtures, including ties.

## fpc-02 — Port /proc sampler and configuration

- Preserve all-process sampling, baseline-only first/new-PID samples, reuse keyed by
  PID/starttime, guest-excluded user CPU and core-summed total CPU, schedstat wait,
  page faults, context switches, memory and I/O rates.
- Inject proc root and time sources for tests; handle process exit/permissions and
  malformed records without crashing the run. Preserve optional-field behavior;
  correcting missing-data semantics is outside this rewrite.
- Resolve clock ticks without cgo or a subprocess (investigate Linux `AT_CLKTCK`
  from auxiliary vector); do not silently hardcode a tick frequency. Use actual page
  size. Test clock/page assumptions explicitly.
- Keep cgroup v1/hybrid and v2, runtime pattern matching and namespace inode behavior.
  Bound new caches to live process identities; report any observable semantic delta.
- Preserve roots `/var/log/lintap/{data,runtime}`, raw `raw_sensor/pidstat` location,
  `PIDSTAT_*` path overrides, hostname and limits.
- Defaults: sample 5s; rotation uses explicit pidstat override then upload interval
  then 300s, minimum rotation 300s; byte cap 1GiB, age cap disabled. Use monotonic
  scheduling/rate duration and wall clock for recorded local time and partitioning;
  test wall-clock jumps and document any intentional difference from old behavior.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector.py §Config, ProcSampler -->

**fpc-02 checkpoint (2026-10-30):** sampler/configuration human-approved.
Three actual raw captures pass exact replay (266/705/1640rows),
two52-row Python-controlled kernel-context fixtures and17config cases match;
14Go tests/vet/module checks and native arm64 raw replay/bounded411-row diagnostic
pass. Source sample epoch, not rounded timestamp, controls rotation. See verification
for declared malformed-counter/cache/monotonic differences.

## fpc-03 — Port durable spool, rotation and Parquet writer

- Prefer retaining `current.tsv`, `current.meta`, and pending TSV/meta format for
  restart/upgrade recovery. Keep spool outside the uploader-swept tree.
- Preserve epoch-aligned windows and local `dayPK=YYYYMMDD/hourPK=HH` partition
  interpretation, filename conventions and collision handling.
- Write `.active`, close the Parquet writer successfully, then atomically publish
  `.parquet` on the same filesystem; remove source spool only after publication.
- Preserve failed conversion input for retry; never publish a partial file. Test
  interrupted metadata/spool transitions and truncated input; do not invent rows
  or discard malformed pending data silently. Document crash vs power-loss guarantees.
- Test SIGTERM/SIGINT sealing, empty-window skip, missing metadata inference,
  multiple pending windows, default ZSTD and configured compression validation.
- Retain oldest-first byte/age eviction scoped only to pidstat completed files;
  tolerate concurrent uploader deletion. Do not change uploader ownership.
- Prevent concurrent collectors from writing the same spool; test the chosen locking
  behavior. This is a correctness guard, not a new telemetry contract.

## fpc-04 — Integrate package/build/service workflow

**fpc-03 checkpoint (2026-10-30):** technical implementation/evidence complete;
human acceptance pending. Compatible legacy spools and durable raw replay pass,
26Go tests/native arm64 fault checks, signal seal/SIGKILL recovery/locking/retry pass.
Journals/unique active ownership strengthen process-crash handling; exactly-once
uploader/power-loss guarantees are not claimed. Original host pytest runner is
unavailable; full-suite execution remains blocked, not waived. See verification.
No package/service unit has started.

- Build/stage the binary matching package architecture; wire Go requirements into
  build preflight only, never post-install runtime provisioning.
- Change both `lintap-pidstat.service` units to direct binary ExecStart while retaining
  environment file and existing enable/start/restart policy.
- Update Debian/RPM payload assertions, RPM file list, installation messages, env
  comments, packaging/top-level README and relevant cleanup guidance.
- Remove Python/bootstrap/launcher from the new package payload after parity passes.
   Retain an executable, revision-pinned Python reference until differential review
   and final acceptance complete. Inspect usage before removing source files; preserve unrelated Python tools and
  operator-owned venvs/data. Decide source retirement explicitly in review.
- Deprecate `PIDSTAT_VENV_DIR`, `PIDSTAT_PYTHON`, bootstrap interpreter/spec and
  `PIDSTAT_DUCKDB_THREADS` knobs explicitly; no fabricated Go meanings.
- Verify staged package has no collector runtime dependency on uv/Python/DuckDB or
  download instructions. Other Lintap components may still have their own dependencies.
- Run packaging regression tests for both formats and install/start/restart a fresh
  Debian arm64 artifact in the approved guest window. Record artifact hash and payload.

## fpc-05 — Qualify Ubuntu arm64 and review

1. Use dedicated test data/spool roots in `lintap-dev`; preserve existing telemetry
   and services. Run with root's restricted system PATH. Record OS/kernel/architecture,
   Go version, dependency versions, git revisions and binary SHA256.
2. Run deterministic tests, `go vet`, race-enabled tests where supported, golden
   Parquet comparisons and original relevant regression cases. A cgo-enabled race
   test toolchain does not change the `CGO_ENABLED=0` production build requirement.
3. Default 5s/300s run: at least three rotation boundaries, plus SIGTERM seal; read
   every output, inspect per-file rows/windows/nulls, and verify no partial publications.
4. Restart with valid leftover Python and Go spools; inject conversion failure;
   exercise midnight/hour rollover and caps using isolated fixtures.
5. Measure Go CPU/RSS, native threads, process/child behavior and rotation latency.
   Run the required real Python/Go replay and paired-live comparison above, and
   compare resources on equivalent workload/cadence; report measurements
   without promising a reduction. Go runtime threads are not child processes. With
   an approved sensor-on window, inspect whether thread churn causes telemetry noise.
6. Run canonical `../Wintap-PyUtil` pidstat staging against fresh **Python and Go**
   output separately and a mixed old/new
   fixture. No production SQL changes to hide writer incompatibility.
7. Review actual diffs and evidence; repair findings and rerun affected plus cumulative
   tests. Promote verified deployment facts to canonical wiki and log limitations.

## Engineering Loop For Later OpenCode Work

For each unit: **read contract → implement one unit → run deterministic gates →
review diff and evidence → repair → rerun → checkpoint**. Update verification with
commands, exit status, counts, findings and evidence paths; mark done only after review.
Approval to run the loop is separate from this planning session.

Use native `/pidstat-loop` in Analytics; see [[wiki/tool/pidstat-implementation-loop]]
and `validation/pidstat-loop/README.md`. The current Build session loads a skill,
with three candidate revisions or 60 minutes per requested unit by default.
`evidence.py` performs one deterministic capture/comparison/static/startup experiment;
it never calls an LLM or controls repairs. Record budget/evidence in verification.md.
The first-pass external controller and custom agent profiles have been removed.
<!-- GROUND_TRUTH: ../Wintap-Analytics/.opencode/commands/pidstat-loop.md; ../Wintap-Analytics/.opencode/skills/pidstat-loop/SKILL.md; ../Wintap-Analytics/validation/pidstat-loop/evidence.py -->

Before starting, explicitly approve Lintap/VM scope and agree exact commands,
reference revisions and acceptance criteria. There is no frozen config wiring or
approval-token command. Stop after fpc-01; the human can open a new Analytics
session and run `/pidstat-review` for fresh-context Plan review, then explicitly
approve fpc-02. Neither command spawns another session. No model/plugin is forced.
Workflow preparation alone grants no implementation rights. The separately approved
fpc-01/fpc-02 are human-approved; fpc-03 technical checks are complete and awaiting
review. No packaging unit has started.

Stop/escalate for schema/semantic drift, unexplained row loss, cgo/native dependency,
missing downstream source, blocked permissions, shared service/data conflicts or
exhausted iteration budget. Never weaken tests to make the loop green. Review after
`fpc-01` before committing to the full port; review before package/live qualification
and final acceptance. No automatic field deployment, push, merge or release.

## Files Likely To Change (Later, With Authorization)

- New Lintap Go module, collector command/packages, tests and build target/script.
- `../Lintap/packaging/lintap-{deb,rpm}/{build-*.sh,lintap-pidstat.service,lintap.env}`.
- `../Lintap/README.md`, packaging docs and cleanup guidance.
- Existing collector/bootstrap/launcher and Python tests only as explicitly reviewed
  retirement/compatibility work; unrelated Python project dependencies stay intact.
- Wiki artifacts here; canonical `wiki/repo/lintap-supporting-repo.md` after verification.

## Rollback / Compatibility

Keep the prior package and runtime environment until new package qualification is
accepted. Rollback stops the new collector and restores the known prior package/service
with operator approval; it does not delete Parquet or spools. Retained TSV format allows
compatibility testing in both directions. Do not run both collectors on one spool.
RHEL 8 amd64 live/RPM acceptance remains a follow-on gate; cross-build is not runtime proof.

## Done Checklist

- [x] User-authorized four-hour sensor-on VM soak launched before packaging; default5s/300s, recurring five-family canaries, bounded shutdown and private evidence retrieval prepared.
- [x] Four-hour completion, every-file inspection and same-session resource/smoke review documented:49files/399312rows,2880sample times,80stimuli; see soak_review and verification.
- [ ] Human accepts four-hour review and remaining sensor/qualification limits before packaging.
- [x] Human confirmed Go rewrite and Ubuntu arm64 `lintap-dev` first-target scope.
- [x] Plan and later-loop boundaries recorded (planning initially made no source/VM changes).
- [x] Native commands, bounded skill and deterministic evidence utility prepared/tested in Analytics only; first-pass external controller removed.
- [x] Approved fpc-01 Lintap/VM scope, actual commands/reference revisions and effective permissions ready.
- [x] fpc-01 technical spike and evidence complete; stopped for human review.
- [x] fpc-01 static build and Parquet compatibility spike accepted by human 2026-10-30.
- [x] fpc-02 technical sampler/configuration and raw-replay evidence complete (candidate3).
- [x] fpc-02 sampler/configuration parity accepted by human (“fpc-02 approved. proceed”).
- [x] fpc-03 technical spool/recovery implementation and evidence complete (candidate3); original host pytest runner unavailable.
- [ ] fpc-03 spool/writer/recovery parity accepted.
- [ ] fpc-04 packaging/service integration accepted.
- [ ] Real Python/Go identical-input and paired-live comparisons reviewed; all fields,
  row counts and unmatched cases accounted for without unexplained differences.
- [ ] fpc-05 live Ubuntu arm64, consumer and review gates accepted.
- [ ] Durable wiki facts promoted; deferred RHEL/amd64 gates explicitly recorded.
