---
title: "Wintap Workbench"
type: tool
confidence: high
grounded_by:
  - ../wintap/shared/Wintap-Workbench/README.md
  - ../wintap/shared/Wintap-Workbench/src/app/app-routing.module.ts
  - ../wintap/wintap/core/api/StreamsController.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: wintap-api
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/shared/Wintap-Workbench; ../wintap/wintap/core/api/StreamsController.cs; ../wintap/wintap/core/infrastructure/EventChannel.cs
tags: [wintap-workbench, ui, tool]
---

# Wintap Workbench

Wintap Workbench is the Angular-based web UI shipped with Wintap. Its stack includes Angular 15, PrimeNG, SignalR client, CodeMirror, and charting dependencies, and its built frontend is copied into the .NET application output when `shared/Wintap-Workbench/dist/Workbench` exists.
<!-- GROUND_TRUTH: ../wintap/shared/Wintap-Workbench/README.md §Wintap Workbench; §Tech Stack; §Build Integration -->

The route map exposes dashboard, query builder, process/tree view, ETW explorer, DuckDB, chat, and documentation areas.
<!-- GROUND_TRUTH: ../wintap/shared/Wintap-Workbench/src/app/app-routing.module.ts §routes -->

## EPL Query Path

Workbench queries are posted to `/api/streams`. The backend delegates query state to `EventChannel.ManageWorkbenchQuery`, attaches event handlers to active Esper deployments, and sends query results to clients over the `WorkbenchHub` SignalR channel.
<!-- GROUND_TRUTH: ../wintap/wintap/core/api/StreamsController.cs §WorkbenchHub; §Post; §ActiveQuery_Events -->

`EventChannel` persists workbench query state in `workbench-state.json` under the Wintap file data root and resets saved queries to stopped state on startup.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §WORKBENCH STATE MANAGEMENT -->

## Boundary

The Workbench is an interactive inspection and query surface. It should not be treated as the authoritative source for telemetry semantics; those belong to `WintapMessage`, sensor producers, and ETL EPL.
<!-- SYNTHESIS: inferred from ../wintap/shared/Wintap-Workbench/README.md, ../wintap/wintap/core/api/StreamsController.cs, and ../wintap/shared/WintapAPI/WintapMessage.cs -->
