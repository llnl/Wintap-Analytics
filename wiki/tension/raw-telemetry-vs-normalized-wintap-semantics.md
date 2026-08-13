---
title: "Raw Telemetry vs Normalized Wintap Semantics"
type: tension
confidence: medium
grounded_by:
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs
  - ../Lintap/README.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: cross-domain
audience: mixed
status: open
source_paths: ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/wintap/core/infrastructure/EventChannel.cs; ../wintap/wintap/platform/windows/sensor/etw; ../Lintap/README.md
resolution: null
poles:
  - "Expose direct host telemetry details so researchers can inspect raw ETW/sysdig/eBPF behavior and diagnose collection fidelity."
  - "Normalize events into stable WintapAPI semantics so analytics can operate across event domains and platforms."
tags: [tension, telemetry-semantics, wintap-api]
---

# Raw Telemetry vs Normalized Wintap Semantics

## Tension

Wintap producers preserve many source-specific details, such as ETW activity names, TCP sequence/window fields, file-key/path resolution, and Security log event-derived process fields. At the same time, the shared `WintapMessage` model normalizes these into a common envelope with `MessageType`, `ActivityType`, `PID`, `PidHash`, `ProcessName`, `AgentId`, and domain objects.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §WintapMessage -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs §sendFileEvent -->

`EventChannel.Send` is the practical normalization boundary. It enriches events with agent and process context, handles fallback process attribution, registers process events, and routes to Esper. This makes downstream analytics more stable but can hide whether a field came directly from the producer or from Wintap enrichment.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->

Lintap sharpens the same tension from the Linux side: the repo describes raw Linux telemetry collection and transformation into the semantic Wintap data model, while newer TeleTap/eBPF support has moved into the Wintap repo.
<!-- GROUND_TRUTH: ../Lintap/README.md §Lintap; §Running Lintap (sysdig) -->

## Current Holding Pattern

Document both the producer-side origin and the normalized WintapAPI meaning on event-type pages. For downstream analysis, state whether a field is raw telemetry, WintapAPI enrichment, ETL aggregation, or analysis annotation.
<!-- SYNTHESIS: inferred from ../Wintap-Analytics/AGENTS.md, ../wintap/shared/WintapAPI/WintapMessage.cs, and ../wintap/wintap/core/infrastructure/EventChannel.cs -->
