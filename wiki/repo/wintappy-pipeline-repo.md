---
title: "Wintappy (Wintap-PyUtil) Pipeline Repository"
type: repo
confidence: high
grounded_by:
  - ../Wintap-PyUtil/extras/raw-sensor-compact/README.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/models/silver/selinux_attribution.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/network_keys.sql
  - ../Wintap-PyUtil/tests/test_selinux_sql.py
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql
  - ../Wintap-PyUtil/tests/test_dbt_source_validation.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../Wintap-PyUtil/tests/test_compacted_s3_migration.py
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintappy/README.md
  - ../Wintappy/pyproject.toml
  - ../Wintappy/wintap_dbt/dbt_project.yml
  - ../Wintappy/wintap_dbt/macros/paths.sql
  - ../Wintappy/wintap_dbt/macros/raw_sources.sql
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/models/gold/process_file_summary.sql
  - ../Wintappy/wintap_dbt/models/gold/process_net_summary.sql
  - ../Wintappy/wintap_dbt/models/gold/process_summary.sql
  - ../Wintappy/wintap_dbt/models/schema.yml
  - ../Wintappy/wintap_dbt/macros/time.sql
  - ../Wintappy/review-notes/Architecture.md
  - ../Wintappy/review-notes/DataModel.md
  - ../Wintappy/review-notes/ProjectSummary.md
  - ../Wintappy/review-notes/OpenQuestions.md
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-11-12
repo_scope: Wintappy
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Wintappy/README.md; ../Wintappy/pyproject.toml; ../Wintappy/review-notes; ../Wintappy/wintap_dbt; ../Wintappy/wintappy
tags: [wintappy, wintap-pyutil, dbt, duckdb, etl, data-pipeline, repo]
---

# Wintappy (Wintap-PyUtil) Pipeline Repository

`../Wintappy` is the canonical Python/DBT/DuckDB post-processing repository for Wintap and Lintap telemetry. Its Python package is named `wintappy`; its upstream project name is `Wintap-PyUtil`, described as "Python, DuckDB, and DBT utilities for processing Wintap/Lintap telemetry data."
<!-- GROUND_TRUTH: ../Wintappy/README.md §Wintap-PyUtil -->

Its README carries the same LLNL release identifier, `LLNL-CODE-837816`, that appears in the Wintap-Analytics README, indicating both are registered under the same umbrella LLNL software release even though `pyproject.toml` declares an MIT license for the package itself.
<!-- GROUND_TRUTH: ../Wintappy/README.md §Release -->
<!-- GROUND_TRUTH: ../Wintappy/pyproject.toml §project -->

## Canonical Architecture

### DuckDB maintenance baseline (2026-10-24)

The canonical Python dependency is pinned to DuckDB **1.5.6**; the current
adapter/core tuple remains **dbt-duckdb1.9.6 / dbt-core1.12.2**. The local uv lock
remains intentionally ignored by repo policy; the tracked manifest carries the
engine pin. A fresh full DBT build on retained revision7 AXON drain inputs passed
40 models/42 tests plus its startup hook, retaining collector birth and metadata.
This is dependency validation, not repair of existing data-quality defects or
rollout to installed collectors. See [[wiki/work/duckdb-1-5-maintenance/verification]].
<!-- GROUND_TRUTH: ../Wintappy/pyproject.toml; ../Wintappy/.gitignore; ../Wintappy/uv.lock; wiki/work/duckdb-1-5-maintenance/validation_receipt.json -->

DBT is the primary canonical ETL path. The intended flow is sensor `raw_sensor`
Parquet (plus the newly supported `compacted` Parquet representation) into
`Wintap-PyUtil/wintap_dbt`, into a DuckDB analysis database, into notebooks/SQL/
future Parquet export. The older flat binary/legacy `merged` directory stage is
deprecated; it is distinct from this new partition-preserving compacted input.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/README.md §Compaction migration contract; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql -->
The older review notes below describe the raw-only architecture before this
explicitly approved input expansion.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Current architectural stance -->
<!-- GROUND_TRUTH: ../Wintappy/review-notes/ProjectSummary.md §Key decisions -->

Component boundaries are explicit in the repo's own review notes: the `wintap` repo owns event collection and raw `raw_sensor` parquet materialization and should not own DBT transformations; `Wintap-PyUtil` (this repo) owns canonical ETL transformations, dependency ordering, and tests; analytics notebooks (Wintap-Analytics) own exploratory analysis and modeling, not canonical ETL; `Lintap/teletap` owns development visualization/scaffolding, not the main pipeline.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Major component boundaries -->

## DBT Model Layers

### Integer timestamp precision (2026-10-24 candidate)

FILETIME timestamp/minute macros now use integer epoch subtraction/floor division,
preserving UTC TIMESTAMPTZ output without floating tick loss. Generic integer text
parsing rejects malformed/decimal/scientific/out-of-BIGINT text;raw100ns values and
identity inputs are untouched. Exact raw round-trip requires microsecond-representable
inputs.12fresh full builds recover all12collector births;2,900process lifetimes pass
raw-integer checks. Floating convenience fields/older builder paths remain approximate.
Unordered silver metadata,OS labels and sensor conservation gaps are not fixed here.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/time.sql; ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintappy/tests/test_filetime_precision_sql.py -->
Contract:[[wiki/concept/filetime-derived-timestamp-precision]];
proof:[[wiki/work/host-process-identity-patch/timestamp_and_trace_results]].

DBT bronze models own raw-source schema compatibility: they scan `raw_sensor` parquet partitioned by `dayPK`/`hourPK`(/`protoPK` for network), tolerate optional or missing raw sources, and normalize source drift such as synthesizing missing `ProcessArgs` from `CommandLine`.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/DataModel.md §DBT bronze models -->

For the Linux split-root layout, `WINTAP_DBT_DATASET` defaults directly to
`WINTAP_DATA_ROOT`, so DBT resolves `$WINTAP_DATA_ROOT/raw_sensor/...` rather
than a nested `parquet/` directory.
<!-- GROUND_TRUTH: ../Wintappy/Makefile -->

DBT silver models are the normalized, process-centric detail objects: `host`, `host_ip`, `process`, `process_conn_incr`, `process_net_conn`, `process_file`, `process_registry`, `process_image_load`, `files`, `all_files`, and `process_path`, keyed by `pid_hash` as the primary process entity key used by downstream summaries and labels.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/DataModel.md §DBT silver detail models -->

DBT gold models are analyst-facing summaries: `process_registry_summary`, `process_file_summary`, `process_net_summary`, `process_image_load_summary`, `process_summary`, and `process_uber_summary`. Optional enrichment inputs feeding `process_uber_summary` — labels/networkx, LOLBAS, MITRE, and Sigma — are currently typed empty DBT stubs, not real wired inputs.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Gold -->
<!-- GROUND_TRUTH: ../Wintappy/review-notes/OpenQuestions.md §In progress / high priority -->

### Gold lifetime aggregation correction (2026-10-23 candidate)

Current source groups file/network lifetime summaries only by `pid_hash`, not
mutable process name or agent UUID. Latest observed name/agent is selected with
`arg_max` and a lexical tie-break; this is summary display metadata, not a complete
exec/image timeline. Host display uses `min`; conflicting metadata needs separate QA.
File counters accept case-normalized spelling and include `Open_Events`.
`process_summary` computes full elapsed seconds with `epoch(interval)`, and both
process gold summary models now test lifetime-key uniqueness.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/gold/process_file_summary.sql; ../Wintappy/wintap_dbt/models/gold/process_net_summary.sql; ../Wintappy/wintap_dbt/models/gold/process_summary.sql; ../Wintappy/wintap_dbt/models/schema.yml -->

Regression fixtures and read-only real-sample projections validate these SQL changes;
the original materialized database is unchanged. These corrections neither recover
historical orphan identities nor repair producer receive-byte measurements or OS labels.
<!-- GROUND_TRUTH: ../Wintappy/tests/test_process_gold_quality_sql.py; wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §historical QA/counters archive members -->

## pidstat Bronze Input (promoted 2026-08-17, patched 2026-08-20)

The pidstat bronze model (`stg_pidstat_metrics`) now behaves like the other optional raw events instead of using a pidstat-only path override. `dbt_project.yml` defines `raw_sensor_dataset` from `WINTAP_DBT_RAW_SENSOR_DATASET` with fallback to `WINTAP_DBT_DATASET`; the shared raw-source helpers build `<raw_sensor_dataset>/raw_sensor/pidstat/...` globs and existence checks from that root. `stg_pidstat_metrics` uses those shared helpers (`raw_event_exists('pidstat')`, `raw_sensor_partition_globs_sql('pidstat')`, and `partition_filter()`), so pidstat now respects the same dataset-root split-I/O/S3 configuration and the same day/hour partition narrowing as models such as `stg_raw_host`.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/dbt_project.yml §vars -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/paths.sql §raw_sensor_dataset_path/raw_sensor_path/raw_sensor_partition_globs_sql/partition_filter -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/raw_sources.sql §raw_event_exists -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql §model -->

The dedicated `PIDSTAT_DATA_PATH` override and `wintap_dbt/macros/pidstat.sql` helper were removed in that follow-up bugfix, so pidstat is now just another canonical optional `raw_sensor` event. It still carries `hostname` and container-attribution columns (`cgroup_path`, `pid_ns_inode`, `container_runtime`, `container_id`), and it still builds a typed empty table when no pidstat parquet exists. The former tab-CSV input remains retired; bronze is parquet-only, and pre-2026-08 CSV datasets still need one-time conversion. Producer side: [[wiki/repo/lintap-supporting-repo]] pidstat collector.
<!-- GROUND_TRUTH: ../Wintappy/Makefile §dbt vars -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/README.md §Configuration -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql §typed empty fallback -->

## Source-aware DBT preflight (2026-10-31)

Current checkout path: `../Wintap-PyUtil` (older citations use `../Wintappy`).
PyUtil owns the implementation; Analytics hosts this wiki and verification record.

`make dbt-check-config` validates the effective raw input root:
`WINTAP_DBT_RAW_SENSOR_DATASET`, falling back to `WINTAP_DBT_DATASET`.
Local input requires a readable `<raw-root>/raw_sensor` **or compacted** directory, including
split local input/output roots. S3 input requires `s3://bucket[/prefix]` and explicit
inclusive `YYYYMMDD` start/end dates, but **no local raw_sensor placeholder**.
Other URI schemes are rejected. Local date discovery uses both effective input roots,
not unrelated output-root partitions. Database output remains local; date/hour
validity/order and output-directory writability are checked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/scripts/check_dbt_config.py -->

`make dbt-check-source` uses DBT/DuckDB and the existing S3 credential-chain,
endpoint/path-style/TLS configuration to list supported bronze events/aliases in
the requested partitions and read one matching Parquet schema. When `AWS_PROFILE`
is set, the macro explicitly selects that named profile via DuckDB's `config` chain;
otherwise the default credential chain is used. The macro gets region from
`AWS_DEFAULT_REGION` / `AWS_REGION` and endpoint only from `AWS_ENDPOINT_URL`; it
does not import a profile's custom `endpoint_url` setting, which must be exported
for Garage/path-style stores. Event names precede
wildcards so S3 LIST prefixes include day/hour narrowing; nested `protoPK` is
supported. Listing stops at a sample. An empty supported-event window fails;
missing individual optional events remain valid. Engine access/TLS/Parquet errors
are not suppressed as empty input. This is basic access evidence, not an all-file
integrity scan or full DBT/Go-pidstat qualification. New bronze event names must also
be added to the probe's event list.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql -->

`make dbt-build` runs both checks. `make print-dbt-config` stays offline and now
prints the raw root/type and hour window without credentials. `qa-dashboard` and
`qa-pidstat` check only the existing local database, not raw-source availability
or dates; querying S3-backed bronze views still needs S3 access. Regression scope
and limits: [[wiki/work/dbt-source-validation/verification]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt/README.md -->

## Unioned raw/compacted input (2026-11-12 candidate)

PyUtil's shared macros now scan `<raw_sensor_dataset>/raw_sensor/<event>/...`
and `<raw_sensor_dataset>/compacted/<event>/...`. An optional
`WINTAP_DBT_COMPACTED_ROOT` overrides the direct compacted event root. Partition
globs, event/alias/optional-column discovery and preflight include both; absent
local roots are allowed when the other exists. S3 auth is configured if either
root is remote. The DuckDB 1.5.6 pin is unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql; ../Wintap-PyUtil/wintap_dbt/dbt_project.yml; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql; ../Wintap-PyUtil/scripts/check_dbt_config.py -->

Input is name-aligned UNION ALL, preserving missing-field NULLs and duplicates.
No new overlap masking/deduplication/preference rule; existing bronze duplicate
accounting and silver/gold transformations remain unchanged. PyUtil owns the
standalone [DuckDB 2.0.0 compactor](../../../Wintap-PyUtil/extras/raw-sensor-compact/README.md)
and DBT adapter/config/tests; Analytics hosts the shared wiki and feature evidence.
The compactor's own lockfile and environment keep it separate from DBT's 1.5.6 pin.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/README.md; ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml -->
Deployment sequence is merge → validate every leaf → delete closed source hour
prefix after UTC grace → rebuild DBT. The human accepts rare clock skew and
transient/failure overlap; reconcile failures manually before a build. Bronze
views bind discovered physical globs and need rebuild along with materialized
models after source deletion.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/README.md §Compaction migration contract; wiki/work/raw-sensor-file-aggregation/interview.md §Dual-Root DBT And Prefix Deletion Approval -->

Qualification: all 54 full synthetic models match in fresh raw/mixed/compacted
databases (139 gates each); live-copy host/pidstat migration preserves 897,395 rows,
matches 4 scoped models, deletes 29 copied sources and preserves all original
hashes. Full available-family qualification is recorded below; broader datasets,
benchmark and production rollout remain separate. [[wiki/work/raw-sensor-file-aggregation/verification]] records
commands and bounded results; [[wiki/tool/raw-sensor-compaction]] records operation.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_compacted_inputs.py; ../Wintap-PyUtil/tests/test_compacted_s3_migration.py; wiki/work/raw-sensor-file-aggregation/verification.md §Dual-Root DBT And Prefix-Deletion Tests -->

Expanded 399-file/9-family live input builds all 54 models with 139 passing
gates in raw, mixed, and unchanged-input mixed-repeat runs. Strict results do
not match: 17 models differ in raw/mixed, and 18 in identical-input replay.
`process.sql` uses unordered `ANY_VALUE` for representative names/paths/parents;
derived filename/file_id propagate selection changes to downstream models.
The shipping-SQL order-reversal diagnostic reproduces this on identical rows.
This is existing analytics nondeterminism, not evidence of compactor payload loss.
The human explicitly accepts this existing quality debt as non-blocking for
compaction. The full live test's approved diagnostic mode requires exact schemas,
model sets, bronze and models outside the ANY_VALUE dependency closure; affected
result/count differences remain visible. This is not a representative fix or a
claim of fully equivalent downstream results. No production semantics were
changed. The all-family migration rerun passes all 54 builds/139 gates in each
state, with exact schemas/all 11 bronze models, 36 exact model results across
states, and reported differences in 18 affected models. It conserves 2,668,265
rows, deletes 399 isolated copied sources → 10 outputs, and preserves all 399
original source hashes. The compacted copy supported read-only full builds at
`s3://lintap-alpha/compaction-tests/dbt-union-all-20261112-02`, day 20261111/hour 08.
It was subsequently removed with this work's other S3 artifacts at the human's
request (445 objects total, original raw hashes unchanged); the saved-copy command
is now historical. This bounded acceptance excludes nonempty registry/image-load
families (absent), performance defaults and production cutover.
[[wiki/tension/dbt-arbitrary-representatives-vs-compaction-equivalence]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/tests/test_compacted_inputs.py §test_existing_process_model_depends_on_row_order; wiki/work/raw-sensor-file-aggregation/verification.md §Full-Model Live-Copy Expansion -->
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/verification.md §Accepted ANY_VALUE Diagnostics And All-Family Rerun; ../Wintap-PyUtil/wintap_dbt/README.md §Read-only full-model test of the surviving compacted copy -->

## SELinux pipeline (2026-11-11 candidate)

PyUtil owns optional bronze/silver/gold support for `raw_selinuxavc`,
`raw_selinuxinteraction`, and `raw_selinuxtransition`; missing families produce
typed empty relations. Silver retains raw timestamps and normalizes Unix-second
`EventTime` and FILETIME observation bounds. Bronze removes identical rows with
`num_dups` retained; gold preserves normalized producer `EventCount`, not raw
duplicate contributions. Interaction telemetry is folded/permission-expanded,
not one distinct kernel event per row or count unit.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/README.md §SELinux telemetry; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_selinuxinteraction.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/selinux_interaction.sql -->

`selinux_attribution` accepts exact identity or one host/PID/lifetime candidate;
ambiguous and unmatched observations remain unassigned. Shared gold detail,
context, and process summaries preserve these outcomes. The Marimo overview
exposes family counts, producer counts, context completeness and attribution QA.
Sensor collection remains owned outside PyUtil; Analytics hosts the evidence:
[[wiki/work/selinux-dbt-pipeline/verification]]. Synthetic tests cover all four
attribution outcomes, including cases absent from the supplied sample.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/selinux_attribution.sql; ../Wintap-PyUtil/tests/test_selinux_sql.py; ../Wintap-PyUtil/notebooks/wintap_dbt_overview.py -->

## Temporary network connection IDs (2026-11-11 candidate)

The current silver `process_conn_incr` replaces raw producer `connid` with an
uppercase MD5 of canonical JSON containing context `llnl`, normalized protocol,
and ordered IP/port endpoint pairs. Reversed endpoints share an ID; incomplete
tuples yield NULL. This is a temporary DBT shim pending authoritative Wintap .NET
implementation, not a unique connection-instance key. Repeated five-tuples share
the key; producer-ID joins and existing materialized IDs can change. Rebuild
dependent models together and qualify downstream consumers before release.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/network_keys.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintap-PyUtil/wintap_dbt/README.md §Temporary network identity compatibility change -->

## Legacy Python ETL

Pre-DBT Python/DuckDB console commands (`rawtorolling`, `rawtostdview`, `ubersummary`) remain installed as package entry points and are explicitly kept only "as legacy/reference tooling while the DBT path is hardened"; the README instructs new work to use DBT instead.
<!-- GROUND_TRUTH: ../Wintappy/README.md §Legacy Python ETL commands -->
<!-- GROUND_TRUTH: ../Wintappy/pyproject.toml §project.scripts -->

## Code Dependency From Wintap-Analytics

Wintap-Analytics does not just consume Wintappy's *output* files — its Streamlit apps import the `wintappy` Python package directly. `streamlit/projects/common/dqautil.py` imports `wintappy.datautils.rawutil`, and `streamlit/projects/DataQA/pages/raw_events.py` imports `wintappy.datautils.stdview_duckdb`. This makes `wintappy` a runtime code dependency of Wintap-Analytics' DataQA/eda tooling, not merely a producer of data those tools happen to read.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/common/dqautil.py §import wintappy.datautils.rawutil -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py §import wintappy.datautils.stdview_duckdb -->

## Known Limitations

DBT parquet export is not implemented yet; DuckDB is the current official output, even though some notebooks and published workflows still expect `stdview-*` parquet directories. See [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]] for the resulting cross-repo tension.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/OpenQuestions.md §2. Implement DBT parquet export -->

Optional enrichment sources (labels, LOLBAS, MITRE, Sigma) are not fully wired into DBT; current gold models are typed empty stubs pending real input loading.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/ImplementationStatus.md §Current limitations -->

## Wiki Boundary

Wintappy pages should document the DBT bronze/silver/gold pipeline, its `raw_sensor` input contract, and its role as the canonical post-processing engine. Do not treat Wintappy as a source for sensor/collector semantics (that belongs to [[wiki/repo/wintap-primary-sensor-repo]]) or for exploratory analysis workflows (that belongs to [[wiki/repo/wintap-analytics-host-repo]]).
<!-- SYNTHESIS: inferred from ../Wintappy/review-notes/Architecture.md and ../Wintap-Analytics/AGENTS.md -->

See also [[wiki/repo/wintap-primary-sensor-repo]], [[wiki/repo/wintap-analytics-host-repo]], [[wiki/repo/lintap-supporting-repo]], [[wiki/workflow/future-experiment-analysis-workflows]], and [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]].
