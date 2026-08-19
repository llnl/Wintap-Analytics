---
title: "wpc-06 Smoke-Run Out-of-Scope Observations"
type: concept
confidence: high
grounded_by:
  - ../wintap/developer_docs/audits/wpc-06-wire-in-removal.md
  - ../wintap/developer_docs/audits/wpc-07-boot-etl-coverage.md
  - ../wintap/developer_docs/audits/wpc-09-bug-sweep.md
policy: agent-editable
last_validated: 2026-08-19
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/developer_docs/audits/wpc-06-wire-in-removal.md; ../wintap/developer_docs/audits/wpc-07-boot-etl-coverage.md
tags: [feature-work, process-events, etw, windows-sensor, follow-up, wpc]
---

# 2026-08-17 wpc-06 smoke-run out-of-scope observations

## 2026-08-18 overnight smoke validation and wpc-09 sweep findings

The Architect manually validated slice 2 on 2026-08-18 after a published local
build, reboot, and overnight service run. Positive validation summary: the
captured process tree reached back to kernel-era roots, usernames were present
on all reviewed records, and the overnight run was stable.

The same smoke produced four findings now assigned to final code unit `wpc-09`
(minor bug sweep):

1. **Boot-trace arming did not trigger from config alone.** The Architect set
   `EnableBootProcessTrace = True` in `Wintap.dll.config` and restarted Wintap,
   but the Global Logger registry values were never written and the boot trace
   did not arm. Manual registry setup was required; after that, the boot replay
   path worked end-to-end. Initial code inspection supports the hypothesis that
   `BootProcessTraceHelper.ArmForNextBoot()` is currently called only from
   `WindowsSubscriptionManager.Stop()`, while `Properties.Settings.Default` is
   loaded at process start. An enable-then-restart therefore leaves the stopping
   instance holding `False` in memory and skips arming, so the first boot after
   enabling is not covered.
2. **Disarm gap on disable.** `WindowsSubscriptionManager.Start()` only calls
   `StopOwnedBootSessionDisarmAndGetReplayPath()` when the setting is true. If a
   user arms the feature, then changes the setting to false, startup never runs
   the owned-session stop/disarm cleanup. The Global Logger can remain armed on
   every boot while Wintap no longer stops/replays the owned kernel session.
3. **Missing parent-process warnings.** A handful of `Could not resolve parent
   process` warnings appeared during the overnight run. These may be the same
   early-lifetime races noted below in item 3, or may represent genuinely
   unresolvable parents that exited before Wintap observed them. `wpc-09` should
   triage from Wintap logs first, then either fix a concrete resolution gap or
   rate-limit/annotate the warning if expected behavior is confirmed.
4. **Process-name / DuckDB command-line parsing errors.** A couple of
   process-name parsing errors appeared during the overnight run, possibly the
   same root as the DuckDB unterminated-quote parser errors below in item 4.
   `wpc-09` should triage from logs and, if the root is the DuckDB insert path,
   fix parameterization or escaping for command lines rather than sanitizing the
   telemetry data.

Items intentionally **not** in `wpc-09`: SensSensor null-value load failure
(pre-existing, unrelated to the process path) and missing `SignedS3UrlAdapter`
(deployment/config gap in the upload path).

During the Architect-executed elevated manual smoke run that closed wpc-06
(PASS, 2026-08-17; full evidence in
`../wintap/developer_docs/audits/wpc-06-wire-in-removal.md`, "Manual smoke
results"), several warnings were observed that are **out of scope for the
improve-windows-process-collection feature** but are recorded here as future
follow-up candidates. None affected the wpc-06 pass criteria.

## Follow-up candidates

1. **SensSensor load failure** — `SensSensor problem loading sensor: Value
   cannot be null` at startup. Pre-existing sensor-loading defect unrelated to
   the process path.
2. **Missing `SignedS3UrlAdapter`** — upload adapter not found at runtime.
   Likely deployment/config gap in the ETL upload path rather than a code
   regression.
3. **Parent-process resolution warnings** — several `Could not resolve parent
   process` warnings during live collection. Worth checking against the
   wpc-08 lineage-accuracy harness runs before treating as a defect; may be
   normal early-lifetime races.
4. **DuckDB unterminated-quote parser errors** — DuckDB statement parse errors
   on command lines containing unterminated quoted strings. Suggests a
   parameterization/escaping gap somewhere in the DuckDB insert path for
   process command lines.
5. **Cosmetic: QA counter logger tag** — interval/shutdown QA counter lines are
   attributed to `[WindowsProcessSensor..ctor]` instead of the actual emitting
   method. Cosmetic only; proposed as an optional one-line rider in the wpc-07
   instruction rather than a separate unit.

## Disposition

- Item 5 is offered to the Architect as an optional wpc-07 rider.
- Items 1–4 are candidates for separate follow-up units or issues outside this
  feature; none block slice 2 (wpc-07) or slice 3 (wpc-08).

### Final disposition at feature closeout (2026-08-19)

The wpc-09 bug sweep (wintap develop-dave 19e89dc) resolved all four
2026-08-18 overnight findings: boot-trace arm-on-enable and disarm-on-disable
lifecycle gaps fixed with foreign-session safety, missing-parent warnings
triaged as expected best-effort attribution and annotated, DuckDB
command-line parser errors fixed via parameterized inserts, and the cosmetic
QA-counter logger tag fixed. A follow-up overnight smoke (2026-08-18→19)
passed with boot replay confirmed end-to-end; see
[[wiki/work/improve-windows-process-collection/verification]].

Remaining open items from the original follow-up-candidates list are outside
this (now closed) feature and stay future candidates: **SensSensor null-value
load failure** (item 1) and **missing `SignedS3UrlAdapter`** (item 2). Items
3–5 are closed by wpc-09.
