---
title: "FILETIME and derived timestamp precision"
type: concept
confidence: high
grounded_by:
  - ../Wintappy/wintap_dbt/macros/time.sql
  - ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintappy/tests/test_filetime_precision_sql.py
  - wiki/work/host-process-identity-patch/timestamp_and_trace_results.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../Wintappy/wintap_dbt/macros; ../Wintappy/tests
tags: [filetime, timestamps, precision, dbt, identity]
---

# Separate raw identity time from analysis time

Raw FILETIME is an integer count of100ns ticks since1601. Process identity uses
the canonical raw birth,not a derived DuckDB timestamp. The Wintappy DBT timestamp
macro now subtracts the Unix epoch in integer arithmetic and floors to microseconds,
including dates before1970. It produces a timezone-aware timestamp with the correct
UTC instant;sensor/raw values are not rewritten.
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ProcessIdentity.cs; ../Wintappy/wintap_dbt/macros/time.sql §win32_to_timestamp_expr; §floor_integer_div_expr -->

Exact round-trip back to raw FILETIME is possible only for values divisible by10.
Other values intentionally discard the submicrosecond remainder toward the earlier
instant. This is a representability contract,not permission to relax identity or
exact-birth checks for representable inputs. Use integer raw times for identity QA.
<!-- GROUND_TRUTH: ../Wintappy/tests/test_filetime_precision_sql.py §test_direct_filetime_exact_floor_and_timezone -->

The generic FILETIME/timestamp helper accepts integer text without DOUBLE parsing;
null,malformed,decimal/scientific-notation or out-of-BIGINT text becomes null.
Existing aware timestamps retain their instant. Naive timestamps retain the prior
session-timezone interpretation. Numeric network minute bins use integer floor
division rather than floating seconds,so near-boundary ticks cannot round forward.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/time.sql §win32_or_timestamp_expr; §win32_to_minute_timestamp_expr; ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql -->

# Producer and downstream implications

This change belongs to **Wintappy post-processing**,not the Wintap sensor. It fixes
derived process/file/network/registry/image-load timestamp conversion. Floating
epoch-seconds convenience fields and older conversion paths remain approximate;
they are not canonical identity evidence. Corrected timestamps also change derived
durations. Historical databases remain unchanged until separately authorized rebuilds.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/time.sql §win32_to_epoch_expr; ../Wintappy/wintap_dbt/models/silver/process.sql; ../Wintappy/wintap_dbt/models/gold/process_summary.sql -->

On12preserved captures,fresh full DBT builds pass12/12and restore all12collector
births. Independent integer checks pass2,900process lifetimes. Process/agent keys,
raw file hashes,connection IDs,counters and row multiplicities are protected by
comparisons. Unordered silver `any_value` metadata can vary across identical SQL
reruns;names/paths/args and derived executable file IDs are not promised stable by
this timestamp fix. Linux-as-Windows labeling and prior sensor losses remain open.
<!-- GROUND_TRUTH: wiki/work/host-process-identity-patch/timestamp_and_trace_results.md; wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §precision archive members -->

Verification:[[wiki/work/host-process-identity-patch/timestamp_and_trace_results]].
Related:[[wiki/concept/telemetry-identity-and-endpoint-orientation]],
[[wiki/repo/wintappy-pipeline-repo]],[[wiki/concept/wintap-ecosystem-glossary]].
