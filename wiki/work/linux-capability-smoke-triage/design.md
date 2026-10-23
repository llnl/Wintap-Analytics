---
title: "Design: Linux capability evidence and smoke triage"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs
  - ../wintap/devtools/smoke_parquet.py
  - streamlit/projects/SmokeTests/queries.py
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap/wintap; ../wintap/devtools; streamlit/projects/SmokeTests
tags: [feature-work, design, clone, parquet, triage]
---

# Design

## Collection and resolver semantics

CO-RE Clone reads child PID/TGID and parent TGID, rejecting thread births. The
tracepoint fallback supplements legacy clone/vfork flags with clone3 reads, but
remains best-effort when flags/hooks are unavailable. Native ERR_PTR links are
rejected by a shared primary/auxiliary attach helper.

Clone messages mark provisional birth metadata with `PROC_START_SRC=sched_fork`.
A late birth cannot overwrite an established resolver row or reactivate its cache.
Raw fork/exec records remain distinct observations of one identity, not duplicates
to be suppressed. Windows producers are unchanged.

## Startup evidence

`RuntimeCapabilities` records versioned allowlisted settings, component-effective
limits, sensor enablement, selected object/tier/hash, attempts, hooks and failures.
Completion freezes the canonical JSON; restart creates a fresh capture UUID.
Idempotent lazy plugin initialization preserves earlier evidence. Final HOST
publication is independent of regular ETL/merge timers.

`RuntimeCapabilitiesJson` is a HOST string property and is included by existing
dynamic schema construction, even when null. The reviewed HOST-specific
`union_by_name` branch in RawSensorWriter was discarded; mixed legacy staging
schemas are not supported by this feature. No source writer compatibility branch
is added. Receipt JSON is startup evidence, not a persistent health monitor.

## Smoke data

Shared wrappers retain early/final JSON on success and failure. Optional Python
DuckDB export writes typed run metadata plus full manifest JSON/SHA-256, with up
to three immutable revisions: start, first selectors and final. First selectors
are a publication trigger, not necessarily proof all stimulus finished.

Files publish via `.parquet.active`→`.parquet` under
`raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH`; UTC publication partitions
do not define run identity. Run UUID/revision/hash controls grouping and conflict
handling. Existing mounts/uploaders move this dataset without a new sensor or
serializer. No retry daemon, delivery watermark or source retention requirement.

## Read-only analysis

Analytics scans run envelopes separately from telemetry, rejects hash/metadata or
same-revision conflicts, selects latest revisions and evaluates aggregate case
checks. Details use bounded row reads. Host/time/PID/path/endpoint scope is explicit;
unlabelled direct data needs a user assertion and same-host overlaps are ambiguous.

Overview: red = harness failure or explicit observed invariant violation; yellow =
pending/missing/limited/skipped/ambiguous/stimulus-only evidence; green = scoped
passing harness plus selected observations (actual-object trace report scope only
for that test); gray = no run supplied. Missing rows never become PASS merely
because enough wall time elapsed. HOST status/hook details remain available.

## Alternatives and exclusions

Rejected raw-event deduplication and new smoke sensors. JSON-only transfer was
superseded by parquet ride-along; manual JSON remains useful fallback. Generic
uploader durability hardening, DBT models and direct S3 reads remain out of scope.

Related: [[wiki/work/linux-capability-smoke-triage/brief]],
[[wiki/work/smoke-test-dashboard/durable-evidence-plan]].
