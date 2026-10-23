---
title: "Feature brief: Linux collection capability evidence and smoke-test triage"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/devtools/smoke_manifest.py
  - ../Lintap/packaging/lintap-deb/lintap.env
  - streamlit/projects/SmokeTests/main.py
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/devtools; ../wintap/wintap; ../Lintap/packaging; streamlit/projects/SmokeTests
tags: [feature-work, linux, clone, runtime-capabilities, smoke-tests, retrospective]
---

# Linux collection capability evidence and smoke-test triage

## Problem

Fork-only processes need collection coverage without confusing threads with
process births. Analysis must identify the collector's actual startup capabilities
and distinguish missing telemetry from successful stimulus generation. Manually
moving smoke manifests separately from telemetry becomes cumbersome across hosts.

## Goals

- Prefer authoritative CO-RE Clone process/thread classification; preserve raw
  fork/exec observations while protecting resolver identity from late birth metadata.
- Enable packaged Clone by default with administrator opt-out preserved.
- Persist versioned per-startup capability evidence on HOST, including selected
  objects, hook outcomes, configuration provenance and effective component settings.
- Provide editable named process/file/network workloads and repeatable validators.
- Publish portable smoke run evidence beside telemetry through the existing
  durable-data path, with independent collection and analysis hosts.
- Provide read-only host/test/run triage, scoped queries, clear absence states and
  navigation to interesting results.

## Non-goals

Legacy dataset/schema preservation; raw-event deduplication; continuous sensor
health; uploader redesign/acknowledgements/long-term source spool; direct S3
browsing; new DBT models; Windows collection changes or universal distro certification.

## User-facing behavior

Package templates enable Clone, retaining `WINTAP_ENABLE_CLONE_SENSOR=false`.
Startup publishes frozen HOST `RuntimeCapabilitiesJson` even in ETL/sensor-disabled
diagnostic runs. Failed/partial/disabled outcomes remain explicit. Fallback warns
that absent syscall flag hooks may admit false thread births.

All eight decorated smoke families accept `--manifest`, `--smoke-data-root` and
`--no-smoke-parquet`. Configured `WINTAP_DATA_ROOT` also enables optional DuckDB
export. Atomic immutable run snapshots live under
`raw_sensor/raw_smoke_test/dayPK=.../hourPK=...`; partitions mean UTC publication
time. JSON remains a fallback. The dashboard discovers runs alongside telemetry,
deduplicates revisions, filters hosts/history and distinguishes red/yellow/green/gray
states. Workload completion alone never constitutes capture PASS.

## Acceptance criteria

1. Ubuntu arm64 bounded baseline/churn captures include process births, exclude
   thread Starts and preserve parent/identity correctness; opt-out removes fork-only births.
2. HOST JSON equals final startup logging, stays frozen and receives a fresh run ID
   on restart; disabled/fallback evidence is retained.
3. Named workload generates representative process/file/loopback network stimuli;
   failures retain run selectors and reports.
4. Mounted Linux→Mac analysis discovers repeated runs without separately transferring JSON.
5. Queries isolate hostname/time/PID/path/endpoint selectors; unlabelled direct data
   needs an explicit single-host assertion. Missing/ambiguous/limited data remains
   attention, not PASS. Thread absence requires positive companion evidence.
6. Focused resolver/receipt/serializer, workload/manifest and dashboard regressions pass.

## Ownership and boundaries

Wintap owns sensor/resolver/receipt/workload code; Lintap owns package defaults and
payload/version validation; Analytics owns dashboard and shared wiki. Wintappy
has no new feature changes. Keep `feature/improve-lintap-data-quality` in all repos.
Exclude generated data, FUSE files, local state/editor settings and unrelated experiments.

## Open follow-ups

RHEL/x86_64 fresh acceptance; Clone-only overhead/loss-counter review; server TCP
Accept/UDP Receive gaps; namespace/PID reuse and downstream receipt temporal joins.
These are explicitly not certified by Ubuntu evidence.

## Workflow provenance

This brief was reconstructed from implemented work and explicit user decisions,
then confirmed on 2026-10-23. It is not a fabricated pre-implementation interview.
See [[wiki/work/linux-capability-smoke-triage/interview]],
[[wiki/work/linux-capability-smoke-triage/design]],
[[wiki/work/linux-capability-smoke-triage/references]],
[[wiki/work/linux-capability-smoke-triage/implementation_plan]],
[[wiki/work/linux-capability-smoke-triage/verification]] and
[[wiki/work/linux-capability-smoke-triage/pr_summaries]].
