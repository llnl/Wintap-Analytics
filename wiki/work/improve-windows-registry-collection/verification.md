---
title: "Verification: Improve Windows Registry Collection"
type: concept
confidence: high
grounded_by:
  - ../wintap/developer_docs/audits/wrc-03-payload-decode-core.md
  - ../wintap/developer_docs/audits/wrc-04-capture-enablement-engine.md
  - ../wintap/developer_docs/audits/wrc-05-wintapmessage-registry-schema.md
  - ../wintap/developer_docs/audits/wrc-06-manifest-registry-sensor.md
  - ../wintap/developer_docs/audits/wrc-07-mask-canary-live-verification.md
  - ../wintap/developer_docs/audits/wrc-08-parquet-value-plumbing.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: mixed
status: reviewed
source_paths: wiki/work/improve-windows-registry-collection/verification.md
tags: [feature-work, registry, etw, windows-sensor, capture-mode, verification, live-run]
---

# Verification: Improve Windows Registry Collection

Verification record against the frozen acceptance criteria in
[[wiki/work/improve-windows-registry-collection/brief]] (frozen 2026-08-25).

> **Provenance note:** `/developer_docs/` is **gitignored** in the wintap
> repo — instruction and audit artifacts are local-only process files, not
> version-controlled. This page preserves the durable verification evidence;
> the audits remain the detailed local record.

## Unit audits (2026-08-25)

All six Developer units are implemented on branch `develop-wrc` — committed
as **`1f66a47`** ("Add wrc: manifest-only registry sensor via undocumented
capture-mode filter (wrc-01..08)", 32 files; single feature commit, added at
close-out) — with audits filed, each **Status: Complete** (verified on disk
2026-08-25):

- `../wintap/developer_docs/audits/wrc-03-payload-decode-core.md`
- `../wintap/developer_docs/audits/wrc-04-capture-enablement-engine.md`
- `../wintap/developer_docs/audits/wrc-05-wintapmessage-registry-schema.md`
- `../wintap/developer_docs/audits/wrc-06-manifest-registry-sensor.md`
- `../wintap/developer_docs/audits/wrc-07-mask-canary-live-verification.md`
- `../wintap/developer_docs/audits/wrc-08-parquet-value-plumbing.md`
  (added at close-out: 9/9 wrc-08 tests, 134/134 `Category~wrc`, 299/299
  full suite; the standalone NEsper compile smoke test passed — the
  documented fallback was not needed)

The recurring root-solution `MSB4249` Wintap-Workbench deviation appears in
the wrc-06/wrc-07/wrc-08 audits; the documented project-scoped fallback
builds passed. Per-unit test commands and counts live in the audits.

## Live verification — Architect-run record (2026-08-25)

Performed by the **Architect** on the lab host, branch build (`develop-wrc`),
per the wrc-07 evidence contract
(`../wintap/developer_docs/instructions/wrc-07-mask-canary-live-verification.md`
§Implementation Note 3). Results recorded **verbatim**:

**Registry:**

- 0x5300 mask confirmed.
- 30-second serialization interval confirmed.
- No queue-limit warnings or dropped events.
- Batches stayed manageable: generally 500–1,100 events, with bursts of 3,369 and 6,162.
- Canary remained healthy.
- Five-minute capture reassertion completed normally.
- No capture-loss or recovery-failed messages.
- Remaining issue: process attribution is still bursty. Unresolved registry events ranged from 13/1,314 to 239/1,839, often dominated by one short-lived PID.

**Process (observed in the same run):**

- Snapshot and reconciliation completed normally.
- SID extraction, command-line capture, and manifest metrics show no errors.
- Only the initial synthetic refresh was reported unresolved.
- stop_without_start rose from 3 to 19, indicating occasional stop events without a matching process record. Warrants monitoring; not currently severe.

**Architect's verdict (verbatim):** "Registry throughput and canary health
now look good. The queue/flush changes solved the observed data-loss problem.
The remaining concern is short-lived-process attribution rather than registry
capture or serialization."

## Evidence-contract coverage (wrc-07 §3, items 1–6)

Honest accounting against the six required items. Missing items are recorded
as **missing data** per the mini-lab never-gates rule — never invented, never
a gate. Engineer inferences are labeled as such and are **not** part of the
Architect's verbatim record above.

| # | Required evidence (wrc-07 §3) | Status | What the record contains / what is missing |
|---|---|---|---|
| 1 | Config under test: branch/commit; mask in effect (0x5300 + a second short 0x5700 window); capture filter asserted; re-assert interval/count | **Partial** | Branch build on `develop-wrc`; 0x5300 mask confirmed; five-minute capture reassertion completed normally. Missing data: commit hash not recorded; the `CollectRegistryRead=true` → 0x5700 second window was not reported; no explicit enabler assert-log line or re-assert count quoted. |
| 2 | Event-rate evidence: ≥3 `EventsPerSecond` samples over ≥15 minutes | **Missing data** | Not recorded. Volume proxy present: batch sizes at the confirmed 30 s serialization interval — generally 500–1,100 events, bursts 3,369 and 6,162. |
| 3 | Explicit comparison to both baselines (probe5 ≈16k/s firehose; probe8 ≈31/s masked) | **Missing data** (as an explicit statement) | Derivable from the item-2 proxy — see Engineer inference below — but no measured-rate-vs-baselines statement was recorded. |
| 4 | Correctness spot-check: six-type writes + overwrite + delete from a non-Wintap elevated shell, emitted messages verified (paths, decoded Data, PreviousData, `PreviousDataType=NONE` on first writes) | **Missing data** | Outcome not reported in this run's record. |
| 5 | Canary health: ≥1 healthy cycle; zero false loss detections; (optional) deliberate-clear demo | **Covered** | Canary remained healthy over the observation window; no capture-loss or recovery-failed messages (zero false detections). The optional deliberate-clear demonstration was not run (Architect's call per the contract). |
| 6 | Session integrity: ETW events-lost counter (probe8 baseline 0) + one-line CPU/memory observation | **Partial** | No dropped events and no queue-limit warnings recorded. Missing data: no numeric events-lost counter; no CPU/memory one-liner. |

**Engineer inference (rate proxy, clearly separated from the Architect's
record):** typical batches of 500–1,100 events per 30 s serialization
interval ≈ **17–37 events/s** typical steady state — consistent with probe8's
~31/s masked baseline and orders of magnitude below probe5's ~16k/s firehose.
<!-- SYNTHESIS: arithmetic on the Architect-reported batch sizes and 30 s interval; not a measured EventsPerSecond sample -->

## Criteria impact notes

- Nothing in the record **contradicts** the frozen criteria; the gaps above
  are missing data, not conflicts.
- Criterion 2 (capture-loss detectable/recoverable, re-assert): supported —
  canary healthy, reassert completed normally, no recovery-failed messages.
- Criterion 6 (explicit mask + measured event-rate/overhead evidence):
  configuration half satisfied (0x5300 confirmed); measurement half is
  partial per items 2/3 above.
- Criterion 8 (live verification recorded in verification.md): this record.
- The remaining attribution burstiness is **process-tree/attribution-domain**,
  not registry capture or serialization (Architect's verdict); queued as
  sweep items 13–14 in [[wiki/diagnostic/windows-sensor-sweep-queue]].

## Close-out addendum (2026-08-25): wrc-08 live smoke test — Architect-verbal acceptance

Per the wrc-08 instruction (§Architect Verification Addendum), the owed
evidence was a single live-data DuckDB query showing the three new columns
(`Reg_DataType`, `Reg_PreviousData`, `Reg_PreviousDataType`) populated. The
Architect ran the live smoke test on 2026-08-25 and accepted it;
**verdict, verbatim: "smoke test looks fantastic."**

Honest accounting per the never-gates rule: the DuckDB query output itself
was **not pasted into the close-out session** — the acceptance is recorded
here as **Architect-verbal, with the query evidence as missing data** (never
invented, never a gate). The unit-test layer (18-column contract, enum-name
rendering, first-write `NONE` encoding, null guards — 9/9 in the wrc-08
audit) plus the verbal acceptance stand as the recorded evidence.

## Availability anchor — FINALIZED at close-out (2026-08-25)

The Architect **accepted the feature against the frozen brief criteria on
2026-08-25**. The availability anchor is the Architect-run live
verification of 2026-08-25 (the wrc-07 record above) **together with the
wrc-08 live smoke test** (addendum above) — the first Architect-accepted
dated demonstration of the frozen criteria on a branch build.
**`ts_available` = 2026-08-25**; lead time from the 2026-08-25 open is
same-day, recorded as the minimum 1 calendar day in
[[wiki/work/improve-windows-registry-collection/metrics]] (the protocol is
silent on same-day features; the choice is stated there). Feature closed
2026-08-25.
