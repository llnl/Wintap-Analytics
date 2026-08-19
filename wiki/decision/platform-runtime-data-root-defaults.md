---
title: "Decision: Use Platform Runtime Data-Root Defaults When Unconfigured"
type: decision
status: accepted
decided_on: 2026-08-19
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/Env.cs
  - ../wintap/wintap/core/shared/ConfigManager.cs
  - ../wintap/wintap/core/etl/ETLConfig.json
policy: human-review-required
last_validated: 2026-08-19
repo_scope: wintap
implementation_area: packaging
event_domain: none
audience: developer
source_paths: ../wintap/wintap/core/shared/Env.cs; ../wintap/wintap/core/shared/ConfigManager.cs; ../wintap/wintap/core/etl/ETLConfig.json
tags: [wintap, packaging, dev-environment]
---

# Decision: Use Platform Runtime Data-Root Defaults When Unconfigured

## Context

The shared `ETLConfig.json` and `ConfigRoot.DataRoot` previously defaulted to
`/tmp/lintap-data`. Because configured values precede `Env.FileDataRoot`, a
clean Windows deployment resolved that slash-rooted value as
`C:\tmp\lintap-data` instead of `%ProgramData%\Wintap`. A reboot smoke exposed
the operational consequence when Code42-AAT opened the live DuckDB in that
temporary location and blocked Wintap startup.

## Decision

An unconfigured deployment uses the platform defaults owned by `Env.cs`:

- Windows: `%ProgramData%\Wintap`
- macOS: `/Library/Application Support/Mactap`
- Linux and other Unix: `/var/lib/lintap`

The shared shipped `ETLConfig.json` does not specify `DataRoot`, and
`ConfigRoot.DataRoot` has no non-empty initializer. Explicit programmatic,
`WINTAP_DATA_ROOT`, and JSON `DataRoot` overrides remain supported in that
precedence order.

## Rationale

The shared configuration is copied to every platform, so it must not contain a
platform-specific default. `Env.cs` already owns the cross-platform decision
and selects durable OS-appropriate locations without requiring operator setup.

## Consequences

Fresh deployments are platform-correct by default. Existing deployments that
implicitly relied on `/tmp/lintap-data` move to the platform location after
upgrade unless they set an explicit override. The wpc-09 fix does not migrate,
copy, merge, or delete an old data store.

## Alternatives Considered

- Require `WINTAP_DATA_ROOT` in every deployment: rejected because clean
  installs remain unsafe and platform-incorrect without operator repair.
- Put `%ProgramData%\Wintap` in the shared JSON: rejected because the JSON is
  also copied into Linux and macOS outputs.
- Add platform-specific JSON files: rejected as unnecessary duplication of the
  existing `Env.cs` ownership boundary.
