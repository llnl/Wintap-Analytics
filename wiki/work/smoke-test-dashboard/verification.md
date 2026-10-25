---
title: "Verification: smoke-test results dashboard"
type: diagnostic
confidence: medium
grounded_by:
  - streamlit/projects/SmokeTests/test_queries.py
  - streamlit/projects/SmokeTests/test_app.py
  - ../wintap/devtools/test_smoke_manifest.py
  - ../wintap/devtools/test_telemetry_smoke_workload.py
  - streamlit/projects/SmokeTests/test_s3_source.py
  - streamlit/projects/SmokeTests/test_s3_http.py
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/SmokeTests; ../wintap/devtools
tags: [streamlit, smoke-tests, verification, cross-host]
---

# Verification: smoke-test results dashboard

## Scope

Analytics owns `streamlit/projects/SmokeTests/`; Wintap owns smoke workloads and
shared portable manifest writer. Existing unrelated dirty files preserved. No
legacy inferred test groups; test UUID plus manifest selectors distinguish runs.
Normal rows are scoped by hostname/time/PID/path/ports. Direct-parquet missing
hostname requires an explicit single-source test-host assertion, never Mac hostname.
Only finalized `.parquet` files are read, no writable dataset/DBT state opened.

## Commands / evidence

- App-local isolated macOS venv: installed Streamlit 1.50.0, DuckDB 1.4.5;
  no global dependency changes or lockfile rewrites.
- Seven DuckDB query regressions pass: host/PID/path/time isolation, timestamp
  scales, mixed normal/direct schemas, empty/broken files, independent uploaded
  manifests/repeated run IDs and exact HOST captureRunId.
- Full app suite: **11/11 pass**, including empty-state sections/commands and UI
  switching between two runs without mixing their PID selectors.
- Linux `test_smoke_manifest.py -v`: passes success/failure envelope retention.
- Linux `test_telemetry_smoke_workload.py -v`: two tests pass after portability
  changes, including exported envelope and internal worker separation.
- Nine modified smoke Python modules parse successfully.
- Deliberately absent-data file-capture run returns failure (exit 2) and saves
  `/home/ubuntu/dashboard-file-manifest.json` with exact path/PID/time selectors.
- Actual-object CO-RE Clone validation with new envelope passes 80 process/60
  thread cases, no missing/duplicate/false births, parent errors or skips. Envelope
  `/home/ubuntu/dashboard-clone-trace.json`; trace data at
  `/home/ubuntu/clone-validation/dashboard-clone-trace`.
- Fresh packaged normal-ETL capture completed on `lintap-clone-package`; two
  sequential workload manifests bundled independently with `raw_sensor`, transferred
  to Mac and queried using app code. **33 parquet files, two runs, no query errors.**
  Evidence in approved temp `dashboard-smoke-analysis/mac-query-report.json`.
  Run `e7301101-0364-4708-ae1a-7f45e6f71d36` observes process Start/Stop, five
  FileOps activities, client TCP connect/send/recv/disconnect and UDP send/recv.
  Server TCP Accept and server UDP Receive are **not observed**; dashboard exposes
  these rather than claiming full network acceptance. Thread TID has no process row.
  First run `30371dc3-6241-4bd1-aad6-201848c05fd4` ran before sensors were ready
  (systemctl return is not attach readiness); no matching rows in any case. It
  remains separate, not backfilled with second-run telemetry. Service stopped.
  Streamlit AppTest renders transferred data on Mac: **36 tables**, two run choices,
  no app exceptions/errors; switching to missing-data first run remains isolated.
  Early run's manifest predates final thread-negative/port improvements; it was
  used only to test missing-data isolation, not as a compatibility target.

## Durable evidence / triage extension — 2026-10-22

- User authorized implementation after accepting mounted/uploader latency and
  source deletion. No transport hardening, acknowledgements, retention daemon,
  package rebuild, DBT or direct S3 browser changes.
- macOS isolated venv: `python -m unittest discover -s
  streamlit/projects/SmokeTests -p 'test_*.py' -v`: **19/19 pass**. Added producer
  schema roundtrip, latest/reordered UTC partition revisions, multi-host copies,
  conflicting/hash/metadata rejection, partial arrival, severity/negative-companion
  checks, capability limitations, overview history/filter/navigation regressions.
- `multipass exec lintap-clone-package -- /home/ubuntu/receipt-venv/bin/python
  -m unittest discover -s /home/ubuntu/wintap/devtools -p 'test_smoke_manifest.py'
  -v`: **4/4 pass**. Explicit/environment roots, opt-out, failure JSON/final outcome,
  atomic lifecycle, UTC rollover and identical retry. Also pass on macOS.
- Linux workload regression command with `-p 'test_telemetry_smoke_workload.py'`:
  **2/2 pass**. Named workload remains stdlib-capable; worker runs stay separate.
- `py_compile` of app/query/producer/exporter passes; `git diff --check` passes
  in Analytics and Wintap. Unrelated dirty work preserved, no commits/pushes.
- New temporary Multipass mount: Mac approved temp `durable-smoke-analysis` →
  `/home/ubuntu/durable-smoke-analysis`. Installed package 104 launched directly
  with isolated data/runtime roots and 10/15-second ETL intervals, existing service
  left stopped/configuration unchanged. Two sequential named workloads generated
  source-only JSON `/home/ubuntu/durable-run-{0,1}.json`; **no JSON transfer**.
- Mac reads **23 telemetry + 6 evidence parquet files**, auto-discovers two final
  runs `65309265-7cca-4fb8-9450-a68f8c727570` and
  `c0688bc0-bedb-4e40-9d47-c11acd2dbc3a`. No manifest/query errors. AppTest renders
  **37 tables**, two run choices and overview 0 red / 1 yellow / 0 green / 7 gray
  (latest per test/host). Capture app terminated cleanly, exit 0.
- Both runs observe process Start/Stop, all five FileOps activities, client TCP/UDP
  and positive companion process capture with no named thread process row. Server
  TCP Accept and UDP Receive remain missing/yellow, not certified failures; optional
  native helper skipped and workload success is stimulus-only.
- Evidence report: approved temp `durable-smoke-analysis/mac-durable-report.json`;
  collector log/runtime on VM `/home/ubuntu/durable-smoke-collector.log` and
  `/home/ubuntu/durable-smoke-runtime`. Temporary mount/data retained for viewing.

## Remaining limits

### Read-only Garage/S3 extension — 2026-10-25

User authorized implementation/commit/push on the same feature branch; operator
reports smoke evidence arriving in S3. Added private credential-free JSON config,
standard AWS env/profile credentials, path-style addressing and a temporary in-memory
DuckDB secret; connection-time extension cache selection retains signature checks.
HTTPS verification remains enabled; explicit isolated-network HTTP warns. No object
writes/deletes, persistent credentials, dataset sync or collector/uploader changes.
Shared remote evidence/telemetry connection retains local query/manifest semantics.
UTC day-pruned paginated listing and file caps fail closed; refresh relists.

- Fresh isolated temporary uv environment uses DuckDB **1.5.6**, Streamlit **1.66.1**
  and boto3 **1.43.118**; no global or Wintappy environment/lock changes.
- `python -m unittest discover -s streamlit/projects/SmokeTests -p 'test_*.py' -v`:
  **42 passed** before adding the opt-in real HTTP transport test. Backend fixtures
  cover config rejection, date windows, pagination, exclusions, caps, duplicate roots,
  read-only secret/session-token settings and credential-safe errors; AppTest covers
  configured S3 discovery and fail-closed UI behavior. Local regressions still pass.
- `SMOKE_S3_HTTP_TEST=1 python -m unittest discover -s
  streamlit/projects/SmokeTests -p 'test_s3_http.py' -v`: **1 passed**. Real boto3
  signed listing and DuckDB range reads against a synthetic loopback HTTP server
  discover and join evidence/telemetry through explicit S3 URLs, using GET/HEAD only.
  The initial transport test caught unsupported `CREATE TEMP SECRET` syntax;
  corrected to `CREATE TEMPORARY SECRET` and reran successfully.
- Live Garage credentials/TLS/authorization and actual multi-host data validation
  remain operator pilot gates. No real host data/configuration/output persisted.
- Final complete suite with `SMOKE_S3_HTTP_TEST=1`: **43/43 passed**. All dashboard
  Python modules parse; `git diff --check` passes and app-local `garage.local.json`
  is confirmed Git-ignored. Streamlit bare-mode warnings are expected in AppTest.

The following general limits continue to apply:

Dashboard observation indicators do not reimplement all original harness checks;
saved results remain authoritative for those assertions. Event rows have no smoke
UUID: overlapping same-host process/network runs with reused identities/windows
can be ambiguous. Use sequential runs and narrow clock padding. Dataset source
host for unlabelled direct output is a user assertion, not auto-detected evidence.
DBT retention, continuous sensor health, other distros and legacy runs are out of scope.
