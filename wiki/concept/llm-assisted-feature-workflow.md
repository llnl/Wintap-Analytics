---
title: "LLM-Assisted Feature Workflow"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-07-06
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

A lightweight workflow for moving from an idea to implemented, verified code while preserving context in the wiki.

## Workflow Stages

| Stage | Purpose | Typical Artifact |
| --- | --- | --- |
| Define functionality | Problem, goals, non-goals, behavior, acceptance criteria, test ideas | `brief.md` |
| Gather context | Repo references, specs, related pages, prior decisions | `references.md` |
| Design | Proposed approach, alternatives, risks, edge cases | `design.md` |
| Spike | Small proof-of-concept when uncertainty is high | `spike.md` |
| Plan implementation | Steps + verification checklist | `implementation_plan.md` |
| Implement and verify | Code changes + commands run + results | `verification.md` |
| Close out | Promote durable facts into canonical pages + log follow-ups | update `wiki/log.md` |

## Invocation

Use this phrase to start a new feature skeleton:

```text
Start a new feature using the LLM-assisted feature workflow: <feature name>
```
