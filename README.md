<img width="200" src="https://user-images.githubusercontent.com/50601643/218871643-2d3af433-0923-4786-b5e5-24c6a72e803e.png" alt="Wintap logo">

# Wintap-Analytics

Wintap-Analytics is the research and analysis workspace for Wintap host
telemetry. It contains notebooks, DuckDB/Parquet workflows, Streamlit tools,
sensor-validation harnesses, workshop material, annotations, and the
cross-repository Wintap ecosystem wiki.

This repository is primarily an analysis host. The Linux sensor is built from
the sibling `../wintap` repository, and the canonical DBT/DuckDB post-processing
pipeline is maintained in `../Wintappy` (Wintap-PyUtil).

## What Is Here

| Directory | Purpose |
|---|---|
| `notebooks/` | Reusable process-tree, process-path, NetworkX, and DuckDB notebooks |
| `2025-acme4-explore/` | ACME4 standard-view exploration project managed with `uv` |
| `2025-dmbd/` | Earlier dataset exploration notebooks and scripts |
| `2026-stamp/` | Process-tree, embedding, matching, and file-path investigations |
| `streamlit/` | Interactive EDA and DataQA applications |
| `validation/process-creation/` | Sensor-neutral process lifecycle and parent-join validation |
| `validation/fileops-differential/` | Baseline/candidate FileOps differential harness |
| `validation/perf-collection/` | Runtime and `/proc` performance collection tools |
| `annotations/` | ACME4 labels, CALDERA-derived reports, and annotation utilities |
| `workshop/` | Hands-on DuckDB, SQL, Python, and Wintap analysis guidance |
| `extras/` | Diagnostics and supporting operational utilities |
| `wiki/` | Cross-repository architecture, telemetry semantics, workflows, and feature records |
| `raw/` | External documents and notes with provenance headers |

## Data Flow

Typical analysis starts with event data written as partitioned Parquet, often
under a layout such as:

```text
<data-root>/parquet/raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/*.parquet
```

DuckDB is the primary local query engine for Parquet and event-store data.
Wintappy consumes raw sensor Parquet and produces bronze/silver/gold analysis
models. The notebooks and Streamlit applications in this repository consume
those datasets or construct focused DuckDB views for exploration.

The ACME4 project uses a separate standard-view dataset and can query the
published Parquet files directly over HTTP with DuckDB HTTPFS or from a local
download.

## Getting Started

### Root Python Environment

The root environment is managed with Pipenv and is intended for the general
Jupyter, DuckDB, pandas, NetworkX, and plotting toolchain:

```sh
git clone https://github.com/LLNL/Wintap-Analytics.git
cd Wintap-Analytics
python3 -m pip install --user pipenv
pipenv install --dev
pipenv shell
```

Equivalent Make targets are available:

```sh
make venv
make requirements
make fmt
```

`make fmt` formats the repository with Black and isort. Review its broad
scope before running it on a branch containing unrelated work.

### ACME4 Exploration

The ACME4 project requires Python 3.11 or newer and uses `uv`:

```sh
cd 2025-acme4-explore
uv sync
uv run python -m ipykernel install --sys-prefix \
  --name acme4-explore \
  --display-name "ACME4 Explore"
uv run jupyter lab
```

By default, the project connects to the published ACME4 standard view. To use
a local copy, create `2025-acme4-explore/.env` with:

```text
URI_DATASET="${HOME}/stdview-20240819-20240923"
```

See [`2025-acme4-explore/README.md`](2025-acme4-explore/README.md) for dataset
access, JupyterHub setup, and configuration details.

### Streamlit EDA

The EDA and DataQA applications are separate small Streamlit projects. Install
their local requirements, configure the relevant settings file, and start the
application from its project directory:

```sh
cd streamlit/projects/eda
python3 -m pip install -r requirements.txt
streamlit run main.py
```

The DataQA project follows the same pattern:

```sh
cd streamlit/projects/DataQA
python3 -m pip install -r requirements.txt
streamlit run main.py
```

These applications expect a dataset/database layout appropriate to the selected
project. They are not a replacement for Wintappy's DBT pipeline.

## Validation Workflows

### Process Creation

The process validation project runs mock evaluations on macOS and real sensor
workloads on Linux:

```sh
cd validation/process-creation
uv run --extra dev pytest
uv run wpv-mock-run --run-dir /tmp/wpv-mock
```

The evaluator covers fork, exec-attempt, exec-success, exit, parent joins,
duplicate starts, identity collisions, and sensor-loss metrics. Live eBPF runs
require a Linux VM with Lintap already running.

### FileOps Differential

Generate a deterministic workload and compare baseline and candidate Parquet:

```sh
python3 validation/fileops-differential/fileops_workload.py \
  --work-dir /tmp/fileops-workload \
  --manifest /tmp/fileops-manifest.json

python3 validation/fileops-differential/compare_fileops.py \
  --baseline '/tmp/baseline/parquet/raw_sensor/raw_process_file/**/*.parquet' \
  --candidate '/tmp/candidate/parquet/raw_sensor/raw_process_file/**/*.parquet'
```

### Performance Collection

The performance collector is also managed with `uv`:

```sh
cd validation/perf-collection
uv sync
uv run --extra dev pytest
```

Use the project README for live collection commands and required privileges.

## Cross-Repository Setup

For live sensor work, keep the repositories adjacent:

```text
git/
  Wintap-Analytics/
  wintap/
  Lintap/
  Wintappy/
```

`../wintap` owns the Wintap sensor and shared C# data model. `../Lintap`
contains supporting Linux packaging and older Linux telemetry tooling.
`../Wintappy` owns the canonical Python/DBT/DuckDB post-processing pipeline.

The wiki documents how those repositories relate and records live source paths
instead of copying source code. Start with [`wiki/index.md`](wiki/index.md) and
[`AGENTS.md`](AGENTS.md) when working on ecosystem documentation.

## Documentation

- [`wiki/index.md`](wiki/index.md): architecture and workflow index
- [`workshop/`](workshop/): practical analysis tutorials
- [`2025-acme4-explore/README.md`](2025-acme4-explore/README.md): ACME4 setup and data access
- [`validation/process-creation/README.md`](validation/process-creation/README.md): process validation
- [`extras/lintap-runtime-diagnostics/README.md`](extras/lintap-runtime-diagnostics/README.md): runtime diagnostics

## License

This project is released under the [MIT License](LICENSE).

Release identifier: `LLNL-CODE-837816`.
