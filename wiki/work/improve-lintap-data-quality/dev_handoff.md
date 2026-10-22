---
title: "Dev Handoff: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - wiki/work/improve-lintap-data-quality/brief.md
  - wiki/work/improve-lintap-data-quality/spike.md
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: stable
source_paths: wiki/work/improve-lintap-data-quality/dev_handoff.md
tags: [feature-work, lintap, data-quality, handoff]
---

# Dev Handoff: Improve Lintap Data Quality

**CLOSED 2026-10-22.** This is a historical implementation handoff; do not
restart its pending-work instructions. Final state and commands are in
[[wiki/work/improve-lintap-data-quality/verification]].

## Copy/Paste Prompt

    Switch to code-development mode for improve-lintap-data-quality.

    Read, in order:
    - wiki/work/improve-lintap-data-quality/brief.md
    - wiki/work/improve-lintap-data-quality/spike.md
    - wiki/work/improve-lintap-data-quality/implementation_plan.md
    - wiki/work/refactor-data-log-paths/verification.md

    ldq-00 is complete: use the existing `lintap-quality` source-build VM,
    its mounted checkout at `/home/ubuntu/git`, and its feature-specific data
    root at `/home/ubuntu/data/quality`. Begin with the then-pending ldq-01
    warm-up/attach-state matrix and attribution benchmark. For ldq-03, the
    current capture proves that Clone was disabled; enable it only for a clean
    controlled before/after capture, then compare DBT orphan composition. Do
    not select queue limits, orphan thresholds, or schema changes without
    measured evidence. Preserve zero-new-drop and >=95% file-path coverage as
    hard capture gates. Update verification, checklist, and wiki log as work
    proceeds.

## Non-Goals

No Windows parity or RPM acceptance work in this feature.
