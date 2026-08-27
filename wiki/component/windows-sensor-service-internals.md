---
title: "Windows Sensor and Service Internals"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/WintapSvcCore.cs
  - ../wintap/wintap/core/infrastructure/SubscriptionManager.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/infrastructure; ../wintap/wintap/platform/windows/infrastructure; ../wintap/wintap/platform/windows/sensor/etw
tags: [wintap, windows-sensor, component]
---

# Windows Sensor and Service Internals

The Windows service entry point is `WinTapSvc`, a `BackgroundService` that initializes logging, starts asynchronous service startup, keeps the host alive until cancellation, and performs graceful shutdown of plugins and collectors.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §SERVICE LIFECYCLE -->

Startup initializes platform-specific data-directory permissions on Windows, logs the agent ID, obtains `IProcessResolver` from dependency injection, initializes `EventChannel`, creates `PluginManager`, starts a `Watchdog`, registers plugins, optionally starts the DuckDB UI server, waits briefly for plugins, and then starts sensors through `SubscriptionManager` unless `WINTAP_DISABLE_SENSORS` is set.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §INITIALIZATION & STARTUP -->

## Collection Dispatch

`SubscriptionManager` chooses the platform-specific subscription path at runtime. On Windows it starts `WindowsSubscriptionManager`; on Linux it starts `LinuxSubscriptionManager`; macOS is scaffolded behind compile-time guards. Shutdown iterates active collectors and calls `Stop()`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/SubscriptionManager.cs §Start; §Stop -->

`WindowsSubscriptionManager` starts `ProcessSensor` first so later events can receive process attribution. It then loads enabled modeled sensors from settings, discovers kernel trace flags requested by those sensors, starts configured generic ETW providers as `GenericSensor`, and finally creates the shared kernel ETW listening thread with the accumulated kernel flags.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs §Start -->

## Event Flow

Sensor producers build `WintapMessage` objects and call `EventChannel.Send`. At that point Wintap attaches `AgentId`, process identity, parent process context, process registrations, and finally submits the event to Esper as `WintapMessage` unless environment flags bypass the relevant stages.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->

Since 2026-08-25, every message that reaches egress is also inspected by the always-on sensor health monitor (constant-time data-quality checks, stream-liveness watchdog, aggregated `SensorHealth` lines in Wintap.log) via `EventChannel.InspectForHealth` on both egress branches plus the `MemoryMapSensor` direct-send bypass; the monitor starts right after `subscriptionMgr.Start()` and stops first during shutdown. See [[wiki/component/sensor-health-monitor]].
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §InspectForHealth; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync/§StopAsync -->

## Operational Notes

The service has explicit environment-variable escape hatches for investigation and isolation, including `WINTAP_DISABLE_DUCKDB_UI`, `WINTAP_DISABLE_SENSORS`, `WINTAP_DISABLE_ETL`, `WINTAP_SKIP_PROCESS_RESOLVE`, `WINTAP_SKIP_PARENT_PROCESS_RESOLVE`, `WINTAP_SKIP_PROCESS_REGISTER`, and `WINTAP_SKIP_ESPER_SEND`.
<!-- GROUND_TRUTH: ../wintap/documentation/wintap-developer-guide.md §Key Runtime Variables -->

See also [[wiki/event_type/process-events]], [[wiki/event_type/file-events]], [[wiki/event_type/network-events]], and [[wiki/component/plugin-and-mcp-samples]].
