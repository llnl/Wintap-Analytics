---
title: "Lintap Supporting Repository"
type: repo
confidence: high
grounded_by:
  - ../Lintap/README.md
  - ../Lintap/teletap/README.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: Lintap
implementation_area: packaging
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Lintap/README.md; ../Lintap/teletap/README.md; ../Lintap/Multipass.md; ../Lintap/packaging
tags: [Lintap, dev-environment, packaging, repo]
---

# Lintap Supporting Repository

`../Lintap` is a Linux proof-of-concept host-based event sensor repository that implements Wintap-like functionality for Linux environments and transforms Linux telemetry into the semantic Wintap data model for analysis.
<!-- GROUND_TRUTH: ../Lintap/README.md §Lintap -->

This wiki treats Lintap as supporting infrastructure, not the main Wintap sensor implementation. The Lintap README states that the newer TeleTap/eBPF implementation has moved into the Wintap repository, while this repo still contains initial post-processing code and the older sysdig-based playground.
<!-- GROUND_TRUTH: ../Lintap/README.md §Running Lintap -->

## Two Linux Paths

The current TeleTap-oriented workflow requires Linux root access, eBPF tools, .NET 8, Python, DuckDB, and both Wintap and Lintap repos. Build commands run from the Wintap repo and build/run `Lintap.csproj`.
<!-- GROUND_TRUTH: ../Lintap/teletap/README.md §Prerequisites; §Build Commands -->

TeleTap output is expected to include canonical raw sensor Parquet under `raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/` and raw process connection increments partitioned by protocol. The old merged-to-raw conversion step is explicitly removed, and the canonical full ETL is stated to live in `Wintap-PyUtil/wintap_dbt`, not in the TeleTap directory.
<!-- GROUND_TRUTH: ../Lintap/teletap/README.md §Data output; §Full ETL with DBT -->

The older sysdig workflow captures process, file, network, and optional SELinux activity as TSV/SCAP, converts raw TSV into raw Wintap format, and then relies on Wintap-style ETL scripts for final datasets.
<!-- GROUND_TRUTH: ../Lintap/README.md §Running Lintap (sysdig); §Post-processing -->

## Wiki Boundary

Lintap pages should focus on Linux dev-environment setup, packaging/deployment support, raw-to-normalized data transition, and compatibility tensions. Do not use Lintap as the canonical source for Windows Wintap sensor semantics.
<!-- SYNTHESIS: inferred from ../Lintap/README.md, ../Lintap/teletap/README.md, and ../Wintap-Analytics/AGENTS.md -->

See also [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]].
