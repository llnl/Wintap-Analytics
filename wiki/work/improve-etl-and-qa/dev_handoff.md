---
title: "Dev Handoff: Improve ETL and QA"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-etl-and-qa/verification.md
  - wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31.md
  - wiki/work/improve-etl-and-qa/esper-sender-path-analysis-2026-08-30.md
  - wiki/component/fileops-event-pipeline.md
  - wiki/component/process-table-retention.md
policy: agent-editable
last_validated: 2026-08-31
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/improve-etl-and-qa/dev_handoff.md
tags: [feature-work, dev-handoff, lintap, pidstat, memory, perf]
---

# Dev Handoff: Improve ETL and QA

## Copy/Paste Prompt

    Switch to code-development mode for improve-etl-and-qa.

    Read AGENTS.md and these artifacts before editing:
    - wiki/work/improve-etl-and-qa/implementation_plan.md
    - wiki/work/improve-etl-and-qa/verification.md
    - wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31.md
    - wiki/component/fileops-event-pipeline.md
    - wiki/component/process-table-retention.md

    Continue from the August 31 current state, not the superseded serializer or
    sender gates. Implement conservative process-exit plus age/capacity eviction
    for the FileOps FD-path cache, preserve telemetry fidelity, and repeat a
    unique-run-ID long comparison with exact windows and artifact hashes.

    Owning sibling commits are ../wintap c03d731..2d3f795,
    ../Lintap 1b23f77, and ../Wintappy a53cce6..e4b3bc3.

## Current State

- Wintappy's pidstat bronze/silver/gold path and canonical Marimo QA flow are
  implemented and exercised with non-empty data. Broader event-family cleanup
  and Analytics-side legacy conflict handling remain open.
- The Analytics `validation/perf-collection/` package writes raw-style procfs and
  structured `.NET` counter parquet. The focused root wrapper is the validated
  path for the root-owned `Lintap` service on `spk16`; every future run must use
  a unique `RUN_ID`.
- FileSerializer's five-second cadence alone was insufficient, but the later
  5,000-event high-water drain passed the controlled 6,000-file gate and the
  10h23m deployment with zero serializer backlog warnings.
- The exact `tenable-utils-L` pre-ring policy passed its controlled scan gate.
  It is a narrow operator policy, not a general claim about all Tenable work.
- The no-Tenable run then proved the pre-cache FileOps sender was unsustainable:
  run `lintap-perf-20260830-no-tenable`, exact UTC window
  `2026-08-30T21:49:06Z..22:49:05Z`, recorded `601126` sender drops while
  FileSerializer remained healthy. See [[no-tenable-run-analysis-2026-08-30]].
- Isolated NEsper testing ruled out Esper statement evaluation as the primary
  live ceiling. The empty broad subscriber route was removed, while outbound
  threading and context replacement were rejected. See
  [[esper-sender-path-analysis-2026-08-30]].
- A bounded 32,768-entry historical process-identity cache was deployed in RPM
  `lintap-0.3.4-1.el8.x86_64`. The installed DLL SHA-256 was
  `7bd7ab380ac07b004f04357e5bb46d23bf45f0bdca871949137b080cc7e9a235`.
- The cache passed 10h23m plus a 6,000-file recovery burst with zero sender,
  summary, aggregation, serializer, or File-send loss. Aggregate cache hit rate
  was `75.4%`; weighted sender latency was `560.6 us`, versus `5135.7 us` in the
  prior saturated run.
- Retrieved pidstat SHA-256
  `17e19df37746f2cb5f2126e79d6199c1ddecae2759e17f0c08bbc20d8b883230`
  showed stable CPU but post-warm-up RSS growth. FD-path entries grew
  `24 -> 11184`; level correlation with RSS was `0.929` overall and `0.938`
  after 22:00. This makes FD-path cache eviction the leading residual memory
  hypothesis, not a proven sole cause.

## Next Slice

Implement bounded FileOps FD-path state without weakening path or event
fidelity:

1. Add process-exit cleanup where identity is reliable.
2. Add conservative age and capacity bounds for orphaned entries.
3. Emit eviction reasons and cardinality counters in existing diagnostics.
4. Add short-lived-process, PID-reuse, active-FD, and capacity-pressure tests.
5. Re-run focused build/tests and the file-capture smoke.
6. Deploy only after review, then repeat a unique-run-ID long comparison against
   the August 31 evidence window.

Acceptance requires zero ring/sender/summary/serializer loss, FileOps count and
byte conservation, successful controlled recovery, bounded FD-path state, and
no regression in sender latency or historical identity-cache behavior.

## Evidence Discipline

- Do not use `/tmp` or `/var/log` as high-confidence frontmatter anchors.
- Record ephemeral paths only as artifact locators accompanied by SHA-256, run
  ID, host/PID, exact UTC/local windows, and the exact analysis command.
- Use [[historical-cache-overnight-validation-2026-08-31]] as the durable
  August 31 comparison record.
- Owning commits now exist: `../wintap@c03d731..2d3f795`,
  `../Lintap@1b23f77`, and `../Wintappy@a53cce6..e4b3bc3`.

## Non-Goals

- Do not redesign the QA notebook in the FD-cache slice.
- Do not enable adaptive sampling as a substitute for fixing bounded state.
- Do not increase queue caps to mask throughput or fidelity defects.
- Do not infer causality from level correlation alone.
- Do not modify sibling repositories without explicit authorization.

## Closeout

- Update `verification.md` with exact commands, hashes, windows, and results.
- Update the implementation-plan checklist accurately; partial canonical
  promotion must remain described as partial.
- Append a new `wiki/log.md` entry without rewriting earlier chronology.
- Replace sibling commit placeholders only with actual committed IDs.
