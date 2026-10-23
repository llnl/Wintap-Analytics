---
title: "Retrospective interview: Linux capability smoke triage"
type: concept
confidence: medium
grounded_by:
  - wiki/work/clone-default-true/verification.md
  - wiki/work/smoke-test-dashboard/durable-evidence-plan.md
  - wiki/work/smoke-test-dashboard/verification.md
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/linux-capability-smoke-triage
tags: [feature-work, interview, retrospective]
---

# Retrospective interview

## Context established before reconstruction

Reviewed live uncommitted diffs across Wintap, Lintap, Analytics and Wintappy, and
existing Clone, receipt and dashboard evidence. Earlier improve-lintap-data-quality
remediation is committed work and is not re-counted as this new feature.

## Decisions recovered from the conversation

- Favor fork-only telemetry coverage; packaged Clone defaults true, explicit opt-out retained.
- Preserve separate raw fork/exec observations; guard resolver state instead of deduplicating.
- Use HOST for detailed startup evidence and shared durable-data storage for smoke runs.
- Accept normal mounted/uploader latency and source deletion; transport hardening,
  acknowledgements and long-term local retention are not blockers.
- Include a concise dashboard severity overview and cross-host run selection.
- Keep existing branches; commit selected feature work and supply appendable PR summaries.

## Constraints

No legacy data preservation. Collection and analysis hosts can differ. Missing
data is not PASS; generated stimulus and observed capture are different facts.
RHEL testing occurs elsewhere and must not be inferred from Ubuntu validation.
Preserve unrelated dirty/untracked work and do not push existing PR branches.

## Delegated implementation choices

User authorized implementation of the reviewed parquet/triage plan. Typed metadata
plus full JSON/hash, immutable coarse run revisions and UTC publication partitions
were adopted. DuckDB export is optional; JSON remains the stdlib fallback.

## Deferred

Direct S3 analysis access, DBT propagation, continuous health, namespace/PID reuse,
broader performance and remaining network coverage investigation.

## Confirmed playback

On 2026-10-23 the user accepted the umbrella feature scope/name after a cross-repo
inventory, and authorized retrospective artifacts and commits. Scope is distilled
in [[wiki/work/linux-capability-smoke-triage/brief]].

## Sealed — human estimates

Not collected. This is an explicitly retrospective workflow; no prospective
estimates or availability prediction are invented and no Velocity score is reported.
