---
title: "Feature Design: SELinux DBT pipeline"
type: concept
confidence: medium
grounded_by:
  - wiki/work/selinux-dbt-pipeline/references.md
  - ../Wintap-PyUtil/wintap_dbt/dbt_project.yml
  - ../Wintap-PyUtil/wintap_dbt/macros/relations.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - ../wintap/wintap/core/etl/esper/selinux.epl
  - ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs
policy: agent-editable
last_validated: 2026-11-04
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt; ../wintap/wintap/core/etl; ../wintap/wintap/platform/linux/sensor/ebpf
tags: [feature-work, selinux, dbt, lintap, design]
---

# Feature Design: SELinux DBT pipeline

## Model layout

Use one bronze and one silver model per native event family:

```text
raw_selinuxavc          -> stg_raw_selinuxavc          -> selinux_avc
raw_selinuxinteraction  -> stg_raw_selinuxinteraction  -> selinux_interaction
raw_selinuxtransition   -> stg_raw_selinuxtransition   -> selinux_transition
                                                               |
                         attribution and normalization --------+
                                                               v
                    family detail, context, and process summaries
```

Bronze models follow the optional-source pattern: scan and deduplicate when the directory exists; otherwise return a typed empty relation. This preserves normal builds for datasets that do not contain SELinux data.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/relations.sql; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process_registry.sql -->

## Silver contract

Each family-specific silver model should:

- retain the raw envelope (`MessageType`, `PID`, `PidHash`, `ProcessName`, `AgentId`, `Hostname`, `PolicyEpoch`);
- preserve native payload columns and raw timestamp columns;
- expose normalized `event_time`, `first_seen`, and `last_seen` values;
- retain `EventCount` and bronze `num_dups` separately;
- provide a deterministic family-specific event ID at the declared grain;
- expose `event_family` for common monitoring without flattening away family-specific fields.

The family tables remain authoritative. A nullable common event index may be added for monitoring and attribution, but it must not turn AVC, interaction, and transition fields into indistinguishable generic text.
<!-- SYNTHESIS: proposed normalization from the native producer contract and existing DBT stage conventions -->

## Attribution contract

Use a separate attribution relation so the same policy is applied to all three families:

1. Preserve the raw hostname and compare normalized host values.
2. Accept a direct identity only when the hash is valid, non-sentinel, and consistent with host context.
3. For events without accepted direct identity, find process candidates using host, PID, and event time within process lifetime bounds.
4. Accept the fallback only when one candidate remains.
5. Mark zero candidates `unmatched` and multiple candidates `ambiguous`.
6. Preserve candidate count, match method, quality, raw PID/hash/name, and selected process identity.

This is deliberately a bounded fallback, not a PID-only ownership rule. When producer-side identity quality improves, exact matches should increase without changing the meaning of historical unmatched rows.
<!-- SYNTHESIS: combines the selected exact-identity and constrained temporal-fallback policy -->

## Gold contract

- `selinux_event_detail`: normalized event index with family, ID, attribution state, time bounds, and native payload reference.
- `selinux_context`: distinct contexts from AVC source/target, interaction source/target, and transition old/new values, with family counts and observation bounds.
- `selinux_avc_summary`: host/process/context/class/result/enforcing/policy-epoch rollups with summed `EventCount` and time bounds.
- `selinux_interaction_summary`: host/process/SID/context/class/permission/novelty/policy-epoch rollups with summed `EventCount` and time bounds.
- `selinux_transition_summary`: host/process/old-new SID/context/executable/policy-epoch rollups.
- `selinux_process_summary`: accepted process attribution summaries plus separate unmatched and ambiguous counts.

The gold models must document whether counts are row counts or `EventCount` sums. High-volume interaction data should be summarized at useful analytical grains while retaining a queryable detail model where practical.

## Alternatives considered

- One wide table as the only output: rejected because the native grains and payload semantics differ.
- Direct PID-only joins: rejected because PID reuse and missing identity can create false ownership.
- Treating raw rows as individual events: rejected because interaction output is folded and permission-expanded.
- Making SELinux sources mandatory: rejected because existing datasets may not contain the optional event families.
