---
title: "Future fix: reuse the ETL DuckDB instance"
type: concept
confidence: speculative
grounded_by:
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
policy: agent-editable
last_validated: 2026-11-03
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wintap/core/etl/load/RawSensorWriter.cs; wintap/core/infrastructure/ProcessResolver.cs
tags: [feature-work, etl, duckdb, performance, memory]
priority: medium
work_status: deferred
---

# Future fix: reuse the ETL DuckDB instance

**Medium priority; deferred.** Record for future implementation, not an approved
implementation instruction or a confirmed fix for the unresolved CPU problem.
Code belongs to Wintap; this wiki holds the planning record.

## Problem

`RawSensorWriter.WriteParquetWithDuckDB` opens a new in-memory DuckDB instance
for every parquet materialization, executes a read-parquet/COPY operation, and
disposes it. The operation creates no persistent application tables. Existing
operation timing excludes connection opening and disposal.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/RawSensorWriter.cs §WriteParquetWithDuckDB -->

Repeated engine initialization may waste CPU and native resources. Reuse is an
optimization hypothesis: it may not remove RNG contention occurring per scan/task.

## Proposed scope

- Reuse a dedicated, lazily initialized, ETL-owned in-memory instance. Do not
  share the process resolver connection/database: bulk materialization should
  not contend with latency-sensitive identity queries or couple their lifetimes.
- Start with serialized connection access, accounting for concurrent merge and
  host-serialization callers. Measure backlog before considering a bounded pool.
- Dispose each command and any readers promptly; retain no per-input objects.
  Dispose the engine during coordinated shutdown after in-flight work completes.
- Preserve parquet schema, partitions, naming, output publication, and failure
  semantics. Recover cleanly after failed materializations.
- Retain a way to compare with the existing fresh-instance behavior during
  qualification; do not change thread settings in the same comparison.

These are proposed design constraints, not implemented behavior. Engine-owned
caches and allocator high-water retention can persist despite stateless SQL.

## Acceptance and validation

- Compare fresh versus reused instances using identical artifacts, thread counts,
  and bounded input sequences. Measure full lifecycle CPU, latency, throughput,
  instance-open counts, and queue depth; quantify benefit before default rollout.
- Verify identical output content/schema and correct concurrent-call/shutdown
  behavior, with no dropped work or unacceptable backlog regression.
- Soak repeated inputs, many distinct bounded files, and alternating large/small
  inputs. Track process RSS, DuckDB memory, threads, and open file descriptors.
  Distinguish a stable high-water plateau from continued resource growth; DuckDB
  memory limits do not strictly bound total process RSS.
- Inject corrupt/missing inputs and write failures; subsequent work must succeed
  without retained handles, commands, or temporary-state accumulation.
- Keep diagnostics numeric/aggregated. Raw files, logs, profiles, and databases
  stay private and outside Git; no SQL/parameters, host identifiers, or credentials
  in saved findings, and no S3 uploads for this qualification.

**Next action when scheduled:** review ETL lifecycle/concurrency ownership, then
prepare a small implementation instruction and bounded benchmark/soak gates.
