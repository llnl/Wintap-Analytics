---
title: "Wintap Primary Sensor Repository"
type: repo
confidence: high
grounded_by:
  - ../wintap/README.md
  - ../wintap/documentation/wintap-developer-guide.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: windows-sensor
event_domain: none
audience: mixed
status: draft
source_paths: ../wintap/README.md; ../wintap/documentation/wintap-developer-guide.md; ../wintap/wintap/
tags: [wintap, windows-sensor, repo]
---

# Wintap Primary Sensor Repository

`../wintap` is the primary implementation repository for Wintap sensor code, runtime infrastructure, ETL, shared WintapAPI contracts, and platform-specific builds. The current README describes Wintap as a researcher-first host telemetry and analytics platform for security research, behavioral analysis, and exploratory investigations rather than enterprise endpoint management.
<!-- GROUND_TRUTH: ../wintap/README.md §Wintap -->

The active source tree is `../wintap/wintap/`. The solution contains Windows, Linux, and macOS project entry points through `Wintap.csproj`, `Lintap.csproj`, and `Mactap.csproj`, with core source areas under `core/infrastructure`, `core/etl`, `core/shared`, and platform-specific code under `platform/windows`, `platform/linux`, and `platform/macos`.
<!-- GROUND_TRUTH: ../wintap/documentation/wintap-developer-guide.md §Project Layout -->

## Architecture Map

Wintap is organized around four layers: platform-specific collectors and sensors, core routing and enrichment through `EventChannel`, ETL and serialization to Parquet and related outputs, and optional adapters, plugins, and MCP integrations.
<!-- GROUND_TRUTH: ../wintap/README.md §Architecture Summary -->

Important runtime components called out by the developer guide are `SubscriptionManager`, `EventChannel`, `ProcessResolver`, `WintapSvcCore`, and serializer classes under `core/etl/extract` and `core/etl/load`.
<!-- GROUND_TRUTH: ../wintap/documentation/wintap-developer-guide.md §Architecture Overview -->

## Wiki Role

This wiki treats `../wintap` as the source of truth for sensor semantics, WintapAPI-normalized event shape, Esper/NEsper stream processing, and platform-specific collector behavior. Related pages should cite live files from this repo rather than copying source code into `raw/`.

See also [[wiki/component/windows-sensor-service-internals]], [[wiki/component/wintap-api-shared-data-model]], [[wiki/event_type/process-events]], [[wiki/event_type/file-events]], [[wiki/event_type/network-events]], and [[wiki/pipeline/nesper-esper-event-stream-processing]].
