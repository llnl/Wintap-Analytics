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
policy: agent-editable
last_validated: 2026-08-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/improve-pidstat-collector/dev_handoff.md
tags: [feature-work, handoff, lintap, pidstat]
---

# Dev Handoff: Improve pidstat Collector

Slice 1 (collector core: rotation, parquet conversion, salvage, accumulation
guard, 7-test suite) is complete, committed (`../Lintap` c76ea87), and
reviewed — accepted 2026-08-12 with follow-ups. This handoff covers **slice
2**: review fixes, systemd packaging, and the Wintappy parquet migration.

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

```text
Switch to code-development mode for the improve-pidstat-collector feature,
slice 2.

Work from the Wintap-Analytics repository root. Read AGENTS.md first and
confirm code-development mode is active for this task.

Use these wiki files as the handoff context, in this order:

- wiki/work/improve-pidstat-collector/implementation_plan.md (steps 5-8 are
  this slice; steps 1-4 are done)
- wiki/work/improve-pidstat-collector/verification.md (slice-1 results and
  the 2026-08-12 Independent Review findings you will fix)
- wiki/work/improve-pidstat-collector/design.md (including the post-review
  -p ALL decision and the resolved deployment findings)
- wiki/work/improve-pidstat-collector/brief.md

Goal: implement slice 2 — plan steps 5 through 8: review follow-up fixes in
the collector, systemd packaging, the Wintappy DBT parquet migration, and
the verification runs.

Authorization: you are explicitly authorized to create and modify files in
../Lintap and ../Wintappy for this feature. Do NOT modify ../wintap (it
remains read-only). Leave ../Lintap/pidstat-collect.sh untouched.

Slice-2 work items, in recommended order:

1. Collector fixes in ../Lintap/pidstat-collector.sh, each with a test:
   - Derive sample_date from the window-start epoch, not processing-time
     date (fixes ~24h-forward timestamps for samples in flight at midnight).
   - In normalize_pidstat_line, emit valid leading records from a partially
     malformed glued chunk instead of dropping the whole chunk.
   - Capture DuckDB stderr into the collector log when conversion fails.
2. Document -p ALL and the PIDSTAT_* environment knobs in
   ../Lintap/README.md (the decision and rationale are already recorded in
   the design page — summarize, do not re-litigate).
3. systemd unit in ../Lintap/packaging/ (Restart=always), with install notes
   in the README.
4. Wintappy DBT migration in ../Wintappy/wintap_dbt/:
   - pidstat macros: default glob $WINTAP_DATA_ROOT/raw_sensor/pidstat/**/*.parquet,
     PIDSTAT_DATA_PATH still honored as an override.
   - stg_pidstat_metrics: read_parquet with filename=true provenance;
     casting already happens at collection time, so bronze becomes a typed
     passthrough. Keep the empty-input case building a typed empty table.
   - Legacy CSV data: recommended approach is parquet-only bronze plus a
     one-time DuckDB conversion script for existing CSV datasets; a
     temporary union is acceptable if it is genuinely cleaner. Record the
     choice in design.md under Open Questions (resolve the pending item).
5. Verification (record everything in verification.md):
   - Install shellcheck (or run it via container) and get a clean run on
     collector + tests; record the result.
   - Re-run the full collector test suite.
   - DBT build against rotated parquet output and against an empty input.
   - 1h+ end-to-end run per the validation-thread Multipass setup; S3 upload
     verification stays opt-in/manual (S3Adapter is disabled in the shipped
     ETLConfig.json — see design.md).

Environment expectations (verify before coding, report what is missing):
- Sibling checkouts: ../Lintap, ../wintap, ../Wintappy.
- Host tools: pidstat (sysstat), duckdb CLI, shellcheck (install if absent),
  and a working Wintappy dev environment for dbt runs.
- No S3 access is assumed.

As you work:
- Update verification.md with every command run and its results.
- Check off implementation_plan.md Done Checklist items as they complete.
- Resolve the legacy-CSV open question in design.md when you decide it.
- Append a concise entry to wiki/log.md for substantial progress.
- Do not push data to any external service; no git commits unless the human
  driving the session asks for them.
```

## Handoff Summary

The collector (`../Lintap/pidstat-collector.sh`) works end-to-end locally:
it samples `pidstat -u -d -r -w -h -p ALL` (5 s default), spools outside the
swept tree, rotates on 300 s epoch-aligned windows, converts to typed parquet
(bronze schema + `hostname`), and enforces byte/age accumulation caps. Slice 2
hardens it (three review fixes), packages it (systemd), and connects the
downstream consumer (Wintappy parquet migration). After slice 2, only the
S3-enabled end-to-end confirmation and closeout promotion remain.

## Primary Sources For The Dev Agent

- [[wiki/work/improve-pidstat-collector/implementation_plan]] - steps 5-8 and
  the Done Checklist.
- [[wiki/work/improve-pidstat-collector/verification]] - slice-1 command log
  and the Independent Review findings (items 2-4 are this slice's fixes).
- [[wiki/work/improve-pidstat-collector/design]] - mechanism facts, the
  `-p ALL` decision, deployment findings (`S3Adapter.Enabled=false`,
  `UploadIntervalSec=300`), and the pending legacy-CSV open question.
- `../Lintap/pidstat-collector.sh` and `../Lintap/tests/pidstat-collector-tests.sh`
  - the code being extended.
- `../Wintappy/wintap_dbt/macros/pidstat.sql` and
  `models/bronze/stg_pidstat_metrics.sql` - the models being migrated.

## Non-Goals For This Slice

- No `../wintap` code changes.
- No changes to Wintappy silver/gold semantics beyond the bronze source swap.
- No collector-side volume filtering — `-p ALL` stays; volume reduction, if
  ever needed, happens in the ETL layer (recorded design decision).
- No S3-dependent default tests.
- Closeout promotion to canonical pages waits until after this slice.

## Testing Expectations

- Every review fix lands with a regression test in
  `../Lintap/tests/pidstat-collector-tests.sh`.
- shellcheck clean (or documented, reproducible container invocation).
- DBT: parquet fixture build, empty-input typed table, and — if the union
  approach is chosen for legacy CSV — a mixed-source test.
- 1h+ run: partition correctness across at least one hour boundary, row
  counts in the expected order of magnitude, no conversion retries.

## Closeout Instructions

When the slice is done:

- Update [[wiki/work/improve-pidstat-collector/verification]] (commands,
  results, and a slice-2 results section).
- Update the [[wiki/work/improve-pidstat-collector/implementation_plan]] done
  checklist.
- Resolve the legacy-CSV open question in
  [[wiki/work/improve-pidstat-collector/design]].
- Append a concise entry to `wiki/log.md`.
- Flag immediately in the design page and log if anything contradicts the
  recorded mechanism facts.

## Operating Mode Note

`AGENTS.md` distinguishes wiki-maintainer mode from code-development mode.
This handoff is used with the explicit trigger in the copy/paste prompt. For
slice 2 the agent may modify files in `Wintap-Analytics/`, `../Lintap`, and
`../Wintappy` (newly authorized this slice for the DBT migration). `raw/` and
`../wintap` remain protected.
