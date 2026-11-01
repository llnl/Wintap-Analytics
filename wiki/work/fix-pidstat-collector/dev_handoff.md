---
title: "Dev Handoff: Fix pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../Lintap/tests/test_pidstat_collector.py
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/fix-pidstat-collector/dev_handoff.md
tags: [feature-work, handoff, pidstat, go, engineering-loop]
---

# Dev Handoff: Fix pidstat Collector

## Status / Authorization Gate

fpc-01 and fpc-02 are human-approved; **fpc-03 durable spool/recovery technical checks
complete; human review/acceptance pending**, candidate3of3 under the unit budget
beginning21:52PDT. Original host pytest runner is missing; not counted as PASS.
Scoped Lintap edits and isolated Ubuntu arm64 guest work were explicitly
approved. The human subsequently authorized topic commits on
`work/pidstat-and-dbt-validation`; packaging/service changes and agent deployment
remain outside this authorization.
Read [[wiki/work/fix-pidstat-collector/verification]] and inspect actual datasets and
source diffs before proceeding. fpc-03 used all3 candidate revisions; further repair
requires explicit budget extension. Do not start packaging/service work under this
authorization. Read the guarantee/rollback limits and uploader-receipt tension.
Use `validation/pidstat-loop/README.md` and [[wiki/tool/pidstat-implementation-loop]].
Canonical consumer `../Wintap-PyUtil` received separate authorization for the
source-aware local/S3 preflight, documented in
[[wiki/work/dbt-source-validation/verification]]. That change is not a pidstat
compatibility workaround or canonical real-host DBT qualification.

**Four-hour run completed and technically reviewed:** default5s/300s sensor-on
`lintap-dev`,2026-10-31T05:18:50Z–09:18:50Z; all processes stopped cleanly.
49pidstat files/399312rows,2880uninterrupted5s sample times, exact26-column schema,
80/80smoke generations, measured Go median0.47%one-coreCPU/~17MiB RSS. Read
[[wiki/work/fix-pidstat-collector/soak_review]] and the latest verification entry.
Local evidence: `validation/pidstat-loop/evidence/four-hour-20261031T0520/`;
guest originals: `/var/tmp/pidstat-four-hour-20261031T0520`. Private archive-copy
transfer fixed SFTP parent permissions without relaxing original evidence access.
Do not reset the root, restart this completed test or delete evidence. Retain
startup-harness, incidental shared NuGet restore and sensor coverage findings.
Same-session technical collection pass, **not human acceptance**; packaging remains
blocked. Paired-live Python, comparative resources, DBT and platform gates remain.

## Review Now; Historical Start Prompt Below

Open a new Analytics session and run `/pidstat-review fpc-03; inspect source and
evidence recorded in wiki/work/fix-pidstat-collector/verification.md`. Record human
decision before any fpc-04 work; same-session inspection is not independent review.

Start with `/pidstat-loop fpc-01: prove static binaries and actual Python/Go
Parquet compatibility; stop for human review`. The command loads the skill in the
current Build session. The following supplies the full scope if needed:

> Implement the compatibility-preserving Go pidstat rewrite using
> `wiki/work/fix-pidstat-collector/brief.md` and `implementation_plan.md`.
> Read applicable repository instructions and `verification.md` first. The first
> live target is the existing Multipass lintap-dev, Ubuntu arm64; do not recreate
> it or infer RHEL 8 proof. Work only within the expressly approved Lintap collector,
> build/test/package/docs scope plus Analytics wiki records. Preserve unrelated work,
> services, environments and telemetry. Start with fpc-01: freeze actual Python
> output and demonstrate pure-Go Parquet compatibility and static arm64/amd64 builds.
> Preserve and execute the existing Python reference through final review. Require
> exact replay parity on identical captured real /proc inputs and a paired-live
> comparison with predefined timing tolerances. Review actual results from both
> versions, every column, row multiplicity and unmatched rows; synthetic fixtures
> alone are not acceptance. Use ../Wintap-PyUtil for canonical downstream checks.
> Pause for review of the spike before the full port. No uv/Python/DuckDB/cgo runtime
> dependency, no child sampler/converter, no production downstream changes to hide
> incompatibilities. Follow the native pidstat-loop skill: three candidate revisions
> or 60 minutes per requested unit unless explicitly changed. Use evidence.py for
> deterministic evidence, not an external controller. Confirm permissions first.
> Record commands/results/findings after each unit, rerun affected and cumulative
> gates, and escalate rather than weaken compatibility tests. No field rollout,
> source deletion outside reviewed scope, commit/push/merge/release without approval.

## Required Context

- [[wiki/work/fix-pidstat-collector/brief]]
- [[wiki/work/fix-pidstat-collector/implementation_plan]]
- [[wiki/work/fix-pidstat-collector/verification]]
- `../Lintap/pidstat-collector.py`, bootstrap/launcher, collector tests.
- Both package builders/units/env files, canonical packaging guide, applicable AGENTS.md.
- [[wiki/concept/lintap-cpu-unit-conventions]], [[wiki/repo/lintap-supporting-repo]].
- Historical [[wiki/work/improve-pidstat-collector/design]]; current source wins over
  obsolete historical runtime/deployment details.
- Read `../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` and shared
  `macros/{paths,raw_sources}.sql`. Wintappy's checkout was renamed to Wintap-PyUtil;
  the canonical source location is resolved.

## Deferred Decisions

Go1.27.3, parquet-go0.32.0/pure-Go ZSTD and `../Lintap/pidstat-go` are the spike's
tested initial choices accepted at fpc-01; release license/security review is pending.
The Python reference is unchanged and hash-pinned in verification.md. Sampler/config
raw replay and durable recovery checks now pass. The default-cadence four-hour
resource observation is complete; packaging, comparative resources, paired-live,
DBT and inspected native RHEL/amd64 qualification remain pending. The operator
reports successful RHEL execution, not yet inspected native evidence. Review fpc-03
evidence/blocked pytest runner and authorize the next unit; use `/pidstat-review`
in a manually opened new session for fresh review. Human velocity
estimates were not collected in this planning session; do not invent retrospective
sealed values or read future sealed estimates before independent estimating.
