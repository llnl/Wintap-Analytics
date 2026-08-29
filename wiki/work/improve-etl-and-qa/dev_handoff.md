---
title: "Dev Handoff: Improve ETL and QA"
type: concept
confidence: medium
grounded_by:
  - ../Wintappy/notebooks/wintap_dbt_overview.py
  - wiki/work/improve-etl-and-qa/verification.md
  - wiki/work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md
  - validation/perf-collection/README.md
  - validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py
policy: agent-editable
last_validated: 2026-08-29
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/improve-etl-and-qa/dev_handoff.md
tags: [feature-work, dev-handoff, lintap, pidstat, memory, perf]
---

# Dev Handoff: Improve ETL and QA

## Copy/Paste Prompt

Use this prompt to continue the live memory-growth experiment on the host that is
currently running `Lintap`:

    Switch to code-development mode for improve-etl-and-qa.

    Use these wiki files as the handoff context:

    - wiki/work/improve-etl-and-qa/brief.md
    - wiki/work/improve-etl-and-qa/design.md
    - wiki/work/improve-etl-and-qa/implementation_plan.md
    - wiki/work/improve-etl-and-qa/verification.md
    - wiki/work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md
    - wiki/work/improve-etl-and-qa/milestone-2026-08-28.md

    Goal: continue the live Lintap performance experiment directly on the host,
    inspect the newly collected parquet, and tighten the collectors/analysis so
    we can distinguish true retained state from allocator/runtime ratcheting.

    Before editing code, read AGENTS.md and confirm code-development mode is
    active for this task.

## Handoff Summary

Current state:

- Wintappy now has a useful pidstat QA notebook with:
  - metric-selectable Plotly time series
  - host filter
  - command substring filter
  - `Per process instance` vs `Aggregate by command`
  - event-volume correlation chart by event family
- A manual-batch collector now exists in this repo under
  `validation/perf-collection/` and writes raw-style parquet event types:
  - `perf_smaps_rollup`
  - `perf_proc_status`
  - `perf_fd_map`
  - `perf_dotnet_counters` via file-based `dotnet-counters collect`
  - optional raw command captures:
    - `perf_lintap_diag_raw`
- A real host run has already been performed. Row counts reported by the user:
  - `perf_smaps_rollup`: `60`
  - `perf_proc_status`: `60`
  - `perf_fd_map`: `60`
  - older monitor-based `.NET` capture produced `478` raw lines, but the
    current collector code now targets structured `perf_dotnet_counters` via
    `dotnet-counters collect`
- The new collect-based host paths are now verified on `spk16`:
  - short smoke run under `/tmp/lintap-perf-collect/` produced `108`
    `perf_dotnet_counters` rows across `27` counter keys plus matching procfs
    rows
  - a collect-based one-hour rerun produced `9720` `perf_dotnet_counters` rows
    across `27` counter keys plus `714` rows each for `perf_smaps_rollup`,
    `perf_proc_status`, and `perf_fd_map`

Most important current insight:

- `smaps_rollup` suggests the Lintap process is carrying mostly private /
  anonymous memory, not primarily file-backed growth.
- `AnonHugePages` is large, which pushes suspicion toward heap/allocator/native
  buffer retention rather than file-mapping growth.
- The current pidstat/event-volume analysis also suggests file-event workload is
  the strongest external correlate of the stair-step memory pattern.
- On the mostly idle host, the collect-based one-hour rerun did not show simple
  monotonic memory ratcheting. RSS, anonymous memory, and AnonHugePages all
  stayed within bounded bands, which strengthens the earlier burst/workload
  hypothesis over a purely time-since-start explanation.
- Lintap CPU during the collect-based one-hour rerun was still moderate rather
  than near-zero: about `12.9%` min, `23.1%` max, `19.0%` average. CPU had only
  weak-to-moderate correlation with memory (`corr(cpu, working_set) ~= 0.31`,
  `corr(cpu, rss) ~= 0.28`), so CPU activity alone does not explain the memory
  shape.

Critical caveat for the next operator/dev to keep in mind:

- DuckDB is long-running in the `Lintap` .NET process. That means a meaningful
  portion of the stair-step memory behavior could come from the in-process
  DuckDB engine itself, its buffering, or its interaction with the .NET process,
  not just from sensor queues or the file pipeline. Treat DuckDB-in-process as a
  first-class suspect, not an afterthought.

## Primary Sources For The Dev Agent

- `validation/perf-collection/README.md`
- `validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py`
- `validation/perf-collection/src/wintap_perf_collection/procfs.py`
- `../Wintappy/notebooks/wintap_dbt_overview.py`
- `wiki/work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md`

## Recommended First Live-Host Tasks

1. Inspect the collected parquet directly on the host.

   Start with:

    - `perf_smaps_rollup`
    - `perf_proc_status`
    - `perf_fd_map`
    - `perf_dotnet_counters`

    Confirm whether the memory stairs align more with:

    - anonymous/private memory growth
    - fd/mmap growth
    - or runtime/heap signals from .NET

   Important operational note:

   - use a unique `RUN_ID` for every future host capture; an earlier rerun reused
     `lintap-perf-60m`, which made naive cross-partition DuckDB queries blend an
     older monitor-era run with the newer collect-based rerun

2. Confirm the current `smaps_rollup` parser stays clean on repeated runs.

   The previous bogus extra column derived from the first header line has been
   fixed. The next operator should just confirm new host parquet still has the
   expected schema.

3. Keep using the new file-based `dotnet-counters collect` path on-host.

   The old terminal-scraping `monitor` path has been removed. The current code
   now runs `dotnet-counters collect --format json|csv` and parses the emitted
   file into structured `perf_dotnet_counters` rows. This path is now validated
   both by fixtures and by real host smoke/one-hour runs on `spk16`, and should
   be treated as the canonical runtime-counter collection path for future runs.

4. Keep DuckDB-in-process explicitly in the hypothesis set.

   Ask, for each newly observed memory rise:

   - does it line up with event bursts?
   - with write throughput?
   - with counter/heap changes?
   - or with patterns that look more like embedded DuckDB buffering / retention?

5. Run the next contrast experiment under known workload.

   The idle-baseline and collect-based idle rerun now suggest that simple
   elapsed time is not enough to force continued memory ratcheting. The next
   highest-value experiment is a controlled file-heavy perturbation run, using a
   distinct `RUN_ID`, so CPU/heap/RSS behavior can be compared directly against
   the idle baseline.

## Non-Goals For This Slice

- Do not redesign the whole QA notebook again.
- Do not prematurely promote the manual-batch collectors into a long-running
  sidecar until the command set and signal usefulness are proven on-host.
- Do not assume the issue is purely a Lintap queue/cache leak without checking
  the embedded DuckDB angle.

## Testing Expectations

- Re-run the manual-batch collectors on the host after any collector/parser
  change.
- Validate the resulting parquet with quick DuckDB queries on-host.
- If `dotnet-counters` collection/parsing changes, verify a small real capture
  rather than relying only on fixtures.

## Closeout Instructions

- Update `wiki/work/improve-etl-and-qa/verification.md` with commands run and results.
- Update `wiki/work/improve-etl-and-qa/implementation_plan.md` done checklist if a stage meaningfully advances.
- Append a concise entry to `wiki/log.md`.
- Promote durable facts into canonical wiki pages once the behavior stabilizes.
