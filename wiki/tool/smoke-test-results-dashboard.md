---
title: "Smoke-test results dashboard"
type: tool
confidence: high
grounded_by:
  - streamlit/projects/SmokeTests/main.py
  - streamlit/projects/SmokeTests/queries.py
  - streamlit/projects/SmokeTests/README.md
  - ../wintap/devtools/smoke_manifest.py
  - ../wintap/devtools/network_endpoint_smoke_test.py
  - streamlit/projects/SmokeTests/s3_source.py
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/SmokeTests; ../wintap/devtools
tags: [streamlit, smoke-tests, portable-manifests, cross-host, validation]
---

# Smoke-test results dashboard

From **Wintap-Analytics**, on the analysis machine:

```bash
python3 -m pip install -r streamlit/projects/SmokeTests/requirements.txt
python3 -m streamlit run streamlit/projects/SmokeTests/main.py
```

Separate sections cover the named cross-domain workload, process/file/network
capture validators, Clone trace/direct/package harnesses and runtime-capability
checks, plus TCP endpoint normalization. Each offers a run command, run selector, saved result, tailored SQL,
coverage indicators and raw rows. Missing runs/data are expected, never PASS.
Read-only in-memory DuckDB queries do not start tests, stop collectors, run DBT
or modify data. Analytics owns the app; Wintap owns scripts/manifest production.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/main.py §main -->

## Portable test-host evidence

Updated Wintap smoke scripts accept `--manifest /path/to/run.json`; default
`./smoke-results/<test>-<uuid>.json`. The shared `smokeManifestVersion: 1` envelope
identifies test/run UUID, hostname/platform/architecture, UTC boundaries, runner,
selectors, status and optional saved report. It is written before validation and
completed on failure as well as success. Never overwrite an existing run manifest.
Internal named-workload workers do not produce separate top-level runs.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §smoke_run; ../wintap/devtools/telemetry_smoke_workload.py §__main__ -->

## Automatic durable evidence

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

Set `WINTAP_SMOKE_CONFIG` to a local, uncommitted JSON config; example and launch
commands are in `streamlit/projects/SmokeTests/README.md`. Config fields are endpoint,
region, dataset roots containing `raw_sensor`, optional UTC day window/file cap and
extension cache. Credentials are excluded from config/UI and resolved from the AWS
chain. Boto3 performs paginated ListObjectsV2; DuckDB reads explicit S3 object URLs
using a temporary in-memory secret, path-style addressing and normal HTTPS checks.
No object mutation, persistent credential store, collector management or local
dataset sync is introduced. Explicit isolated-network HTTP warns; no TLS bypass.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/s3_source.py §load_config, open_source, discover_files -->

Both evidence and telemetry share the configured connection. Listing narrows to
inclusive UTC day partitions (default yesterday/today, maximum 31 days); file caps
abort rather than silently truncate. UI refresh relists; arrival is not a completeness
watermark. Existing hash/conflict, host/PID/time and pending/stimulus-only semantics
remain unchanged. Sensitive remote error details are suppressed. The operator
reports evidence reaching S3; dashboard validation against that real source is pending.
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

The top-level host-by-test overview defaults to latest runs with optional history,
host and attention filters, status counts and section/run navigation. Red means
harness/workload failure or observed thread/identity/parent violation; yellow means
pending/incomplete/limited/ambiguous evidence, skipped tests or stimulus-only success;
green is a scoped passing harness plus required selected observations (trace report
only for actual-object trace); gray means no run supplied. Thread absence requires
positive companion process capture. Elapsed time is not a transfer watermark;
missing rows remain yellow. Overlapping same-host runs sharing PID/time selectors
are conservatively ambiguous, but an existing red failure/violation remains red;
ambiguity never downgrades it to yellow. An entirely missing host cannot be inferred from
absent manifests. Aggregate checks cover all matching events; detail reads are bounded.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §evaluate_case, evaluate_run, mark_overlaps, overview; streamlit/projects/SmokeTests/main.py §main -->

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
<!-- GROUND_TRUTH: ../wintap/devtools/network_endpoint_smoke_test.py §validate_rows; ../wintap/devtools/network_capture_smoke_test.py §main; streamlit/projects/SmokeTests/queries.py §evaluate_case; §evaluate_run -->

Scoped Ubuntu arm64 live proof: [[wiki/work/network-endpoint-normalization/verification]].
