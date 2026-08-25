# FileOps Differential Harness

This harness supports `optimize-fileops-poller` A/B checks. It creates a deterministic regular-file workload and compares baseline vs candidate `raw_process_file` parquet output.

The comparator is intentionally conservative: candidate output must contain every baseline regular-file event tuple `(pid, normalized_path, op)` unless an allowed removal class is explicitly configured for a later slice. Socket, pipe, anon-inode, `/proc`, `/sys`, `/dev`, and Lintap data-root paths are treated as non-regular/noise rows and reported separately.

## Workload

```bash
python3 validation/fileops-differential/fileops_workload.py --work-dir /tmp/fileops-workload --manifest /tmp/fileops-manifest.json
```

## Compare

```bash
python3 validation/fileops-differential/compare_fileops.py \
  --baseline '/tmp/baseline/parquet/raw_sensor/raw_process_file/**/*.parquet' \
  --candidate '/tmp/candidate/parquet/raw_sensor/raw_process_file/**/*.parquet'
```

The script exits non-zero if candidate regular-file tuples are missing.
