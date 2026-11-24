---
title: "To-Do: Unify Lintap Runtime and ETL Configuration Without Overwriting Local Settings"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/ConfigManager.cs
  - ../wintap/wintap/core/etl/shared/Utilities.cs
  - ../wintap/wintap/core/etl/ETLConfig.json
  - ../wintap/wintap/Wintap.Common.props
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Lintap/packaging/README.md
policy: agent-editable
last_validated: 2026-11-23
repo_scope: cross-repo
implementation_area: packaging
event_domain: none
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/shared/ConfigManager.cs; ../wintap/wintap/core/etl; ../Lintap/packaging
tags: [todo, priority, lintap, configuration, etl, packaging, debian, rpm, upgrade]
---

# To-Do: Unify Lintap Runtime and ETL Configuration Without Overwriting Local Settings

**Priority:** P2 — Medium (provisional; the split creates operator confusion and
upgrade risk, but a confirmed field configuration loss has not been recorded).
**State:** Open — investigation requested; no configuration format, migration, or
installer change is authorized by this TODO.
**Likely next step:** Inventory every setting, reader, default, override and package
destination in both configuration paths; then design one canonical operator-facing
configuration with explicit migration, validation and upgrade-preservation semantics.

## Finding

Lintap currently presents two configuration surfaces. The systemd service imports
`/etc/lintap/lintap.env`, while ETL code reads assembly-adjacent
`ETLConfig.json`. `ConfigManager` also reads JSON and permits environment overrides
for recognized root properties, but `Utilities.GetETLConfig()` independently reads
the assembly-adjacent JSON into the typed ETL configuration and applies only a
bounded set of environment overrides. The result is overlapping rather than fully
unified ownership and precedence.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/lintap.service; ../wintap/wintap/core/shared/ConfigManager.cs §LoadConfig/GetValue; ../wintap/wintap/core/etl/shared/Utilities.cs §GetETLConfig/GetETLConfigPath -->

The Linux packages already give `lintap.env` package-manager preservation
semantics: Debian declares it as a conffile and RPM marks it `%config(noreplace)`.
By contrast, `ETLConfig.json` is copied into the application output and packaged
under `/usr/lib/lintap`, so it is ordinary application payload rather than an
external administrator-owned config file. A package upgrade can therefore replace
an edited installed copy even though `lintap.env` is intended to survive upgrades.
<!-- GROUND_TRUTH: ../wintap/wintap/Wintap.Common.props §ETLConfig.json; ../Lintap/packaging/lintap-deb/build-deb.sh §conffiles; ../Lintap/packaging/lintap-rpm/build-rpm.sh §files; ../Lintap/packaging/README.md §Upgrade, removal, and disposable-host cleanup -->

The requested outcome is **one unified, canonical operator-facing configuration**
and installer behavior that does not silently overwrite existing operator values.
Package defaults or generated runtime artifacts may remain implementation details,
but they must not create multiple independently editable active configurations.
The serialization format is still open; the design must preserve typed/nested ETL
settings and cross-platform needs rather than flattening configuration prematurely.
<!-- HUMAN-DECISION: one unified operator-facing configuration, with installers preserving existing configuration values; conversation 2026-11-23. -->

## Investigation questions

1. Which settings exist only in `lintap.env`, only in `ETLConfig.json`, in both,
   or as code defaults, and which runtime reader actually consumes each one?
2. What is the canonical precedence among compiled defaults, package defaults,
   administrator config, environment overrides and command-line/test overrides?
3. Which format and canonical location should hold the one administrator-owned
   configuration on Linux, and what equivalent location should Windows use?
4. How should nested ETL adapter settings and sensitive values be represented,
   validated and permissioned if the env and JSON surfaces are combined?
5. What are the corresponding Windows configuration and installer requirements;
   which parts are Linux packaging policy rather than shared sensor semantics?
6. How are existing installations migrated without losing local values, silently
   changing defaults, or leaving two active files with ambiguous precedence?
7. How should schema/version evolution expose new defaults while retaining local
   edits and reporting obsolete, renamed or invalid settings?

## Required installer behavior

- Clean install may seed defaults, but upgrade must not silently replace an
  administrator-modified active configuration file.
- Debian and RPM must use their native preservation mechanisms or an equivalently
  explicit migration strategy; any Windows installer must provide the same semantic
  guarantee for its administrator-owned configuration.
- Packaged defaults and the canonical local configuration must have distinct
  ownership. Any vendor-default or generated file must not become a second
  operator-edited active configuration.
- Upgrade, downgrade, reinstall, remove and purge behavior must be explicit for
  configuration separately from telemetry and runtime state.
- Invalid or unmigratable configuration must fail safely with actionable diagnostics;
  the installer must not “repair” it by replacing it with defaults.

## Completion criteria

- A complete setting/reader/default/override inventory exists for both current files.
- One approved canonical configuration contract covers shared Wintap behavior plus
  platform-specific service settings; only one active file is operator-edited.
- Migration preserves representative locally modified legacy configurations and is
  idempotent across reinstall and repeated upgrade.
- Fresh install, modified-config upgrade, unmodified-config upgrade, downgrade,
  remove and purge tests pass for both Debian and RPM; applicable Windows installer
  behavior is either qualified or explicitly separated into a follow-up.
- Runtime tests prove the effective values and their source, including typed ETL
  settings, service environment values and invalid-input diagnostics.
- Packaging and operator documentation identifies the canonical editable file,
  shipped defaults, precedence, permissions and recovery procedure.

## Disposition

This is a cross-repo configuration and packaging intake item, not authorization to
change Wintap configuration semantics or installer behavior. Promote it to a feature
folder before implementation because it requires a migration design and coordinated
changes across Wintap plus Debian/RPM packaging.
