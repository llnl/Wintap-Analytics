# Recent Host Activity dashboard

Standalone, manually refreshed Streamlit view of S3 `raw_sensor` object metadata
and, optionally, raw Parquet row counts. The default metadata view reads object
keys and sizes only; it does not open Parquet contents. The optional row-count
view uses an in-memory DuckDB connection. Neither mode requires DBT, a
materialized database, or another Analytics app.

Activity is always **Live diagnostic — uncoordinated**. Reads can overlap
compaction/entity publication and observe partial, duplicated or mixed-generation
data. They are not a consistent snapshot or authoritative verification, even when
advisory status reports `OPEN`.

## Configure and run

Use the same environment variables as `wintap_dbt`. The dataset value is the
root **containing** `raw_sensor/`, not the `raw_sensor` directory itself:

```bash
export WINTAP_DBT_RAW_SENSOR_DATASET=s3://your-bucket/your-dataset
# Or use WINTAP_DBT_DATASET; WINTAP_DATA_ROOT is the final fallback.
export AWS_PROFILE=your-read-only-profile
# Optional, using the same variable names (region prefers AWS_DEFAULT_REGION):
export AWS_DEFAULT_REGION=us-west-2  # or AWS_REGION
# AWS_ENDPOINT_URL may be a bare host[:port] or an HTTP(S) origin.
export AWS_ENDPOINT_URL=s3-compatible.example
export DUCKDB_USE_SSL=true

cd streamlit/projects/HostActivity
uv sync
uv run streamlit run main.py
```

Credentials come only from the standard AWS credential chain / selected profile;
the app has no credential input, config file, or dashboard-specific S3 variables.
At the bottom of the sidebar, an effective-environment info box shows
the resolved dataset and non-secret AWS/transport settings. Credential values
are never displayed.
Use a profile restricted to read/list access for the selected dataset. Metadata
mode uses boto3 `ListObjectsV2` and S3's `Size` field; it sends no object GETs.
The optional row-count mode creates an in-memory DuckDB S3 secret that is closed
after refresh. No S3 writes are issued. `httpfs` may be installed by DuckDB on
first launch if it is not already available.

## Advisory Status, Runs and Partitions

Navigation also exposes a manually refreshed local producer export. Status reads
need no dataset/AWS configuration, SDK calls, DuckDB connection or coordinator lock.
Configure all three deployment values before using **Refresh advisory status**:

```bash
export WINTAP_STATUS_EXPORT=/absolute/path/to/coordinator-state/status.json
export WINTAP_STATUS_BINDING_SHA256='<64-lowercase-hex canonical binding hash>'
export WINTAP_STATUS_LEDGER_ID='<32-lowercase-hex ledger identity>'
```

Use independently trusted operator configuration for the pins, not values copied
automatically from an untrusted export. The binding hash covers the entire canonical
producer binding, including every active root and optional entity policy (PyUtil
`protocol.digest(binding)`). The path must be an absolute regular `status.json`
file, not a final-component symlink, FIFO, device or database. Serving-account read
permission must be explicitly arranged; same server does not imply access. The
producer normally publishes the export with mode `0600`.

- Supported producer contract: `wintappy.coordination.service.status_page` v1,
  at most 1 MiB and 100 records per kind. Only allowlisted summaries are rendered;
  binding roots, authority payloads and free-form block diagnostics are withheld.
- Missing/unpinned/unreadable/malformed exports and wrong identities/versions show
  **unavailable**, never `OPEN` or zero activity. Observation and retrieval times
  are distinct. An observation over 180 seconds old is visibly stale; age is only
  presentation, never process-death or recovery evidence.
- Within one session, a producer timestamp rollback is refused. V1 has no monotonic
  sequence; same-second changes and whole-session restarts cannot prove freshness.
  Changed deployment pins/path clear cached summaries. Navigation uses the cache
  and never polls automatically or fetches subsequent ledger pages.
- **Status** shows reported mode/cursor/owner and reserved/queued counts. Reserved
  is not grant delivered. Process-lock observation, progress and delivery are unavailable.
- **Runs** shows bounded raw-run intent markers, sorted by intent time and run ID.
  Actual launch/finish and completion certificates are unavailable. `COMPLETED` is
  reported disposition only; maintenance `FINISHED` does not authorize reopening.
  Continuations mean incomplete history, not a seven-day or latest-run selection.
- **Partitions** is a metadata-only raw/compacted hourly-presence overview. It
  defaults to the most recent 42 complete UTC days and discovers the union of
  event-family directories under `raw_sensor/` and `compacted/`. Each heatmap
  cell is `compacted-present-hours / 24`; raw-only hours contribute zero,
  compacted/raw overlap counts as compacted, and a cell is blank only when no
  hour is present in either root. Hover details include raw, compacted, overlap,
  and observed-hour counts. The view performs bounded S3 `ListObjectsV2`
  prefix/delimiter requests only; it does not read Parquet or claim migration
  completeness. A Live diagnostic warning remains visible.

Advisory status is never permission to read, complete, delete, repair or reopen.
Its pins identify only the status source; Activity keeps its separately configured
raw root. Activity remains synchronous/raw-only. Full catalog/timeline, managed
live jobs and optional coordinated refresh are not yet implemented or qualified.
 No recovery controls, scheduler or deployment are added.

## Dashboard semantics and limits

- The default query mode is **File metadata**, intended as a quick herd overview.
  The default time range is the rolling last 12 hours in UTC. Choose **Custom
  dayPK/hourPK range** to select the first and last UTC partition hours; both
  endpoints are inclusive, and the whole selected hours are processed. Custom
  ranges have no duration cap. A short warning appears above 24 hours.
  All-family (or one-family) metadata mode groups per-host file counts and S3
  object sizes over time and shows a per-host summary. Both metrics have their
  own collect-time chart. It does not read Parquet data.
- Filenames use `hostname+event_type+FILETIME.parquet`; the Win32 FILETIME in
  the filename is treated as collect time, not S3 upload/`LastModified` time.
  The same capture time determines `dayPK`/`hourPK`, and the filename timestamp
  is filtered to the exact rolling 12-hour interval. Malformed filenames are
  counted and reported but excluded from host/time totals.
- **Raw Parquet rows** remains available as a separate, slower query mode. It
  requires selecting one family, inspects schemas, and applies row-level event
  time filtering. It reports physical source-row counts, not logical-event totals.
- For `raw_process`, the chart can instead select **Experimental: likely user
  activity**. This deliberately cheap heuristic counts distinct normalized
  process names from `ActivityType = Start` events per user and fixed 15-minute
  UTC bucket, after small documented system/user and process deny-lists. It is
  a process-diversity/background-activity proxy, not interactive-session
  detection. Select one host to see a time-scaled heatmap with usernames on the
  y-axis and process-type diversity as cell intensity. Command lines, paths,
  and individual process details are not shown. The existing raw-row chart
  remains unchanged.
- Refresh is manual; changing query mode, family, or range does not query S3.
  The rolling default can intersect 13 hourly partitions because its boundary
  hours are partial. A custom range selects complete UTC partition hours. Both
  modes then filter filenames/event timestamps to the exact `[start,end)` range.
- Discovery lists only supported event families under overlapping
  `dayPK=YYYYMMDD/hourPK=HH` partitions. Recursive matching preserves nested
  network `protoPK` folders; metadata mode filters exact filename collect time,
  while row mode filters its family-specific event timestamp.
- In row mode, families with supported row-level host/time columns are counted
  as raw Parquet rows. A raw row is not necessarily a logical event, and counts
  from different families are not a universal event total.
- Timestamp interpretation follows producer semantics. Process `EventTime` is
  FILETIME; `raw_host`, `raw_process_file`, `raw_process_conn_incr`, and SELinux
  producer `EventTime` values are Unix seconds. File activity prefers
  `FirstSeen`/`LastSeen` FILETIME, and connection increments prefer
  `FirstSeenMs`/`LastSeenMs` FILETIME. Native timestamps and ISO strings are
  normalized to UTC-naive values; unknown numeric encodings are not guessed.
  The selected snapshot shows its timestamp fields and encoding priority.
  `Computer` is accepted as a hostname alias alongside `Hostname`/
  `ComputerName`. Unsupported families are listed with a reason.
- The initial bucket is five minutes. It widens to bound host/bucket chart
  points. For each host with at least one accepted observation in the selected
  interval, every bucket across the full interval is plotted; buckets with no
  returned files/rows are zero-filled. A host with no usable observation in the
  interval cannot be identified and does not get a synthetic series.
- Absolute raw-row counts can use linear or symmetric logarithmic scale (which
  remains compatible with zero-valued buckets). Normalized mode
  divides each host's values by that host's own peak and is only for comparing
  temporal shape, not volume.
- Chart hover text stays concise: UTC bucket time, host, and only the selected
  metric. Metadata hovers show file count or object size in MiB; raw-row hovers
  show row count or the normalized peak ratio; the experimental heatmap also
  shows the authorized username and process-type cell count.
- Limits fail closed for every range: at most 10,000 discovered objects and
  1,000 chart points per view. Partition discovery is lazy (metadata listing has
  at most eight concurrent partition requests; raw-row glob scans are chunked
  by 24 hours), so long ranges do not materialize all listing work at once.
  Standard row-mode families also retain the 2,000,000 in-window
  raw-row cap. `raw_process_file` instead aggregates all matching rows directly
  in DuckDB (no sampling/raw-row truncation), under a 120-second query limit,
  1 GB memory and temporary-storage limits, and a 20,000 intermediate
  host/time-group limit; its output still obeys the 1,000-point budget. Any
  exceeded limit yields no partial chart.
  The experimental `raw_process` user heatmap also uses an aggregate-only SQL
  scan and SQL-generated user/bucket cells. It remains available when the
  physical raw-row count exceeds the standard 2,000,000-row chart budget; in
  that case only the raw-row chart is withheld. Its fixed-resolution grid has a
  separate 20,000-cell budget instead of the ordinary 1,000-point line-chart
  budget.
- During refresh, the status panel reports metadata listing and aggregation, or
  row-mode object listing/schema inspection/aggregation. Elapsed time is shown
  in the completed status and alongside the resulting snapshot. Budget/schema
  failures are reported without producing partial charts.

This is an availability snapshot, not a completeness or collector-health
assertion. A zero-filled bucket means no qualifying object/row was returned for
that observed host and bucket; it does not establish true zero activity, complete
collection, or healthy telemetry. Missing files, late arrivals, absent partitions,
malformed names, and missing hostnames can still reduce coverage. File size is S3
object size and does not establish that Parquet content is valid or complete.

## Offline checks

```bash
cd streamlit/projects/HostActivity
uv run python -m unittest discover -s . -p 'test_*.py' -v
```

Tests create temporary local Parquet fixtures and use mocked file-discovery and
S3 metadata results. They do not access AWS or require a live S3 profile. A
bounded live 12-hour pilot confirmed selected-family row reads for representative
families; metadata mode has not been checked against live S3. See the linked wiki
feature record for anonymized measurements.
