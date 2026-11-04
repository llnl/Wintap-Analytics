---
title: "Verification: SELinux DBT pipeline"
type: concept
confidence: low
grounded_by:
  - wiki/work/selinux-dbt-pipeline/implementation_plan.md
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxavc/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxinteraction/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxtransition/
policy: agent-editable
last_validated: 2026-11-04
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt; ../../../data/lintap-alpha/raw_sensor
tags: [feature-work, selinux, dbt, lintap, verification]
---

# Verification: SELinux DBT pipeline

## Planning baseline

No implementation commands have been run for this work definition yet. The following checks are the required verification sequence.

## Build commands

Run from `../Wintap-PyUtil` with the supplied data root:

```bash
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-check-config
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-check-source
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-build
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-test
```

## Required checks

- All three bronze, silver, and gold family relations exist for the supplied sample.
- A build with the three source directories absent still succeeds and returns typed empty relations.
- Raw-to-bronze row counts and duplicate counts are explained.
- Raw and gold `EventCount` sums are compared by family.
- Timestamp conversions preserve ordering and expected units.
- Blank context rates are reported by family and field.
- Exact, unique-temporal, ambiguous, and unmatched attribution counts are reported separately.
- Gold summary keys are unique at their declared grain.
- Interaction row counts are not presented as individual kernel-event counts.

## Results

To be filled during implementation with commands, outcomes, sample counts, deviations, and any producer-side identity observations.
