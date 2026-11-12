---
title: "Historical Verification: PowerShell ETW POC"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/brief.md
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/verification.md
tags: [feature-work, powershell, etw, verification]
---

# Historical PowerShell ETW POC Verification

> This page records the October native-tool capture and wrapper tests only. It
> does not verify the later Wintap sensor. The integrated sensor's code-level
> test coverage and optional smoke harness are listed in
> [[wiki/component/powershell-sensor]], but were not run for this documentation
> update; live ETW load/loss and host logging-policy qualification remain open.

Evidence chain: [[wiki/work/powershell-sensor/P0.1-native-etw-wrapper]] (20 tests),
[[wiki/work/powershell-sensor/Patch-P0.1a-file-entry-default]] (23 tests; fixes the
operator's pre-capture -File empty-path failure), and
[[wiki/work/powershell-sensor/P0.2-focused-scriptblock-output]] (35 tests; full commands/
outputs retained). Native capture calls are mocked in unit tests; actual unprivileged
entry reaches the elevation guard. The first operator 5.1 capture was independently
inspected: start/stop/decode succeeded, 25,212 records matched the summary, 89 events
were lost, one metadata record failed decoding, and PowerShell payloads had no
processing errors; Pester overlap dominated traffic. The confirmed interactive
`write-host hi` appears in complete empty-path 4104 and 7937 start/stop context.
Post-filter validation keeps all 140 script-block events, including five incomplete
fragments and 67 empty paths, while preserving SHA-256/size/mtime of five originals;
see [[wiki/work/powershell-sensor/findings]]. On 2026-10-28 the operator reported
"cool that works" after the focused-output change: rerun success is operator-reported,
not independent inspection of its newer dataset or formal POC acceptance. PowerShell 7,
logging baselines, Ctrl+C and general input/execution coverage remain unqualified;
no policy, provider-traffic or loss reduction is claimed. At the time, the next POC
step was review of the findings and recording any acceptance anchor in
[[wiki/work/powershell-sensor/metrics]].
For the later sensor's event contract and DBT status, see
[[wiki/event_type/powershell-events]].
