---
title: "Wintap / Lintap ETL data flow"
type: workflow
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze
  - ../Wintap-PyUtil/wintap_dbt/models/silver
  - ../Wintap-PyUtil/wintap_dbt/models/gold
  - ../Wintap-PyUtil/extras/raw-sensor-compact/README.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - wiki/tool/durable-process-entity-manager.md
  - wiki/tool/raw-sensor-compaction.md
  - wiki/work/raw-sensor-file-aggregation/implementation_plan.md
  - ../Lintap/teletap/README.md
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/wintap/core/etl/load; ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Lintap/teletap
tags: [wintap, lintap, wintap-pyutil, dbt, duckdb, etl, s3, bronze, silver, gold, drawio]
---

# Wintap / Lintap ETL data flow

The editable [draw.io diagram](wintap-etl-data-flow.drawio) follows host-local
sensor Parquet through S3, optional hourly compaction, dual-root DBT input and
bronze → silver → gold. It also breaks out the separate durable process-entity
snapshot store, processing-checkpoint store and principal Makefile validation targets.

## Local-only single-user workflow

Small environments can use **local raw Parquet → DBT → local DuckDB** directly.
With the normal Python/DBT environment installed, run from Wintap-PyUtil with DBT
overrides unset:

```sh
export WINTAP_DATA_ROOT='/path/to/local-dataset'
make dbt-build
```

The root must contain supported Parquet under
`raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/.../`. Local date bounds are discovered
automatically; output defaults to `$WINTAP_DATA_ROOT/duckdb/wintap.duckdb`.
A `compacted/` directory is optional, and an unset/empty
`WINTAP_DBT_PROCESS_ENTITY_ROOT` disables durable enrichment. S3 credentials,
compactor installation and entity initialization are unnecessary for this path.
The proposed coordinator likewise preserves direct local execution.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §defaults/dbt-build; ../Wintap-PyUtil/scripts/check_dbt_config.py §validate; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §matching_raw_sensor_partition_globs; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_process_entities; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

When reusing a shell previously configured for remote builds, reset its DBT
overrides before the two commands above:

```sh
unset WINTAP_DBT_DATASET WINTAP_DBT_RAW_SENSOR_DATASET WINTAP_DBT_COMPACTED_ROOT
unset WINTAP_DBT_PROCESS_ENTITY_ROOT WINTAP_DBT_PROCESS_ENTITY_HOSTS WINTAP_DBT_PROCESS_ENTITY_NAMESPACE
unset WINTAP_DBT_PROCESSING_METRICS_ROOT WINTAP_DBT_PROCESS_UNKNOWN_IDENTITY_POLICY WINTAP_DBT_PROCESS_UNKNOWN_IDENTITY_MAX_RATIO
unset WINTAP_DBT_DATABASE WINTAP_DBT_START_DAY WINTAP_DBT_END_DAY
unset WINTAP_DBT_START_HOUR WINTAP_DBT_END_HOUR
```

The current S3 setup macro also reacts to an inherited remote processing-metrics
override when entities are disabled, so include that variable in the reset.
With overrides cleared, the local-only path needs no metrics directory.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_processing_metrics.sql -->

Without durable enrichment, process context comes from the selected raw event
window; retained historical entity snapshots are an optional source of additional
ancestry. Local analysis output is still a normal DuckDB database. Coordination
compatibility requirements: [[wiki/work/dbt-compaction-coordination/design]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §entity_mode -->

## Storage glossary

The diagram uses these short storage names; paths are relative to the configured
dataset, entity or metrics root. `protoPK` appears where protocol partitioning applies.

| Diagram label | Layout |
|---|---|
| **Raw Event Store** | `<dataset>/raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/<file>.parquet` |
| **Compacted Event Store** | `<dataset>/compacted/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/<merged>.parquet`; sibling to `raw_sensor`, unless a direct compacted-root override is configured. |
| **Process Entity Snapshot Store** | `<entity-root>/hostPK=<sha256(trimmed uppercase hostname)>/entities.parquet`; separate from both event scan roots, one complete snapshot per expected host. |
| **Processing Checkpoint Store** | `<metrics-root>/dayPK=YYYYMMDD/hourPK=HH/metrics.parquet`; defaults to `<dataset>/processing_metrics`, separate from event/entity roots; operational coverage, not telemetry. |

## Read the flow

- Wintap and Lintap/TeleTap write canonical event Parquet to host-local
  **Raw Event Store** paths. The configured uploader sends eligible files to
  its S3 destination, preserving the relative layout.
  Failed uploads retain files for retry; successful upload may delete the local
  copy. Upload depends on the deployed adapter/destination configuration.
- Wintap-PyUtil can read a local dataset root or an S3 **Raw Event Store**
  directly. The input root/window are configured independently of the local
  DuckDB output path.
- **Hourly compaction:** the manually invoked PyUtil compactor writes merged
  event Parquet to the **Compacted Event Store**. For selected closed
  partitions it validates output schemas and source/output row totals. Source is
  retained by default;
  explicit validated prefix deletion is optional. Existing destination hours
  skip, so partial output requires manual reconciliation. Automated scheduling
  remains deferred. See [[wiki/tool/raw-sensor-compaction]].
- DBT discovers event files from both the **Raw Event Store** and
  **Compacted Event Store** and reads them with name-aligned `UNION ALL`. After
  a successful migration removes the corresponding source prefix, compacted
  partitions plus still-raw partitions
  provide a single event-history input. There is no overlap suppression: when
  both copies remain, both contribute rows. Completeness still depends on the
  source archive and selected partitions; the job does not infer missing hours
  or recover events never collected.
- **Separate durable process entities:** the optional combined compaction mode
  updates complete per-host Parquet snapshots in the **Process Entity Snapshot
  Store**, outside both event scan roots. It validates/publishes entity state
  before raw process merge/deletion; a failed entity phase blocks source
  deletion. This state retains long-lived and exited process context, and is not
  itself raw event history.
- **Processing checkpoints:** entity-enabled init/replay publishes hourly coverage
  after the entity phase; combined compaction publishes it after raw processing.
  Each fixed-hour checkpoint carries namespace, snapshot/input identities,
  identity-policy/quarantine evidence and operation status. A final checkpoint
  failure may occur after raw deletion; recovery must reconcile entity state,
  raw migration and checkpoint coverage.
- When enabled, DBT reads the **Process Entity Snapshot Store** separately into
  process-entity/context relations and uses that context to enrich process/path
  models. It does not add old snapshot rows to raw bronze or count them as
  in-window lifecycle events.
  It also validates compatible version-3 checkpoints for every selected
  process-bearing hour and materializes `stg_processing_metrics` for QA. Active or
  unprocessed hours without checkpoints fail preflight. Checkpoints do not certify
  complete historical ancestry or bind a restored snapshot to current coverage.
  Entity enrichment is opt-in; production bootstrap, capacity qualification and
  scheduling/cutover remain deferred. See
  [[wiki/tool/durable-process-entity-manager]].
- `make dbt-build` performs the config check, source preflight, and DBT build.
  Bronze stages the dual-root event input; silver creates normalized details
  and (when enabled) process context; gold builds analyst-facing summaries.
- The output is the configured local DuckDB database. DBT Parquet export is not
  implemented, so the diagram does not depict bronze/silver/gold Parquet objects
  being published back to S3.

## Core Makefile validation targets

Run these from the Wintap-PyUtil repository root:

| Target | What it checks / does |
|---|---|
| `make print-dbt-config` | Runs offline config checks and prints effective input root/type and date/hour window; does not print credentials. |
| `make dbt-check-config` | Checks the local or S3 raw-input configuration, date/hour window, and local DuckDB output location. |
| `make dbt-check-source` | Lists selected raw/compacted inputs and reads one matching event schema. Entity mode additionally validates expected snapshots and selected process-hour checkpoints; the event probe is not an all-file/all-row integrity scan. |
| `make dbt-build` | Runs config and source checks, then builds DBT models. |
| `make dbt-test` | Runs configured DBT model/data tests. |
| `make dbt-check-output` | Checks the configured local output path/database; this is the prerequisite for the dashboard targets, not a raw-source check. |
| `make qa-pid-hash` | Runs SQL checks for `pid_hash` relationship/orphan issues. |
| `make qa-dashboard` | Launches the PyUtil Marimo overview for built DBT relations and QA summaries. |
| `make qa-pidstat` | Launches the pidstat QA notebook. |

The two QA dashboard targets check that the local output root/database is
available; they do not establish raw-input availability. Queries over raw-backed
bronze views still need access to their configured local or S3 source. When entity
enrichment is enabled, configured entity snapshots and processing checkpoints are
additional DBT inputs with schema/coverage checks. A passing raw source preflight
proves only bounded access/schema evidence, not complete dataset integrity or
semantic quality. These dependencies and limits are reflected in the diagram.
The proposed lock covers all active input roots and the writer's final checkpoint
publication; a read grant does not guarantee that its requested window is covered.
Implementation review: [[wiki/work/dbt-compaction-coordination/implementation-review]].

Related: [[wiki/repo/wintap-primary-sensor-repo]],
[[wiki/repo/lintap-supporting-repo]],
[[wiki/component/sensor-upload-cache-pipeline]],
[[wiki/repo/wintappy-pipeline-repo]],
[[wiki/tool/raw-sensor-compaction]],
[[wiki/tool/durable-process-entity-manager]], and
[[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]].
