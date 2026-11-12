---
title: "Feature Brief: SELinux DBT pipeline"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-PyUtil/wintap_dbt/dbt_project.yml
  - ../Wintap-PyUtil/wintap_dbt/macros/raw_sources.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/relations.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - ../wintap/wintap/core/etl/esper/selinux.epl
  - ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../Wintap-Analytics/wiki/work/selinux-monitoring/brief.md
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxavc/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxinteraction/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxtransition/
policy: agent-editable
last_validated: 2026-11-04
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt; ../wintap/wintap/core/etl; ../wintap/wintap/platform/linux/sensor/ebpf
tags: [feature-work, selinux, dbt, lintap, analytics]
---

# Feature Brief: SELinux DBT pipeline

## Problem

The current DBT project has bronze, silver, and gold patterns for several Wintap event families, but it does not yet model the native `raw_selinuxavc`, `raw_selinuxinteraction`, and `raw_selinuxtransition` parquet streams. These events therefore stop at the raw-sensor boundary instead of receiving the same documented transformations, quality checks, and analytical summaries as the other event families.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/dbt_project.yml; ../Wintap-PyUtil/wintap_dbt/models/ -->

The producer-side SELinux work already defines three distinct streams and their serialized envelope. This work starts at those raw parquet directories and carries them through DBT; it does not change capture behavior.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/selinux.epl; ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs; ../Wintap-Analytics/wiki/work/selinux-monitoring/brief.md -->

## Goals

- Add optional bronze models for AVC, interaction, and transition records.
- Add silver models that preserve native fields, normalize timestamps, retain event-count semantics, and expose a common event-family contract.
- Add gold detail and summary models while keeping the three native event grains distinct.
- Measure process attribution using valid identity first and a constrained host/PID/time fallback second.
- Keep ambiguous and unmatched attribution explicit rather than creating false process ownership.
- Add schema tests, quality checks, and monitoring for row counts, event counts, timestamps, contexts, and attribution outcomes.

## Non-goals

- Changes to the Linux sensor, serializer, Esper statements, or raw event schemas.
- Reconstructing the historical auditd batch transformation.
- A broad PID-only join that ignores process lifetime or PID reuse.
- Combining AVC, interaction, and transition data into one lossy replacement for the native models.

## Acceptance criteria

1. A dataset without SELinux directories still builds successfully through the normal DBT workflow.
2. The supplied SELinux sample produces documented bronze, silver, and gold relations for all three families.
3. Raw fields, family identity, timestamp bounds, and `EventCount` semantics remain queryable after transformation.
4. Attribution reports exact matches, unique temporal fallback matches, ambiguous candidates, and unmatched events separately.
5. Gold summaries preserve family-specific meaning and do not equate interaction rows with individual kernel events.
<!-- SYNTHESIS: scope and acceptance criteria are derived from the current DBT conventions, producer contract, and supplied sample -->
