---
title: "To-Do: Add Filename-Based Hostname Filtering to Direct DBT Builds"
type: diagnostic
confidence: medium
grounded_by:
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintap_dbt/dbt_project.yml
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/relations.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintap-PyUtil/wintappy/etlutils/downloadfroms3.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/README.md
policy: agent-editable
last_validated: 2026-11-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: none
audience: mixed
status: stub
source_paths: ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/wintappy/etlutils; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [todo, backlog, p3, dbt, hostname-filter, raw-sensor, s3, data-pipeline]
---

# To-Do: Add Filename-Based Hostname Filtering to Direct DBT Builds

**Priority:** P3 — Low; opportunistic usability and read-reduction enhancement.
**State:** Open — design intake only; no implementation is authorized by this
TODO.
**Likely next step:** Implement and qualify a direct raw-only hostname selector,
starting with local fixtures and a loopback S3 source-preflight test.

## Finding

`make dbt-build-direct` currently restricts DBT input to raw Parquet and an
inclusive day/hour window, but it has no hostname selector. The DBT project exposes
dataset and temporal variables only, while the shared path macros generate all
Parquet globs under the selected partitions. Most bronze models use the shared
`parquet_relation()` macro; `stg_pidstat_metrics` performs its own direct scan and
must be included in any common filtering change.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §DBT_DIRECT_ROUTE/dbt-build-direct; ../Wintap-PyUtil/wintap_dbt/dbt_project.yml §vars; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §partition_globs_for_path/raw_sensor_partition_globs; ../Wintap-PyUtil/wintap_dbt/macros/relations.sql §parquet_relation; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql -->

Raw object names carry a hostname prefix. The inspected downloader accepts both
legacy `hostname=...` and newer `hostname+...` forms; current documentation also
contains two timestamp delimiter variants. A selector should therefore parse only
the basename's hostname prefix and delimiter, rather than depend on the complete
event/timestamp filename grammar.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/etlutils/downloadfroms3.py §parse_filename; ../Wintap-PyUtil/AWS_S3.md §Filenames; ../Wintap-PyUtil/review-notes/RawSensorContract.md §Filename guidance -->

## Proposed direction

Add a comma-separated `WINTAP_DBT_HOSTNAMES` setting. For the first version it
should be supported only when `WINTAP_DBT_INCLUDE_COMPACTED=false`, which is the
mode enforced by `dbt-build-direct`.

The DBT path layer should enumerate candidate files in the requested date/hour
partitions, extract each basename, and pass only matching exact file paths to
`parquet_scan`. This is preferable to adding DuckDB's virtual `filename` column to
every relation because it preserves existing model schemas and duplicate/grouping
behavior. Matching should be exact, delimiter-aware, and case-insensitive.

Source preflight must use the same selector as the build. A requested hostname with
no matching files should fail clearly; absent optional event families should remain
valid. The no-filter path should remain unchanged.

Compacted shard filenames are implementation-defined and are not reliable host
provenance, so enabling the selector with compacted input should initially fail
closed rather than silently omit or misattribute merged data.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/README.md §shard filenames; ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql §validate_raw_sensor_source -->

## Investigation and implementation questions

1. Add Makefile export, offline syntax validation, and effective-config reporting
   for `WINTAP_DBT_HOSTNAMES`.
2. Add a shared file-selection macro used by path discovery, source preflight,
   `parquet_relation`, and the PIDSTAT bronze model.
3. Ensure the direct target's configuration prerequisite sees its raw-only setting;
   the current recipe applies `WINTAP_DBT_INCLUDE_COMPACTED=false` only after the
   prerequisite runs.
4. Decide whether malformed or hostless filenames are skipped with diagnostics or
   cause a filtered build to fail.
5. Test whether exact file-list scans provide sufficient S3 listing/read reduction;
   optimize with host-specific object globs only after correctness is established.
6. If filtering is later exposed through coordinated `dbt-build`, include the
   selector in coordination identity or explicitly reject it there. The current
   coordination binding does not include a general host filter.

## Verification and completion criteria

- Two synthetic hosts in the same event/day/hour produce output only for the
  selected host.
- Matching is case-insensitive and does not confuse a hostname prefix with a
  different longer hostname.
- Legacy and current filename delimiters, nested `protoPK` paths, local input, and
  loopback S3 preflight are covered.
- PIDSTAT and every bronze event family use the same selection semantics.
- A missing selected host fails preflight with an actionable message.
- An unset selector preserves current input discovery, schemas, and row behavior.
- Use with compacted input is rejected or separately qualified with an explicit
  row/manifest-based design.
- A fixture containing a row hostname inconsistent with its filename establishes
  whether filename authority is sufficient or a second row-level quality check is
  required.

## Open questions

- Should `WINTAP_DBT_HOSTNAMES` remain direct-only, or should coordinated builds
  eventually support it through a protocol/binding revision?
- Is filename authority guaranteed for every raw event producer and historical
  filename generation path?
- Should the build merely select files by filename, or also enforce row-level
  hostname consistency after reading them?
- What listing and scan-cost threshold justifies a host-specific S3 glob strategy?

## Disposition

This is a cross-repo PyUtil/DBT enhancement intake item, not implementation
authorization. Promote it to a feature folder before changing DBT macros, Make
targets, source validation, or coordinated-reader semantics.
