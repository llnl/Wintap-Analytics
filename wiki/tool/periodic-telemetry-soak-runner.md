---
title: "Periodic Linux telemetry soak stimuli"
type: tool
confidence: high
grounded_by:
  - validation/telemetry-soak/run-smoke-soak.sh
  - validation/telemetry-soak/network-endpoint-stimulus.py
  - validation/telemetry-soak/canary-stimulus.py
  - validation/telemetry-soak/README.md
  - ../wintap/devtools/smoke_manifest.py
  - ../wintap/devtools/smoke_parquet.py
  - ../wintap/wintap/core/etl/load/CacheManager.cs
policy: agent-editable
last_validated: 2026-10-30
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

Diagram and terminology: [[wiki/workflow/live-collector-validation]] — live-collector
validation, with recurring bounded runs described as telemetry canaries.

For the root-owned data-directory/Python setup and S3 handoffs, start with
[[wiki/tool/named-telemetry-smoke-workload]]. Create its persistent venv as the login
user, then pass `PYTHON="$HOME/.local/share/wintap-smoke/venv/bin/python"` to
`sudo bash ... --python "$PYTHON"`. The runner README's `uv run --no-sync` lookup
assumes an existing project environment; a temporary `uv run --with` interpreter
is not a substitute. Supply the actual local collector
`--data-root`; the runner passes it to each workload as `--smoke-data-root`.
Its Python environment requires DuckDB 1.5.6. Keep the runner's evidence root outside
collector data/runtime roots and configured file filters because it also contains
the file stimuli; `$HOME/qa/wintap-smoke-soak` is an example. Begin with `--rounds 1`.
<!-- SYNTHESIS: validation/telemetry-soak/README.md §Generation; validation/telemetry-soak/run-smoke-soak.sh §ROUND, args; ../wintap/devtools/README.md §Portable smoke run manifests and results dashboard -->
<!-- CONTRADICTION[soft]: the runner README example puts evidence-root under runtime/smoke-soak, while shared workload guidance excludes collector runtime paths; prefer an external QA root for portable file-capture checks. -->

The operator explicitly wants the signal generator disconnected from the regular
deployed Lintap service, launched separately on each Linux test host (e.g. tmux),
with SmokeTests dashboard analysis rather than DBT manifest integration. Shared
evidence-root publication is the only coupling; stopping either process does not
control the other.

The runner repeats five non-interfering **canary** families: named cross-domain
process/file/IPv4 loopback TCP/UDP, the existing process lifecycle generator with
six short-lived children and per-PID Stop expectations, eight-file activity,
one optional prebuilt native clone helper round, and same-host non-loopback TCP
endpoint stimuli. Each publishes its own `canary-*` manifest, distinct from dev-time
capture/tracer/package/startup qualification. It does not run local capture queries:
successful collector upload deletes local parquet, so local-only polling would race
the intended S3 path. Success is explicitly stimulus-only, not capture acceptance.
<!-- GROUND_TRUTH: validation/telemetry-soak/run-smoke-soak.sh; validation/telemetry-soak/network-endpoint-stimulus.py; ../wintap/wintap/core/etl/load/CacheManager.cs §upload -->

No collector management, settings changes, tracer attachment, public-network probes
or pressure tests are added. Python execveat unavailability and native helper/kernel
skips are explicit, not fabricated coverage; posix_spawn remains libc-selected best
effort. Passive HOST correlation now lives in the dashboard, not a recurring test; full
runtime capability/restart/opt-out tests remain manual. Existing running generators
must be stopped/relaunched independently for expanded coverage; preserve old evidence.
<!-- GROUND_TRUTH: validation/telemetry-soak/canary-stimulus.py; validation/telemetry-soak/README.md -->

The shared wrapper exports immutable evidence snapshots under
`<data-root>/raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH/`. It understands
`WINTAP_DATA_ROOT` or `--smoke-data-root`, not `WINTAP_DATA_PATH`. The runner supplies
the explicit root so sudo environment filtering cannot silently disable export.
JSON/logs/workload files remain protected outside Git in unique session/round roots;
real selectors are local evidence, never committed documentation.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §smoke_run; ../wintap/devtools/smoke_parquet.py §publish; validation/telemetry-soak/run-smoke-soak.sh -->

Runner exports a shared `WINTAP_CANARY_ROUND_ID` for the five adapters, recorded as
`canaryRoundId` in each manifest. This is grouping metadata, not an event identity or
sensor setting. Older expanded runs can group by their shared manifest round directory.
<!-- GROUND_TRUTH: validation/telemetry-soak/run-smoke-soak.sh; validation/telemetry-soak/canary-stimulus.py; validation/telemetry-soak/network-endpoint-stimulus.py; streamlit/projects/SmokeTests/analysis.py §round_key -->

Defaults: 900-second delay after a sequential round, 120-second timeout per workload
plus 5-second kill grace, unlimited rounds. `--rounds 1` runs a pilot. Failures and
incomplete/export-error manifests remain visible while later rounds continue. One
flock per evidence root excludes same-root concurrent runners. Ctrl-C stops only
the runner; no service/security/credential/retention changes are made. Evidence and
total storage remain open-ended and require operator review; no automatic pruning.
<!-- GROUND_TRUTH: validation/telemetry-soak/run-smoke-soak.sh -->

Native clone-family stimulus is optional and explicitly skipped without a supplied
already-built helper. Runner tests are mocked orchestration, not native host proof.
The operator reports a pilot round completed and smoke evidence arriving in S3;
agent Garage all-round validation now records process/file/TCP endpoint observations,
TCP Accept/UDP Receive gaps and explicit native-clone skips in
[[wiki/work/smoke-test-dashboard/verification]]. Steady-state ground-truth coverage
and long-duration performance remain pending; no full acceptance inferred.

**DBT does not currently ingest or validate smoke manifests.** Existing SmokeTests
dashboard discovery works with mounted/synced raw smoke parquet or the configured
read-only Garage/S3 source; DBT ground-truth joins remain a follow-up, not implied
by a passing DBT build. See
[[wiki/tool/smoke-test-results-dashboard]] and
[[wiki/tool/named-telemetry-smoke-workload]].
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/dbt_project.yml; streamlit/projects/SmokeTests/queries.py §load_manifests -->
