---
title: "Smoke-test results dashboard"
type: tool
confidence: high
grounded_by:
  - streamlit/projects/SmokeTests/main.py
  - streamlit/projects/SmokeTests/queries.py
  - streamlit/projects/SmokeTests/README.md
  - streamlit/projects/SmokeTests/garage.example.json
  - streamlit/projects/SmokeTests/requirements.txt
  - ../wintap/devtools/smoke_manifest.py
  - ../wintap/devtools/network_endpoint_smoke_test.py
  - streamlit/projects/SmokeTests/s3_source.py
  - streamlit/projects/SmokeTests/page_views.py
  - streamlit/projects/SmokeTests/analysis.py
  - streamlit/projects/SmokeTests/batch_views.py
  - streamlit/projects/SmokeTests/result_store.py
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/SmokeTests; ../wintap/devtools
tags: [streamlit, smoke-tests, portable-manifests, cross-host, validation]
---

# Smoke-test results dashboard

End-to-end diagram: [[wiki/workflow/live-collector-validation]] — known activity,
shared telemetry/evidence delivery, and explicit S3-backed validation.

## Configure and launch against S3

Run these steps on your **analysis machine** (for example your Mac), as your normal
login user, from the **Wintap-Analytics repository root**. This recipe uses `uv` to
install the app's Streamlit, DuckDB and boto3 dependencies and keep them available
while Streamlit runs.

### 1. Create the connection config

For first-time setup, copy the example and edit it (`cp -n` preserves an existing
config):

```bash
mkdir -p "$HOME/.config/wintap-smoke"
cp -n streamlit/projects/SmokeTests/garage.example.json \
  "$HOME/.config/wintap-smoke/garage.json"
nano "$HOME/.config/wintap-smoke/garage.json"
```

Set these values to the destination used by your collector uploader:

```json
{
  "endpoint": "https://garage.example.invalid",
  "region": "us-east-1",
  "datasets": ["s3://example-bucket/example-prefix"],
  "max_files": 10000
}
```

| Field | What to enter |
|---|---|
| `endpoint` | S3 API origin, including `http://` or `https://` and a port if needed. The bucket/prefix belongs in `datasets`. |
| `region` | Region used by the existing S3/Garage deployment. |
| `datasets` | S3 root containing the uploaded `raw_sensor/` tree; one or more roots are supported. |
| `max_files` | Listing cap; `10000` is the starting default. |

For example, if an uploaded object is
`s3://example-bucket/example-prefix/raw_sensor/raw_smoke_test/dayPK=20261030/hourPK=14/example.parquet`,
use **`s3://example-bucket/example-prefix`** as the dataset. A dataset ending in
`/raw_sensor` is also accepted. The app's config path is local to the analysis
machine; its dataset entries are remote S3 URLs.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/garage.example.json; streamlit/projects/SmokeTests/s3_source.py §load_config, dataset_parts -->

### 2. Select credentials in the same terminal

Use an existing AWS profile with access to that S3 dataset; replace the example
profile name:

```bash
export AWS_PROFILE="your-existing-profile"
```

The app uses boto3's standard credential chain. Existing `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY` and optional `AWS_SESSION_TOKEN` environment variables also
work; when using those, omit the profile command. Environment credentials take
precedence over profile credentials. Credentials belong in that chain, not in
`garage.json` (the config parser rejects credential fields).

If this machine has no profile yet and the AWS CLI is installed, create one
interactively using the credentials issued for the existing S3/Garage dataset:

```bash
aws configure --profile wintap-smoke
export AWS_PROFILE=wintap-smoke
```

Reading requires bucket listing and object reads. Saving all-canary summaries also
uses the sibling `analysis/smoke-tests/v1/` prefix described below.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/s3_source.py §open_source; streamlit/projects/SmokeTests/README.md §Read directly from Garage / S3; streamlit/projects/SmokeTests/result_store.py §save_result -->

### 3. Launch Streamlit

Still in the **Wintap-Analytics repository root**, in that same terminal:

```bash
export WINTAP_SMOKE_CONFIG="$HOME/.config/wintap-smoke/garage.json"
uv run --no-project \
  --with-requirements streamlit/projects/SmokeTests/requirements.txt \
  python -m streamlit run streamlit/projects/SmokeTests/main.py \
  --server.address 127.0.0.1 \
  --server.port 8501
```

Open **<http://127.0.0.1:8501>** on that analysis machine. Leave the terminal running;
**Ctrl-C** stops the app. Later sessions only need the credential selection and
launch commands. Here `uv run` owns the entire running app process, so its dependency
environment remains available for the app's lifetime.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/README.md §Read directly from Garage / S3; streamlit/projects/SmokeTests/requirements.txt; streamlit/projects/SmokeTests/main.py §main -->

### 4. Load and validate your run

1. The sidebar should select **Garage / S3** and show your **Local S3 JSON config**
   path automatically. Leave the local parquet root and optional JSON inputs empty
   for automatic S3 discovery.
2. Set **Start partition day** / **End partition day** to include the run's UTC
   collection/publication days, using `YYYYMMDD`. Default is yesterday through today.
3. Click **Refresh files / results**. The page reports evidence and telemetry file
   counts; uploaded `raw_smoke_test` supplies the run manifests automatically.
4. Select the test host, then **Canary Tests** → `telemetry-workload` → the exact
   run → **Validate selected run**. For a recurring expanded round, use
   **Run all validations for this canary**.

If no run appears, check the dataset prefix, UTC window and uploaded
`raw_smoke_test` objects. If the app reports **Cannot read S3 source**, check the
launching shell's credentials, endpoint connectivity and DuckDB `httpfs` availability;
the extension-cache option is documented in the source README's S3 section.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/main.py §main; streamlit/projects/SmokeTests/page_views.py §test_page; streamlit/projects/SmokeTests/batch_views.py §canary_batch_page; streamlit/projects/SmokeTests/README.md §Read directly from Garage / S3 -->

## App behavior

Streamlit pages separate **Overview**, **Canary Tests** and **Dev-time Tests**.
Overview reads manifests only, without telemetry metadata/scans. Test pages offer
family/run selection, saved selectors/reports and explicit selected-run validation
with tailored SQL, coverage and rows. Missing runs/data are expected, never PASS.
Read-only in-memory DuckDB queries do not start tests, stop collectors, run DBT
or modify raw data. All-canary analysis writes summary-only results beside the dataset.
Analytics owns the app; Wintap owns scripts/manifest production.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/main.py §main -->

Canaries are bounded stimuli against the already-running collector, not unattended
dev-time acceptance. Analytics owns the adapters/runner; Wintap owns the reused
generators and shared manifest publisher. New canary test IDs cover cross-domain,
process lifecycle/short-lived children, eight-file activity, optional native clone
and same-host TCP endpoints. Legacy `stimulusOnly` runs route to Canary Tests but
do not establish new suite coverage. Dev-time capture/tracer/package/startup tests
stay manual because some manage collectors, alter settings or use public networks.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/page_views.py §is_canary, test_page; validation/telemetry-soak/canary-stimulus.py; validation/telemetry-soak/run-smoke-soak.sh -->

## Portable test-host evidence

Updated Wintap smoke scripts accept `--manifest /path/to/run.json`; default
`./smoke-results/<test>-<uuid>.json`. The shared `smokeManifestVersion: 1` envelope
identifies test/run UUID, hostname/platform/architecture, UTC boundaries, runner,
selectors, status and optional saved report. It is written before validation and
completed on failure as well as success. Never overwrite an existing run manifest.
Internal named-workload workers do not produce separate top-level runs.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §smoke_run; ../wintap/devtools/telemetry_smoke_workload.py §__main__ -->

## Automatic durable evidence

**Root-owned field-host quick start:** follow
[[wiki/tool/named-telemetry-smoke-workload]] for the full user-created persistent
venv → sudo-Python →
`--smoke-data-root` → S3 → selected-run validation procedure. It includes separate
checks for generation, local parquet publication and S3 arrival, plus the exact
interpreter handoff when root cannot find `uv` or import DuckDB. Use the named
venv's `bin/python`, not a temporary `uv run --with` interpreter path.

All decorated harnesses accept `--smoke-data-root PATH`, where PATH contains
`raw_sensor`. `WINTAP_DATA_ROOT` enables it too; `--no-smoke-parquet` opts out.
Python DuckDB exports typed metadata/full manifest JSON/SHA-256 into
`raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH/` using UTC **publication** time.
Up to three immutable start/first-selectors/final snapshots share a run UUID;
first selectors do not necessarily mean the entire stimulus has finished. Active
files are ignored, latest revision wins across partitions, hash/metadata conflicts
warn and exclude the run. JSON remains local/manual fallback; export failures warn
without changing the workload result. No retry daemon or long-term source spool.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §_publish, smoke_run; ../wintap/devtools/smoke_parquet.py §publish -->

Dashboard automatically discovers run parquet alongside telemetry. Source deletion
and normal mounted/uploader latency are accepted; no transport hardening or delivery
acknowledgements required. Local mode uses analysis-local/mounted/synced paths;
read-only Garage/S3 mode uses a private JSON config and AWS environment/profile
credentials. JSON manifest directory/upload is optional. VM selector paths remain
telemetry values, not files the Mac must open. DBT integration is deferred.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §load_manifests -->

### Read-only Garage/S3 source

Use the [configuration and launch quick start](#configure-and-launch-against-s3)
above. `WINTAP_SMOKE_CONFIG` selects a local, uncommitted JSON config. Config fields are endpoint,
region, dataset roots containing `raw_sensor`, optional UTC day window/file cap and
extension cache. Credentials are excluded from config/UI and resolved from the AWS
chain. Boto3 performs paginated ListObjectsV2; DuckDB reads explicit S3 object URLs
using a temporary in-memory secret, path-style addressing and normal HTTPS checks.
No raw-object mutation, persistent credential store, collector management or local
dataset sync is introduced. Explicit isolated-network HTTP warns; no TLS bypass.
Summary persistence separately requires read/write on the sibling analysis prefix;
missing permissions are reported without changing policies or raw-data permissions.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/s3_source.py §load_config, open_source, discover_files -->

Both evidence and telemetry share the configured connection. Listing narrows to
inclusive UTC day partitions (default yesterday/today, maximum 31 days); file caps
abort rather than silently truncate. UI refresh relists; arrival is not a completeness
watermark. Existing hash/conflict, host/PID/time and pending/stimulus-only semantics
remain unchanged. Sensitive remote error details are suppressed. The operator
reports evidence reaching S3; agent all-round validation is recorded in
[[wiki/work/smoke-test-dashboard/verification]]. Operator UI acceptance remains separate.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/main.py §main; streamlit/projects/SmokeTests/queries.py §load_manifests, prepare_data -->

Selector entries must be objects with a supported `process`, `file`, `network`
or `host` domain. Invalid entries (including JSON `null`) warn and exclude that
manifest without preventing valid runs from rendering. Empty selector lists remain
valid for early lifecycle snapshots.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §validate_manifest, load_manifests -->

Queries require test hostname + UTC window + PID, plus file paths/prefix or socket
ports/protocol as available. FirstSeen fields are preferred to serializer flush
time; FILETIME and Unix time scales normalize to UTC. HOST checks match exact
captureRunId. Normal ETL hostname matches case-insensitively; unlabelled direct
output is excluded unless the user asserts a single-source test-host name.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §prepare_data, selector_query -->

## Results and limits

Run grouping is test + UUID, **not** process name or machine-local file path.
Repeated manifest copies deduplicate; conflicting copies warn. Event rows do not
carry smoke UUID, so overlapping same-host runs with shared PID/time/endpoints
remain potentially ambiguous; run sequentially and keep clock padding narrow.

Saved harness PASS/FAIL and current query observations are distinct. Named workload
status is stimulus completion only. Original identity/loss/parent assertions are
not all revalidated by dashboard coverage. File mmap is Read; normal ETL aggregates;
row counts are not EventCount or distinct-process counts. Consult
[[wiki/schema/runtime-capability-receipt]] for hook/filter context. Legacy run
inference and DBT outputs are intentionally unsupported.

The manifest overview defaults to latest runs per host/test with optional history
and host filters; saved failure is red, otherwise capture remains not-evaluated/yellow.
It never infers green from a saved generator/harness success. Canary inventory marks
unrecorded new suites explicitly. **Validate selected run** and **Run all validations
for this canary** are explicit telemetry scan triggers; navigation/selectors do not
evaluate history automatically. Matching persisted round summaries need no new scan.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/page_views.py §manifest_rows, overview_page, test_page -->

Selected-run red means harness/workload failure or observed thread/identity/parent
violation; yellow means
pending/incomplete/limited/ambiguous evidence, skipped tests or stimulus-only success;
green is a scoped passing harness plus required selected observations (trace report
only for actual-object trace); gray means no run supplied. Thread absence requires
positive companion process capture. Elapsed time is not a transfer watermark;
missing rows remain yellow. Overlapping same-host runs sharing PID/time selectors
are conservatively ambiguous, but an existing red failure/violation remains red;
ambiguity never downgrades it to yellow. An entirely missing host cannot be inferred from
absent manifests. Attribution checks include hidden/unevaluated run intervals.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §evaluate_case, evaluate_run, mark_overlaps -->

**Quality assertions:** file activities are checked per explicitly expected path
(with its own activities when `pathExpectations` is present, e.g. rename lifecycle)
(or every observed path for older count-only manifests). Lifecycle rows require
non-placeholder identities, and required Stops must link to each observed Start
identity. This is not canonical-hash recomputation or PID-reuse proof. Repeated Starts
retain raw Clone/Exec observations and source-classification counts; missing provenance
is unconfirmed, not an automatic duplicate birth. Network selectors retain expected-
protocol mismatches and either host-relative or directed matching ports. All bound
Send/Recv candidates are checked, including malformed extra rows; independently
contradictory known fields remain red even when other fields are null. All known
fields must match one consistent bound endpoint role; missing fields are separately
incomplete and genuinely unbound candidates remain yellow. No reported violations
still does not certify all selected observations. Original counterexamples are in
[[wiki/work/wintap-telemetry-identity-and-data-quality/quality_followup_analysis]].
The bounded working set and saved-summary fingerprints cover the stronger checks.
No strict dev-time gate was weakened. IPv4 TCP/UDP endpoint assertions use each
`endpointExpectations` protocol; older TCP-only manifests default to TCP.
Casefold-only path matches are explicitly unconfirmed, not exact Linux identity;
older normal-ETL output lost case. The approved sensor projection now preserves
producer path case and persists nullable `ProcessStartSource`; dashboard normalization
uses that explicit field whenever its column exists, including authoritative null/
invalid values as unknown. Only files lacking the column fall back to real Arguments
breadcrumbs: complete whitespace-delimited tokens, one distinct recognized value,
no conflicting/unknown values, never CommandLine text. Missing source stays
unclassified; source-classified repeated Starts
still are observations, not additional births or a capture-completeness verdict.
See [[wiki/tension/linux-file-path-case-projection]] and
[[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]].
The optional explicit local CLI adds trusted-object/projection gates and the same
summary persistence; see [[wiki/work/wintap-telemetry-identity-and-data-quality/rhel9_validation]].
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §selector_query, evaluate_case; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §HandleEvent -->

Validation normalizes the selected source's candidate files, scans the union of
the selected run's exact selector predicates once into a temporary in-memory table,
then reuses it for checks/details. Overlapping selectors do not duplicate rows.
Row budget is 100,000 matching observations; DuckDB memory is 256 MB with disk spill
disabled. Budget/read failure is unavailable validation, not a truncated PASS.
These bounds do not cap network bytes or wall-clock duration. Individual details
remain fresh/explicit; round summary persistence is described below. Native timestamp
pushdown/partition pruning remains a follow-up: uncertain files are not discarded.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/page_views.py §materialize_run, test_page -->

### All-canary summary and startup context

**Run all validations for this canary** evaluates every recorded family/case in one
round, including skips/missing families, using one shared bounded observation table.
Membership uses explicit `canaryRoundId`, or the shared `--manifest` parent `round.*`
directory for older expanded manifests; otherwise the run stays standalone. No guessed
time grouping or dev-time harness execution. Original strict loss/count assertions are
not all reconstructed by these selected-observation checks.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/analysis.py §canary_rounds, analyze_round; validation/telemetry-soak/run-smoke-soak.sh -->

HOST history is listed independently of the canary partition window, with fail-closed
file/receipt budgets. Validation compares collector enabled/status/tier/hook outcomes,
numeric/boolean features and effective settings from the latest preceding complete
startup. Temporal correlation is not continuous health or exact collector ownership;
conflicts/startup races/restarts yield ambiguous, missing/invalid receipts unknown.
Disabled/failed/partial collectors explain possible gaps, never PASS or red downgrades.
Unique short/FQDN relations from manifest/receipt names are optional inferred aliases;
collisions/different DNS suffixes are rejected. Individual queries remain exact-hostname.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/analysis.py §read_receipts, runtime_context, hostname_aliases, case_context; streamlit/projects/SmokeTests/s3_source.py §discover_host_files -->

Summary JSON and a latest pointer live at the dataset's sibling
`analysis/smoke-tests/v1/<hashed-round>/`, on S3 (first configured dataset) or local
files. Writes/read-back verification never touch raw telemetry/manifests. Summary
contains run references, checks/counts/skips and sanitized startup context, not raw
rows/credentials/source configuration. Local destinations must remain outside Git
and cannot escape through symlinks. Saved results are private dataset artifacts.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/result_store.py §location, save_result -->

Fingerprint includes manifests/hidden overlaps, listed object identities, source/window,
normalization assertion, budgets/padding, evidence errors, evaluator/source/store code
and DuckDB version. Matching summaries reload without telemetry scans. Changed inputs
show prior results with **STALE** warning; explicit/forced validation refreshes them.
Listing/evidence reads still repeat and are not an atomic snapshot or completeness
watermark. SHA-256 catches accidental corruption, not malicious tampering; incompatible
results fail closed. Save failures stay visibly memory-only, with save retry without
rescanning. No disk-spilled telemetry or credentials are introduced.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/analysis.py §input_fingerprint; streamlit/projects/SmokeTests/batch_views.py §canary_batch_page; streamlit/projects/SmokeTests/result_store.py §load_result, save_result -->

Workload: [[wiki/tool/named-telemetry-smoke-workload]].
Verification: [[wiki/work/smoke-test-dashboard/verification]].

### TCP endpoint confirmation

`network-endpoints` manifests exercise separate-process and same-process socket
ends via one assigned non-loopback IPv4 address. Normal-ETL network capture now
includes these checks by default. The dashboard independently checks each role's
Send/Recv using directed SourcePort/DestinationPort, Local/Remote IP-and-port pairs,
and stable/distinct process hashes. Even same-IP/same-PID receive reversals are red;
missing directed provenance remains unconfirmed. Explicit network opt-outs remain
yellow. Old/direct parquet cannot certify normalized endpoint correctness.
Dashboard checks now include additional candidates bound by the expected host-relative
or directed port pair. Shared-PID traffic without a complete binding stays ambiguous;
the standalone dev-time validator remains a separate contract.
<!-- GROUND_TRUTH: ../wintap/devtools/network_endpoint_smoke_test.py §validate_rows; ../wintap/devtools/network_capture_smoke_test.py §main; streamlit/projects/SmokeTests/queries.py §evaluate_case; §evaluate_run -->

Scoped Ubuntu arm64 live proof: [[wiki/work/network-endpoint-normalization/verification]].
