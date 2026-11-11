# Recent Host Activity dashboard

Standalone, manually refreshed Streamlit view of raw Parquet rows by host and
event family. It reads `raw_sensor` directly with an in-memory DuckDB connection;
it does not require DBT, a materialized database, or another Analytics app.

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
Use a profile restricted to read/list access for the selected dataset. The DuckDB
S3 secret exists only in a temporary in-memory connection, which is closed after
refresh. No S3 writes are issued. `httpfs` may be installed by DuckDB on first
launch if it is not already available.

## Dashboard semantics and limits

- Choose an event family before refreshing (the default is Process). Each
  explicit refresh scans only that family and snapshots the exact last 12 hours
  in UTC. Switching families does not query S3; click Refresh to load the newly
  selected family. The S3 scan is first
  restricted to the `dayPK`/`hourPK` directories intersecting that interval
  (partial boundary hours can mean 13 hourly partitions); exact event-timestamp
  filtering then runs only over Parquet objects found in those directories.
  Refresh is manual; UI selection changes do not trigger another S3 query.
- Discovery lists only supported event families under overlapping
  `dayPK=YYYYMMDD/hourPK=HH` partitions. Recursive matching preserves nested
  network `protoPK` folders; the query then filters exact event-time bounds.
- Event families with supported row-level host/time columns are counted as raw
  Parquet rows. A raw row is not necessarily a logical event, and counts from
  different families are not a universal event total.
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
  per family snapshot. Standard families also retain the 2,000,000 in-window
  raw-row cap. `raw_process_file` instead aggregates all matching rows directly
  in DuckDB (no sampling/raw-row truncation), under a 120-second query limit,
  1 GB memory and temporary-storage limits, and a 20,000 intermediate
  host/time-group limit; its output still obeys the 1,000-point budget. Any
  exceeded limit yields no partial chart.
- During refresh, the status panel reports object listing, schema inspection,
  and exact-timestamp aggregation stages; elapsed time is shown in the completed
  status and alongside the resulting snapshot. A family-level budget/schema
  failure is reported without producing a partial chart.

This is an availability snapshot, not a completeness or collector-health
assertion. Late arrivals, absent partitions, missing timestamps, and missing
hostnames are not interpreted as zero activity.

## Offline checks

```bash
cd streamlit/projects/HostActivity
uv run python -m unittest discover -s . -p 'test_*.py' -v
```

Tests create temporary local Parquet fixtures and use mocked file-discovery
results. They do not access AWS or require a live S3 profile. A bounded live
12-hour pilot confirmed selected-family reads for representative families, but
not complete family coverage or operational latency acceptance; see the linked
  wiki feature record for anonymized measurements.
