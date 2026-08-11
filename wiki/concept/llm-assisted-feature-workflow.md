---
title: "LLM-Assisted Feature Workflow"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-08-11
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: wiki/concept/llm-assisted-feature-workflow.md
tags: [workflow, llm, requirements, design, verification]
---

# LLM-Assisted Feature Workflow

## Purpose

The LLM-assisted feature workflow is a lightweight process for moving from an
idea to implemented, verified code while preserving useful context in the wiki.
It is intended to be structured enough for implementation and review, but light
enough that it does not become a heavyweight requirements process.

This workflow combines several familiar practices:

- RFC-style feature proposals for requirements and design.
- ADRs for durable architecture or process decisions.
- Spikes for small proof-of-concept experiments.
- Docs-as-code for storing supporting artifacts in version control.
- Requirements traceability from feature brief to tests and implementation.

## When To Use It

Use this workflow for feature work that is large enough to benefit from written
context before coding. In this ecosystem it is especially useful when the change
affects sensor telemetry semantics, WintapAPI data models, ETL/DBT pipeline
behavior, schemas, validation harnesses, notebooks/Streamlit workflows, or
anything that spans more than one repo (`../wintap`, `../Wintappy`, `../Lintap`,
this repo).

Skip the full workflow for small, localized fixes where a direct code change and
test are clearer than a new feature folder.

Long-running research threads (as opposed to bounded features) may also live
under `wiki/work/`; they typically anchor on an `index.md` plus dated snapshot
and handoff pages rather than the full artifact set. See
[[wiki/work/lintap-process-creation-validation/index]] for a live example.

## Workflow Stages

| Stage | Purpose | Typical Artifact |
| --- | --- | --- |
| Define functionality | Problem, goals, non-goals, behavior, acceptance criteria, test ideas | `brief.md` |
| Gather context | Repo references, specs, related pages, prior decisions | `references.md` |
| Design | Proposed approach, alternatives, risks, edge cases | `design.md` |
| Spike | Small proof-of-concept when uncertainty is high | `spike.md` |
| Plan implementation | Steps + verification checklist | `implementation_plan.md` |
| Hand off to a dev agent | Copy/paste prompt + curated context for code-development mode | `dev_handoff.md` |
| Implement and verify | Code changes + commands run + results | `verification.md` |
| Close out | Promote durable facts into canonical pages + log follow-ups | Updated canonical pages and `wiki/log.md` |

## Operating Rule

Feature work artifacts are scaffolding, not the final source of truth. Once a
feature ships, durable facts should be promoted into canonical wiki pages under
`tension/`, `decision/`, `concept/`, `component/`, `data_model/`, `event_type/`,
`pipeline/`, `schema/`, `tool/`, `workflow/`, `repo/`, or `diagnostic/`. The
feature folder can remain as historical context for review and future
reflection.

## Invocation

Use this phrase to start a new feature skeleton:

```text
Start a new feature using the LLM-assisted feature workflow: <feature name>
```

Expected behavior: create a feature folder under `wiki/work/<feature-slug>/`
with the artifacts that add value for the feature (see
[[wiki/concept/feature-work-template]] — only `brief.md` is always required),
then update `wiki/index.md` and append an entry to `wiki/log.md`.

## Related

- [[wiki/decision/feature-work-artifacts]] - accepted artifact organization
- [[wiki/concept/feature-work-template]] - reusable skeleton templates
- [[wiki/work/lintap-process-creation-validation/index]] - example of a research thread under `wiki/work/`
