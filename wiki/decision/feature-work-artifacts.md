---
title: "Feature Work Artifacts"
type: decision
confidence: medium
grounded_by:
  - wiki/concept/llm-assisted-feature-workflow.md
  - wiki/concept/feature-work-template.md
policy: human-review-required
last_validated: 2026-07-06
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: wiki/decision/feature-work-artifacts.md
tags: [decision, workflow, llm]
---

# Feature Work Artifacts

## Context

Some changes benefit from lightweight written context (requirements, design, verification), especially when multiple repos, schemas, or pipelines are involved.

## Decision

Use `wiki/work/<feature-slug>/` as the standard location for LLM-assisted feature-work artifacts in this repo.

## Consequences

- Feature work becomes auditable and easier to hand off.
- Durable facts should be promoted from work artifacts into canonical wiki pages after the feature stabilizes.

See also [[wiki/concept/llm-assisted-feature-workflow]] and [[wiki/concept/feature-work-template]].
