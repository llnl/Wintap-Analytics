---
title: "Dev Handoff: Debian Package Refresh"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
policy: agent-editable
last_validated: 2026-10-03
repo_scope: Lintap
implementation_area: packaging
event_domain: none
audience: llm-agent
status: draft
source_paths: wiki/work/debian-package-refresh/dev_handoff.md
tags: [feature-work, lintap-packaging, debian, dev-handoff]
---

# Dev Handoff: Debian Package Refresh

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

    Switch to code-development mode for the Debian package refresh (dpr).

    Use these wiki files as the handoff context:

    - wiki/work/debian-package-refresh/brief.md
    - wiki/work/debian-package-refresh/references.md
    - wiki/work/debian-package-refresh/implementation_plan.md
    - wiki/work/debian-package-refresh/dev_handoff.md

    Goal: bring ../Lintap/packaging/lintap-deb/ to parity with the
    field-proven RPM builder per the dpr-01..dpr-04 slices, then run the
    amd64 smoke (dpr-05).

    Before editing code, read AGENTS.md and confirm that code-development
    mode is active for this task. Do NOT read the "Sealed — human estimates"
    section of wiki/work/debian-package-refresh/interview.md.

## Handoff Summary

The deb builder predates and fell behind the RPM builder the RHEL 8 field
deployments hardened. Refresh it in place: tier-aware tracer validation, MCP
publish parity with `--skip-mcp`, native work-root, field-parity `lintap.env`
(keep Snappy — deliberate divergence), upgrade-safe maintainer scripts, and an
`ldd`-verified `Depends:` line. Validate with install + short smoke on native
Ubuntu amd64 and arm64 hosts.

## Authorization

- The human explicitly authorized writes to `../Lintap/packaging/lintap-deb/`
  (and only there) for this feature, 2026-10-03.
- Explicitly NOT authorized: `../Lintap/packaging/lintap-rpm/`, any `../wintap`
  source or eBPF Makefile change, sibling repos otherwise. If a needed change
  falls outside `lintap-deb/`, stop and ask.
- Field-host rules in [[wiki/workflow/lintap-dev-field-workflow]] apply if any
  field host gets involved; the smoke hosts here are dev hosts.

## Primary Sources For The Dev Agent

- Parity source: `../Lintap/packaging/lintap-rpm/build-rpm.sh` (mirror its MCP
  publish, work-root, validation, hygiene; do NOT mirror its
  libnironcompress.so deletion, GLIBC warning, or Uncompressed override).
- Field env: `../Lintap/packaging/lintap-rpm/lintap.env`.
- Tracer tiers: `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile`
  (`TRACEPOINT_OBJS` vs `CORE_OBJS`; `selinux_tracer` is CO-RE and
  opportunistic).
- MCP coupling: `../wintap/wintap/Lintap.csproj` §BuildMcpServer.

## Recommended First Implementation Slice

dpr-01 + dpr-02 together (script + env are one coherent diff), then dpr-03,
dpr-04. Build locally after each slice with `--skip-mcp --no-restore` dry runs
where NuGet access is uncertain; a release candidate build must be a fresh
publish.

## Non-Goals For This Slice

- lintian/changelog/copyright polish; systemd hardening; apt hosting.
- Extended runtime gates.
- Touching the RPM builder even where sharing code is tempting.

## Testing Expectations

- Script assertions must pass for: native amd64 build (both tiers + selinux if
  built), cross-build (tracepoint tier only — must not fail on missing CO-RE
  objects).
- dpr-05/06 smoke per brief acceptance criteria; record exact commands,
  outputs, and package SHA-256 in verification.md.
- Upgrade test: build two revisions, install sequentially, confirm services
  stay enabled/running.

## Closeout Instructions

- Update wiki/work/debian-package-refresh/verification.md with commands run and results.
- Update the wiki/work/debian-package-refresh/implementation_plan.md done checklist.
- Append a concise entry to wiki/log.md.
- Promote durable facts into canonical wiki pages once behavior stabilizes
  (likely [[wiki/repo/lintap-supporting-repo]]).
