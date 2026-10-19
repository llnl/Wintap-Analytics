---
title: "Decision: Separate Durable Data From Host Runtime State"
type: decision
status: accepted
decided_on: 2026-10-19
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/Env.cs
  - ../wintap/wintap/core/etl/shared/Paths.cs
  - ../Lintap-rdp/packaging/lintap-deb/lintap.env
  - ../Lintap-rdp/packaging/lintap-rpm/lintap.env
policy: human-review-required
last_validated: 2026-10-19
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
source_paths: ../wintap/wintap/core/shared/Env.cs; ../wintap/wintap/core/etl/shared/Paths.cs; ../Lintap-rdp/packaging
tags: [wintap, lintap, packaging, data-pipeline, paths]
---

# Decision: Separate Durable Data From Host Runtime State

## Context

The former single data root mixed finalized `raw_sensor` parquet with logs,
DuckDB state, serializer staging, diagnostics, and other host-local state.
That made the intended shared dataset root unsafe to mount across sensor hosts.

## Decision

Use independent roots. `WINTAP_DATA_ROOT` directly contains the durable,
shareable `raw_sensor/` tree. `WINTAP_RUNTIME_ROOT` contains host-local runtime
state, including logs, event store, Esper staging, diagnostics, recordings,
and pidstat spool.

The default Linux roots are `/var/log/lintap/data` and
`/var/log/lintap/runtime`. The Windows and macOS defaults are sibling `data`
and `runtime` directories under their existing platform application roots.

Neither package installation nor application startup migrates, links, merges,
or removes a prior tree. A disposable test host may run the separate manual
cleanup utility before installation.

## Rationale

The split leaves the finalized dataset mountable and archiveable without
cross-host runtime interference, while retaining independently configurable
operator overrides and the existing `raw_sensor` partition contract.

## Consequences

- `WINTAP_DATA_ROOT` is the dataset root, not a parent containing `parquet/`.
- Downstream DBT consumers use the data root directly and resolve
  `raw_sensor/` beneath it.
- Operators who set only `WINTAP_DATA_ROOT` get the default runtime root unless
  they explicitly set `WINTAP_RUNTIME_ROOT`.
- Existing data must be handled manually when a disposable deployment is reset.

## Alternatives Considered

- Keep a mixed single root: rejected because it contaminates shared storage
  with host-local state.
- Retain a `parquet/` intermediate directory: rejected because it adds an
  unnecessary level to the new dataset root.
- Automatically migrate or symlink old paths: rejected to keep package and
  runtime behavior predictable.
