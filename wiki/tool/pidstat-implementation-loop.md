---
title: "Bounded pidstat Implementation Loop"
type: tool
confidence: high
grounded_by:
  - ../Wintap-Analytics/validation/pidstat-loop/evidence.py
  - ../Wintap-Analytics/validation/pidstat-loop/capture_python.py
  - ../Wintap-Analytics/validation/pidstat-loop/test_evidence.py
  - ../Wintap-Analytics/validation/pidstat-loop/README.md
  - ../Wintap-Analytics/.opencode/commands/pidstat-loop.md
  - ../Wintap-Analytics/.opencode/commands/pidstat-review.md
  - ../Wintap-Analytics/.opencode/skills/pidstat-loop/SKILL.md
  - ../Lintap/pidstat-go/main.go
  - ../Lintap/pidstat-go/schema.go
  - ../Lintap/pidstat-go/Makefile
  - ../Lintap/pidstat-go/sampler.go
  - ../Lintap/pidstat-go/kernel.go
  - ../Lintap/pidstat-go/replay.go
policy: agent-editable
last_validated: 2026-10-30
repo_scope: Wintap-Analytics
implementation_area: dev-environment
event_domain: process
audience: mixed
status: draft
source_paths: validation/pidstat-loop
tags: [pidstat, engineering-loop, opencode, verification, feature-work]
---

# Bounded pidstat Implementation Loop

The **current native OpenCode session** owns observe → hypothesize → change → verify
for [[wiki/work/fix-pidstat-collector/implementation_plan]]. `/pidstat-loop` selects
Build and loads the workflow skill. `validation/pidstat-loop/evidence.py` runs one
deterministic experiment; it has no LLM calls or edit/retry controller. The first-pass
external runner/custom profiles were removed at the human's request.
<!-- GROUND_TRUTH: ../Wintap-Analytics/.opencode/commands/pidstat-loop.md; ../Wintap-Analytics/.opencode/skills/pidstat-loop/SKILL.md; ../Wintap-Analytics/validation/pidstat-loop/evidence.py -->

## Start and checkpoint

**fpc-01/fpc-02 human-approved; fpc-03 technical checks complete, review pending.** To start another authorized unit,
run `/pidstat-loop fpc-01 ...` in Analytics. Default workflow budget is three candidate
revisions or 60 minutes per requested unit. Retain goal/hypothesis, commands, source
diff/revisions, failures, evidence and remaining budget in the verification page.
This budget and authorization discipline are skill instructions, not a state machine
or OS sandbox. No plugin, forced model or frozen configuration template is required.

Stop after fpc-01 for human approval before fpc-02. For fresh-context review, manually
open a **new** Analytics session and run `/pidstat-review fpc-01; evidence is ...`.
This selects Plan in its current session; neither command spawns another agent.
Record the human decision and reviewed evidence before resuming. Separate context
is not independent empirical proof. See `validation/pidstat-loop/README.md` for usage.
<!-- GROUND_TRUTH: ../Wintap-Analytics/.opencode/commands/pidstat-review.md; ../Wintap-Analytics/.opencode/skills/pidstat-loop/SKILL.md -->

## Utility and evidence limits

The Go diagnostics at `../Lintap/pidstat-go` use pinned Go1.27.3,
parquet-go0.32.0 and pure-Go ZSTD. Both Linux architectures build with cgo disabled;
arm64 executed in the Ubuntu guest. Captured Python TSV encodes to exactly matching
26-column DuckDB/physical column schemas, values, nulls and window/partition membership
for 266,705 and1640 real-reference rows. Five controlled writer rows supplement that
evidence. See [[wiki/work/fix-pidstat-collector/verification]] for hashes and commands.
fpc-02 now includes the raw sampler/configuration port: exact raw-input replay passes
the same3captures,17configuration cases and two52-row Python-controlled kernel-context
fixtures. Native arm64 replay and bounded411-row sampling pass. Timestamp microsecond
rounding is separate from source-epoch partition/windows; cache/monotonic/malformed
fault-handling differences are explicit in verification. This is not a durable
replacement service or accepted release. Fpc-03 now adds explicit durable modes,
legacy spool/journal recovery, no-overwrite publication, locking, caps and signals;
exact durable replay/actual Python spool comparisons and native arm64 tests pass.
Original host pytest runner is blocked; packaging/default-cadence/resources/paired-live
and DBT remain open. Publication/uploader crash gaps remain at-least-once, not an
exactly-once promise. See [[wiki/tension/pidstat-publication-versus-uploader-receipts]].
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/main.go; ../Lintap/pidstat-go/schema.go; ../Lintap/pidstat-go/sampler.go; ../Lintap/pidstat-go/replay.go; ../Lintap/pidstat-go/Makefile; ../Wintap-Analytics/wiki/work/fix-pidstat-collector/verification.md -->

- `capture-python`: actual source sampler/writer in existing **lintap-dev, Ubuntu
  arm64**, with isolated private data/spool roots, observed raw inputs, snapshots,
  TSV/Parquet and source/output hashes. Requires an existing guest Python/DuckDB
  interpreter; root never invokes uv. Workload generation is separately authorized.
- `compare`: reference hash/row validation, exact 26-column/schema/value multiset
  parity, partitions and rotation-window epochs, decoded rows and mismatch reports.
  Review also verifies actual candidate inputs/commands; manifests are not attestations.
- `static`: actual arm64/amd64 ELF architecture and absence of interpreter/needed
  libraries. Build commands must separately establish `CGO_ENABLED=0`.
- `smoke`: hash-matched root restricted-PATH `--help` startup only.
- `record`: argv, logs, timing and exit status for one supplied command.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/evidence.py; ../Wintap-Analytics/validation/pidstat-loop/capture_python.py -->

Missing evidence is INCOMPLETE, never PASS. Host comparison requires development
DuckDB, not installed Go runtime DuckDB. Utility tests include the actual Python
writer with controlled fixtures; they are not live Python/Go parity. Paired-live
tolerance/identity accounting, sustained collection, child-process absence,
durability/soak, packaging and separate/mixed `../Wintap-PyUtil` DBT qualification
remain pending collector gates. Ubuntu arm64 startup is not RHEL/amd64 runtime proof.

Private evidence stays under ignored `validation/pidstat-loop/evidence/`; existing
outputs are not overwritten or automatically cleaned. Timeouts kill local clients,
not necessarily guest work. Inspect before retrying; never reset unrelated work or
delete service data to recover. No collector/sibling/VM operations were performed
during workflow preparation.

## Related

- [[wiki/work/fix-pidstat-collector/brief]]
- [[wiki/work/fix-pidstat-collector/dev_handoff]]
- [[wiki/work/fix-pidstat-collector/verification]]
