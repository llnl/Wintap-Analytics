---
title: "Implementation Plan: SELinux DBT pipeline"
type: workflow
confidence: medium
grounded_by:
  - wiki/work/selinux-dbt-pipeline/design.md
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintap_dbt/models/schema.yml
  - ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql
policy: agent-editable
last_validated: 2026-11-11
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/Makefile
tags: [feature-work, selinux, dbt, lintap, implementation-plan]
---

# Implementation Plan: SELinux DBT pipeline

## 0. Lock the observed contracts

- [x] Record the three raw schemas from the supplied sample.
- [x] Confirm timestamp conversion for Unix-second `EventTime` and Wintap FILETIME `FirstSeen`/`LastSeen`.
- [x] Confirm `EventCount` semantics and conservation expectations for each family.
- [x] Confirm the unknown/sentinel process hash and define when it is non-attributable.
- [x] Record sample row counts, host counts, context completeness, and initial attribution coverage.

## 1. Bronze models

- [x] Add optional `stg_raw_selinuxavc.sql` with current columns and a typed empty branch.
- [x] Add optional `stg_raw_selinuxinteraction.sql` with current columns and a typed empty branch.
- [x] Add optional `stg_raw_selinuxtransition.sql` with current columns and a typed empty branch.
- [x] Add the three event names to source validation/discovery without making any event mandatory.
- [x] Add model descriptions and field tests to `models/schema.yml`.

## 2. Silver models

- [x] Add one normalized silver model per family.
- [x] Normalize event and observation timestamps while retaining raw values.
- [x] Preserve `EventCount`, `num_dups`, policy epoch, envelope fields, and native payloads.
- [x] Add deterministic IDs and document each model's grain.
- [x] Add a common event index only if it avoids lossy family coercion.
- [x] Add the shared attribution candidate/match relation.
- [x] Test timestamp ordering, nonnegative counts, ID stability, and attribution cardinality.

## 3. Gold models and monitoring

- [x] Add family-specific detail and summary models.
- [x] Add the distinct context model with source-family counts and observation bounds.
- [x] Add process-centric summaries with accepted, ambiguous, and unmatched counts separated.
- [x] Add SELinux coverage and attribution metrics to existing build monitoring or a dedicated quality summary.
- [x] Run the complete pipeline against the supplied sample and compare raw-to-gold row and `EventCount` totals.

## 4. Documentation and handoff

- [x] Document each model's grain, timestamp units, count semantics, and optional-source behavior.
- [x] Record sample results and deviations in `verification.md`.
- [x] Promote durable DBT model semantics into canonical analytics pages after implementation stabilizes.
<!-- SYNTHESIS: ordered implementation checklist based on the DBT conventions and native event contract -->

## Implementation results

Canonical semantics: [[wiki/repo/wintappy-pipeline-repo]]. Combined-branch
regressions and outstanding release qualification are recorded in
[[wiki/work/selinux-dbt-pipeline/verification]]. Required PR approval and live-S3
qualification remain outstanding; promotion does not claim release acceptance.

- The sample schemas contain the shared envelope (`MessageType`, `PID`, `PidHash`,
  `ProcessName`, `AgentId`, `Hostname`, `FirstSeen`, `LastSeen`, `EventTime`,
  `EventCount`, `PolicyEpoch`, `dayPK`, and `hourPK`) plus native AVC, interaction,
  or transition payload fields.
- `EventTime` is Unix whole seconds; `FirstSeen` and `LastSeen` are Wintap
  FILETIME values. The timestamp test allows the documented one-second truncation
  tolerance for `EventTime`.
- AVC and transition rows represent native observations with `EventCount = 1` in
  the sample. Interaction rows are folded/permission-expanded producer output;
  their 5,348,812 normalized rows carry an `EventCount` sum of 16,903,971,905.
- Sentinel or blank PID hashes are not accepted as direct identity. The bounded
  fallback uses host, PID, and process lifetime, accepting only one candidate.
