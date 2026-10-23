---
title: "Interview: Fix Hardcoded AgentId"
type: concept
confidence: high
grounded_by:
  - ../wintap/linux-tcp-investigation-2026-06.md
  - ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs
policy: agent-editable
last_validated: 2026-10-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: network
audience: mixed
status: draft
source_paths: wiki/work/fix-hardcoded-agentid/interview.md
tags: [feature-work, agentid, linux, tcp]
---

# Feature Interview: Fix Hardcoded AgentId

## Initial Idea

Start a guided feature for “fix hardcoded agentid,” migrate the misplaced Linux
TCP investigation into the Analytics wiki, validate its claims, and address its
issues on a new branch.

## Context Established Before Questioning

- The source memo is a dated June 2026 Wintap investigation.
- `TcpConnectionSerializer` still writes the literal `grantj` AgentId.
- Only `wintap/wintapstate.json` is tracked; the repository-root state file is
  untracked runtime state.
- Current sources already include explicit network-program attachment,
  socket-keyed TCP PID attribution, protocol fallback, and default-enabled
  ProcessRundown.

## Decisions

- Create `fix/hardcoded-agentid` branches in both Wintap-Analytics and Wintap.
- Treat the work as the full memo scope, but validate existing TCP fixes rather
  than reimplementing them.
- Restore TCP AgentId propagation, correct TCP/UDP Linux watchdog wording, and
  reset the tracked state template only.
- Investigate a bounded negative resolver cache only after profiling shows
  repeated lookup cost.
- Migrate the memo as a historical diagnostic page with a current-status
  addendum, not as an unqualified current guide.

## Constraints

- Leave untracked root runtime state untouched.
- Do not duplicate the already-fixed Parquet null/logging or ProcessRundown
  work.
- Live kernel validation requires a Linux host with deployment access; host
  details were not supplied during the interview.

## Deferred / Open Questions

- Linux host distribution/kernel, access method, and restart/bpftool authority.
- Whether profiling demonstrates a worthwhile bounded resolver negative cache.

## Playback Summary

Confirmed 2026-10-20: deterministic AgentId, state-template, and watchdog
defects are implementation work; existing network attachment/PID/rundown work
is validation work; live evidence remains an explicit closure gate.

## Sealed — human estimates

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available?**
**A:** “3 days”

**Q: With the AI workflow, on what date do you predict this feature will be
available?**
**A:** “1 day”
