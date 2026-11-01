---
description: Implement and verify one bounded pidstat Go rewrite unit
agent: build
subagent: false
---

Implement and test the pidstat collector work requested here: $ARGUMENTS

Load the pidstat-loop skill. Follow its observe → hypothesize → change → verify
procedure in this session. Use validation/pidstat-loop/evidence.py for actual
Python reference capture, exact Parquet comparison and static-binary checks.
Read the current verification record before resuming. Confirm Lintap/VM scope
before edits or guest operations. Stop after fpc-01 for human review/approval;
do not launch fpc-02 automatically. No outer agent runner is needed.
