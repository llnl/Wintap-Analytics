---
title: "Dev Handoff: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-pidstat-collector/brief.md
  - wiki/work/improve-pidstat-collector/references.md
  - wiki/work/improve-pidstat-collector/design.md
  - wiki/work/improve-pidstat-collector/implementation_plan.md
  - wiki/work/improve-pidstat-collector/verification.md
  - wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec.md
policy: agent-editable
last_validated: 2026-08-20
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/improve-pidstat-collector/dev_handoff.md
tags: [feature-work, handoff, lintap, pidstat, python]
---

# Dev Handoff: Improve pidstat Collector

Slice 1 (bash collector: rotation, parquet conversion, salvage, accumulation
guard) was accepted 2026-08-12 — but a RHEL 8 field test found its hot loop
forks ~7 subshells per pidstat line (~700 forks/sec), flooding the very
sensor it feeds ([[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]]).
**Slice 2 is therefore a rewrite in Python** (human decision 2026-08-14),
plus systemd packaging and the Wintappy parquet migration.

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

```text
Switch to code-development mode for the improve-pidstat-collector feature,
slice 2.

Work from the Wintap-Analytics repository root. Read AGENTS.md first and
confirm code-development mode is active for this task.

Use these wiki files as the handoff context, in this order:

- wiki/work/improve-pidstat-collector/implementation_plan.md (steps 5-8 are
  this slice; note steps 6/6b — the Python rewrite and pytest port)
- wiki/work/improve-pidstat-collector/design.md (the 2026-08-14 Python
  decision section lists the carried-over semantics as requirements)
- wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec.md (why the bash
  collector is being retired — do not reintroduce per-line subprocesses)
- wiki/work/improve-pidstat-collector/verification.md (slice-1 evidence and
  review findings the rewrite must absorb)

Goal: replace the bash collector with a single-process Python collector
(../Lintap/pidstat-collector.py) using the duckdb Python API, port the test
suite to pytest, add systemd packaging, and migrate Wintappy DBT to the
parquet layout.

Authorization: you are explicitly authorized to create, modify, and delete
files in ../Lintap and ../Wintappy for this feature. Do NOT modify
../wintap (read-only). Leave ../Lintap/pidstat-collect.sh untouched (it
stays as the simple example); DELETE ../Lintap/pidstat-collector.sh once
the Python collector passes its tests.

Hard requirements on the Python collector (details in design.md):

- Single process: at most ONE child at steady state — zero with the
  preferred /proc sampler, one if the pidstat-child option is chosen.
  Parsing happens in-process; parquet conversion uses the duckdb Python
  module, never a CLI subprocess. No per-line process spawning of any kind.
- Telemetry source: read design.md's "Telemetry Source Investigation"
  section and implement behind a small sampler interface. Preferred:
  option B, a stdlib /proc sampler (stat/io/status/schedstat — full bronze
  schema coverage verified; own the delta/rate math, parse stat after the
  last ')', detect PID reuse via starttime). Fallback: option A, the
  pidstat child. Either way keep pidstat as the test oracle: a test runs
  both sources over the same window and asserts rates agree within
  tolerance. Do NOT use psutil (schema-incomplete; see design). Record
  your choice and evidence in design.md.
- Container attribution (added 2026-08-14, high value): emit cgroup_path,
  pid_ns_inode, and best-effort container_runtime/container_id columns
  from /proc/<pid>/cgroup and /proc/<pid>/ns/pid, cached per
  (pid, starttime). Handle both cgroup v1/hybrid (RHEL 8) and v2 unified
  formats. Add the new columns to the Wintappy bronze model in the same
  migration (step 7) so the schema changes once, not twice. Unknown/
  unparseable runtime = NULL columns with cgroup_path preserved raw.
- Preserve the slice-1 validated semantics unchanged: PIDSTAT_* env
  interface, spool/pending/meta crash salvage outside raw_sensor/,
  dayPK=/hourPK= partitioning + atomic rename, bronze schema + hostname
  column, accumulation guard (bytes + age), SIGTERM window sealing,
  empty-window skip, rotation default 300s synced to
  WINTAP_ETL_UPLOAD_INTERVAL_SEC, all-processes sampling at a configurable
  interval (default 5s) regardless of source option.
- Absorb the three open review findings: row date derived from the
  window-start epoch (midnight correctness); glued pidstat records parsed
  so valid leading records survive a malformed tail (port the bash test
  fixture); conversion failures logged with full exception detail and the
  spool retained for retry.
- Decide the Python runtime/packaging (RHEL 8 default python3 is 3.6 —
  too old for duckdb wheels; RHEL 8 offers 3.9/3.11 modules). Record the
  decision in design.md and pin the interpreter in the systemd unit.

Tests (pytest, in ../Lintap's uv project): port all seven bash cases
(conversion/partitioning, line parsing, glued records, salvage, byte cap,
age cap, live row preservation), add a midnight/window-date case, and add
a fork regression guard asserting the steady-state collector spawns no
children beyond the single pidstat process.

Then: systemd unit in ../Lintap/packaging/ (Restart=always, pinned
 interpreter); README update (Python collector usage, deps, -p ALL and env
 knobs); Wintappy DBT migration per plan step 7 (parquet bronze with
 filename=true, empty-input typed table preserved, legacy-CSV path decided
 and recorded in design.md; follow-up bugfix later removed the pidstat-only
 override so pidstat now uses shared raw-event helpers).

Environment expectations (verify before coding, report what is missing):
- Sibling checkouts: ../Lintap, ../wintap, ../Wintappy.
- Host tools: pidstat (sysstat), a Python >= the version you select with
  the duckdb package installable, uv, and a working Wintappy dev
  environment for dbt runs.
- No S3 access is assumed; upload verification stays opt-in/manual
  (S3Adapter is disabled in the shipped ETLConfig.json).

As you work:
- Update verification.md with every command run and its results (new
  slice-2 section).
- Check off implementation_plan.md Done Checklist items as they complete.
- Record the runtime/packaging and legacy-CSV decisions in design.md.
- Append a concise entry to wiki/log.md for substantial progress.
- Do not push data to any external service; no git commits unless the
  human driving the session asks for them.
```

## Handoff Summary

Known issue (2026-08-15): the sensor's delete-after-upload never fires
(adapters never raise `UploadCompleted`), so uploaded files currently repeat
and accumulate — fixed separately in
[[wiki/work/fix-upload-cache-deletion/brief]]. The collector's accumulation
guard is the effective local bound until then; nothing in this slice changes.

The bash collector proved the mechanics (spool → rotate → typed parquet →
ride the sensor's upload sweep) and its test suite defined the behavior, but
its implementation language fought the hot loop: command substitutions made
the collector itself the biggest process-event source on the machine. The
Python rewrite keeps every validated behavior and the same operational
interface while collapsing steady state to two processes. After this slice,
only the S3-enabled end-to-end confirmation and closeout promotion remain.

## Primary Sources For The Dev Agent

- [[wiki/work/improve-pidstat-collector/implementation_plan]] - steps 5-8,
  requirements, Done Checklist.
- [[wiki/work/improve-pidstat-collector/design]] - carried-over semantics
  (2026-08-14 decision section), mechanism facts, edge cases.
- [[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]] - the fork
  storm root cause; the anti-pattern the rewrite must not repeat.
- `../Lintap/pidstat-collector.sh` and
  `../Lintap/tests/pidstat-collector-tests.sh` - the behavior spec to port
  (then retire the .sh collector).
- `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql`,
  `wintap_dbt/dbt_project.yml`, and the shared raw-source macros under
  `wintap_dbt/macros/` - the consumer-side files that were migrated and later
  aligned with the standard raw-event pathing.

## Non-Goals For This Slice

- No `../wintap` code changes.
- No changes to Wintappy silver/gold semantics beyond the bronze source swap.
- No collector-side volume filtering — `-p ALL` stays (recorded decision);
  volume reduction, if needed, happens in the ETL layer.
- No S3-dependent default tests.
- Closeout promotion to canonical pages waits until after this slice.

## Testing Expectations

- pytest green in `../Lintap`: seven ported cases + midnight case + fork
  regression guard.
- A short live run on the dev VM confirming rotated parquet loads in DuckDB
  with expected row counts (mirror the slice-1 smoke methodology).
- DBT: parquet fixture build, empty-input typed table, and — if a legacy-CSV
  union is chosen — a mixed-source test.

## Closeout Instructions

When the slice is done:

- Update [[wiki/work/improve-pidstat-collector/verification]] (slice-2
  section: commands, results).
- Update the [[wiki/work/improve-pidstat-collector/implementation_plan]]
  done checklist.
- Record the runtime/packaging and legacy-CSV decisions in
  [[wiki/work/improve-pidstat-collector/design]].
- Append a concise entry to `wiki/log.md`.
- Flag immediately in the design page and log if any carried-over semantic
  cannot be preserved as specified.

## Operating Mode Note

`AGENTS.md` distinguishes wiki-maintainer mode from code-development mode.
This handoff is used with the explicit trigger in the copy/paste prompt. For
slice 2 the agent may modify files in `Wintap-Analytics/`, `../Lintap`
(including deleting the retired bash collector), and `../Wintappy`. `raw/`
and `../wintap` remain protected.
