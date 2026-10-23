---
title: "Verification: Linux capability smoke triage"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/tests/Wintap.Tests/RuntimeCapabilitiesTests.cs
  - ../wintap/devtools/test_smoke_manifest.py
  - ../wintap/devtools/test_telemetry_smoke_workload.py
  - streamlit/projects/SmokeTests/test_durable.py
  - wiki/work/clone-default-true/verification.md
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap/tests; ../wintap/devtools; streamlit/projects/SmokeTests
tags: [feature-work, verification, retrospective]
---

# Verification

## Analytics PR review regressions — 2026-10-23

- Isolated venv command: `python -m unittest discover -s
  streamlit/projects/SmokeTests -p 'test_*.py' -v` — **23 passed**.
- New tests reproduce two passed process harnesses sharing thread TID 43 with
  a recorded Start: both remain red after overlap marking, retaining violation
  and ambiguity reasons. Green overlapping runs still become yellow.
- Invalid selector entries and missing/null/unknown domains are rejected with
  indexed warnings; valid companion manifests remain available. Empty selectors
  remain accepted. Streamlit AppTest confirms a null-selector JSON file does
  not abort valid-run or overview rendering.
- No sensor/package changes or live captures required for these dashboard fixes.

## Fresh pre-commit checks — 2026-10-23

- Wintap: `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter
  'FullyQualifiedName~RuntimeCapabilities|FullyQualifiedName~ProcessResolver|FullyQualifiedName~SerializerSchedule'
  --no-restore -v quiet` — **127 passed, zero failures/skips**. Existing
  Windows-platform/static-analysis warnings remain; no broad Windows suite claim.
- Analytics isolated venv: `python -m unittest discover -s
  streamlit/projects/SmokeTests -p 'test_*.py' -v` — **19 passed**.
- Ubuntu arm64 VM: `multipass exec lintap-clone-package --
  /home/ubuntu/receipt-venv/bin/python -m unittest discover -s
  /home/ubuntu/wintap/devtools -p 'test_smoke_manifest.py' -v` — **4 passed**,
  including intentional export-failure warnings and retained JSON.
- Same VM with `-p 'test_telemetry_smoke_workload.py'` — **2 passed**.
- Lintap: `bash -n packaging/lintap-deb/build-deb.sh
  packaging/lintap-rpm/build-rpm.sh` — passes.
- Selected source/package diffs pass `git diff --cached --check`; Analytics
  diff passes `git diff --check`. Selected stage excludes local state and experiments.

## Previously recorded live acceptance

Ubuntu 24.04 arm64 kernel 6.8.0-147-generic, fresh self-contained Debian 0.1.0-104:
80 baseline/400 churn process births captured, no false thread Starts, wrong worker
parents or PidHash splits. HOST/log equality, fresh restart IDs and opt-out passed.
Normal fallback hooks capture 80 processes/exclude 60 threads; deliberate missing
flag hooks admit 60 false thread births and remain explicitly unsafe.
Details: [[wiki/work/clone-default-true/verification]].

Mounted VM→Mac: 23 telemetry and 6 smoke-evidence parquet, two isolated final runs,
37 rendered tables, no separate JSON transfer or query errors. Process/five file
activities/client TCP/UDP observed; server TCP Accept/UDP Receive absent. Details:
[[wiki/work/smoke-test-dashboard/verification]].

## Review boundary

HOST property remains added; RawSensorWriter has no uncommitted change after the
user discarded the mixed-schema branch. Earlier recorded mixed-version claims
are historical tests, not the committed compatibility contract. Existing HOST
model/scheme construction includes the property even when null.

No package rebuild or fresh long capture was performed during this commit pass.
Package service-version stamping is syntax-reviewed, not a new RPM acceptance.
Local state/editor/FUSE/dataset artifacts and unrelated DLT/Fedora experiments are
excluded. Wintappy has no tracked change; its nested checkout is clean/detached.

## Known gaps

RHEL/Fedora acceptance, isolated Clone overhead/loss review, missing server network
activities, namespace/PID reuse, exact cross-event captureRunId attribution and
DBT receipt propagation remain open. Receipt is startup evidence, not continuous
health; green dashboard results are scoped, not platform certification.

Commit/PR record: [[wiki/work/linux-capability-smoke-triage/pr_summaries]].

Wintap commit `859a47b` (39 files); Lintap commit `cfc3f35` (seven files).
Analytics app/wiki/retrospective artifacts are committed together. No Wintappy
commit, no branch changes and no pushes.
