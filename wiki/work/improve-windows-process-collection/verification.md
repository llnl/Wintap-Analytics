---
title: "Verification: Improve Windows Process Collection"
type: concept
confidence: high
grounded_by:
  - ../wintap/developer_docs/audits/wpc-06-wire-in-removal.md
  - ../wintap/developer_docs/audits/wpc-07-boot-etl-coverage.md
  - ../wintap/developer_docs/audits/wpc-09-bug-sweep.md
  - ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/BootProcessTraceHelper.cs
policy: agent-editable
last_validated: 2026-08-19
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: developer
status: draft
source_paths: wiki/work/improve-windows-process-collection/verification.md
tags: [feature-work, verification, process-events, etw, windows-sensor, wpc]
---

# Verification: Improve Windows Process Collection

## Wiki Starting Point

Use this page as the closeout verification record for the
improve-windows-process-collection feature (`wpc`, closed 2026-08-19). It
captures the accepted manual validation evidence in place of the skipped
formal wpc-08 harness, the final unit-test/build state, and the boot-replay
validation that resolved the wpc-09 audit's pending item. Durable semantics
are promoted to [[wiki/event_type/process-events]]; per-unit implementation
evidence lives in `../wintap/developer_docs/audits/wpc-01…wpc-09`.

## Code State at Close

All units landed on wintap branch `develop-dave`:

- `9862131` — wpc-01 SID extraction helper (2026-08-17)
- `b500966` — wpc-02 sensor core + wpc-03 snapshot refresh (2026-08-17)
- `9009d1d` — wpc-04 field enrichment (2026-08-17)
- `0f273e0` — wpc-05 stop-metrics merge + wpc-06 wire-in/legacy removal (2026-08-17)
- `19e89dc` — wpc-07 boot ETL coverage + wpc-09 bug sweep with boot-start fixes (2026-08-19)

wpc-08 (formal validation harness) was skipped by Architect decision
2026-08-18 (see Skip Rationale below). wpc-09 was the final code unit.

## Test Commands

Run from `../wintap` (project-scoped commands are the documented fallback for
the pre-existing solution-level `Wintap-Workbench` `MSB4249` issue):

```powershell
dotnet build "wintap\Wintap.csproj" -c Release
dotnet test "tests\Wintap.Tests\Wintap.Tests.csproj" --filter "Category~wpc"
dotnet test "tests\Wintap.Tests\Wintap.Tests.csproj"
```

## Unit Test / Build State at Close

Per the wpc-09 audit (`../wintap/developer_docs/audits/wpc-09-bug-sweep.md`),
re-verified green 2026-08-19:

- `dotnet build "wintap\Wintap.csproj" -c Release`: **0 errors** (708
  pre-existing package/analyzer/platform-compatibility warnings).
- `Category=wpc-09`: 19/19 passed.
- `Category~wpc` (whole feature): **64/64 passed**.
- Full test project: **65/65 passed**.

## Accepted Manual Validation Evidence

The Architect accepted manual validation in place of the formal wpc-08
harness. Evidence, in chronological order:

### wpc-06 elevated smoke — PASS (2026-08-17)

Architect-executed elevated manual smoke after wire-in and legacy-sensor
removal (full evidence in
`../wintap/developer_docs/audits/wpc-06-wire-in-removal.md`): wire-in
ordering confirmed (`WindowsProcessSensor` starts first), Start/Stop/Refresh
parquet flow observed, parseable interval/shutdown QA counter lines (e.g.
`snapshot_count=489`). Audit-policy-off evidence waived by the Architect —
the Security-log dependency was removed outright with the legacy sensors.
Out-of-scope observations recorded in
[[wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17]].

### wpc-07 deploy / reboot / overnight run — PASS (2026-08-18)

Architect published and deployed the wpc-07 build locally, rebooted, and ran
the service overnight. Accepted validation summary: full process tree reached
back to kernel-era roots, usernames were present on all reviewed records, and
the overnight run was stable. This is the manual evidence that motivated the
wpc-08 skip decision. Four findings from the same smoke were assigned to
wpc-09 (boot-trace arm-on-enable gap, disarm-on-disable gap, missing-parent
warnings, DuckDB command-line parser errors).

### wpc-09 sweep findings — fixed (2026-08-18, commit 19e89dc)

All four overnight-smoke findings were resolved (evidence in
`../wintap/developer_docs/audits/wpc-09-bug-sweep.md`):

- Boot-trace lifecycle corrected: enabled startup re-arms immediately
  (fixing the enable-then-restart arming gap), disabled startup still runs
  owned-session stop/disarm cleanup, and foreign "NT Kernel Logger" sessions
  are never stopped or disarmed.
- DuckDB Start/Refresh process inserts parameterized; hostile command lines
  (unterminated quotes, embedded quotes) persist exactly, with regression
  tests in `ProcessResolverTests.cs`.
- Missing-parent warning triaged from logs as expected best-effort
  attribution (parents unavailable/exited during snapshot emission), kept
  rate-limited once per parent PID and annotated with the unknown-parent
  sentinel.
- QA-counter logger attribution fixed (named logger method replaces the
  constructor lambda).
- Shared `/tmp/lintap-data` defaults removed; unconfigured deployments now use
  the platform roots owned by `Env.cs`, with pure precedence/platform tests.

### Final overnight smoke-test with boot replay — PASS (2026-08-18 → 2026-08-19)

Architect ran an overnight smoke-test after the wpc-09 bug-fix round; result
good. **Boot replay is confirmed end-to-end**: Global Logger armed at
shutdown, owned-session stop/disarm at startup, and boot events replayed
into the live stream. This resolves the wpc-09 audit's pending item
("boot-session stop/disarm/replay validation remains pending") — recorded
here rather than in the audit because audits are Developer-owned artifacts.
The earlier blocker was an external `Code42-AAT` process holding the DuckDB
event store open; the wpc-09 bug-fix round also fixed the Windows runtime
data-root fallback that contributed (see `Env.cs`/`ConfigManager.cs` changes
and `RuntimeDataRootTests.cs` in commit `19e89dc`).

## wpc-08 Skip Rationale

The formal Windows validation harness (wpc-08, slice 3 of the implementation
plan) was skipped by Architect decision on 2026-08-18, without renumbering.
Rationale: the manual slice-2 validation already demonstrated the feature's
core acceptance behaviors — complete lineage to kernel-era roots, user
identity on all reviewed records, and overnight stability — and the
subsequent wpc-09 sweep plus the final boot-replay-confirming overnight smoke-test
closed the remaining runtime unknowns. The harness remains available as
future work if reproducible scoring artifacts (start/stop coverage rates,
PidHash stability matrices, identity-context runs) are ever needed; the
sensor-neutral harness design in
[[wiki/work/lintap-process-creation-validation/validation-harness-design]]
is the starting point.

## Known Gaps / Follow-Ups

- Measured production-load rates for `cmdline_empty` / `cmdline_peb_recovered`
  and null/malformed SID counters were deferred with the wpc-08 skip; the QA
  counters expose them from any running instance when wanted.
- Out-of-feature follow-up candidates remain open in
  [[wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17]]:
  SensSensor null-value load failure and the missing `SignedS3UrlAdapter`
  upload adapter. Both are pre-existing and outside this feature.
