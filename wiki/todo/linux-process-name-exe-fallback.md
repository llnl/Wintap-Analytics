---
title: "To-Do: Validate and Fix Linux Process Names Labeled `exe`"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcessSensorHelper.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
policy: agent-editable
last_validated: 2026-11-10
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor
tags: [todo, priority, linux, process-events, data-quality, telemetry-semantics, lintap, wintap]
---

# To-Do: Validate and Fix Linux Process Names Labeled `exe`

**Priority:** P1 — High (provisional; the reported label obscures executable
identity across many process records).
**State:** Open — intake finding; validation and implementation have not started.
**Likely next step:** Quantify the affected rows in the reviewed DuckDB, trace
them back through silver/bronze to raw process observations, then reproduce the
name-selection path on a Linux host before choosing a source fix and any
historical-data repair.

## Finding

The user reports that many processes in the reviewed local example database
have `process_name = 'exe'`. The suspected cause is Linux sensor fallback behavior
that derives a process name from `/proc/<pid>/exe` without resolving that procfs
symlink to its target. The reported row count, affected models, source events,
and cause have not been independently queried or confirmed for this intake.
<!-- HUMAN-REPORTED: user observation and suspected cause from review of a local example DuckDB; row counts and lineage not independently queried -->

Current source makes that failure mode plausible but does not establish it for
the reviewed rows. `ProcReader` records the `/proc/<pid>/exe` symlink target, or
the procfs path itself when no target is available. Linux process producers
attempt to resolve procfs paths, but retain the original path when resolution
does not produce a target. `ExtractProcessName` then takes the path basename;
for an unresolved `/proc/<pid>/exe` path that basename is literally `exe`.
Confirm which producer and fallback sequence emitted the reviewed values,
including whether the deployed sensor version matches the inspected source.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §ReadExe; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcessSensorHelper.cs §ExtractProcessName; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §ResolveExecutablePath; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §ResolveExecutablePath; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §ResolveExecutablePath, CreateRefreshMessage -->

## Validation and repair work

1. Count `exe` process names by source table/model, host/agent, event source,
   and time range. Check whether the value is also present in raw process
   observations or is introduced by a bronze/silver transformation.
2. For affected process identities, compare `process_name` with raw
   `ProcessPath`, command line/argv, process-start provenance, and any available
   executable-path evidence. Separate unresolved procfs-link paths from a real
   executable whose basename is `exe`.
3. Reproduce the producer paths for exec, clone, and rundown observations when
   `/proc/<pid>/exe` resolves normally, cannot be read, points to a deleted
   executable, or becomes unavailable during a process-exit race. Verify the
   deployed source revision and configuration against the current source.
4. Correct the producer fallback so an unresolved procfs magic-link name is not
   presented as an executable basename. Define when to use kernel `comm`, a
   captured argv[0], another reliable path, or an explicit unknown/unresolved
   value; do not silently fabricate an executable path.
5. Add regression coverage for each relevant producer and a downstream data
   quality check that identifies unexpected `exe` values while allowing
   independently verified legitimate executable names.
6. Determine whether affected historical silver data can be rebuilt or repaired
   from trustworthy raw evidence. Leave unsupported rows explicitly unresolved
   rather than guessing; compare row counts and process identity joins before
   and after any approved repair.

## Completion criteria

- The reviewed database's affected row count and source lineage are documented.
- The `exe` labels are either shown to be valid executable names or explained by
  a reproduced fallback path; unexplained instances are not hidden by a broad
  replacement rule.
- Sensor regressions cover resolved and unresolved `/proc/<pid>/exe` links and
  the selected fallback semantics.
- DBT/data validation detects unexpected labels, and any historical repair is
  backed by raw evidence with before/after checks.

## Related findings

Coordinate process-level validation with
[[wiki/todo/linux-process-executable-attribution]], which tracks nondeterministic
selection among Linux exec observations in the silver process model. Keep this
producer-side `exe` fallback issue separately testable from the downstream
choice of which valid observation represents a process lifetime.

## Disposition

This is a validation and bug-intake item, not authorization to change Wintap,
Wintappy, schemas, or historical data. Promote it to a feature-work folder only
after the affected rows, deployed producer path, and repair scope are established.
