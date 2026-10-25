# Smoke-test results dashboard

From **Wintap-Analytics** on the analysis machine (macOS is supported):

```bash
python3 -m pip install -r streamlit/projects/SmokeTests/requirements.txt
python3 -m streamlit run streamlit/projects/SmokeTests/main.py
```

This standalone app does not require Wintappy, DBT or a writable DuckDB database.
It reads finalized raw parquet with DuckDB in memory. Each section has a test-run
selector, run command, saved result, tailored SQL, activity/event-count summary,
coverage indicators and matching rows. Empty/missing tests and data are normal.
It **never executes tests or changes collector configuration**.

## Collection host and analysis host can differ

Updated scripts in `../wintap/devtools/` accept `--manifest /path/to/run.json`.
Without it they write `./smoke-results/<test>-<uuid>.json`. Choose a fresh filename.
The manifest is written before validation and finalized even when the test fails.
It carries a UUID, test name, test hostname, UTC interval, selectors and saved
results. No old-data inference is supported.

On the Linux test host, from the Wintap repo:

Wait for collector startup and HOST capability publication before generating the
workload. `systemctl start` returning does not necessarily mean sensor attachment
is complete. A startup-race run can correctly show generated activity but no data.

```bash
python3 devtools/telemetry_smoke_workload.py \
  --output /home/ubuntu/qa/stimulus-001 \
  --manifest /home/ubuntu/qa/manifests/run-001.json
```

## Automatic durable evidence (recommended)

Use a Python environment with `duckdb` installed on the test host:

```bash
python3 devtools/telemetry_smoke_workload.py \
  --output /home/ubuntu/qa/stimulus-002 \
  --smoke-data-root /var/log/lintap/data
```

All harnesses share `--smoke-data-root PATH` (the directory **containing**
`raw_sensor`). Setting `WINTAP_DATA_ROOT` also enables export automatically;
`--no-smoke-parquet` disables it. An interactive shell does not inherit the service's
environment file: set the root explicitly. Ensure the user has write access to the
smoke subtree; do not make the entire data tree world-writable. Workload files must
remain outside the collector's filtered data/runtime roots.

Completed evidence is written atomically to:

```text
raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH/
  <host>+raw_smoke_test+<run-id>+<revision>+<hash>.parquet
```

Parquet holds typed metadata plus the complete manifest JSON and SHA-256. Up to
three immutable snapshots (start, first nonempty selectors, final) share a UUID.
Partitions mean **UTC publication time**, not run start. Latest revision wins
across partitions; duplicate conflicts/hash or metadata mismatches are reported.
Active files are ignored. SIGKILL can leave only an incomplete snapshot: yellow.

This new evidence type rides the existing mounted-directory/uploader path with
normal latency; no transport changes, acknowledgements or long-term source retention
are required. Point the dashboard at the analysis-visible data root or `raw_sensor`
directory: it discovers runs automatically, without a separate manifest transfer.
S3 upload needs no new event allowlist. The app reads local/mounted/synced files or
**Garage/S3 directly** using the configuration below. A stopped/disabled uploader
will not transfer anything; mounted developer datasets remain directly visible.

## Read directly from Garage / S3

Run on the analysis machine, independently of collectors and signal generators.
From Wintap-Analytics, copy `garage.example.json` to a private config outside Git
(for example `~/.config/wintap-smoke/garage.json`) and edit only local values:

```json
{
  "endpoint": "https://garage.example.invalid",
  "region": "us-east-1",
  "datasets": ["s3://example-bucket/example-prefix"],
  "max_files": 10000
}
```

Each dataset is a root **containing `raw_sensor/`**, or that `raw_sensor/` directory
itself. Add multiple roots for separate host prefixes, or one shared collection root
if all hosts write to its common `raw_sensor` tree. Do not enter the bucket root if the
actual layout is `bucket/<collection-prefix>/raw_sensor/`. Scheme, endpoint, bucket
and prefix must match the existing uploader configuration; never paste real values
or credentials into committed documentation. App-local `*.local.json` files are
also Git-ignored, but an outside-repo config is preferred.

Credentials use the normal AWS environment/profile chain. Select an existing
**read-only** profile with `AWS_PROFILE`, or provide `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY` and optional `AWS_SESSION_TOKEN` privately in the launching
environment. Do not put key values in JSON, commands saved to shell history or UI.
The config rejects credential/unknown fields. Required access is ListBucket on the
selected prefixes plus GetObject on their telemetry/evidence objects; no write or
delete access is needed. Path-style addressing supports Garage. HTTPS certificate
verification stays enabled. Explicit `http://` is allowed with a UI warning for an
intentionally isolated test endpoint; there is no insecure-TLS option.

Launch with a disposable uv dependency environment (does not sync/alter Wintappy):

```bash
export WINTAP_SMOKE_CONFIG="$HOME/.config/wintap-smoke/garage.json"
# Optional: export AWS_PROFILE=<your-existing-read-only-profile>
uv run --no-project \
  --with-requirements streamlit/projects/SmokeTests/requirements.txt \
  python -m streamlit run streamlit/projects/SmokeTests/main.py \
  --server.address 127.0.0.1
```

Open the local URL Streamlit prints. The config environment variable selects Garage
mode automatically; alternatively choose **Garage / S3** in the sidebar and supply
the config path. Local/mounted mode remains unchanged. No settings are persisted by
the dashboard. Boto3 lists objects and DuckDB reads them directly with a temporary,
in-memory S3 secret; there is no dataset download/sync or persistent secret file.

Default window is yesterday through today (UTC); optional `start_day` and `end_day`
config fields and sidebar controls use **YYYYMMDD**. Listing is paginated and pruned
to `dayPK=` prefixes, inclusive 1–31 days. Evidence partitions reflect publication
time, so include adjacent days for midnight runs. Objects uploaded late may require
an older partition window; the window is not a transport-completeness watermark.
Listing refreshes on every rerun/Refresh click. File caps fail closed, never silently
truncate a passing result. Large windows still require per-file schema reads and
can be slow; start with one or two days.

Both `raw_smoke_test` and telemetry use the **same configured connection/source**;
manifest hashes, revision conflicts, hostname/run selectors and missing-data triage
remain unchanged. S3 connection/read diagnostics suppress details that might contain
credentials or signed URLs. An unavailable source is an error, not empty green data.

On a network-restricted analysis host, optionally set `extension_directory` to a
shared local DuckDB extension-cache directory with official `httpfs` installed for
**DuckDB 1.5.6 and that OS/architecture**. This setting is applied at connection time.
Linux and macOS extension binaries are not interchangeable. No auditing/signature
checks are disabled; prepare the appropriate cache on a compatible connected system.

Collector upload success and smoke-generation success do not prove complete sensor
capture. The operator reports smoke evidence arriving in S3; actual Garage dashboard
validation remains a separate pilot check.

JSON is still saved locally for manual troubleshooting. Missing DuckDB, write
permissions, or oversized (>4 MiB) manifests produce a visible export warning
without changing the workload's outcome. There is no retry daemon. You can still
upload JSON or set an optional manifest directory. VM file paths in selectors are
telemetry values, not files the Mac must open.

Run grouping is **test + run UUID**. Queries additionally require the manifest's
test hostname, UTC window and PID/path/ports. Hostnames are case-normalized.
Repeated runs are never combined merely because their process names match. If
same-revision manifest copies disagree, the app warns and excludes that run.

## At-a-glance triage

The host-by-test overview has status counts, host filters, history/attention-only
filters and links/run-selection buttons to jump to the interesting section:

- 🔴 Harness/workload failure or observed thread/identity/parent violation.
- 🟡 Pending/incomplete data, missing coverage, skipped cases, ambiguous overlaps,
  export/read errors, or stimulus-only completion.
- 🟢 Finished passing harness plus required selected observations; actual-object
  trace green is scoped to its saved trace report, not pipeline collection.
- ⚪ No run supplied. Entirely missing hosts cannot be inferred from absent evidence.

Harness outcome and observed coverage are separate columns. Missing data stays
yellow—normal transfer latency is accepted, and elapsed time is not a delivery
watermark. Green is not full platform certification. Thread absence needs positive
companion process capture; overlapping same-host runs sharing PID/time selectors
are conservatively ambiguous. The overview evaluates aggregate queries once per
refresh; detail events are fetched with a bounded display limit, not all rows.

Normal ETL has Hostname. For **unlabelled direct-parquet**, select a root containing
only that host's unlabelled data and explicitly enter the *test* hostname. Without
it the rows remain unattributed. Never enter the analysis machine's name by default.
Overlapping same-host runs sharing PID/time/ports can still be ambiguous: event rows
do not carry smoke run UUID. File paths are unique; run tests sequentially for clean
process/network attribution. Clock tolerance is explicit and adjustable (default
15 seconds). FILETIME and Unix seconds/milliseconds/microseconds/nanoseconds or
ISO times are normalized; FirstSeen fields are preferred to serializer flush time.

## Tests covered

- Named cross-domain Python workload (process/file/TCP/UDP cases).
- Existing process, file and network capture tests.
- TCP endpoint normalization, including same-host separate-PID and same-PID sockets.
- Clone actual-object trace, direct pipeline and packaged acceptance.
- Runtime capability receipts, matched by exact captureRunId.

Actual-object trace's report is its primary result: that runner does not emit
sensor parquet. Direct/packaged/startup harnesses are operational tests for an idle
designated host; heed their command warnings. Network-capture uses external public
endpoints; use the standalone TCP endpoint test when external traffic is inappropriate.

The saved **harness result** is distinct from dashboard **observations**. Coverage
indicators are not a replacement for original parent/hash/loss assertions. Current
Linux mmap folds into Read; rename/truncate have no dedicated activity. Normal ETL
aggregates events: row count differs from EventCount, and Starts differ from distinct
processes. Missing data is never displayed as PASS. DBT retention/joins, continuous
health and certification across distros remain out of scope.

## Tests

```bash
python3 -m unittest discover -s streamlit/projects/SmokeTests -p 'test_*.py' -v
```

Tests exercise empty UI, repeated run selection, uploaded portable manifests,
host/PID/path/time isolation, timestamp formats, normal and direct schemas, and
exact HOST receipt matching, plus live-producer parquet schema, revision/conflict/
hash validation and overview severity/filter/navigation. Contract tests read
`../wintap/devtools/smoke_parquet.py` live, so that sibling checkout is required
for these tests (not for running the app). The sibling Wintap manifest/workload regressions run
with `python3 devtools/test_smoke_manifest.py -v` and
`python3 devtools/test_telemetry_smoke_workload.py -v` on Linux.

S3 tests use synthetic configs/listings/credentials and injected files, including
Streamlit source selection, read-only connection settings and fail-closed limits.
The optional real loopback HTTP/S3 test requires cached httpfs and is enabled with
`SMOKE_S3_HTTP_TEST=1`. It exercises signed boto3 listing plus DuckDB range reads,
not real Garage/TLS/authorization or multi-host acceptance.
## TCP endpoint confirmation

The **TCP endpoint normalization** section runs two same-host cases via an assigned
non-loopback IPv4 interface: separate client/server processes and a single process
owning both ends. It independently checks directed source/destination ports against
normalized local/remote IP-and-port pairs and process hashes. The normal network
command also enables these checks (now the normal-ETL default).

New sensor parquet must contain `SourcePort` and `DestinationPort`; old data or
direct-parquet output cannot prove this invariant. Missing provenance stays
unconfirmed; observed reversals are red. Explicit network-test opt-outs stay yellow.
The one-process case intentionally has the same IP and `pid_hash` at both ends;
only the directed socket ports distinguish the roles.
