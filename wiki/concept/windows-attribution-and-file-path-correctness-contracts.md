---
title: "Windows Attribution and File-Path Correctness Contracts"
type: concept
confidence: low
grounded_by: []
policy: agent-editable
last_validated: 2026-10-19
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ""
tags: [wintap, windows-sensor, process-attribution, file-paths, testing, historical-summary]
---

# Windows Attribution and File-Path Correctness Contracts

Sanitized historical contracts retained before developer-archive deletion. Source references are intentionally omitted; statuses below reflect the reviewed records, not current-code verification or new implementation authorization. Results are preserved in [[wiki/diagnostic/windows-attribution-validation-executive-summary]].

## Accepted contracts

- **Measurement:** `process_unresolved` means an unknown owner name **or** the unknown-process hash sentinel. It does not measure wrong-but-resolved ownership, parent linkage, or event loss. Divide failures by completed evaluations of that check, not Parquet rows. Overall rates use summed counts; empty intervals are `n/a`. Concurrent reporting snapshots are not atomic cohorts.
- **Acceptance:** File and Registry each require **strictly below 5% unresolved over a fresh-start 24-hour cohort**, including startup. Restart resets the cohort; short runs do not satisfy the gate. Minimum workload volumes remain unspecified.
- **Identity:** Preserve an issued identity for the same process instance; PID reuse creates a separate identity. ETW occurrence time and OS creation time need not agree. Greater precision does not establish a safe matching tolerance or justify renaming published identities.
- **Windows maintenance remediation:** Disable continuous stale-open reconciliation, including inferred closure and hash repair, even if the former override requests it. Retain explicit Start/Stop handling, startup recovery, closed-history cleanup, heartbeat, and non-Windows behavior. Tradeoff: missed Stops can retain open rows and ancestors; bounded caches do not prove bounded database growth.
- **Approved owner routing:** Use active cache → historical cache → database for Windows non-Process messages in normal EventChannel processing. Only File retains its existing prepopulated-identity exception. Process registration/parents, unresolved fallback, health ordering, non-Windows behavior, actual MemoryMap direct egress, and direct-Parquet bypass remain unchanged.

## Reported implementation to protect with regression tests

- **Lifetime queries:** Both durable lookups bind typed PID and UTC event-time parameters rather than millisecond-formatted strings. Preserve inclusive lifetime bounds, newest-generation ordering, maintenance, and live fallback. Test sub-millisecond boundaries, time-kind handling, and cold/warm caches. This precision fix does not settle cross-source identity matching.

## Validation rules and open work

- Establish child identity independently and confirm actual child-write coverage. Background I/O on the same file is not automatically misattribution. Early exit does not guarantee historical-cache coverage; test that path deterministically.
- Retrieve sampled executable metadata by **attributed hash plus PID**, without falling back to the current PID occupant. Samples establish plausibility, not an independent ownership error rate. Keep `INCONCLUSIVE` distinct from `PASS`.
- Preserve outstanding checks for cache/durable newest-generation disagreement, correction/publication cache coherence, concurrent inspection/reporting, and exception-counter accounting. Replay/overlap/publication-race scenarios were deferred, not proven safe.
- Sustained Registry attribution, missing/delayed lifecycle evidence, and validator cleanup reliability remain unresolved. **Proposed persistence validation** should use finalized, run-scoped output; distinguish missing events, wrong owners, and broken linkage; join by agent/PID/hash; and use File occurrence ranges rather than serializer timestamps.

## Approved FILE-path design — implementation unverified

- Normalize once before emission, grouping, hashing, and output. Prefer valid drive/UNC access paths, including directory mounts; otherwise preserve native semantics. Never invent a drive mapping. Snapshot conversion requires a mapping to that snapshot, not its live volume.
- Use a FILE-specific immutable mapping snapshot with a **60-second monotonic lease** and bounded single-flight demand refresh. No native discovery or per-file opens on the event thread; do not reuse the legacy fabricated-drive fallback.
- Use invariant lowercase and remove the second culture-sensitive serializer lowercase operation **Windows-only**. Lowercasing loses case-sensitive distinctions; current mappings cannot reconstruct historical topology. Changed paths affect grouping/hashes without historical backfill. Process executable-path enrichment is a separate concern.
