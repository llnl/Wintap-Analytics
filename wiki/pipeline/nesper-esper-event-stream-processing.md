---
title: "NEsper/Esper Event-Stream Processing"
type: pipeline
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - ../wintap/wintap/core/etl/esper/esper-context.epl
  - ../wintap/diagnostics/nesper-repro/README.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: esper
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/infrastructure/EventChannel.cs; ../wintap/wintap/core/etl/extract/Serializer.cs; ../wintap/wintap/core/etl/esper; ../wintap/diagnostics/nesper-repro
tags: [esper, nesper, event-stream-processing, pipeline]
---

# NEsper/Esper Event-Stream Processing

Esper is Wintap's runtime event-stream processing layer. `EventChannel` initializes an Esper configuration, registers `WintapMessage` as an event type, creates the default runtime, compiles/deploys EPL, and sends normalized events into Esper as `WintapMessage` beans.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §ESPER INFRASTRUCTURE LIFECYCLE; §Send -->

## Query Compilation

`EventChannel.CompileDeploy` adapts EPL before compilation, adds a workbench name prefix for most queries, adds the existing Esper runtime path to compiler arguments, validates syntax, compiles, and deploys the statement. Query adaptation runs through `EnumFormatter.FormatQueryForCompile` and can be altered by `WINTAP_DISABLE_ESPER_ENUM_CAST`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §QUERY COMPILATION & DEPLOYMENT; §FormatQueryForCompile -->

## Serializer Registration

ETL serializers register one or more EPL queries, attach event handlers to deployed statements, queue query outputs, and flush batches to Parquet. `Serializer` deploys the shared `Every10Seconds` context once per process, then registers per-domain queries such as process, file, TCP, and UDP.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §regContext; §registerQuery; §ProcStatement_Events -->

The shared context is defined as a 10-second context initiated immediately and terminated after 10 seconds. TCP and UDP aggregation queries use this context; file aggregation uses a 10-second time batch window.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/esper-context.epl §context -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/tcp.epl §query -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/file.epl §query -->

## Workbench Queries

The Workbench can create and manage interactive EPL queries through `EventChannel.ManageWorkbenchQuery`. Only one query is treated as active at a time; active query state is persisted and reset to stopped on startup.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §WORKBENCH STATE MANAGEMENT -->

## Backpressure And Drops

Serializers maintain in-memory queues before Parquet handoff. Optional environment variables can bound queue depth globally or per serializer and choose drop-newest or drop-oldest behavior. Dropped events are reported through `EventChannel.AddDroppedEvents`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §initSensor; §Save -->

## Diagnostic Caveat

The `diagnostics/nesper-repro` project isolates a Fedora/shared-mount NEsper compile/deploy failure. The README records `EPCompileException: Bad IL range` for even a simple `SELECT * FROM SimpleEvent` when built on a shared mount, while native `/tmp` builds pass. This indicates a filesystem/output-location problem rather than an EPL semantic problem.
<!-- GROUND_TRUTH: ../wintap/diagnostics/nesper-repro/README.md §NEsper Fedora Repro -->

See also [[wiki/diagnostic/nesper-repro]] and [[wiki/tool/wintap-workbench]].
