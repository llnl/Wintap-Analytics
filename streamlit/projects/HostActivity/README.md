# Recent Host Activity dashboard

Standalone, manually refreshed Streamlit view of S3 `raw_sensor` object metadata
and, optionally, raw Parquet row counts. The default metadata view reads object
keys and sizes only; it does not open Parquet contents. The optional row-count
view uses an in-memory DuckDB connection. Neither mode requires DBT, a
materialized database, or another Analytics app.

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
Use a profile restricted to read/list access for the selected dataset. Metadata
mode uses boto3 `ListObjectsV2` and S3's `Size` field; it sends no object GETs.
The optional row-count mode creates an in-memory DuckDB S3 secret that is closed
after refresh. No S3 writes are issued. `httpfs` may be installed by DuckDB on
first launch if it is not already available.

## Dashboard semantics and limits

- The default query mode is **File metadata**, intended as a quick herd overview.
  It lists all supported event families (or one selected family) under the
  `dayPK`/`hourPK` partitions intersecting the last 12 hours in UTC. It groups
  per-host file counts and S3 object sizes over time and shows a per-host summary.
  Both metrics have their own collect-time chart. It does not read Parquet data.
- Filenames use `hostname+event_type+FILETIME.parquet`; the Win32 FILETIME in
  the filename is treated as collect time, not S3 upload/`LastModified` time.
  The same capture time determines `dayPK`/`hourPK`, and the filename timestamp
  is filtered to the exact rolling 12-hour interval. Malformed filenames are
  counted and reported but excluded from host/time totals.
- **Raw Parquet rows** remains available as a separate, slower query mode. It
  requires selecting one family, inspects schemas, and applies row-level event
  time filtering. It reports physical source-row counts, not logical-event totals.
- Refresh is manual; changing query mode or family does not query S3. Partial
  boundary hours can mean 13 hourly partitions. Metadata listing is limited to
  those partitions; row mode then filters the precise event-time interval.
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
- The initial bucket is five minutes. It widens to bound expected host/bucket
  chart points. The chart includes observed buckets only; it does not fill gaps
  with zeroes.
- Absolute raw-row counts can use linear or logarithmic scale. Normalized mode
  divides each host's values by that host's own peak and is only for comparing
  temporal shape, not volume.
- Limits fail closed: at most 10,000 discovered objects and 1,000 chart points
  per view. Standard row-mode families also retain the 2,000,000 in-window
  raw-row cap. `raw_process_file` instead aggregates all matching rows directly
  in DuckDB (no sampling/raw-row truncation), under a 120-second query limit,
  1 GB memory and temporary-storage limits, and a 20,000 intermediate
  host/time-group limit; its output still obeys the 1,000-point budget. Any
  exceeded limit yields no partial chart.
- During refresh, the status panel reports metadata listing and aggregation, or
  row-mode object listing/schema inspection/aggregation. Elapsed time is shown
  in the completed status and alongside the resulting snapshot. Budget/schema
  failures are reported without producing partial charts.

This is an availability snapshot, not a completeness or collector-health
assertion. Missing files, late arrivals, absent partitions, malformed names, and
missing hostnames are not interpreted as zero activity. File size is S3 object
size and does not establish that the Parquet content is valid or complete.

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
