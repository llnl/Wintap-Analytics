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
  - ../wintap/developer_docs/audits/sfx-01-linux-process-names.md
policy: agent-editable
last_validated: 2026-11-22
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
**State:** Promoted — the source repair and synthetic/normal-ETL qualification are
implemented in the uncommitted `sfx-01` candidate; bounded Linux `live-01` name
evidence passed 8/8 multi-exec cases. Affected-row lineage and any historical
repair remain open.
**Likely next step:** Trace the reviewed DuckDB values through silver/bronze to raw
observations before any historical-data decision. The separate repaired-binary
direct-Parquet timing gate passed in `live-02`.

## Finding

The user reports that many processes in the reviewed local example database
have `process_name = 'exe'`. The suspected cause is Linux sensor fallback behavior
that derives a process name from `/proc/<pid>/exe` without resolving that procfs
symlink to its target. The reported row count, affected models, source events,
and cause have not been independently queried or confirmed for this intake.
<!-- HUMAN-REPORTED: user observation and suspected cause from review of a local example DuckDB; row counts and lineage not independently queried -->

The repaired source no longer treats an unresolved `/proc/<pid>/exe` alias as an
executable basename. It uses resolved readlink target evidence, otherwise observed
`comm`, otherwise `unknown`; it never parses command-line text as an executable
path. A genuine executable named `exe`, case, spaces and deleted-image link targets
remain valid. This establishes the candidate behavior, not the lineage or deployed
revision behind previously reported rows.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §ReadExe; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcessSensorHelper.cs §ReadExecutableLink/ResolveExecutablePath/ExtractProcessName; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §SelectExecutableMetadata; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §SelectExecutableMetadata; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §CreateRefreshMessage -->

The authorized `live-01` workload produced eight multi-exec cases. Every case had
the expected first/second executable-derived names and paths, and none used the
synthetic command tokens as names. This closes the bounded live-name assertion,
not the lineage of previously reported rows or deployment acceptance.

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

The source repair was selected under
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief]]. Keep this item
promoted until affected-row lineage closes the remaining historical data questions.
The passed repaired-binary `live-02` timing gate does not reopen the passed
`live-01` name assertion. No historical repair or Wintappy change is implied.
