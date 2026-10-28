---
title: "POC Findings: PowerShell ETW Event Shapes"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/references.md
  - ../Wintap-Analytics/wiki/work/powershell-sensor/verification.md
policy: agent-editable
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/findings.md
tags: [feature-work, powershell, etw, event-shapes, findings]
---

# PowerShell ETW Findings

The inspected 60-second 5.1 capture (`a0c52268...`) contains 25,210 PowerShell events
plus two trace metadata records, with 89 reported losses; 23,717 events came from
overlapping Pester activity, so volume is not representative of manual use. Eleven
PowerShell IDs appeared: 7937=24,929, 4104=140, 4100=25, 4103=1, 7938=16, 7939=50,
7942=16, 16385=9, 40961=8, 40962=8 and 53504=8, all version 1. **4104** carries Int32
`MessageNumber`/`MessageTotal` and UnicodeString `ScriptBlockText`/`ScriptBlockId`/`Path`;
135 blocks were complete 1/1, five contained only fragment 3/3, and 67 paths were empty.
The operator's interactive `write-host hi` appears as a complete empty-path 4104 and
7937 start/stop in the same emitter/thread; only the 7937 pair shares runspace/activity
context, and no relevant 4103 binding appeared. **7937** distinguishes start/stop by
tasks 102/103, not ID alone; like 4100/4103/7938/7939, its `ContextInfo`, `UserData` and
`Payload` are strings, with host/runspace/pipeline/command/user values embedded in text.
Headers provide provider/ID/version, time, PID/TID, task/opcode/level/keywords and activity
context; they are not canonical Wintap identities. Native templates confirm these types.
The lone decoder error (15005) concerns partition metadata, not PowerShell payloads;
missing fragments have no established cause. Focused export retains all 140 records
without rewriting originals. Script observation does not prove execution, keystrokes,
remoting or one record per repeat; PowerShell 7, logging baselines and lossless coverage
remain unverified. Full raw evidence stays local; [[wiki/work/powershell-sensor/verification]]
distinguishes inspected data from the operator-reported newer rerun.
