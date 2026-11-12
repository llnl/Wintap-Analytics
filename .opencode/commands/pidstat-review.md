---
description: Review pidstat source and real Python/Go parity evidence without repairs
agent: plan
subagent: false
---

Review the pidstat collector unit and evidence described here: $ARGUMENTS

Read wiki/work/fix-pidstat-collector/{brief,implementation_plan,verification}.md
and validation/pidstat-loop/README.md. Inspect the actual source diff, recorded
commands, reference provenance, decoded Python/Go rows and comparison reports.
Report unresolved findings, missing evidence, and a proceed/repair/blocked
recommendation. Do not change collector code, thresholds, reference results,
services or data. Run this command in a NEW OpenCode session when a fresh review
is requested; it does not itself create a separate session. Human approval is
still required before fpc-02. Synthetic fixtures or readability alone cannot
establish real Python parity.
