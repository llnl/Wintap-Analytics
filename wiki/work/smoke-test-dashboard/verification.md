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
  - streamlit/projects/SmokeTests/test_pages.py
  - validation/telemetry-soak/test_canaries.py
  - validation/telemetry-soak/test_runner.py
  - streamlit/projects/SmokeTests/test_analysis.py
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

## Quality follow-up — 2026-10-25

User authorized recommended-order implementation and local disposable-VM iteration.
First strengthened Analytics only: per-path activity completeness, non-placeholder
lifecycle identities, Start/Stop linkage, source-aware repeated-Start counts, and
all-attributable endpoint/protocol checks. Thirteen synthetic adversarial tests were
added; one prior exact-missing-check assertion now includes the new linkage check.
No canonical-hash recomputation, exact birth counts or loss-equivalence claim.

On the idle Ubuntu arm64 qualification VM, a new isolated environment preserves the
pre-existing SDK/Python environments. DuckDB 1.5.6, Streamlit 1.66.1 and boto3
1.43.118 installed; source snapshot excludes local private configuration/evidence.
`SMOKE_S3_HTTP_TEST=1 <isolated-python> -B -m unittest discover -s
streamlit/projects/SmokeTests -p 'test*.py'`: **88 tests passed, zero skips/failures**.
The first Mac run exposed one stale expected-missing-list assertion; corrected
without weakening the new check. VM HTTP/S3 test uses synthetic credentials/data
only and normal DuckDB extension validation. No actual Garage writes or field-host
changes in this slice; unchanged cached summaries become stale via code fingerprint.

## All-round validation, runtime comparison and persistence — 2026-10-25

User requested all validations on the uploaded single-round canary, one action for
all permutations, HOST configuration comparison and persisted results beside data.
Analytics alone changes: shared round grouping metadata (no stimulus changes), one
bounded shared observation table, conservative runtime context and summary-only
S3/local storage with verified writes/checksum/fingerprints/stale warnings.

**Live Garage findings (sanitized; no private input/output artifacts in this repo):**

- The newest uploaded round contains all five families, with generation status passed.
  Initial exact-hostname validation saw no rows: manifest FQDN versus telemetry/HOST
  short name. Optional unique short/FQDN correlation restores observations but is
  explicitly inferred, not exact identity proof; collisions are rejected.
- Process lifecycle/short-lived case: 43 selected rows, all recorded observations
  (including per-PID Start/Stop) present, no reported violations.
- Eight-file case: 40 selected rows, all recorded activities/path expectations present.
- Same-host separate-process and same-process TCP endpoints: 8 selected rows each;
  Send/Recv, endpoint orientation/provenance and identity checks observed, no violations.
- Cross-domain cases capture named process/file/client-network observations and
  positive companion process evidence; thread-only selection has no process row.
  **Server TCP Accept and UDP Receive are missing**, with no other missing recorded
  expectations/observed violations. Native-clone families are explicitly skipped.
- Preceding complete HOST receipt reports Execve, Clone, Exit, FileOps, Network and
  ProcessRundown running; SELinux partial. Network startup does not explain the two
  missing network activities. This is a startup snapshot, not continuous health or
  proof of which collector produced an event. Producer maps those activities and
  EPL preserves activity grouping, so no source-grounded "disabled by design" waiver
  is justified. Root cause/loss stage remains unlocalized.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §HandleEvent; ../wintap/wintap/core/etl/esper/tcp.epl; ../wintap/wintap/core/etl/esper/udp.epl -->
- Final five-family analysis took approximately 57 seconds on the selected source. All
  family triage remains yellow (stimulus-only/inferred attribution/skips/gaps), not
  capture certification. Summary and latest pointer saved/read-verified in the same
  Garage dataset's sibling analysis prefix. No raw telemetry/manifests modified.
  Source/configuration/credentials/host identifiers/raw output were not saved locally
  or committed; S3 summary is a private dataset artifact by explicit user request.

**Regression commands/results:**

- Qualified isolated interpreter: DuckDB 1.5.6, Streamlit 1.66.1, boto3 1.43.118.
  `SMOKE_S3_HTTP_TEST=1 python -B -m unittest discover -s
  streamlit/projects/SmokeTests -p 'test_*.py' -q`: **75 passed**. Includes real
  synthetic HTTP/S3 listing/range reads, round/parity/Stop/budget/alias/collision,
  temporal/race/restart/disabled/unknown, red preservation, hidden overlap, credential-safe
  errors, local/S3 summary writes/read-back/checksum/caps, Git/symlink rejection and
  actual Streamlit all-family one-scan, relaunch reuse, stale and save-retry tests.
- `python3 -B -m unittest discover -s validation/telemetry-soak -p 'test_*.py' -q`:
  **17 passed**, mocked orchestration/adapters (expected rejected unsafe-argument output).
- `bash -n validation/telemetry-soak/run-smoke-soak.sh`, Python AST parse and
  `git diff --check`: pass.

No sibling source, SDK/DuckDB pins, sensor/service settings, tracer attachment or
running generator restart changes. No PR publication. Operator new UI/multi-host/
long-duration acceptance, native clone and unresolved network coverage remain open.
Dashboard does not reconstruct every dev-time strict loss/count/identity assertion.

## Canary and multipage extension — 2026-10-25

User narrowed recurring tests to non-interfering canaries and authorized the app
update with Overview, Canary Tests and Dev-time Tests pages. Added real Streamlit
navigation, manifest-only overview and explicit selected-run validation. Only the
selected run is evaluated; full-source schemas are read on validation, then exact
selector matches are materialized once and all checks/details reuse memory. Limits
are 100,000 matched rows / 256 MB DuckDB memory, spill disabled, fail closed. No
native timestamp/partition pruning or cross-rerun result cache claimed. Hidden run
intervals still participate in overlap warnings; saved failures and stimulus-only
semantics remain conservative. Old stimulus-only manifests route to Canary Tests.

Analytics runner now emits five separately named canary families via safe generator
adapters. Process lifecycle checks require Stop per selected PID; file stimulus is
eight paths; native helper is optional/one round with explicit skips. No collector,
uploader, service/security setting, sibling code or running host workload changed.
No private S3 config/profile, host identifiers or live data were persisted.

Commands/results in the existing isolated temporary dependency environment:

- `SMOKE_S3_HTTP_TEST=1 python -B -m unittest discover -s
  streamlit/projects/SmokeTests -p 'test_*.py' -q`: **51 passed** (DuckDB 1.5.6).
  AppTest switches actual Streamlit file-based pages, proves zero telemetry calls on
  overview/navigation/selection, selected-run-only evaluation, legacy classification,
  empty/invalid evidence handling and remote fail-closed/stimulus-only results.
  Working-set parity/deduplication, row budgets, per-PID Stop and hidden overlaps pass.
  Synthetic real HTTP/S3 listing/range reads retain query parity after materialization;
  the post-materialization plan has no READ_PARQUET scan. No live Garage benchmark.
- `python3 -B -m unittest discover -s validation/telemetry-soak -p 'test_*.py' -q`:
  **17 passed**, mocked Linux tools/generators, including safe adapter boundaries,
  five-family orchestration, failure continuation, private paths, skip and controls.
- `bash -n validation/telemetry-soak/run-smoke-soak.sh`: pass.
- `git diff --check`: pass; all dashboard/page and canary Python modules parse.
  Final additional AppTest cases verify that exhausted working-set budgets never
  call the evaluator, and skipped/no-selector native canaries never read telemetry.

Native expanded canaries, timeout/signal behavior and real Garage page/selected-run
validation remain operator-assisted gates. Startup receipts are not regenerated or
passively correlated by the runner; manual dev-time capability tests remain separate.
Live observations from the earlier read-only investigation were not filed as artifacts.

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
