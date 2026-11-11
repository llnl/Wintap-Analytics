---
title: "Priority To-Do Queue"
type: diagnostic
confidence: medium
grounded_by:
  - wiki/concept/feature-work-template.md
policy: agent-editable
last_validated: 2026-11-08
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: wiki/todo
tags: [todo, backlog, findings, feature-work]
---

# Priority To-Do Queue

Intake queue for concrete bugs, data-quality findings, and enhancement ideas
that are not yet ready for a full feature-work folder. Keep one finding per page
under `wiki/todo/`, with its priority, evidence, open questions, and likely next
step. This lets findings accumulate without prematurely deciding their fixes.

## Priority guide

- **P1 — High:** likely to silently misstate or lose canonical data, or otherwise
  has a significant correctness impact.
- **P2 — Medium:** material issue with bounded impact or a useful improvement.
- **P3 — Low:** opportunistic enhancement or research follow-up.

Priority is a triage signal, not an implementation authorization or schedule.
Revisit it as evidence and competing work change.

## Lifecycle

Use `Open` for an intake finding. When selected for deep investigation, create a
feature folder under `wiki/work/<feature-slug>/` using the feature-work workflow
(typically beginning with `brief.md` and `references.md`) and link it here. The
deep dive may conclude in a bug fix, a feature enhancement, a modeling decision,
or a documented no-change recommendation; do not assume the implementation in
the intake record. Mark an item `Promoted` or `Closed` when its disposition is
recorded.

## Open items

| Priority | Item | State | Summary |
| --- | --- | --- | --- |
| P1 — High | [[wiki/todo/linux-process-executable-attribution]] | Open | Silver process aggregation may select an unconfirmed exec target and independently combine name/path from different observations. |
| P1 — High | [[wiki/todo/lintap-linux-process-command-line-quality]] | Open | Focused VM run reports a high raw command-line blank rate and multiple distinct values behind many nonblank process summaries. |
| P2 — Medium | [[wiki/todo/canonical-process-owned-network-grains]] | Open | Reconcile documented process/network increment and connection grains; preserve metadata conflicts and process-observation semantics for reusable analytics. |
| P2 — Medium (provisional) | [[wiki/todo/transformer-five-tuple-connection-port-key]] | Open | Investigate whether `Transformer.cs:37` passes the high endpoint port for both five-tuple key ports, causing connection-ID collisions. |
| Untriaged | [[wiki/todo/raw-sensor-upload-time-partition]] | Open | Current .NET code partitions at merge time and retries the same S3 key; the requested UTC actual-upload partition contract needs a separate shared-uploader correction. |
| Untriaged | [[wiki/todo/listening-socket-capture-and-modeling]] | Open | Investigate process-attributed listening-socket lifecycle capture and a downstream model distinct from peer-oriented connections; priority and platform scope remain open. |

## Related

- [[wiki/concept/feature-work-template]] — full feature-work artifact structure.
- [[wiki/concept/llm-assisted-feature-workflow]] — process for promoting an
  intake item into a deep dive.
