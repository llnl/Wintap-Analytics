---
title: "Lintap Supporting Repository"
type: repo
confidence: high
grounded_by:
  - ../Lintap/README.md
  - ../Lintap/teletap/README.md
policy: agent-editable
last_validated: 2026-08-11
repo_scope: Lintap
implementation_area: packaging
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Lintap/README.md; ../Lintap/teletap/README.md; ../Lintap/Multipass.md; ../Lintap/packaging
tags: [Lintap, dev-environment, packaging, repo]
---

# Lintap Supporting Repository

`../Lintap` is a Linux proof-of-concept host-based event sensor repository that implements Wintap-like functionality for Linux environments and transforms Linux telemetry into the semantic Wintap data model for analysis.
<!-- GROUND_TRUTH: ../Lintap/README.md §Lintap -->

This wiki treats Lintap as supporting infrastructure, not the main Wintap sensor implementation. The Lintap README states that the newer TeleTap/eBPF implementation has moved into the Wintap repository, while this repo still contains initial post-processing code and the older sysdig-based playground.
<!-- GROUND_TRUTH: ../Lintap/README.md §Running Lintap -->

## Two Linux Paths

The current TeleTap-oriented workflow requires Linux root access, eBPF tools, .NET 8, Python, DuckDB, and both Wintap and Lintap repos. Build commands run from the Wintap repo and build/run `Lintap.csproj`.
<!-- GROUND_TRUTH: ../Lintap/teletap/README.md §Prerequisites; §Build Commands -->

TeleTap output is expected to include canonical raw sensor Parquet under `raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/` and raw process connection increments partitioned by protocol. The old merged-to-raw conversion step is explicitly removed, and the canonical full ETL is stated to live in `Wintap-PyUtil/wintap_dbt`, not in the TeleTap directory. `Wintap-PyUtil` is the `../Wintappy` repo; see [[wiki/repo/wintappy-pipeline-repo]] for its bronze/silver/gold DBT pipeline.
<!-- GROUND_TRUTH: ../Lintap/teletap/README.md §Data output; §Full ETL with DBT -->

The older sysdig workflow captures process, file, network, and optional SELinux activity as TSV/SCAP, converts raw TSV into raw Wintap format, and then relies on Wintap-style ETL scripts for final datasets.
<!-- GROUND_TRUTH: ../Lintap/README.md §Running Lintap (sysdig); §Post-processing -->

## pidstat Collector (promoted 2026-08-17)

`../Lintap/pidstat-collector.py` is a single-process Python host-performance collector: it samples `/proc` directly (stat/io/status/schedstat — full pidstat-equivalent schema plus `hostname` and container-attribution columns from cgroup/ns), computes rates from counter deltas, and rotates typed parquet into the sensor's cache at `raw_sensor/pidstat/dayPK=/hourPK=/` every `PIDSTAT_ROTATE_INTERVAL_SEC` (default 300, synced to the sensor upload cycle), where the sensor's uploader ships it ([[wiki/component/sensor-upload-cache-pipeline]]). Configuration is `PIDSTAT_*` env vars; sampling default 5 s; crash salvage via a spool outside the swept tree; accumulation guard caps unshipped bytes/age. It runs as a systemd service (`lintap-pidstat.service`) from a uv-managed Python 3.12 venv (`pidstat-collector-bootstrap.sh` / `-launch.sh`) because RHEL 8's system python3.6 predates duckdb wheels. `pidstat-collect.sh` remains only as a minimal example; the interim bash rotating collector was retired after its per-line command substitutions caused a ~700 forks/sec storm ([[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]]). Wintappy's DBT bronze reads the parquet layout directly.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector.py; ../Lintap/packaging/lintap-rpm/lintap-pidstat.service; ../Lintap/README.md §Managed pidstat collector -->

Open watch item: collector CPU usage looked higher than expected in early RHEL 8 field runs — investigate with data from more systems (tracked in [[wiki/work/improve-pidstat-collector/implementation_plan]]).

## Wiki Boundary

Lintap pages should focus on Linux dev-environment setup, packaging/deployment support, raw-to-normalized data transition, and compatibility tensions. Do not use Lintap as the canonical source for Windows Wintap sensor semantics.
<!-- SYNTHESIS: inferred from ../Lintap/README.md, ../Lintap/teletap/README.md, and ../Wintap-Analytics/AGENTS.md -->

See also [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] and [[wiki/repo/wintappy-pipeline-repo]].
