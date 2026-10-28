---
title: "Audit Artifact: Patch P0.1a File Entry Default"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/dev_handoff.md
  - ../Wintap-Analytics/wiki/work/powershell-sensor/verification.md
policy: agent-editable
last_validated: 2026-10-28
repo_scope: Wintap-Analytics
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/Patch-P0.1a-file-entry-default.md
tags: [feature-work, powershell, etw, audit]
---

# Audit Artifact: Patch P0.1a File Entry Default

**Date:** 2026-10-28
**Instruction:** `wiki/work/powershell-sensor/dev_handoff.md` — Patch P0.1a
**Status:** Complete

## Scope Implemented
- Fixed Windows PowerShell 5.1 advanced-script `-File` defaults by resolving the output directory after binding; preserved explicit options, rejected empty paths and added capture-free fresh-process regressions.

## Files Created
- `wiki/work/powershell-sensor/Patch-P0.1a-file-entry-default.md`
- Temporary `Probe-ParameterDefault.ps1` reproducer, removed after diagnosis.

## Files Modified
- `<approved-temp>/opencode/powershell-etw-poc/Capture-PowerShellEtw.ps1`
- `<approved-temp>/opencode/powershell-etw-poc/Capture-PowerShellEtw.Tests.ps1`
- `<approved-temp>/opencode/powershell-etw-poc/README.txt`
- `wiki/work/powershell-sensor/dev_handoff.md`
- `wiki/work/powershell-sensor/implementation_plan.md`
- `wiki/work/powershell-sensor/verification.md`
- `wiki/index.md`
- `wiki/log.md`

## Tests Run
- Working directory: approved temporary `opencode/powershell-etw-poc` directory.
- `$r = Invoke-Pester -Script .\Capture-PowerShellEtw.Tests.ps1 -PassThru; if ($r.FailedCount -gt 0) { exit 1 }`
- `. .\Capture-PowerShellEtw.ps1; if (Test-PocAdministrator) { throw 'Refusing to run the unprivileged smoke test elevated.' }; $output = & powershell.exe -NoProfile -File .\Capture-PowerShellEtw.ps1 2>&1; $exitCode = $LASTEXITCODE; if ($exitCode -ne 1 -or ($output | Out-String) -notmatch 'Capture requires an elevated PowerShell prompt') { throw "Unexpected direct-file smoke result: exit $exitCode; $output" }; 'PASS: actual powershell -File launch reaches the elevation guard and exits 1 without capture.'`
- `git diff --check` in Wintap-Analytics for tracked documentation whitespace.

## Test Results

Full final Pester output:

```text
Describing PowerShell ETW native-tool wrapper
 [+] refuses non-elevated execution before native calls or output creation 1.02s
 [+] requires an existing output directory 100ms
 [+] resolves the script directory before dispatch under powershell -File 423ms
 [+] preserves an explicit output path and options under powershell -File 365ms
 [+] rejects an explicitly empty output path at parameter binding 20ms
 [+] rejects durations outside 1 to 120 seconds and unknown providers 27ms
 [+] captures Windows PowerShell with wide keywords, debug-capable level and bounded wait 283ms
 [+] selects the PowerShell Core provider without installing or registering it 69ms
 [+] isolates successive captures in fresh directories and sessions 117ms
 [+] does not modify or stop an existing session 36ms
 [+] does not stop or decode when session creation fails 41ms
 [+] stops an owned session when the active-session query fails 55ms
 [+] stops an owned session after a wait failure and preserves the original error 66ms
 [+] attempts cleanup if logging fails after successful session creation 74ms
 [+] reports stop failure with recovery instructions and does not decode 65ms
 [+] reports a still-active session after a successful stop command 69ms
 [+] reports missing ETL rather than claiming an empty successful capture 64ms
 [+] preserves ETL when decoding fails 73ms
 [+] requires XML output even when the decoder returns success 70ms
 [+] requires summary output even when the decoder returns success 78ms
 [+] preserves both the capture error and cleanup error 61ms
 [+] reads actual provider metadata without starting a capture 200ms
 [+] preserves a nonzero native exit code and diagnostic output 61ms
Tests completed in 3.45s
Passed: 23 Failed: 0 Skipped: 0 Pending: 0 Inconclusive: 0
```

Actual-file smoke output:

```text
PASS: actual powershell -File launch reaches the elevation guard and exits 1 without capture.
```

Tracked documentation whitespace check: no output, exit 0.

## Behavioral Notes
- Reproduced empty parameter default/nonempty body script root under both `powershell -File` and `powershell -f`; new default/empty-path regressions failed before correction (21 pass / 2 fail), exposing function-only tests' explicit-path coverage gap.
- Fresh-process tests use a local production-code copy with capture dispatch stubbed, leaving parameters/body/entry unchanged and adding no production admin bypass; actual unmodified-file smoke verifies only non-elevated refusal, not live capture.
- Empty-path failure occurs before session creation, requiring no cleanup; providers, native flags, duration, policy and dependencies are unchanged.

## Deviations From Instruction
- None

## Follow-up Notes
- Retry the local script elevated; this patch completes only the fix, not live capture, decoding or event-shape acceptance.
