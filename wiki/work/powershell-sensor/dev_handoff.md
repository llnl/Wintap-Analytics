---
title: "Execution Handoff: PowerShell ETW POC"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/brief.md
  - ../Wintap-Analytics/wiki/work/powershell-sensor/references.md
  - ../Wintap-Analytics/wiki/work/powershell-sensor/verification.md
policy: agent-editable
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/dev_handoff.md
tags: [feature-work, powershell, etw, handoff, poc]
---

# PowerShell ETW POC Handoff

Approved local native-tool scope, not Wintap integration: from the elevated operator's
`%TEMP%\opencode\powershell-etw-poc` directory run
`powershell -NoProfile -File Capture-PowerShellEtw.ps1`; defaults are Windows PowerShell,
60 seconds, all keywords/level 255, system clock and 64 MB sequential ETL. Optional
`-Provider PowerShellCore`, `-DurationSeconds` (1–120), and an existing `-OutputDirectory`
remain supported. Generate synthetic activity separately; do not run developer tests
during capture. Inspect `scriptblocks.xml` and `focus-summary.txt`; retain original
ETL, full `events.xml`, `summary.txt`, `commands.log` and `recovery.txt`. The filter keeps
whole selected-provider 4104 events, including empty paths, fragments, duplicates and
error evidence; it neither assembles code nor reduces traffic/loss. Preserve owned-session
cleanup, original errors, body-initialized default paths and streaming/atomic XML output;
never bypass elevation/policy or alter host configuration. Validation command:
`$r = Invoke-Pester -Script .\Capture-PowerShellEtw.Tests.ps1 -PassThru; if ($r.FailedCount -gt 0) { exit 1 }`.
Build/P0.1a/P0.2 evidence is in [[wiki/work/powershell-sensor/verification]]; latest suite
35/35, with original-capture preservation verified. The operator reports rerun success;
next is findings review, not automatic recapture or integration. Code remains temporary,
raw data private, and prior Wintap audit review was denied/not performed; review conventions
and obtain authorization before future sibling-code work.
