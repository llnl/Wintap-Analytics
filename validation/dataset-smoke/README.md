# Local dataset readiness smoke

This opt-in helper checks one explicitly named local dataset snapshot without
modifying it. It reports raw Parquet and built-DuckDB readiness independently. It
does **not** prove sensor completeness, DBT correctness, raw/database parity,
historical repair, or data quality.

## Run

Use the existing HostActivity interpreter from the Analytics repository root:

```sh
timeout --signal=TERM --kill-after=5s 120s \
  streamlit/projects/HostActivity/.venv/bin/python -B \
  validation/dataset-smoke/smoke_dataset.py \
  --dataset-root ../Wintap-PyUtil/data/wintap-analysis/rhel8 \
  --database duckdb/wintap.duckdb
```

Both arguments are required. The database must already exist inside the resolved
dataset root; the helper never creates one. URLs and paths/symlinks escaping that
root are refused. Output is one JSON object containing statuses and bounded counts,
not input paths, object names, row values, stored SQL, or exception details.

Statuses mean:

- `readable`: the selected bounded sample contained at least one row.
- `empty`: the input was readable but no finalized raw file, base table, or sampled
  row was present. This is not positive event evidence.
- `unavailable`: a required path, format, lock/WAL, permission, version, or other
  safe-read prerequisite failed. No repair or retry is attempted.
- `budget_exceeded`: a fixed discovery, file, catalog, or query cap was exceeded.

Exit zero means both checks completed as `readable` or `empty`; exit 2 means at
least one was unavailable or exceeded a budget.

## Fixed scope and budgets

- Raw discovery is limited to 128 directory entries under `raw_sensor`.
- Selection is deterministic and requires one explicit `dayPK`/`hourPK` partition;
  unpartitioned Parquet is not guessed into an hour. At most three finalized
  Parquet files are selected, preferring one each for process, file, and network.
- Each selected file is at most 32 MiB. Schema metadata is inspected and at most
  128 constant sample rows per file are fetched; row values are never returned.
- The built database is opened read-only with external access, extension automatic
  installation/loading, disk spill, and extra threads disabled.
- At most 32 user tables/views are catalogued. Stored views are never executed.
  Exactly one deterministic base table is schema-inspected and sampled to 128 rows.
- DuckDB memory is capped at 256 MiB, each query at 15 seconds and the shared
  raw/database command budget at 120 seconds. The documented process timeout is a
  hard outer bound. Limits are not automatically raised or retried.
- Selected files and the database are checked for size/mtime changes before and
  after reading. This detects observed change; it is not a provenance guarantee.

A database WAL causes refusal. The helper never checkpoints, migrates, upgrades,
recovers, attaches, writes summaries, or uses a persistence output path.

## Synthetic controls

Tests create only synthetic fixtures. Set `TMPDIR` to an approved local scratch
directory when policy requires a specific temporary-data location:

```sh
mkdir -p /data/lintap-compactor/sensor-fixes/dataset-smoke-tests
TMPDIR=/data/lintap-compactor/sensor-fixes/dataset-smoke-tests \
  timeout --signal=TERM --kill-after=5s 120s \
  streamlit/projects/HostActivity/.venv/bin/python -B -m unittest discover \
  -s validation/dataset-smoke -p test_smoke_dataset.py -v
```

Controls cover readable and empty inputs, missing/corrupt inputs, external views,
WAL refusal, escaping paths, sanitization, unchanged source files, and discovery,
file, catalog, row, and query budgets. Default test discovery never references the
real RHEL dataset.
