---
title: "Feature Work Template"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-08-19
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: wiki/concept/feature-work-template.md
tags: [workflow, llm, template, feature-work, metrics]
---

# Feature Work Template

This page defines the reusable skeletons for starting a new feature with the
[[wiki/concept/llm-assisted-feature-workflow]].

Use this invocation:

```text
Start a new feature using the LLM-assisted feature workflow: <feature name>
```

The expected output is:

```text
wiki/work/<feature-slug>/
  interview.md             (optional; record of the context-building Q&A)
  brief.md                 (required)
  references.md            (optional)
  design.md                (optional)
  spike.md                 (optional)
  implementation_plan.md   (optional)
  dev_handoff.md           (optional)
  verification.md          (optional)
  metrics.md               (optional; velocity/ROI mini-lab — see [[wiki/concept/metrics-template]])
  index.md                 (optional; long-running research threads)
```

The interview stage (see [[wiki/concept/llm-assisted-feature-workflow]])
normally runs before any artifact is written; `interview.md` is only created
when its Q&A record adds value beyond what lands in `brief.md`.

Only create the artifacts that are useful for the feature. For a small feature,
`brief.md` plus `verification.md` may be enough. For a high-uncertainty feature,
include `references.md`, `design.md`, and `spike.md` before implementation. Use
`dev_handoff.md` when the work will be handed to a separate code-development
agent or session. Use `index.md` when the folder is a long-running research
thread with dated snapshots rather than a bounded feature.

## Frontmatter For Work Artifacts

Every file under `wiki/work/` is a wiki page and must carry the standard
frontmatter from `AGENTS.md`. Use `type: concept` for work artifacts unless a
page is specifically a `decision` or `tension` (research-thread `index.md`
pages may use `type: workflow`). Start each artifact from this block, adjusting
`title`, `repo_scope`, `implementation_area`, `event_domain`, `tags`, and
`grounded_by` to fit the feature:

```yaml
---
title: "<Artifact>: <Feature Name>"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: YYYY-MM-DD
repo_scope: wintap | Wintap-Analytics | Lintap | Wintappy | cross-repo
implementation_area: windows-sensor | wintap-api | esper | analytics | data-pipeline | packaging | dev-environment
event_domain: process | file | network | cross-domain | none
audience: llm-agent | developer | researcher | mixed
status: draft
source_paths: wiki/work/<feature-slug>/<artifact>.md
tags: [feature-work]
---
```

The body skeletons below assume this frontmatter is present.

## `interview.md`

Record of the interactive context-building session between the human and the
agent. Keep it condensed — resolved topics with outcomes, not a verbatim chat
transcript. Every item under Decisions/Constraints/Delegations must also be
reflected in `brief.md`; this file preserves the *why* behind them.

```markdown
# Feature Interview: <Feature Name>

## Initial Idea

<The human's original statement of the idea, as given.>

## Context Established Before Questioning

<Wiki pages read and repo paths spot-checked; facts taken as given without
asking.>

## Interview Log

### Round <n>

**Q:** <question, with options offered if any>
**A:** <the human's answer, condensed>
**Outcome:** decision | constraint | delegated | deferred — <one line>

## Decisions

## Constraints

## Delegations

## Deferred / Open Questions

## Playback Summary

<The confirmed summary that seeded brief.md.>

## Sealed — human estimates

<Asked as the interview's final two questions, answers recorded as given.
SEALED: any agent that will produce its own estimates (e.g. the Wintap
Engineer at exploration start) must not read this section until feature
close-out. See [[wiki/decision/ai-velocity-roi-mini-lab]] (v2). If the human
declines or the questions were skipped, leave blank — missing data is fine.>

**Q: If you had started this feature solo, without AI, on today's open date,
on what date would it realistically have been available? (Calendar estimate —
weekends and distractions absorbed. An effort amount, e.g. hours or weeks, may
accompany the date; its hours reading becomes the throughput weight.)**
**A:**

**Q: With the AI workflow, on what date do you predict this feature will be
available? (Calendar prediction, open date to availability.)**
**A:**
```

## `brief.md`

```markdown
# Feature Brief: <Feature Name>

## Problem

## Goals

## Non-Goals

## User-Facing Behavior

## Acceptance Criteria

## Affected Areas

## References

## Open Questions

## Test Plan

## Done When
```

## `references.md`

```markdown
# Feature References: <Feature Name>

## Live Repo Sources

## External Sources

## Related Wiki Pages

## Libraries And APIs

## Notes
```

## `design.md`

```markdown
# Feature Design: <Feature Name>

## Summary

## Proposed Approach

## Data Model Or Schema Changes

## Interfaces And User Experience

## Edge Cases

## Error Handling

## Risks

## Alternatives Considered

## Open Questions
```

## `spike.md`

```markdown
# Feature Spike: <Feature Name>

## Question

## Hypothesis

## Experiment

## Prototype Location

## Results

## Recommendation

## Follow-Ups
```

## `implementation_plan.md`

```markdown
# Implementation Plan: <Feature Name>

## Scope

## Steps

## Files Likely To Change

## Tests To Add Or Update

## Migration Or Compatibility Notes

## Rollback Plan

## Done Checklist
```

## `dev_handoff.md`

For handing prepared feature work to a code-development agent or a fresh
session. The copy/paste prompt should activate code-development mode per
`AGENTS.md` and enumerate the exact context files to read.

```markdown
# Dev Handoff: <Feature Name>

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

    Switch to code-development mode for <feature name>.

    Use these wiki files as the handoff context:

    - wiki/work/<feature-slug>/brief.md
    - wiki/work/<feature-slug>/design.md
    - wiki/work/<feature-slug>/implementation_plan.md

    Goal: <one-sentence goal for this slice>.

    Before editing code, read AGENTS.md and confirm that code-development
    mode is active for this task.

## Handoff Summary

## Primary Sources For The Dev Agent

## Recommended First Implementation Slice

## Non-Goals For This Slice

## Testing Expectations

## Closeout Instructions

- Update wiki/work/<feature-slug>/verification.md with commands run and results.
- Update the wiki/work/<feature-slug>/implementation_plan.md done checklist.
- Append a concise entry to wiki/log.md.
- Promote durable facts into canonical wiki pages once behavior stabilizes.
```

## `verification.md`

```markdown
# Verification: <Feature Name>

## Test Commands

## Manual Checks

## Results

## Known Gaps

## Follow-Ups
```

## `index.md` (research threads)

For long-running research threads that accumulate dated snapshots and handoffs
instead of a bounded feature lifecycle. Modeled on
[[wiki/work/lintap-process-creation-validation/index]].

```markdown
# Research Thread: <Thread Name>

<One paragraph: what this thread tracks and why it is separate from
canonical pages until findings are validated.>

## Pages

- [[wiki/work/<thread-slug>/<page>]] <one-line description>

## Current Scope

## Open Research Questions
```

## `metrics.md`

Optional velocity/ROI mini-lab data file. Skeleton, field definitions, and
lifecycle live in [[wiki/concept/metrics-template]]; protocol in
[[wiki/decision/ai-velocity-roi-mini-lab]].

## Related

- [[wiki/concept/llm-assisted-feature-workflow]] - process overview
- [[wiki/decision/feature-work-artifacts]] - accepted organization
- [[wiki/concept/metrics-template]] - velocity/ROI metrics file format
- [[wiki/decision/ai-velocity-roi-mini-lab]] - metrics overlay protocol
