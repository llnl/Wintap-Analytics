# Lintap Runtime Diagnostics

Collects read-only diagnostics for long-running Lintap CPU and `event_store` / pidhash-cache investigations.

Run as root on the affected host:

```bash
sudo bash extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh
```

The script writes a timestamped directory and `.tar.gz` bundle under `/tmp` by default, for example:

```text
/tmp/lintap-runtime-diagnostics-<hostname>-<timestamp>.tar.gz
```

Useful options:

```bash
sudo bash extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh --output-dir /tmp/lintap-diag
sudo bash extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh --data-root /var/log/lintap
sudo bash extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh --pid <lintap-pid>
sudo bash extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh --db /path/to/main.duckdb
```

The utility does not stop or restart services. It first verifies required tools, including the DuckDB CLI. It tries to query the live DuckDB database read-only; if Lintap holds the DuckDB lock, it copies `main.duckdb` plus `main.duckdb.wal` when present into the diagnostics directory and queries the copy. It also collects targeted excerpts from `$WINTAP_DATA_ROOT/Logs/Lintap.log`, including FileOps counter/startup lines, a dedicated recent `FileOps counters` extract, ProcessResolver retention lines, and recent warnings/errors. It fingerprints the deployed install tree when it can determine the active install root, including `Lintap.dll` and installed `*.bpf.o` tracer hashes/stats. When `bpftool` is available, it also captures live BPF program/map/link listings. It redacts common secret-like config keys before saving service/config files.
