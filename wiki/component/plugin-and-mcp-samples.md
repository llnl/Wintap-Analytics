---
title: "Plugin and MCP Samples"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/PluginManager.cs
  - ../wintap/shared/WintapAPI/Interfaces.cs
  - ../wintap/shared/samples/SimpleEventPlugin/SimpleEventPlugin.cs
  - ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: wintap-api
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/infrastructure/PluginManager.cs; ../wintap/shared/WintapAPI/Interfaces.cs; ../wintap/shared/samples; ../wintap/shared/ai
tags: [plugins, mcp, samples, wintap]
---

# Plugin and MCP Samples

Wintap plugins are discovered through a MEF-based directory convention: `Plugins/PluginName/PluginName.dll`. The `PluginManager` loads matching plugin assemblies, composes them with logger and optional inference services, registers event handlers, starts scheduled runners, registers plugin MCP servers where available, and shuts down providers, runners, subscribers, ETW subscribers, and plugin load contexts on service stop.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/PluginManager.cs §PLUGIN CONVENTION; §LoadPluginAssemblies; §UnregisterPluginsAsync -->

`Interfaces.cs` defines the plugin contracts: `ISubscribe`, `ISubscribeEtw`, `IRun`, `IQuery`, `IProvide`, `IProvideMCP`, and `IInfer`. `EventFlags` let subscriber plugins request modeled event families such as process, file, registry, UDP, TCP, session, focus, and image-load activity.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/Interfaces.cs §PLUGIN INTERFACES -->

The simple event plugin exports `ISubscribe`, requests process and file activity events, serializes selected event metadata to `events.json`, and demonstrates the minimum MEF metadata pattern for a subscriber.
<!-- GROUND_TRUTH: ../wintap/shared/samples/SimpleEventPlugin/SimpleEventPlugin.cs §SimpleEventPlugin -->

## MCP Integration

The core MCP tool class exposes `get_current_datetime` and `RunSQL`. Its comments explicitly label the implementation as research/proof-of-concept and warn that `RunSQL` allows arbitrary SQL without input validation, authentication, authorization, or access control.
<!-- GROUND_TRUTH: ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs §mcp_tools remarks; §RunSQL -->

## Boundary

Plugin and MCP samples are useful extension examples, not stable telemetry semantics. Treat their output as downstream or generated activity unless it is explicitly normalized into `WintapMessage` by `PluginManager.Plugin_Events`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/PluginManager.cs §Plugin_Events -->
