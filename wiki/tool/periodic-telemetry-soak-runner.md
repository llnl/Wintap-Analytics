---
title: "Periodic Linux telemetry soak stimuli"
type: tool
confidence: high
grounded_by:
  - validation/telemetry-soak/run-smoke-soak.sh
  - validation/telemetry-soak/network-endpoint-stimulus.py
  - validation/telemetry-soak/README.md
  - ../wintap/devtools/smoke_manifest.py
  - ../wintap/devtools/smoke_parquet.py
  - ../wintap/wintap/core/etl/load/CacheManager.cs
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: validation/telemetry-soak; ../wintap/devtools
tags: [soak, smoke-test, ground-truth, linux, s3, manifests]
---

# Periodic stimuli, deferred validation

The user approved open-ended disposable-host collection, manual stopping, several
hosts and opportunistic S3-backed DBT checks. Analytics owns this small runner;
Wintap owns stimulus/manifest production and the collector uploader; Wintappy owns
the canonical DBT pipeline. See `validation/telemetry-soak/README.md` for commands.

The operator explicitly wants the signal generator disconnected from the regular
deployed Lintap service, launched separately on each Linux test host (e.g. tmux),
with SmokeTests dashboard analysis rather than DBT manifest integration. Shared
evidence-root publication is the only coupling; stopping either process does not
control the other.

The runner repeats named process/file/IPv4 loopback TCP/UDP stimuli followed by
same-host non-loopback TCP endpoint stimuli. It does not run local capture queries:
successful collector upload deletes local parquet, so local-only polling would race
the intended S3 path. Success is explicitly stimulus-only, not capture acceptance.
<!-- GROUND_TRUTH: validation/telemetry-soak/run-smoke-soak.sh; validation/telemetry-soak/network-endpoint-stimulus.py; ../wintap/wintap/core/etl/load/CacheManager.cs §upload -->

The shared wrapper exports immutable evidence snapshots under
`<data-root>/raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH/`. It understands
`WINTAP_DATA_ROOT` or `--smoke-data-root`, not `WINTAP_DATA_PATH`. The runner supplies
the explicit root so sudo environment filtering cannot silently disable export.
JSON/logs/workload files remain protected outside Git in unique session/round roots;
real selectors are local evidence, never committed documentation.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §smoke_run; ../wintap/devtools/smoke_parquet.py §publish; validation/telemetry-soak/run-smoke-soak.sh -->

Defaults: 900-second delay after a sequential round, 120-second timeout per workload
plus 5-second kill grace, unlimited rounds. `--rounds 1` runs a pilot. Failures and
incomplete/export-error manifests remain visible while later rounds continue. One
flock per evidence root excludes same-root concurrent runners. Ctrl-C stops only
the runner; no service/security/credential/retention changes are made. Evidence and
total storage remain open-ended and require operator review; no automatic pruning.
<!-- GROUND_TRUTH: validation/telemetry-soak/run-smoke-soak.sh -->

Native clone-family stimulus is optional and explicitly skipped without a supplied
already-built helper. Runner tests are mocked orchestration, not native host proof.
Garage delivery, steady-state coverage and long-duration performance remain pending.

**DBT does not currently ingest or validate smoke manifests.** Existing SmokeTests
dashboard discovery works with mounted/synced raw smoke parquet; direct S3 ground-
truth joins are a follow-up, not implied by a passing DBT build. See
[[wiki/tool/smoke-test-results-dashboard]] and
[[wiki/tool/named-telemetry-smoke-workload]].
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/dbt_project.yml; streamlit/projects/SmokeTests/queries.py §load_manifests -->
