---
title: "Tension: Raw Sensor Compaction Publication vs. Glob Readers"
type: tension
status: open
poles:
  - "Existing consumers expect one raw_sensor dataset root and recursively glob Parquet without consulting a completion manifest."
  - "Multi-shard compaction and reruns need all-or-nothing reader visibility, while S3 only provides single-key atomic updates."
resolution: null
confidence: high
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/brief.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
policy: agent-editable
last_validated: 2026-11-10
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
source_paths: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql; wiki/work/raw-sensor-file-aggregation/brief.md
tags: [tension, raw_sensor, parquet, s3, compaction, publication, cross-repo]
---

# Tension: Raw Sensor Compaction Publication vs. Glob Readers

## Conflict

The [[wiki/work/raw-sensor-file-aggregation/brief]] requires multi-shard output,
failed-run isolation, and idempotent reruns. Wintappy builds recursive Parquet
globs within the selected raw dataset root and day/hour window; these path
helpers do not select files from a compaction manifest.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_glob/raw_sensor_partition_globs/matching_raw_sensor_partition_globs -->

Amazon S3 documents atomic updates for a single key, not across multiple keys.
A staged-then-copy sequence can expose a subset of new shards; a replacement
can expose both generations or neither. A completion marker alone does not
change the behavior of a glob reader.
<!-- GROUND_TRUTH: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html §ConsistencyModel -->
<!-- SYNTHESIS: inferred from the S3 consistency model and the Wintappy path helpers -->

## Proposed Holding Pattern

The [[wiki/work/raw-sensor-file-aggregation/implementation_plan]] recommends a
fresh immutable dataset root per requested window. Write/validate all selected
leaves, write a completion manifest last, then have the operator select that
exact root for a fresh consumer. Failed candidates remain unselected. This
proposal fits manual operation but is not yet a confirmed publication decision.

The guarantee depends on selecting completed roots: candidate objects still
exist and are directly listable. A run containing one hour does not automatically
provide a continuously accumulating history. Rebuilding a wide window costs
additional reads/storage; selecting only a narrow run reduces available coverage.

## Ownership And Resolution Criteria

Wintap-Analytics owns the proposed compactor and these planning artifacts.
Wintappy owns the current consumer macros. Wintap owns the separate upstream
upload partition correction; Lintap packaging does not solve publication.

Resolve when a recorded decision specifies the supported reader contract,
window coverage, rerun/concurrency behavior, and failure visibility, followed by
tests that pause/fail between shard writes while a fresh consumer reads the
previously selected dataset. Options include explicit immutable-root selection,
manifest-aware readers, or an explicitly coordinated reader outage for replacing
a stable root. Reader changes require their own scope/authorization.

Do not claim multi-object S3 atomicity or close this tension merely because a
completion marker exists.
