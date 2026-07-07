---
title: "NEsper Reproduction Diagnostic"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/diagnostics/nesper-repro/README.md
  - ../wintap/diagnostics/nesper-repro/Program.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: esper
event_domain: none
audience: mixed
status: draft
source_paths: ../wintap/diagnostics/nesper-repro
tags: [nesper, diagnostic, wintap]
---

# NEsper Reproduction Diagnostic

`../wintap/diagnostics/nesper-repro` is a standalone diagnostic project for isolating NEsper compile/deploy behavior from Wintap service startup, ETL workers, sensors, DuckDB, and plugins.
<!-- GROUND_TRUTH: ../wintap/diagnostics/nesper-repro/README.md §NEsper Fedora Repro -->

## What It Tests

The README records that on a Fedora VM shared mount, even a minimal `SELECT * FROM SimpleEvent` query can fail with `EPCompileException: Bad IL range`. Copying the repro and `shared/WintapAPI` to a native `/tmp/opencode` path and building there makes all queries pass. Running the native-built DLL from the shared repo directory also passes, while running the shared-built DLL from native `/tmp/opencode` still fails.
<!-- GROUND_TRUTH: ../wintap/diagnostics/nesper-repro/README.md §NEsper Fedora Repro -->

## Interpretation

The diagnostic narrows this failure to assemblies or output loaded from a shared mount, not current working directory and not necessarily Wintap sensors or ETL semantics.
<!-- SYNTHESIS: inferred from ../wintap/diagnostics/nesper-repro/README.md -->

## Usage

The documented commands build and run the repro from the Wintap repo root with `dotnet build diagnostics/nesper-repro/nesper-repro.csproj` and `dotnet diagnostics/nesper-repro/bin/Debug/net8.0/nesper-repro.dll`.
<!-- GROUND_TRUTH: ../wintap/diagnostics/nesper-repro/README.md §Run from the repo root -->

See also [[wiki/pipeline/nesper-esper-event-stream-processing]].
