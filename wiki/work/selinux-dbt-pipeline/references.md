---
title: "Feature References: SELinux DBT pipeline"
type: concept
confidence: high
grounded_by:
  - ../Wintap-PyUtil/wintap_dbt/dbt_project.yml
  - ../Wintap-PyUtil/wintap_dbt/macros/raw_sources.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/relations.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process_registry.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_registry.sql
  - ../Wintap-PyUtil/wintap_dbt/models/gold/process_registry_summary.sql
  - ../Wintap-PyUtil/wintap_dbt/models/schema.yml
  - ../wintap/wintap/core/etl/esper/selinux.epl
  - ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/EventOwnerSelection.cs
  - ../Wintap-Analytics/wiki/work/selinux-monitoring/design.md
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxavc/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxinteraction/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxtransition/
policy: agent-editable
last_validated: 2026-11-04
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt; ../wintap/wintap/core/etl; ../wintap/wintap/platform/linux/sensor/ebpf
tags: [feature-work, selinux, dbt, lintap, references]
---

# Feature References: SELinux DBT pipeline

## DBT conventions

- `dbt_project.yml` materializes bronze as views and silver/gold as tables.
- `raw_sources.sql` and `relations.sql` provide event discovery, optional-source handling, partition filtering, and Parquet scans.
- Existing bronze models deduplicate raw rows and add `num_dups`; optional models return typed empty relations when a source directory is absent.
- Existing silver models aggregate event counts while retaining first/last observations and normalized timestamps.
- Existing gold models provide entity summaries and are the pattern for SELinux process/context rollups.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/dbt_project.yml; ../Wintap-PyUtil/wintap_dbt/macros/raw_sources.sql; ../Wintap-PyUtil/wintap_dbt/macros/relations.sql; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process_registry.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_registry.sql; ../Wintap-PyUtil/wintap_dbt/models/gold/process_registry_summary.sql -->

## Native raw contract

The current producer contract has three event families:

- AVC records carry source/target contexts, class, requested/denied/audited masks, decoded permission strings, result, enforcing state, policy epoch, and count/time bounds.
- Interaction records carry source/target SIDs and contexts, class, permission, requested mask, novelty, policy epoch, and count/time bounds.
- Transition records carry old/new SIDs and contexts, executable file, policy epoch, and count/time bounds.

The shared message model, Esper projections, serializer, and Linux sensor are authoritative for field names and types. DBT should preserve numeric masks/SIDs and supplied context strings; it should not silently re-derive or discard unresolved values.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/selinux.epl; ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs; ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs -->

## Attribution references

The producer-side work records event-time identity as a design concern, while the current processing code and sample must still be measured. DBT should accept a valid non-sentinel identity when present, then generate host/PID/time candidates against process lifetime bounds. Exactly one candidate is a valid temporal fallback; zero candidates are unmatched; multiple candidates are ambiguous. Candidate count, match method, raw PID/hash/name, and quality state must remain available in the analytical output.
<!-- GROUND_TRUTH: ../Wintap-Analytics/wiki/work/selinux-monitoring/design.md §PidHash stamping; ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs §CreateMessage; ../wintap/wintap/core/infrastructure/EventChannel.cs §TryPopulateCurrentProcessIdentity; ../wintap/wintap/core/infrastructure/EventOwnerSelection.cs -->

## Sample observations

The supplied sample contains approximately 3,382 AVC rows, 5,349,253 interaction rows, and 2,890 transition rows. Interaction data is much larger because records represent folded or permission-expanded observations; `EventCount`, `FirstSeen`, and `LastSeen` must be preserved and summed deliberately. Blank contexts and unsuccessful attribution are quality outcomes to measure, not values to repair by assumption.
<!-- GROUND_TRUTH: ../../../data/lintap-alpha/raw_sensor/raw_selinuxavc/; ../../../data/lintap-alpha/raw_sensor/raw_selinuxinteraction/; ../../../data/lintap-alpha/raw_sensor/raw_selinuxtransition/ -->

## Related work

The producer-side capture and raw landing plan is documented in [[wiki/work/selinux-monitoring/brief]]. This DBT work begins after that raw-sensor boundary.
