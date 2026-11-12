---
title: "Feature Brief: Fix pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../Lintap/pidstat-collector-bootstrap.sh
  - ../Lintap/packaging/lintap-deb/lintap-pidstat.service
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/fix-pidstat-collector/brief.md
tags: [feature-work, pidstat, go, parquet, linux, packaging]
---

# Feature Brief: Fix pidstat Collector

## Problem

Operator report, 2026-10-29: on RHEL 8, the documented command
`sudo bash /usr/lib/lintap/pidstat-collector-bootstrap.sh` fails with
`ERROR: required command not found: uv`. Root cannot be expected to have the
invoking user's `uv`; this deployment problem is not RHEL-specific.

Bootstrap currently requires `uv` on its PATH, creates a Python 3.12 environment,
and installs DuckDB. The service runs as root through a Python launcher.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector-bootstrap.sh; ../Lintap/packaging/lintap-deb/lintap-pidstat.service -->

## Confirmed Scope / Playback

The human accepted a compatibility-preserving Go rewrite, with one self-contained
Linux binary per architecture, and then corrected the first acceptance environment
to the **existing local Multipass `lintap-dev`, Ubuntu arm64**. Planning and native
OpenCode workflow preparation and fpc-01/fpc-02 are human-approved; fpc-03 durable
collector implementation/technical checks are complete, awaiting review. Original
host pytest runner is unavailable. Packaging/service integration has not started.
The original RHEL 8 failure motivates portability but does not make an Ubuntu run
proof of RHEL 8 compatibility.

## Goals

- Eliminate installed-host requirements for Python, uv, DuckDB, Go, or sysstat.
- Keep a single collector process sampling `/proc`; write Parquet in-process using
  a pure-Go library, with no cgo/native DuckDB dependency.
- Target Linux arm64 and amd64 artifacts; qualify arm64 live first on `lintap-dev`.
- Preserve recorded metric meaning, container attribution, output types and layout,
  applicable configuration, recovery and orderly shutdown behavior.
- Preserve the existing sensor upload ride-along and downstream Wintappy contract.
- Remove bootstrap from the normal package-to-service startup procedure.

## Non-Goals

- No new metrics, schemas, uploader, DBT transformations, or container semantics.
- No Windows/macOS collector, field rollout, historical dataset rewrite, or automatic
  deletion of old environments or operator data.
- No promise of lower CPU/RSS before measurement; no unrelated Python dependency cleanup.
- No external agent controller or OpenCode plugin; native commands/skill and a
  deterministic evidence utility are prepared in Analytics, not collector code.

## User-Facing Behavior

After installing a matching package, operators review `/etc/lintap/lintap.env` and
start `lintap-pidstat.service` without bootstrap or network dependency downloads.
Proposed installed executable: `/usr/lib/lintap/pidstat-collector`.
The existing optional-service enable/start policy remains unchanged.

## Acceptance Criteria

1. `CGO_ENABLED=0` builds succeed for Linux arm64 and amd64; artifact inspection
   finds no dynamic interpreter/shared-library runtime dependency. Actual platform
   execution is recorded separately from cross-build success.
2. The arm64 binary runs as root in `lintap-dev` with a restricted system PATH and
   no invocation of uv, Python, DuckDB, Go, sysstat or child sampling/conversion tools.
3. Deterministic fixtures preserve metric math, PID-reuse handling, cgroup v1/v2
   parsing and namespace attribution, including CPU values above 100 percent.
4. Go Parquet agrees with **real results from the existing Python version**, not
   only hand-built fixtures, in column names/order,
   DuckDB-visible types, null/empty treatment, timestamp interpretation and values;
   identical captured `/proc` inputs pass exact differential comparison, and a
   paired live run passes predefined sampling-skew tolerances. Existing Wintappy
   pidstat staging consumes both versions without production-model edits. Review
   must inspect the comparison report, unmatched rows and every column's differences.
5. Rotation, pending/active spool recovery, retry after conversion failure, empty
   windows, collision handling, SIGTERM sealing and accumulation guard pass tests.
6. Debian arm64 package payload and service startup pass on `lintap-dev`; applicable
   RPM build/staging assertions are updated and tested without claiming RPM live proof.
7. A default-cadence VM run spans at least three 300-second rotation boundaries,
   produces readable rows and a final shutdown window, and records resource samples.
   A scoped sensor-on run checks process-event noise separately from OS thread count.
8. Test/review findings, limits, deployment differences and rollback are recorded.

## Affected Areas / Ownership

Lintap owns the collector, Go build, tests, Debian/RPM packaging and operator docs.
Wintap owns the existing upload pipeline (read-only, unchanged). Wintappy owns the
downstream DBT pipeline (read-only consumer verification). Analytics hosts this plan
and verification record. No sibling source edits are authorized by this plan alone.
Wintappy's current checkout directory is **`../Wintap-PyUtil`** (renamed from
`../Wintappy`). Its live staging model scans pidstat Parquet with union-by-name and
filename provenance; its typed empty branch matches the existing Python types.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql -->

## References

- [[wiki/work/fix-pidstat-collector/implementation_plan]]
- [[wiki/work/fix-pidstat-collector/dev_handoff]]
- [[wiki/work/fix-pidstat-collector/verification]]
- [[wiki/work/improve-pidstat-collector/design]] (historical requirements, recheck live code)
- [[wiki/repo/lintap-supporting-repo]]
- [[wiki/concept/lintap-cpu-unit-conventions]]

## Open Questions

- Spike choices: Go1.27.3, parquet-go0.32.0 and pure-Go ZSTD in `../Lintap/pidstat-go`;
  initial static builds/writer parity were human-approved; fpc-02 raw sampler/config
  technical checks pass and were human-approved; fpc-03 durable checks now await
  review, with original pytest runner blocked and packaging still pending.
- Legacy Python-only environment knobs: document explicit deprecated handling rather
  than silently reinterpret them. Preserve telemetry/path/cadence knobs.
- Loop mechanism is resolved: native command + skill + deterministic evidence utility,
  three candidate revisions/60 minutes per requested unit, human pause after fpc-01;
  fresh review via `/pidstat-review` in a manually opened new session. See
  [[wiki/tool/pidstat-implementation-loop]]. Scoped fpc-01 Lintap/VM work was approved;
  fpc-01/fpc-02 were approved. fpc-03 technical evidence now awaits review;
  no package/service work or deployment has started. See
  [[wiki/tension/pidstat-publication-versus-uploader-receipts]] for delivery limits.
- Downstream validation environment/tooling: use canonical `../Wintap-PyUtil`;
  source location is resolved, actual DBT execution remains pending.
- Native RHEL 8/amd64 and broader distro acceptance follow the Ubuntu arm64 gate.

## Test Plan / Done When

Execute the staged gates in the implementation plan. Close only with the stated
first-target evidence and explicit separation of deferred RHEL/amd64 runtime gates;
do not label all Linux targets qualified from one Ubuntu arm64 run.
