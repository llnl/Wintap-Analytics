---
title: "Wiki Scope: Cross-Repo but Wintap-Focused"
type: decision
confidence: high
grounded_by:
  - ../Wintap-Analytics/AGENTS.md
  - ../wintap/README.md
  - ../Wintap-Analytics/README.md
  - ../Lintap/README.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: ../Wintap-Analytics/AGENTS.md; ../wintap/README.md; ../Wintap-Analytics/README.md; ../Lintap/README.md
tags: [decision, cross-repo, wintap]
---

# Wiki Scope: Cross-Repo but Wintap-Focused

## Context

The wiki lives in `../Wintap-Analytics/wiki`, but it covers the Wintap ecosystem across `../wintap`, `../Wintap-Analytics`, and `../Lintap`. The local operating contract states that source repos are read-only for wiki work and that wiki edits must be written only under `wiki/`.
<!-- GROUND_TRUTH: ../Wintap-Analytics/AGENTS.md §Repository Layout; §Source Policy -->

`../wintap` is the primary implementation repository for Wintap sensor internals, shared WintapAPI semantics, Esper/NEsper processing, ETL, plugins, and MCP integration. Its README frames Wintap as a researcher-first host telemetry and analytics platform.
<!-- GROUND_TRUTH: ../wintap/README.md §Wintap; §Architecture Summary -->

`../Wintap-Analytics` is a tooling and documentation host for analyzing and inspecting Wintap data.
<!-- GROUND_TRUTH: ../Wintap-Analytics/README.md §Wintap-Analytics -->

`../Lintap` documents Linux proof-of-concept and support workflows. Its README says the newer TeleTap/eBPF implementation has moved into the Wintap repo, while the Lintap repo still hosts post-processing and legacy sysdig playground material.
<!-- GROUND_TRUTH: ../Lintap/README.md §Lintap -->

## Decision

The wiki is cross-repo but Wintap-focused. It should prioritize Windows sensor internals, WintapAPI-normalized event semantics, Esper/NEsper stream-processing behavior, and analytics workflows that consume Wintap data. It should document Lintap primarily for Linux dev-environment, packaging/deployment, and semantic-compatibility context.
<!-- SYNTHESIS: inferred from ../Wintap-Analytics/AGENTS.md, ../wintap/README.md, ../Wintap-Analytics/README.md, and ../Lintap/README.md -->

## Consequences

Claims about sensor semantics should cite live source paths from `../wintap`, not copied source artifacts. Claims about analytics workflows should cite `../Wintap-Analytics`. Claims about Lintap should explicitly distinguish legacy sysdig workflows from newer TeleTap/eBPF support paths.

See also [[wiki/repo/wintap-primary-sensor-repo]], [[wiki/repo/wintap-analytics-host-repo]], and [[wiki/repo/lintap-supporting-repo]].
