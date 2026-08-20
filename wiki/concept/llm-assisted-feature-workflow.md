---
title: "LLM-Assisted Feature Workflow"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-08-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: wiki/concept/llm-assisted-feature-workflow.md
tags: [workflow, llm, requirements, design, verification, interview, metrics]
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
| Interview | Human and AI establish shared context and flesh out the idea through adaptive Q&A | `interview.md` (optional; distilled into `brief.md`) |
| Define functionality | Problem, goals, non-goals, behavior, acceptance criteria, test ideas | `brief.md` |
| Gather context | Repo references, specs, related pages, prior decisions | `references.md` |
| Design | Proposed approach, alternatives, risks, edge cases | `design.md` |
| Spike | Small proof-of-concept when uncertainty is high | `spike.md` |
| Plan implementation | Steps + verification checklist | `implementation_plan.md` |
| Hand off to a dev agent | Copy/paste prompt + curated context for code-development mode | `dev_handoff.md` |
| Implement and verify | Code changes + commands run + results | `verification.md` |
| Close out | Promote durable facts, record plain-language Velocity Results when enabled, and log follow-ups | Updated canonical pages, optional `metrics.md`, and `wiki/log.md` |

## Interview Stage

The interview is an interactive question-and-answer session between the human
and the agent at the start of feature creation. Its purpose is to establish the
shared context needed to flesh out the idea *before* drafting `brief.md`, so
the brief reflects actual intent rather than the agent's first guess.

### Protocol

1. **Ground first.** Before asking anything, the agent reads `wiki/index.md`
   and skims pages related to the stated idea, and spot-checks relevant live
   repo paths. Never ask the human something the wiki or source code already
   answers — cite it instead and ask only for confirmation if uncertain.
2. **Ask in small batches.** Ask 2–4 questions at a time, highest-leverage
   first. Prefer concrete options with a stated recommendation over open-ended
   prompts, but always allow free-form answers.
3. **Adapt.** Each batch is shaped by prior answers. Stop lines of questioning
   that the human has resolved; open new ones that their answers surface.
4. **Distinguish answer types.** Record each resolved item as one of:
   - *Decision* — the human chose; goes into `brief.md` (and later
     `decision/` pages if durable).
   - *Constraint* — a hard boundary (compatibility, platform, schema).
   - *Delegated* — the human explicitly leaves it to the agent or dev agent;
     record the delegation, don't silently assume it.
   - *Deferred* — genuinely unknown; goes to `## Open Questions` in
     `brief.md`, optionally spawning a spike.
5. **Know when to stop.** The interview is done when the agent can state the
   problem, goals, non-goals, acceptance criteria, and affected areas without
   guessing — typically 2–4 batches. It is a conversation, not a form: end
   early if the idea is already well specified, and say so.
6. **Play back before writing.** Close with a short summary of what was
   decided, constrained, delegated, and deferred, and get the human's
   confirmation before generating `brief.md`.
7. **Ask the two sealed estimate questions last.** After playback, ask exactly
   two fixed metrics questions: (a) the forced counterfactual — if the human
   had to build this exact scope alone, without AI, how many working hours
   would it take, plus a realistic calendar availability date (the hours are
   the feature's solo-hours: the Velocity numerator and portfolio weight);
   (b) with the AI workflow, on what date does the human predict the feature
   will be available. Record the answers verbatim in the
   `## Sealed — human estimates` section of `interview.md`. These are part of
   the hard three-question metrics budget in
   [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1; metric definition in
   [[wiki/concept/velocity-metric]]); if the human skips them, move on —
   never re-ask.

### Question Areas

Draw from these areas as relevant; skip any already answered by context:

- **Problem and motivation** — what hurts today, who feels it, what triggered
  the idea now.
- **Scope boundary** — smallest useful version vs. full vision; explicit
  non-goals.
- **Affected repos and layers** — sensor (`../wintap`), Lintap, WintapAPI
  data model, ETL/DBT pipeline (`../Wintappy`), analytics/notebooks, packaging.
- **Telemetry semantics** — whether raw producer behavior, normalized
  WintapAPI meaning, or downstream analytics interpretation changes.
- **Compatibility** — schema changes, existing recorded datasets, cross-repo
  consumers, Windows/Linux semantic parity.
- **Verification** — how the human will know it works; what evidence closes
  the feature.
- **Uncertainty** — which parts are risky enough to warrant a spike before
  design.

### Artifact

Capturing the interview in `interview.md` is optional. Use it when the
interview surfaced non-obvious rationale worth preserving for the dev agent or
future reflection; skip it when the brief captures everything that mattered.
The brief is always the distilled product — `interview.md` is supporting
context, never a second source of truth. See
[[wiki/concept/feature-work-template]] for the skeleton.

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

Expected behavior: run the interview stage first (ground in existing wiki and
repo context, then ask adaptive question batches until the idea is fleshed
out), play back the resolved context for confirmation, then create a feature
folder under `wiki/work/<feature-slug>/` with the artifacts that add value for
the feature (see [[wiki/concept/feature-work-template]] — only `brief.md` is
always required), then update `wiki/index.md` and append an entry to
`wiki/log.md`.

To skip the interview (e.g. the idea is already fully specified, or the human
is pasting in a prepared brief), say so explicitly:

```text
Start a new feature using the LLM-assisted feature workflow (no interview): <feature name>
```

## Related

- [[wiki/decision/feature-work-artifacts]] - accepted artifact organization
- [[wiki/concept/feature-work-template]] - reusable skeleton templates
- [[wiki/work/lintap-process-creation-validation/index]] - example of a research thread under `wiki/work/`
