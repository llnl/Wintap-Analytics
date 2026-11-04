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
last_validated: 2026-11-04
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/Makefile
tags: [feature-work, selinux, dbt, lintap, implementation-plan]
---

# Implementation Plan: SELinux DBT pipeline

## 0. Lock the observed contracts

- [ ] Record the three raw schemas from the supplied sample.
- [ ] Confirm timestamp conversion for Unix-second `EventTime` and Wintap FILETIME `FirstSeen`/`LastSeen`.
- [ ] Confirm `EventCount` semantics and conservation expectations for each family.
- [ ] Confirm the unknown/sentinel process hash and define when it is non-attributable.
- [ ] Record sample row counts, host counts, context completeness, and initial attribution coverage.

## 1. Bronze models

- [ ] Add optional `stg_raw_selinuxavc.sql` with current columns and a typed empty branch.
- [ ] Add optional `stg_raw_selinuxinteraction.sql` with current columns and a typed empty branch.
- [ ] Add optional `stg_raw_selinuxtransition.sql` with current columns and a typed empty branch.
- [ ] Add the three event names to source validation/discovery without making any event mandatory.
- [ ] Add model descriptions and field tests to `models/schema.yml`.

## 2. Silver models

- [ ] Add one normalized silver model per family.
- [ ] Normalize event and observation timestamps while retaining raw values.
- [ ] Preserve `EventCount`, `num_dups`, policy epoch, envelope fields, and native payloads.
- [ ] Add deterministic IDs and document each model's grain.
- [ ] Add a common event index only if it avoids lossy family coercion.
- [ ] Add the shared attribution candidate/match relation.
- [ ] Test timestamp ordering, nonnegative counts, ID stability, and attribution cardinality.

## 3. Gold models and monitoring

- [ ] Add family-specific detail and summary models.
- [ ] Add the distinct context model with source-family counts and observation bounds.
- [ ] Add process-centric summaries with accepted, ambiguous, and unmatched counts separated.
- [ ] Add SELinux coverage and attribution metrics to existing build monitoring or a dedicated quality summary.
- [ ] Run the complete pipeline against the supplied sample and compare raw-to-gold row and `EventCount` totals.

## 4. Documentation and handoff

- [ ] Document each model's grain, timestamp units, count semantics, and optional-source behavior.
- [ ] Record sample results and deviations in `verification.md`.
- [ ] Promote durable DBT model semantics into canonical analytics pages after implementation stabilizes.
<!-- SYNTHESIS: ordered implementation checklist based on the DBT conventions and native event contract -->
