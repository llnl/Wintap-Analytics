---
title: "Future: Adaptive FileOps Sampling and Diagnostic Data"
type: concept
confidence: speculative
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py
policy: agent-editable
last_validated: 2026-08-31
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: file
audience: mixed
status: stub
source_paths: wintap/platform/linux/sensor/ebpf; wintap/core/etl; validation/perf-collection
tags: [future-work, lintap, fileops, adaptive-sampling, diagnostics, parquet, observability]
---

# Future: Adaptive FileOps Sampling and Diagnostic Data

## Adaptive FileOps Sampling

Investigate a dynamic filter that detects sustained or bursty activity by event
type and source, then changes sampling rate as offered volume rises. Unlike an
exact deny policy, the mechanism should preserve representative evidence of a
Tenable-like scan while protecting ring, sender, resolver, Esper, and serializer
capacity.

Design requirements:

- preserve initial events before sampling begins;
- use event type/rate and an auditable identity dimension such as exact `comm`;
- retain weighted represented-event and represented-byte counts so sampled
  output can estimate original volume;
- report sampling probability/rate, trigger threshold, policy generation, and
  exact sampled/suppressed counters;
- distinguish policy-selected adaptive sampling from intrinsic sensor filters,
  aggregation, capacity drops, and hard deny rules;
- include hysteresis and bounded state so burst exit does not flap;
- validate estimate error and non-sampled workload fidelity under deterministic
  mixed-rate workloads.

Open design question: whether sampling belongs before ring reservation in BPF
(best capacity protection, less context) or after decode in userspace (richer
classification, but ring pressure remains). A hybrid detector/control-map design
may be appropriate.

## Diagnostics As First-Class Data

Convert current timing, queue, cache, policy, resolver, serializer, and loss log
summaries into structured Parquet alongside event data so diagnostics accumulate
with each collected dataset and can be modeled by DBT.

A durable row contract should include:

- `time`, `hostname`, `agent_id`, `session_id`;
- `component`, `metric_name`, `metric_value`, and unit;
- interval/cumulative semantics and observation-window duration;
- bounded dimensions such as operation, rule ID, trigger, and queue name;
- optional count/bytes represented fields;
- `dayPK` and `hourPK` partitions matching raw sensor conventions.

The writer must not feed its own diagnostic output back through FileOps, must not
depend on Esper health to report Esper failures, and must retain low-cardinality
logging for operator visibility. The existing manual `perf_*` raw-style streams
are useful prototypes, but sensor-native diagnostics need a stable schema and
DBT bronze/silver/monitoring models.

## Future Validation

1. Define rate-control and weighted-count semantics before implementation.
2. Build deterministic low/medium/burst/sustained mixed workloads.
3. Compare hard deny, adaptive sampling, and unsampled control runs.
4. Require bounded CPU/memory/state and quantify count/byte estimate error.
5. Define and version the diagnostic Parquet schema.
6. Verify S3 upload, DBT ingestion, and dashboard use without parsing logs.

## Marimo Analysis Follow-Up

Promote the overnight performance workflow into Marimo rather than leaving it
as one-off DuckDB SQL. Either add a focused Lintap performance notebook or a
clearly separated section in Wintappy's canonical
`notebooks/wintap_dbt_overview.py`.

The first version should:

- select local-time windows through `dayPK`/`hourPK` partition pruning;
- identify one host/process instance by hostname, PID, and command;
- label passive and controlled-workload phases;
- show minute/hour CPU, RSS, VSZ, faults, I/O, and context-switch trends;
- align pidstat buckets with structured FileOps queue, cache, sender-stage,
  serializer, and loss diagnostics;
- calculate first/last, half-window averages, slopes, correlations, and burst
  recovery time;
- display explicit fidelity gates and data-availability limitations.

Until sensor diagnostics become first-class Parquet, the notebook may accept a
parsed diagnostic extract, but log parsing should be treated as a temporary
input adapter rather than the durable model.
