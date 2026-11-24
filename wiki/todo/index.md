---
title: "Priority To-Do Queue"
type: diagnostic
confidence: medium
grounded_by:
  - wiki/concept/feature-work-template.md
policy: agent-editable
last_validated: 2026-11-23
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
| P1 — High (provisional) | [[wiki/todo/linux-process-name-exe-fallback]] | Promoted | Source repair and focused qualification complete; bounded Linux name evidence passes 8/8, while affected-row lineage and historical disposition remain open. |
| P1 — High | [[wiki/todo/linux-process-executable-attribution]] | Promoted | Sensor/projection distinguishes attempt/success and path evidence source; deterministic paired name/path and initial/latest successful-image DBT policy remain open. |
| P1 — High | [[wiki/todo/process-observation-time-separate-from-birth]] | Promoted | Linux Start/Refresh timing repair is accepted and `sfx-07` adds complete Stop occurrence metadata with 50/50 live checks; native Windows and full EventTime migration remain open. |
| P1 — High | [[wiki/todo/lintap-linux-process-command-line-quality]] | Promoted | Bounded procfs provenance/status, truncation and child-only clone attribution pass Linux acceptance; immutable exec argv and deterministic DBT selection remain open. |
| P1 — High (provisional) | [[wiki/diagnostic/duplicate-agent-id-and-os-family]] | Open | Replace hardcoded `windows` OS-family labels across canonical DBT models with platform-derived metadata and backward-compatible unknown handling. |
| P2 — Medium (provisional) | [[wiki/todo/linux-nfs-process-network-attribution]] | Open | Qualify why Linux process contexts, including SSH, appear on a shared TCP tuple to the NFS host; distinguish causal I/O attribution from socket ownership. |
| P2 — Medium | [[wiki/todo/canonical-process-owned-network-grains]] | Open | Reconcile documented process/network increment and connection grains; preserve metadata conflicts and process-observation semantics for reusable analytics. |
| P2 — Medium | [[wiki/todo/transformer-five-tuple-connection-port-key]] | Implemented; Windows acceptance deferred | .NET is the sole generator; gateways are metadata, loopback uses hostname context, non-loopback uses `public`, and DBT passthrough qualification passes. Release is a clean new-data cutover with no legacy/mixed-data requirement. |
| P2 — Medium (provisional) | [[wiki/todo/lintap-rpm-amazon-linux-2023]] | Open | Reproduce and classify the current Lintap RPM installation failure on AWS Amazon Linux 2023, then define and qualify the appropriate RPM/build target. |
| P2 — Medium (provisional) | [[wiki/todo/linux-interactive-session-feed]] | Open | Replace the barely acceptable Linux process-start activity proxy with a real interactive session/logon feed, preferring systemd-logind with a PAM fallback. |
| P2 — Medium (provisional) | [[wiki/todo/unify-lintap-runtime-and-etl-configuration]] | Open | Design one canonical operator-facing configuration to replace the split `lintap.env`/`ETLConfig.json` surfaces, with migration and no silent installer overwrite. |
| P3 — Low | [[wiki/todo/daily-compacted-tier]] | Open | Evaluate a verified `compacted2/dayPK` daily roll-up over completed hourly compacted data, with disjoint reader precedence and explicit late-data handling. |
| Untriaged | [[wiki/todo/raw-sensor-upload-time-partition]] | Implemented; endpoint verification pending | S3 now binds UTC upload-time keys with durable unresolved-attempt sidecars and exact-key HEAD validation; live endpoint qualification remains open. |
| Untriaged | [[wiki/todo/listening-socket-capture-and-modeling]] | Open | Investigate process-attributed listening-socket lifecycle capture and a downstream model distinct from peer-oriented connections; priority and platform scope remain open. |
| P1 — High | [[wiki/todo/test-suite-reorganization]] | Promoted | Phase 1 of [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief]]; first draft checked, broader cleanup and fresh-capture iterations remain open. Preserve collection counts and review evidence before merging or archiving cases. |
| P1 — High | [[wiki/todo/periodic-process-refresh-listing]] | Promoted | Linux `live-02` accepts repaired periodic output with null monotonic timing across all Refresh rows; native Windows acceptance remains open. |

## Related

- [[wiki/concept/feature-work-template]] — full feature-work artifact structure.
- [[wiki/concept/llm-assisted-feature-workflow]] — process for promoting an
  intake item into a deep dive.
