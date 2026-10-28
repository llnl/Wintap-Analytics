---
title: "Verification: PowerShell ETW POC"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/brief.md
policy: agent-editable
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/verification.md
tags: [feature-work, powershell, etw, verification]
---

# PowerShell ETW Verification

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
no policy, provider-traffic or loss reduction is claimed. Next review findings before
integration and record any acceptance anchor in [[wiki/work/powershell-sensor/metrics]].
