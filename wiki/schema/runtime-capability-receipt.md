---
title: "HOST runtime capability receipt"
type: schema
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs
  - ../wintap/wintap/core/etl/model/Host.cs
  - ../wintap/wintap/core/etl/extract/HostSerializer.cs
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/devtools/validate_runtime_capabilities.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/wintap/core/infrastructure; ../wintap/wintap/core/etl
tags: [host, parquet, runtime-capabilities, provenance, linux, data-quality]
---

# HOST runtime capability receipt

`RuntimeCapabilitiesJson` is an additive nullable **string column on HOST**.
Its JSON document is versioned (`schemaVersion: 1`, camelCase). Wintap owns
implementation; Analytics owns this schema reference. Packaging/defaults and
Wintappy models are unchanged. Legacy missing/null fields mean **unknown**, not
disabled or equivalent quality.

## Canonical fields

| JSON field | Meaning |
|---|---|
| `schemaVersion` | Receipt contract version, independent of application version |
| `captureRunId` | UUID per app startup; not a boot ID or process identity |
| `startedAtUtc`, `completedAtUtc`, `phase` | Initialization interval and frozen startup snapshot; final phase is `startup-complete`, even if individual sensors fail |
| `platform`, `architecture`, `kernelRelease`, `osRelease` | OS architecture, exact Linux kernel release and `/etc/os-release` text |
| `kernelBtfReadable` | Target BTF could be opened/read; **not** proof an object relocated or a hook attached |
| `applicationVersion`, `instrumentation` | Assembly version and instrumentation coverage (`linux-startup-v1`; other platforms explicitly have uninstrumented sensor outcomes) |
| `settings.<key>.effectiveValue`, `.source` | Allowlisted pipeline/isolation settings and provenance; environment/config/default or component-effective result |
| `sensors.<key>` | Canonical Linux keys: `Execve`, `Clone`, `Exit`, `Network`, `FileOps`, `SELinux`, `ProcessRundown` |

Each sensor contains:

| Field | Meaning |
|---|---|
| `enabled`, `configurationSource` | Effective startup decision; compact/alias sensor environment overrides precede app config/defaults; global disable is explicit |
| `status` | `disabled`, `failed`, `running`, `partial` (or transient `starting` before finalization) |
| `failureReason` | Startup failure evidence when available; generic `start-returned-false` otherwise |
| `loadedObject`, `objectSha256`, `tier` | Selected object basename, SHA-256, `core`/`tracepoint`; null where no object selected |
| `objectAttempts[]` | Ordered attempted objects and outcomes (`not-found`, `open-failed`, `load-failed`, `program-not-found`, `attach-failed`, `events-map-not-found`, `ring-buffer-failed`, `selected`) plus native error when known |
| `hooks.<program>` | `role` = `primary`/`auxiliary`; `outcome` = `attached`, `failed`, `not-found`, `not-applicable`, `exception`; `errorCode` nullable |
| `features` | Component-owned facts: libbpf version, Clone thread-classification method, effective FileOps aggregation/queue/directory-index/deny rules, SELinux interaction mode/enforcing/policy epoch |

`running` means Start succeeded and recorded applicable hook attempts succeeded;
it does **not** guarantee semantic completeness. `partial` conservatively means
Start succeeded but at least one recorded applicable hook did not attach—an
architecture-specific missing legacy syscall can cause this status. Inspect
individual hooks, rather than treating partial as a numeric quality score.
`not-applicable` distinguishes hooks intentionally absent from the selected tier
(e.g. CO-RE Clone needs no syscall flag hooks) from failed required evidence.
Native null-link failures have unknown error codes; no synthetic errno is stored.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs §Finished; ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §AttachProgram -->

Lazy plugin initialization now preserves an already initialized receipt; a
packaged normal-ETL test exposed an unconditional reset that erased previously
recorded startup settings. Regression and correction are tracked in
[[wiki/work/clone-default-true/verification]].

Pipeline settings include actual initialized serializer queue capacities, drop
policies, flush intervals, high-water limits/dedicated-worker selections, writer
backlog limits, and direct-sink limits **when those components initialize before
snapshot completion**. Configuration values are not substituted for uninitialized
component evidence. `etlStarted` is the plugin manager's actual start result.
Arbitrary environment/config dumps and credentials are not exported; configured
file paths and explicit FileOps deny-comm rules can still reveal host context.

## Logging, persistence and startup timing

- Plugin initialization starts the receipt before ETL components initialize.
- Linux sensor completion logs `SENSOR_CAPABILITIES <json>` with run ID, sensor
  key, and the same sensor contract. Disabled states are also in the final receipt.
- After subscription startup, finalization freezes the receipt; the app logs
  `RUNTIME_CAPABILITIES <json>` and awaits a fresh HOST write **on every startup**.
- HOST parquet is written atomically into runtime staging then materialized to
  `raw_sensor/raw_host/dayPK=.../hourPK=...`, independent of ETL/direct-output
  enablement. Successful materialization removes its staging input; failures
  are logged and retain a completed staging parquet for recovery.
- Prior HOST files do not suppress this startup row. The new string property is
  part of the HOST model and included by dynamic schema construction even when
  null. The reviewed HOST-specific `union_by_name` source-writer branch was
  discarded: mixed legacy/new staging schema compatibility is not required.

Consequently HOST metadata now publishes even in sensor-disabled or ETL-disabled
diagnostic runs. Fatal initialization before finalization, storage failures or
shutdown racing startup can still prevent a receipt; absence remains unknown.
This feature does not add startup failure recovery or continuous receipt updates.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/PluginManager.cs §constructor; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync; ../wintap/wintap/core/etl/extract/HostSerializer.cs §WriteHostRecordAsync; ../wintap/wintap/core/etl/load/RawSensorWriter.cs §WriteParquetWithDuckDB -->

## Analysis example and boundaries

Current Linux Network adds PID-filter requested/applied booleans and version-gated
operation facts: `networkContractVersion=2` requires a core object with the new
UDP context map; older objects remain version0/unknown. Accept/UDP successful-return
hook attachment, sampling intervals and byte/address contracts are additive features,
not workload acceptance. PID values are not copied into these feature facts. Object
hash and trusted package inputs must still be verified separately.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §Start -->

```sql
SELECT Hostname, AgentId, EventTime,
       json_extract_string(RuntimeCapabilitiesJson, '$.captureRunId') AS run_id,
       json_extract_string(RuntimeCapabilitiesJson, '$.sensors.Clone.tier') AS clone_tier,
       json_extract_string(RuntimeCapabilitiesJson, '$.sensors.Clone.status') AS clone_status
FROM read_parquet('data/raw_sensor/raw_host/**/*.parquet', union_by_name=true);
```

Relate event streams to HOST by AgentId/hostname and capture time, retaining
startup intervals. **Other event rows do not yet carry this run ID**, so exact
run attribution is not guaranteed for overlapping collectors, delayed rows or
second-resolution HOST timestamps. Do not take a single latest HOST row for an
entire historical dataset or allow downstream hostname deduplication to erase
the receipt history. Wintappy propagation/DBT temporal joins are not implemented.

Not recorded as proven facts: build-host BTF/compiler/package provenance beyond
assembly version/object hashes, namespace/PID-view parity, ongoing health/drop
counters, permission root causes, policy changes after startup, or workload
coverage. Null/absent evidence must remain unknown. Interpretation of selected
tiers/hooks: [[wiki/diagnostic/linux-capability-data-quality-matrix]].

Validation and named evidence:
[[wiki/work/improve-lintap-data-quality/runtime-capability-verification]].

Retrospective feature and current review boundary:
[[wiki/work/linux-capability-smoke-triage/brief]].
