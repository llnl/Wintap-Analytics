---
title: "Dev Handoff: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-pidstat-collector/brief.md
  - wiki/work/improve-pidstat-collector/references.md
  - wiki/work/improve-pidstat-collector/design.md
  - wiki/work/improve-pidstat-collector/implementation_plan.md
policy: agent-editable
last_validated: 2026-08-11
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/improve-pidstat-collector/dev_handoff.md
tags: [feature-work, handoff, lintap, pidstat]
---

# Dev Handoff: Improve pidstat Collector

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

```text
Switch to code-development mode for the improve-pidstat-collector feature.

Work from the Wintap-Analytics repository root. Read AGENTS.md first and
confirm code-development mode is active for this task.

Use these wiki files as the handoff context, in this order:

- wiki/work/improve-pidstat-collector/brief.md
- wiki/work/improve-pidstat-collector/design.md
- wiki/work/improve-pidstat-collector/implementation_plan.md
- wiki/work/improve-pidstat-collector/references.md

Goal: implement the first slice — steps 1 through 4 of the implementation
plan: verify the Linux upload ride-along (read-only), then build the new
collector script with rotation, parquet conversion, crash salvage, and the
accumulation guard, with tests.

Authorization: you are explicitly authorized to create and modify files in
../Lintap for this feature. Do NOT modify ../wintap or ../Wintappy — the
Wintappy DBT change is a later slice, and ../wintap is verify/read-only.
Leave ../Lintap/pidstat-collect.sh untouched; it stays as the simple example.

Environment expectations (verify before coding, report what is missing):
- Sibling checkouts relative to Wintap-Analytics: ../Lintap, ../wintap,
  ../Wintappy.
- Host tools: pidstat (sysstat) and the duckdb CLI. shellcheck for linting.
- No S3 access is assumed; upload verification is opt-in/manual.

As you work:
- Record step-1 findings (does the Linux service build run CacheManager's
  upload loop with an S3 adapter enabled, and what UploadIntervalSec is used)
  in wiki/work/improve-pidstat-collector/design.md under Open Questions, and
  update implementation_plan.md if the findings change the approach.
- Update wiki/work/improve-pidstat-collector/verification.md (create it from
  the skeleton in wiki/concept/feature-work-template.md) with every command
  run and its results.
- Check off wiki/work/improve-pidstat-collector/implementation_plan.md Done
  Checklist items as they complete.
- Append a concise entry to wiki/log.md for substantial progress.
- Do not push data to any external service; no git commits unless the human
  driving the session asks for them.
```

## Handoff Summary

Replace the manually run `../Lintap/pidstat-collect.sh` with a new,
continuously running collector service that samples pidstat (5 s default,
configurable), rotates windows aligned to the sensor's merge/upload cycle,
converts each closed window to typed parquet, and drops it into the sensor's
parquet cache at `{parquetRoot}/raw_sensor/pidstat/dayPK=YYYYMMDD/hourPK=HH/`.
The sensor's existing CacheManager/uploader then ships it to S3 (key mirrors
the local relative path) and deletes it locally. No C# changes are expected —
the upload sweep was verified type-agnostic. The motivating need is
correlating Lintap CPU/memory use with system load and event_store growth
over multi-day runs (`raw/Issues/Long_Running_Cleanup.md`).

## Primary Sources For The Dev Agent

Read these first:

- [[wiki/work/improve-pidstat-collector/brief]] - decisions, acceptance
  criteria, test plan.
- [[wiki/work/improve-pidstat-collector/design]] - mechanism facts (with
  ground-truth citations into `../wintap` source), collector loop, edge
  cases, risks.
- [[wiki/work/improve-pidstat-collector/implementation_plan]] - step list and
  done checklist.
- [[wiki/work/improve-pidstat-collector/references]] - cross-repo source map.
- `../Lintap/pidstat-collect.sh` - the existing minimal collector (do not
  modify).
- `../wintap/wintap/core/etl/load/CacheManager.cs` and
  `adapters/base/Uploader.cs` - the upload pipeline being ridden (read-only).
- `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` - the typed
  schema the parquet output must match (plus a new `hostname` column).

## Recommended First Implementation Slice

Prefer the smallest useful change, in plan order:

1. Step 1 (read-only): confirm the Linux service build runs the CacheManager
   upload loop with an S3 adapter enabled and find the deployed
   `UploadIntervalSec`; record findings in the design page before writing
   collector code.
2. Collector script in `../Lintap` (suggested name `pidstat-collector.sh`):
   sampling loop, spool file outside `raw_sensor/`, wall-clock-aligned
   rotation.
3. DuckDB CLI conversion applying the `stg_pidstat_metrics` casts plus
   `hostname`; atomic rename into the partition layout.
4. Startup salvage of a leftover spool file and the configurable
   accumulation guard (max bytes/age, oldest-first).
5. Tests: shellcheck clean; rotation test producing multiple completed files
   plus one in-progress spool; kill -9 mid-window test.

systemd packaging (plan step 5) is a stretch goal for this slice; include it
only if the above is solid.

## Non-Goals For This Slice

- No Wintappy DBT changes (plan step 6, later slice).
- No `../wintap` code changes at all.
- No S3 or network-dependent default tests; upload verification is opt-in.
- No modification or removal of `pidstat-collect.sh`.
- No migration of existing tab-CSV datasets (decision deferred to the
  Wintappy slice).

## Testing Expectations

Default tests must not require network access, S3 credentials, or a running
Lintap sensor. Good first tests:

- Rotation produces one parquet per closed window, none for empty windows,
  and the in-progress spool is never visible as `*.parquet` under
  `raw_sensor/`.
- Parquet schema matches the bronze column list (names and types) plus
  `hostname`; spot-check values against a captured pidstat sample.
- kill -9 mid-window: completed files intact; next start salvages or
  discards the spool per design.
- Accumulation guard deletes oldest-first past the cap and logs it.

## Closeout Instructions

When the slice is done:

- Fill in [[wiki/work/improve-pidstat-collector/verification]] with commands
  run and results (create from the template if absent).
- Update the [[wiki/work/improve-pidstat-collector/implementation_plan]] done
  checklist.
- Record step-1 findings in [[wiki/work/improve-pidstat-collector/design]].
- Append a concise entry to `wiki/log.md`.
- Leave durable-fact promotion to canonical pages for feature closeout (after
  the Wintappy slice), unless step-1 findings contradict the design — then
  flag it immediately in the design page and the log.

## Operating Mode Note

`AGENTS.md` distinguishes wiki-maintainer mode from code-development mode.
This handoff is intended to be used with the explicit trigger in the
copy/paste prompt above. In that mode the agent may modify files in
`Wintap-Analytics/` and — via the explicit authorization granted in the
prompt — `../Lintap` only. `raw/`, `../wintap`, and `../Wintappy` remain
protected for this slice.
