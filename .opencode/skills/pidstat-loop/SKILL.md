---
name: Pidstat Loop
description: Implement the compatibility-preserving Go pidstat rewrite with real Python evidence, bounded repair iterations and a human fpc-01 checkpoint
---

# Native OpenCode pidstat loop

All paths below are relative to the **Analytics project root**, not this skill
directory. Use the built-in Build agent in the current session. The evidence
utility runs one deterministic experiment; it does not call an LLM or iterate.

## Grounding and scope

Read `wiki/work/fix-pidstat-collector/{brief,implementation_plan,verification}.md`,
`validation/pidstat-loop/README.md`, relevant live Lintap source/tests/packaging
and applicable AGENTS.md. Inspect the existing working diff first.

The implementation repo is `../Lintap`; canonical consumer is `../Wintap-PyUtil`
(read-only). Confirm explicit permission for the requested Lintap edits and
isolated work in existing **lintap-dev, Ubuntu arm64**. Do not recreate the VM,
restart shared services, edit sibling consumers, commit/push or deploy to a field
host without separate approval. Preparing this workflow did not grant those rights.

## Durable record and bounded repair loop

Default budget: **three candidate revisions or 60 minutes**, whichever comes first,
per requested unit. Honor a different explicit budget. These are skill/workflow
bounds, not an external controller or OpenCode scheduling setting. On resumption,
read recorded attempts and remaining budget; do not reset it silently.

1. State the unit, goal, hypothesis, source revision/diff, exact test command and
   agreed acceptance criteria. fpc-01 is the initial spike, not the full rewrite.
2. Capture actual Python results on real `/proc` inputs using `capture-python`.
   Keep the Python source revision/hash unchanged through acceptance. Use isolated
   guest paths, never the running collector's spool/data. Missing Python/DuckDB or
   host access is a blocker, not permission to substitute synthetic results.
3. Make the smallest grounded change and add a regression that catches the defect.
   Run focused local tests before a costly VM experiment. Keep exact replay/schema
   expectations intact; never lower thresholds, omit columns or drop unmatched rows
   to manufacture green. No native DuckDB/cgo in the installed Go binary.
4. Run actual Python/Go comparison and applicable tests/builds. Use the utility's
   `record`, `compare`, `static` and `smoke` modes for saved argv/exit/logs and
   explicit assertions. Read result.json AND the decoded rows/mismatch report.
   A compiler exit zero, --help success, or readable Parquet is not full acceptance.
5. Classify failures, write one new hypothesis, repair, and rerun affected plus
   cumulative checks. Infrastructure/missing evidence is blocked, not PASS.
6. Record exact commands, evidence directories, all failed checks, changes,
   completed matrix cells, attempt count/time and next step in `verification.md`.
   Retain failed evidence. Stop on success, exhausted budget, missing authorization,
   repeated identical failure without a new hypothesis or unexplained semantic drift.

## fpc-01 checkpoint and review

After real Python/Go writer parity, static arm64/amd64 checks and arm64 VM startup
proof, **stop and report fpc-01 evidence**. Ask the human to review/approve before
fpc-02. There is no hash-token approval command or automatic advancement.

For fresh-context review, the human opens a new OpenCode session in Analytics and
runs `/pidstat-review fpc-01; evidence is ...`. That command selects Plan in its
current session; it does not spawn a reviewer. Review must inspect actual outputs,
all 26 columns, row multiplicity, partitions, nulls and missing/unmatched rows.
Do not label same-session self-review independent. Resume only after explicit
human approval, recording the decision and reviewed evidence in verification.md.

## Evidence contract and limits

Capture includes the actual production Python sampler/writer, raw reads as observed
from `/proc`, kernel clock/page context, sample times and normalized snapshots/TSV.
fpc-01 can encode the captured TSV in Go; fpc-02 must replay captured raw inputs
through the Go sampler. Exact comparison is for identical-input replay only.

Final paired-live Python/Go runs require predefined sampling-skew tolerances and
identity-aware accounting in a later test harness. Do not use exact replay's checker
to claim live equivalence, and do not invent blanket tolerances after a failure.
The capture does not generate CPU/I/O/container workloads: declare and run approved
workloads separately, recording their coverage. The utility's smoke mode tests
hash-matched `--help` startup only; it does not prove long-running sampling, absence
of child processes, shutdown, recovery, throughput, downstream DBT or RHEL support.

First target is Ubuntu arm64; amd64 cross-build is not native/RHEL runtime proof.
Use `../Wintap-PyUtil` for separate Python/Go and mixed-input DBT qualification.
No automatic cleanup: evidence and isolated guest captures remain for inspection.
Timeouts stop local clients, not necessarily guest work; inspect before retrying.
