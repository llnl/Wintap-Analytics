---
title: "Verification: Fix pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../Lintap/pidstat-collector-bootstrap.sh
  - ../Lintap/tests/test_pidstat_collector.py
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintap-Analytics/validation/pidstat-loop/evidence.py
  - ../Wintap-Analytics/validation/pidstat-loop/capture_python.py
  - ../Wintap-Analytics/validation/pidstat-loop/test_evidence.py
  - ../Wintap-Analytics/.opencode/skills/pidstat-loop/SKILL.md
  - ../Lintap/pidstat-go/main.go
  - ../Lintap/pidstat-go/schema.go
  - ../Lintap/pidstat-go/main_test.go
  - ../Lintap/pidstat-go/Makefile
  - ../Wintap-Analytics/validation/pidstat-loop/check_spike.py
  - ../Lintap/pidstat-go/sampler.go
  - ../Lintap/pidstat-go/config.go
  - ../Lintap/pidstat-go/kernel.go
  - ../Lintap/pidstat-go/replay.go
  - ../Wintap-Analytics/validation/pidstat-loop/check_sampler.py
  - ../Lintap/pidstat-go/collector.go
  - ../Lintap/pidstat-go/collector_test.go
  - ../Wintap-Analytics/validation/pidstat-loop/check_spool.py
  - ../Wintap-Analytics/validation/pidstat-loop/check_native_spool.py
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/fix-pidstat-collector/verification.md
tags: [feature-work, pidstat, verification, go]
---

# Verification: Fix pidstat Collector

## 2026-10-31 — Topic-commit review

The human authorized multiple topic commits on `work/pidstat-and-dbt-validation`
across the related repositories. This saves the unpackaged fpc-03 checkpoint;
it does not close its human acceptance, packaging or remaining qualification gates.
The operator reports RHEL 8/amd64 execution and successful use of the separately
authorized DBT source preflight; neither report was re-qualified on the live host.

Review corrected stale resource/authorization wording in the handoff and README.
Collector source, dependency pins and existing binaries were not revised.
The unpackaged collector checkpoint is saved in `../Lintap` commit `b9d5d59`
on the authorized branch.

- `../Wintap-PyUtil/.venv/bin/python -m unittest discover -s validation/pidstat-loop -p 'test_*.py' -v`:
  **19 passed**, including the actual Python writer on controlled inputs.
- Python AST parsing: all **10** harness source files pass.
- `make -C ../Lintap/pidstat-go GO=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/pidstat-fpc01-toolchain/go/bin/go test`:
  **blocked/setup failed**, exit 2. The retained temporary toolchain passes its
  version check but cannot find standard-library packages (starting with `bufio`
  under its `go/src`). No Go test/vet/module-verification pass is claimed for this
  review; earlier recorded passes below remain historical evidence. No toolchain
  installation or collector repair was performed to force a new result.
- Private captures, generated binaries, runtime state and local configuration stay
  outside the topic commits. No new VM run or live S3 request was performed.

## 2026-10-29 — Planning Only

- Human report: RHEL 8 documented sudo bootstrap failed because root could not find
  uv. Not independently reproduced here.
- Live source inspection confirms explicit `require_command uv`, uv-managed Python
  environment, Python/DuckDB writer and root service launcher.
- Read current sampler/configuration/spool/writer, pytest cases, package integration
  references and wiki requirements. Defined first live target as existing local
  Multipass `lintap-dev` Ubuntu arm64, per human correction.
- Canonical Wintappy source read failed: expected
  `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` not present locally.
  Human subsequently supplied the renamed directory, `../Wintap-PyUtil`.
- Read live `../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` and
  `macros/{paths,raw_sources}.sql`: Parquet scan, typed empty fallback, filename
  provenance and shared partition-window input contract confirmed. DBT not executed.
- Human explicitly required comparison with real results from the Python version.
  Plan now requires revision-pinned Python reference execution, identical captured
  real-proc replay and paired-live results; reviewers inspect all columns, row
  multiplicity and unmatched cases. These comparisons are pending, not performed.
- `git status --short` before wiki edits: existing untracked `.claude/`; left untouched.
- No Go code, source edits, builds, tests, guest commands, package changes or service
  operations performed. No performance, static-binary, Parquet or platform proof yet.

## Evidence Gates (Current)

| Gate | Required evidence | Status |
| --- | --- | --- |
| fpc-01 | Pinned dependencies/Python reference, real Python golden output, schema/value comparison, both ELF builds, guest arm64 execution | accepted by human 2026-10-30 after technical PASS |
| fpc-02 | Proc/config/rate/reuse/cgroup fixtures and regression results | accepted by human after candidate3 technical PASS |
| fpc-03 | Rotation/recovery/atomic publish/failure/cap/shutdown tests | technical checks PASS, candidate3; acceptance pending; original pytest runner blocked |
| fpc-04 | Both staging regressions, Debian arm64 payload/hash and service proof | pending |
| Python/Go parity | Exact identical-real-input replay and paired-live comparison; all columns, row multiplicity, unmatched cases and predefined tolerances reviewed | pending |
| fpc-05 | Three-boundary live output, shutdown, resource/process evidence, Wintap-PyUtil separate/mixed-input staging and review | pending |
| Later platforms | RHEL 8 amd64 native RPM/runtime and other distro/architecture runs | deferred, unqualified |

## 2026-10-29 — External Runner Preparation (Analytics Only)

**Superseded history:** the controller, profiles and tests described below were
removed on 2026-10-30. These old test results do not verify the replacement.

User authorized the runner/supporting files here, explicitly not collector implementation.
Added `validation/pidstat-loop/{run.sh,runner.py,config.example.json,README.md,test_runner.py}`,
dedicated implementation/review profiles in `.opencode/agents/`, ignored local state/config
paths, and [[wiki/tool/pidstat-implementation-loop]]. Updated plan/handoff/index/log.

- Local `opencode --version`: **v2.0.32**. `opencode run --help` confirms `--agent`,
  `--format json` and `--title`; no `--continue`, `--session` or `--auto` is used.
  Read official V2 CLI/config/agent/permission docs for profile fields and matching.
- `python3 -m unittest discover -s validation/pidstat-loop -p 'test_*.py' -v`:
  **15 tests pass**. Fake OpenCode and temporary repositories only. Covers separate
  sessions, authorization/unwired gates, cumulative checks, finite repair attempts,
  failure overriding refusal, stale/malformed reports, reviewer/client failure,
  scope/contract drift, locks/timeouts, candidate/evidence-bound human approval and
  explicit one-unit advancement through completion.
- `bash -n validation/pidstat-loop/run.sh`: pass.
- `bash validation/pidstat-loop/run.sh --help`: pass; no initialization or agent launch.
- `git diff --check`: pass.
- `git check-ignore validation/pidstat-loop/.runs/default/state.json
  validation/pidstat-loop/config.local.json`: both ignored as intended.

No actual implementation/review model sessions or guest commands launched. No collector
code, Go build, real Python comparison, DBT, package or service operations performed.
CLI/profile integration has not been live-qualified against a provider. Real verification
commands, explicit allowed Lintap paths/reference pins and effective shell permissions
remain setup gates; the supplied template cannot launch an agent. Existing `.claude/`
work was preserved. No commit/push.

Timeouts terminate local process groups only; unresolved remote sessions/guest workloads
require manual inspection/abort before a new authorized run. Blocked/interrupted runs
do not automatically resume, reset source or delete data. This is not an OS sandbox.

## 2026-10-30 — Native Workflow Replacement (Analytics Only)

Human requested reversal of the external-controller implementation in favor of the
Axon-style native command + skill + deterministic utility. Removed the first-pass
controller/config/test/launcher and custom implementation/review profiles. Added
`/pidstat-loop` (current Build session), `/pidstat-review` (current Plan session),
bounded `pidstat-loop` skill and `evidence.py`/`capture_python.py`/offline tests.
Updated README, canonical tool page, brief/plan/handoff/index. History above remains
explicitly superseded; its 15 tests are not replacement evidence.

The native session owns repair iteration: three candidate revisions or 60 minutes
per requested unit by default, durable verification record and human stop after
fpc-01. Fresh review requires a manually opened new session; no automatic agent
launch, approval token, frozen-command configuration or controller state machine.
Actual Python/Go parity requirements and the Ubuntu arm64 first target are unchanged.

### Checks and repairs

- Read official V2 commands/skills documentation; current-session `agent` selection,
  `subagent: false`, project directory discovery and reload behavior confirmed.
  Command templates have not been invoked to start collector work.
- Initial offline run found a test harness error: constructing the Python writer
  without an injected sampler tried macOS `/proc/meminfo`. Repaired the test setup
  to inject a writer-only sentinel and avoid duplicate inherited test execution.
- Utility review repaired unmatched-row accounting after identical-row cancellation,
  added rotation-window epoch comparison (not just day/hour partitions), normalized
  archive duplicate protection, reference path containment and recorded database
  errors as INCOMPLETE. Scoped scandir observation preserves non-proc filesystem APIs.
- `python3 -m unittest discover -s validation/pidstat-loop -p 'test_*.py' -v`:
  **19 tests pass, no skips**. Covers all-column differences, exact multisets,
  duplicates/unmatched rows, nulls, partitions/windows/collision suffixes, Python
  writer schemas (including DOUBLE/missing-column rejection), hashes/file sets,
  malformed Parquet, archive safety, ELF linkage/architecture, command exit/timeout,
  missing evidence, existing-output protection and smoke hash mismatch.
- Actual live Python source sampler/writer executed locally against **controlled
  fixtures**; capture-helper test uses simulated proc/OS context, exercises baseline
  then emitted output, archive/hash validation and restoration of observation hooks.
  This is utility verification, not actual live `/proc`, Linux arm64 or Go parity.
  Existing host DuckDB **1.4.4** used; no installation or upgrade.
- `python3 validation/pidstat-loop/evidence.py record --timeout 300 -- python3 -m
  unittest discover -s validation/pidstat-loop -p 'test_*.py' -v`: **PASS**, command
  exit 0, all 19 tests pass. Saved argv/timing/stdout/stderr/result under ignored
  `validation/pidstat-loop/evidence/20261031T035412Z-aaf7dd53/` (UTC directory timestamp).
- `python3 validation/pidstat-loop/evidence.py --help`: pass, no guest execution.
- `git check-ignore` confirms native evidence and historical local runner state/config
  remain ignored. Five relevant wiki page frontmatters/live source lists, 24 wikilinks
  and README/page local Markdown links pass; removed controller/profile files absent.
- `git diff --check`: pass.

**All collector gates remain pending.** No Go collector/source/build, live Python
reference capture, VM commands, package/service changes, paired-live comparison or
DBT run performed. Capture/smoke Multipass integration is not live-qualified.
`compare` establishes exact recorded-output parity, not independent provenance or
paired-live tolerances; `smoke` establishes hash-matched --help startup only.
Lintap/VM implementation authorization is still required. Existing unrelated work
preserved; no sibling edits, commit or push.

## 2026-10-30 — fpc-01 active (human-authorized)

Human approved scoped Lintap Go module/tests/build support, pinned dependency
downloads and isolated captures/workloads/binary tests in existing lintap-dev;
no shared services/data, packaging, Python-reference changes or commits. Separately
approved a private guest reference-only Python/DuckDB venv because the mounted
Lintap .venv points to a macOS interpreter and system Python lacks DuckDB.

Budget: three candidate revisions or 60 minutes; start approximately 21:07 PDT.
Candidate revisions used: 0 (preflight only). Goal/hypothesis: a pure-Go Parquet
writer can encode actual production Python TSV with exact 26-column physical and
DuckDB schema/value/window parity, including REAL and naive TIMESTAMP semantics.
Require both CGO_ENABLED=0 Linux ELF builds and isolated root arm64 guest execution;
stop for human review after the spike, not advance to the sampler port.

Reference: Lintap HEAD `b229a597977a2ce04820fffd86574a63f658cfcf`, Python source SHA256
`3722ef80c87e226a3c0491f9daff34f4cc8bddfba0d1589cf33052aef6e797c5`.
Lintap has unrelated untracked SysdigToRaw.drawio, dlt/, fedora-setup-first-pass.sh,
teletap/no-dbt.db; preserve them. No nested Lintap AGENTS.md found. Canonical consumer
26-column contract read live from Wintap-PyUtil; it remains unchanged/read-only.

Preflight: Go absent on PATH; downloaded official Go 1.27.3 darwin-arm64 archive to
approved host temporary directory, verified published SHA256
`dd3908cf20959d798c1e06ebe5b72213f0505ce01373b40ce3110975a6cd99c2`.
No system installation/PATH changes. Initial Multipass exec socket failure recovered
on subsequent version/info requests without daemon/VM restart. Host noninteractive
sudo requires a password; do not use it. Guest is running Ubuntu24.04.5 arm64,
kernel6.8.0-147,4CPUs/8GiB; source mounted at `/home/ubuntu/git/Lintap`.
An overly broad interpreter find timed out; subsequent native-path bounded find
found no guest venv. Guest `python3 -c` argument quoting failed; use stdin scripts.

### Observe → hypothesize → change → verify

Observation: actual Python/DuckDB schema probe established all26 columns OPTIONAL,
legacy signed INT32/INT64 and UTF8 converted annotations, FLOAT rates and a
TIMESTAMP_MICROS logical timestamp with `isAdjustedToUTC=false`. The guest's timezone
is America/Phoenix. The hypothesis above held without weakening the comparator.
Added `../Lintap/pidstat-go/{go.mod,go.sum,main.go,schema.go,main_test.go,Makefile,README.md}`.
The command encodes captured Python TSV only; it does not implement Go sampling.
Go1.27.3 and parquet-go0.32.0 are pinned; pure-Go ZSTD uses klauspost/compress1.17.9.
Parquet-go is Apache-2.0; Go/compress BSD-3-Clause; release notices/security review
remain pending. All Go builds/tests/vet use CGO_ENABLED=0 and GOTOOLCHAIN=local.
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/schema.go; ../Lintap/pidstat-go/main.go; ../Lintap/pidstat-go/go.mod; ../Lintap/pidstat-go/Makefile -->

Candidate revisions used: **1 of3**; no failed Go/parity candidate. Pre-compile
inspection corrected the hostname TSV index. Workload stimulus was extended after
the first run to keep churn/I/O overlapping capture; this was test infrastructure,
not a new collector candidate or threshold change. Socket failures, interpreter
find timeout and shell-quoting failure above remain recorded, not counted as PASS.

### Evidence inventory and results

All paths below are under private ignored `validation/pidstat-loop/evidence/`.
Each deterministic utility run retains result.json, exact argv, exit status,
timing and command logs. Capture directories retain actual raw input observations,
kernel clock/page context, snapshots, Python golden.tsv/Parquet and file hashes.
UTC artifact names correspond to local **2026-10-30 PDT** runs.

| Check | Evidence directory | Result |
| --- | --- | --- |
| Private guest reference venv; pinned duckdb==1.4.4 install | `20261031T041501Z-f0d64d1b`, `20261031T041523Z-fd41c45e` | PASS, no system Python/shared venv changes |
| Live Python3.12.3/DuckDB1.4.4, 3samples at2s | `20261031T041538Z-d3c6164c/reference` | 266rows |
| Host Go encoding / exact266 comparison | `20261031T041904Z-4ee99e70`, `20261031T041912Z-72f0665d` | PASS |
| Live Python, 6samples at2s / host Go encoding / exact705 comparison | `20261031T041912Z-61b7d175/reference`, `20261031T042023Z-af7201b2`, `20261031T042056Z-35ad41cd` | PASS |
| Main live Python, 12samples at2s | `20261031T042023Z-0c96a35c/reference` | 1640rows |
| Initial Go5 tests / vet | `20261031T041749Z-634539ee`, `20261031T042118Z-830c4644` | PASS |
| Host / Linux arm64 / baseline amd64 builds | `20261031T041819Z-8ec517ee`, `20261031T041819Z-3e25233c`, `20261031T041819Z-a2be7ce8` | PASS |
| Initial static ELF checks | `20261031T041904Z-3017fb62` | PASS, no interpreter or needed libraries |
| Private guest mkdir / binary install | `20261031T042012Z-534d94bf`, `20261031T042023Z-673ff169` | PASS |
| Hash-matched root restricted-PATH --help | `20261031T042056Z-b99e8bfd` | PASS, narrow startup only |
| Actual root guest TSV-to-Parquet encoding | `20261031T042056Z-98c17580` | PASS,1640rows |
| Guest-output transfer / exact1640 comparison | `fpc01-guest-output-transfer`, `20261031T042118Z-0600663f` | PASS |
| Supplemental actual Python writer5 rows | `20261031T042319Z-af3b9253`, `fpc01-edge-fixtures` | PASS, explicitly controlled fixtures |
| Makefile test/vet/module verify/build | `20261031T042319Z-99360034` | PASS,5tests, all modules verified |
| Rebuilt ELF checks | `20261031T042330Z-c8e9d126` | PASS, both hashes reproduce initial builds |
| Utility regression rerun | `20261031T042330Z-4681a7b8` | PASS,19tests, no skips |
| Source/hash/decoded-output inspection | `fpc01-final-inspection` | PASS, host/guest Python unchanged, matching decoded files |

Exact executable commands are retained in the directories above. Key reproduction
commands, from Analytics root (GO denotes the approved temporary Go1.27.3 executable):

```sh
python3 validation/pidstat-loop/evidence.py capture-python --collector /home/ubuntu/git/Lintap/pidstat-collector.py --python /var/tmp/pidstat-fpc01-reference-20261031T0413/bin/python --samples 12 --interval 2
python3 validation/pidstat-loop/evidence.py record -- multipass exec lintap-dev -- sudo env PATH=/usr/sbin:/usr/bin:/sbin:/bin /var/tmp/pidstat-fpc01-candidate1-20261031T0421/pidstat-spike --input /home/ubuntu/git/Wintap-Analytics/validation/pidstat-loop/evidence/20261031T042023Z-0c96a35c/reference/golden.tsv --output /var/tmp/pidstat-fpc01-candidate1-20261031T0421/parquet-output --timezone America/Phoenix
python3 validation/pidstat-loop/evidence.py compare --reference validation/pidstat-loop/evidence/20261031T042023Z-0c96a35c/reference --candidate validation/pidstat-loop/evidence/fpc01-guest-output-transfer/dataset
python3 validation/pidstat-loop/evidence.py record --timeout 120 -- python3 validation/pidstat-loop/check_spike.py --binary validation/pidstat-loop/evidence/fpc01-candidate1/pidstat-spike-host --output validation/pidstat-loop/evidence/fpc01-edge-fixtures
python3 validation/pidstat-loop/evidence.py record --timeout 300 -- make -C ../Lintap/pidstat-go GO=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/pidstat-fpc01-toolchain/go/bin/go test build
python3 validation/pidstat-loop/evidence.py static --arm64 ../Lintap/pidstat-go/bin/pidstat-parquet-spike-linux-arm64 --amd64 ../Lintap/pidstat-go/bin/pidstat-parquet-spike-linux-amd64
python3 validation/pidstat-loop/evidence.py record --timeout 300 -- python3 -m unittest discover -s validation/pidstat-loop -p 'test_*.py' -v
```

These commands already ran; use new output roots for repetitions, never overwrite
retained evidence. Main reference golden.tsv SHA256 is
`99c19b8793124109e88263221ae34ee2104e3c3c4983cff41f4b72bb75f9439e`;
capture.json is `e897bccbcc9728d80be67fba517dda348fabc3dc35d7e17b192e041d33d8c138`.
The comparator's replay-input hash denotes capture.json, not the TSV actually encoded
in fpc-01; reference.json and recorded encoding argv retain the TSV provenance.

### Same-session output inspection (not independent review)

Read comparison.json, decoded Python/Go rows, schemas and result.json. All three
live comparisons report **26/26 columns with0mismatches and0maximum absolute error**,
equal physical-column/DuckDB schemas and no unmatched Python/candidate rows.
The sorted decoded JSON files are byte-identical for each pair; actual Parquet
bytes may differ. Rows retain local wall times, namespace integers, null runtimes,
and matching day/hour/window epochs. The5 supplemental rows retain duplicates,
Python source rounding (12.345→12.35;250.125→250.12 before FLOAT storage), sanitized
quoted Unicode text, empty-text→null, PID2147483647 and namespace9007199254740993;
midnight spans day20261030/hour23 and day20261031/hour00 in separate300s windows.
Go sampler rounding has not been implemented or tested by this fixture.

Main bounded workload record: `20261031T042012Z-461dd079/01-command.stdout`;
earlier20s workload: `20261031T041904Z-d96b0efc`. The30s stimulus allocates32MiB,
wrote40MiB (4MiB retained), and all10 churn PIDs were observed. Live Python reports
max203.29% core-summed CPU,56920KiB RSS and2047.90KiB/s writes for the workload.
Coverage details: `fpc01-candidate1/workload-coverage.json`. Cached reads produced
0KiB/s observed reads; **uncached-read coverage not established**. All1640rows have
namespace inode; cgroup paths were observed; no live container runtime/ID was present.
Synthetic docker attribution proves writer representation only, not live parsing.

### Frozen artifacts and limitations

Linux arm64 SHA256: `f098ec69aef9a4ddbe5c2202552b658dc97882730af854e68663761db08d46ef`.
Linux amd64 SHA256: `b613a517210f26a68b9b6b7f6e80fa24fd4761b1b2ebb0889f8d754e6fa6ce48`.
Full source/module/test/README/Makefile and host-binary hashes are retained in
`fpc01-final-inspection/manifest.json`; Lintap HEAD and host/guest Python source remain
the frozen values above. Rebuilds are hash-identical. Guest binary and output stay in
`/var/tmp/pidstat-fpc01-candidate1-20261031T0421`; guest reference venv/captures/workload
artifacts are retained, not cleaned. No production service/package/source retirement,
system Python change, consumer source edit, commit or push occurred.

The spike groups all captured rows in memory. It does not implement production
proc sampling, config precedence, PID reuse handling, scheduling, spool recovery,
caps, locking, collision/retry policy or shutdown. TSV alone loses DST-fold/clock-jump
window provenance; tested Phoenix timestamps have no such ambiguity. These facts
do not qualify a deployed collector. No absence-of-children tracing, resource/soak
comparison, paired-live parity, canonical DBT execution or RHEL/native amd64 runtime
qualification is claimed. Pure-Go source and static ELF checks establish the spike's
runtime linkage, not eventual package dependencies.

### Human checkpoint

**STOP: fpc-01 technical evidence PASS; acceptance pending.** Candidate1of3,
budget began21:07PDT; documentation closeout21:26PDT, approximately19minutes used
and41minutes remaining. Budget is not reset on resume.
Human should inspect the source diff, main1640-row comparison/decoded files and all
evidence above. For fresh context open a new Analytics session and run:

```text
/pidstat-review fpc-01; inspect wiki/work/fix-pidstat-collector/verification.md and its recorded source/evidence
```

Do not mark accepted or start fpc-02 without explicit human approval. Later units
retain their pending gates in the table above.

Closeout checks: `git diff --check` passed in Analytics and Lintap; explicit
task-owned-file whitespace checks include untracked spike/docs. Six updated wiki
frontmatters/live source lists and wikilinks pass; all27 timestamped evidence
directories referenced here exist. Existing unrelated tracked/untracked changes
were preserved. No independent review or human acceptance has been recorded.

## 2026-10-30 — fpc-01 approved; fpc-02 active

Human replied **“I approve! Proceed”** after the fpc-01 report and evidence link.
Recorded approval of candidate1 and its evidence above; no independent reviewer
session is claimed. Proceed with fpc-02 under scoped Lintap collector/tests/docs
edits and isolated existing lintap-dev work; no shared service/data/package changes,
consumer edits, commits or deployment. fpc-03 recovery and fpc-04 packaging remain
outside this unit. Preserve original Python source/hash and all fpc-01 artifacts.

New unit budget: three candidate revisions or60minutes; start21:31PDT,
2026-10-30. fpc-01 used approximately19minutes and stopped before approval;
this is an explicitly new unit, not a reset of a resumed fpc-01 attempt.
fpc-02 candidate revisions used:2. Candidate1 passes all3 real raw-input replays;
controlled-source configuration check failed in `20261031T043546Z-4762ed72` on
numeric underscores and lexical '..' paths. Candidate2 hypothesis: matching
Python decimal syntax and pathlib's lexical POSIX representation repairs those
differences without relaxing expected config. Added regressions for separators,
Unicode decimal digits and paths; failed evidence retained. Source-only malformed
optional-counter behavior is intentionally changed from Python ValueError to
per-process skip, consistent with the plan's malformed-input fault handling;
valid/missing input defaults remain unchanged. Candidate2's sub-microsecond midnight
fixture failed in `20261031T044031Z-8ac06253`: Python datetime rounds to microseconds,
while Go had truncated to nanoseconds. Candidate3 hypothesis: round wall timestamps
like Python and separately preserve int(captured_at) rotation provenance; never infer
the sample window from rounded TSV time. This also avoids DST-fold window ambiguity
for raw-capture replay. Candidate revisions used:3of3; no further repair revision
without explicit human budget extension. Acceptance is not yet recorded.

Goal/hypothesis: injected Go proc reads, kernel tick/page context and time sources
can reproduce the actual Python sampler's rows exactly from captured raw inputs,
including baseline/reuse, guest/user CPU, schedstat, faults/memory/I/O/context,
cgroup/runtime and namespace semantics, with Python-compatible two-decimal TSV.
Configuration must preserve Linux paths, override precedence/defaults and limits.
Bound attribution caches to live PID/start identities; actual kernel clock ticks
come from Linux AT_CLKTCK, not a hardcoded constant or child command/cgo.

Planned checks: recorded cgo-disabled `make test build`; replay each retained
live capture through Go and exact `evidence.py compare` without omitted columns or
tolerances; actual Python controlled-source differential fixtures for config,
counter resets/guest/CPU>100/reuse/malformed/missing fields, cgroup variants and
rounding; static builds and isolated native arm64 kernel-context/replay/bounded
sampling diagnostics. A diagnostic sampler is not the fpc-03 durable collector.
Matching replay does not close paired-live timing, durability, packaging or DBT.

### fpc-02 technical results (candidate3)

Added shared injected proc sampler, Linux configuration resolver, native auxv/page
discovery and raw replay/bounded diagnostics; reused the26-column schema adapter.
`--replay capture.json` consumes observed reads/PID enumeration/times and kernel
context only, not normalized snapshots/output rows. A regression changes raw ticks
while leaving bogus normalized output unchanged and observes changed Go rates;
requesting uncaptured input fails rather than fabricating values. Source epochs
are retained separately from rounded local row times for window membership.
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/sampler.go; ../Lintap/pidstat-go/kernel.go; ../Lintap/pidstat-go/config.go; ../Lintap/pidstat-go/replay.go; ../Lintap/pidstat-go/replay_test.go -->

Exact identical-real-input results: **266,705 and1640 rows**, all26 columns with zero
mismatch/maximum absolute error, equal physical-column/DuckDB schemas, nulls,
multiplicity/partitions/windows and no unmatched rows. Python and Go TSV hashes and
sorted decoded JSON hashes match per capture. Native arm64 raw replay matches the
1640-row Python dataset exactly. Python source/Go dependency versions remain frozen.

Actual Python controlled sampler differentials produce **52rows each** with
100Hz/4096-byte and250Hz/16384-byte injected kernel contexts. Cover baseline/reuse,
guest/user/total CPU, schedstat, memory, counter resets, I/O/defaults/context switches,
missing status/short stat, Docker/Podman/containerd/crio, v1/v2/hybrid cgroups, null
namespace/runtime, sanitized Unicode commands and namespace9007199254740993.
Backward captured wall time tests Python's0.001s elapsed clamp. **17configuration
cases** match actual Python valid results/invalid rejection, including override/minimum
rotation, paths, separators and Unicode decimal digits. Five writer rows and19utility
regressions remain green. These are controlled fixtures, not extra live coverage.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/check_sampler.py; ../Lintap/pidstat-go/sampler_test.go -->

Boundary inspection: **7rows** with rounded time2026-10-31T00:00:00 correctly stay
under day20261030/hour23/window1793429700 because captured epoch is1793429999.9999998;
subsequent midnight samples enter day20261031/hour00/window1793430000. This preserves
Python's timestamp-versus-sample-window distinction, not a new schema. Go tests also
cover negative epochs and large positive rotation values.

All following paths are under private ignored `validation/pidstat-loop/evidence/`;
utility runs retain exact argv, exit, timing, logs and result.json.

| Final gate | Evidence directory | Result |
| --- | --- | --- |
| Candidate3 Go14tests/vet/modules/build | `20261031T044228Z-4e481d17` | PASS; cgo disabled |
| Host build | `20261031T044228Z-ac13f5fc` | PASS |
| Host raw1640/266/705 encodes | `20261031T044242Z-5f380852`, `20261031T044242Z-22185920`, `20261031T044242Z-d1c17415` | PASS |
| Host exact1640/266/705 comparisons | `20261031T044254Z-3957fb5e`, `20261031T044254Z-d6192a91`, `20261031T044254Z-8320d8ba` | PASS |
| Python sampler/config supplement | `20261031T044242Z-6ac648ab`, `fpc02-candidate3/final-fixtures` | PASS;52+52rows,17config cases |
| Python writer5rows | `20261031T044254Z-35f16b63`, `fpc02-candidate3/writer-regression` | PASS |
| Static final ELF | `20261031T044254Z-174fb67a` | PASS; no interpreter/needed libraries |
| Guest private directory/install | `20261031T044254Z-6ecec78b`, `20261031T044310Z-10314d8f` | PASS |
| Hash-matched root restricted-PATH --help | `20261031T044326Z-f4624c54` | PASS; narrow startup |
| Native AT_CLKTCK/page discovery | `20261031T044326Z-3d12b068` |100Hz/4096bytes, matches Python sysconf |
| Native raw replay / retrieved exact1640 comparison | `20261031T044326Z-da84295c`, `fpc02-candidate3-native-transfer`, `20261031T044358Z-4eeda99d` | PASS |
| Bounded live4samples at1s | `20261031T044326Z-a0439181` |411rows;137last-sample identities/cache entries |
| Final cumulative make rerun | `20261031T044359Z-e71eecde` |14tests/vet/modules/build PASS; binary hashes reproduce |
| Final utility rerun | `20261031T044359Z-8fe90a28` |19tests PASS, no skips |
| Source/raw/decoded/kernel/native inspection | `fpc02-final-inspection` | PASS; saved411live rows/schema and hashes |

Key commands, from Analytics root (already run; repetitions need new output roots):

```sh
python3 validation/pidstat-loop/evidence.py record --timeout 300 -- make -C ../Lintap/pidstat-go GO=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/pidstat-fpc01-toolchain/go/bin/go test build
python3 validation/pidstat-loop/evidence.py record --timeout 60 -- validation/pidstat-loop/evidence/fpc02-candidate3/pidstat-spike-host --replay validation/pidstat-loop/evidence/20261031T042023Z-0c96a35c/reference/capture.json --output validation/pidstat-loop/evidence/fpc02-candidate3/replay-1640 --timezone America/Phoenix
python3 validation/pidstat-loop/evidence.py compare --reference validation/pidstat-loop/evidence/20261031T042023Z-0c96a35c/reference --candidate validation/pidstat-loop/evidence/fpc02-candidate3-native-transfer/datasets/replay-1640
python3 validation/pidstat-loop/evidence.py record --timeout 120 -- python3 validation/pidstat-loop/check_sampler.py --binary validation/pidstat-loop/evidence/fpc02-candidate3/pidstat-spike-host --output validation/pidstat-loop/evidence/fpc02-candidate3/final-fixtures
python3 validation/pidstat-loop/evidence.py record --timeout 60 -- multipass exec lintap-dev -- sudo env PATH=/usr/sbin:/usr/bin:/sbin:/bin PIDSTAT_INTERVAL_SEC=1 /var/tmp/pidstat-fpc02-candidate3-20261031T0443/pidstat-spike --sample-count 4 --output /var/tmp/pidstat-fpc02-candidate3-20261031T0443/live-diagnostic --timezone America/Phoenix
```

Intermediate passing/failed evidence remains in timestamped runs and
`fpc02-candidate1/`, `fpc02-candidate2/`. Candidate1 initial build/test
`20261031T043422Z-1e6b50bb` and candidate2 `20261031T043710Z-36f9769b` passed;
config failure `20261031T043546Z-4762ed72` and timestamp/window-boundary failure
`20261031T044031Z-8ac06253` are retained. Candidate2 native401-row diagnostic and
1640-row replay remain under `fpc02-native-transfer`; final qualification uses
candidate3, not those superseded binaries. No fourth repair revision occurred.

Final arm64 SHA256: `391ec002490d6ce2b5bf56719f7498176433f1852ace00eeff85c54eaad236f1`;
amd64: `e8406d84bfb1dbaeaeed1d79681cfde5c5afea5f125f29966cc9aec5073c0ea5`;
host: `4842fbc7cdf08334df623368cd10d057720a991a1fcb48de301b9a20f8eaee3f`.
Binary copies are retained in `fpc02-candidate3/`. Guest binary/output remains under
`/var/tmp/pidstat-fpc02-candidate3-20261031T0443`; earlier guest artifacts are retained.
Full input/source/module/binary hashes: `fpc02-final-inspection/manifest.json`;
documentation closeout hashes are separate, not an overwrite of that inspection.

### Differences, limitations and stop

- Malformed optional integer counters: Go per-process skip versus Python ValueError;
  actual exception and Go regression recorded. Valid math/missing-field zero/default
  semantics unchanged. Cache evicts exited/superseded PID/start identities where
  Python retains stale entries; temporarily unreadable enumerated identities remain.
- Live elapsed/scheduling is monotonic, avoiding wall-clock jumps; raw replay uses
  captured Python differences/clamp. Sustained scheduling/clock-jump integration
  remains later qualification. Raw replay retains DST-fold window provenance;
  bare TSV cannot reconstruct it.
- Configuration resolution has no mkdir side effects; diagnostics write only new
  explicit output, not configured production roots. No durable daemon/spool/caps,
  locks, restart/retry/collision policy or signal handling exists. Compression is
  resolved, not wired into a production writer. Legacy DuckDB threads is validated/
  reported only, with no Go runtime meaning; explicit deprecation is later work.
- Config/counters use signed64-bit bounds rather than Python arbitrary precision;
  oversized config rejects. Invalid-byte UTF8 decoding beyond captured Python
  replacement text remains unqualified. Live container runtime IDs and uncached
  reads were not newly qualified; earlier workload limitations still apply.
- Four-sample readability is not paired-live equivalence, child tracing, resource/
  soak, recovery, packaging, DBT or RHEL/native amd64 runtime proof. No production
  service/data/package changes, consumer edits, Python retirement, commit or push.

**STOP: fpc-02 technical PASS; review/acceptance pending.** Candidate3of3;
budget began21:31PDT; documentation closeout21:48PDT (~17minutes,43remaining).
The revision budget is exhausted even though time remains; another implementation
repair needs explicit extension. Same-session inspection only, not independent
review. fpc-03 has not started. Record review/next authorized unit before resuming.

Closeout: `git diff --check` passes in Analytics and Lintap; explicit untracked
task-owned source/docs whitespace checks pass. Six wiki frontmatters/live source
lists/wikilinks and all51 timestamped evidence directories referenced in this record
validate. Final documentation/source snapshot hashes and verification source archive
are retained in `fpc02-closeout/`; earlier inspection evidence is not overwritten.
Unrelated tracked/untracked changes remain preserved; no independent reviewer was run.

## 2026-10-30 — fpc-02 human-approved; fpc-03 active

Human replied **“fpc-02 approved. proceed”** following the candidate3 report.
Acceptance covers the recorded fpc-02 evidence/differences; no independent reviewer
session is claimed. New fpc-03 unit budget: three revisions or60minutes, starting
21:52PDT (candidate0/preflight). This is a new authorized unit, not a reset of fpc-02.
Scope remains Lintap collector/tests/build/docs and isolated existing Ubuntu arm64
lintap-dev experiments; Python/reference, consumers, services/packages and shared
telemetry stay unchanged. No commits/push/deployment.

Hypothesis: compatible TSV/meta plus explicit seal/publication journals and synced
atomic no-overwrite publication can recover old Python spools and interrupted Go
transitions without losing rows or duplicating successful publication. Stream rows
through the pinned schema adapter, retaining source window metadata, failed inputs,
oldest-first pidstat-only caps and exclusive spool locking. Test injected failures,
restart/metadata/truncation/collision/empty windows/compression/caps and signal seal.
Planned commands: recorded `make test build`, actual Python spool differential on
retained real captures plus controlled recovery supplements; exact `evidence.py
compare`, cumulative sampler/writer/utility regressions, static checks and isolated
native arm64 recovery/SIGTERM experiments. Packaging/default-cadence soak/paired-live/
DBT/RHEL remain later gates. Python SHA256 stays frozen as recorded above.

Candidate1 failed `20261031T045535Z-76704008` only on the obsolete writer-only CLI
warning assertion; recovery/collision/compression tests passed their initial scope.
Actual-Python spool differential `20261031T045656Z-9ca77a46` passed current valid/
missing-meta but failed strict filename validation on Go's extra collision suffix
number; comparator retained unchanged. Candidate2 hypothesis: preserve legacy two-
number collision suffix with no-overwrite allocation, update obsolete warning and
match actual DuckDB accepted codecs including LZ4 alias/BROTLI (observed in
`fpc03-compression-observe`). Batch diagnostic appends by sample epoch to avoid
unnecessary per-row fsync. Candidate revisions used:2of3. An empty-stdin command
`20261031T045724Z-e4fa32cd` produced no observations and is not codec evidence.

Candidate2 passed all real replay/spool/codec checks (`20261031T045842Z-94d95048`),
cumulative tests/build and native arm64 tests/signals/recovery. Earlier spool harness
`20261031T045819Z-b83fcf43` failed because macOS case-insensitive paths made codec-ZSTD
and codec-zstd collide; indexed fixture directories fixed the harness, not collector
expectations. Self-review before closeout identified a cross-spool shared-output
race: an interrupted receipt could remove another writer's same-name .active.
Candidate3 hypothesis: exclusively reserved unique .active paths recorded in each
receipt; recognize prior publication by inode plus hash (identical unrelated rows
must not be deduplicated), and retain atomic no-replace linking. Add regression for
two paused writers with separate spools sharing output and identical rows. Also use
the same orphan-receipt startup cleanup in live mode as --recover. Revisions:3of3;
no further implementation revision without human budget extension.

### fpc-03 technical results — candidate3

Implemented explicit `--collect`, `--recover` and `--spool-replay` modes, compatible
legacy TSV/meta, restartable seal/publication journals, exclusive spool flock,
successful-close synced atomic no-overwrite publication, retained-input retry,
configured compression, metadata-selected epoch/local partition windows, collision
allocation, pidstat-only age/byte caps and signal shutdown. Configured hostname owns
the filename; row hostname stays a nullable data value. Older diagnostic modes stay
isolated/in-memory and do not exercise the durable path.
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/collector.go; ../Lintap/pidstat-go/main.go -->

Final **26Go tests** pass on host and as a cgo-disabled native arm64 test binary.
Includes3seal and4publication crash checkpoints, published-receipt/uploader removal,
failed writer.Close, malformed/truncated tails, absent/invalid meta inference,
empty windows, multiple pending/repeated collisions, stale active preservation,
compression validation, caps scope/symlinks/missing files, backward rotation and
separate spool writers sharing output with identical rows. Unique reserved active
paths and inode+hash recognition preserve independent row multiplicity; no schema/
comparison relaxation. These are deterministic tests, not live uploader/power-loss
fault qualification.
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/collector_test.go -->

Exact **durable raw-input replay** passes all retained real captures (266/705/1640),
all26 columns/schema/nulls/multiplicity/partitions/windows, zero unmatched/error.
Unchanged Python Collector methods produce real-row current spools with valid or
missing metadata and pending spools with multiple files or invalid metadata; Go
recovers each1640-row scenario exactly against actual Python output. Eight valid
codec spellings (ZSTD/zstd/SNAPPY/GZIP/LZ4_RAW/UNCOMPRESSED/LZ4/BROTLI) match actual
Python writer output, while invalid compression rejects/preserves input. Supplemental
52-row actual-Python durable replay preserves7rounded-midnight rows in the previous
sample window. Existing52+52sampler rows/17config cases,5writer rows and19utility
regressions stay green.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/check_spool.py; ../Wintap-Analytics/validation/pidstat-loop/check_sampler.py -->

Final native Ubuntu arm64 experiments, private
`/var/tmp/pidstat-fpc03-candidate3-20261031T0504/checks`:

- Unchanged native Python-produced leftover spool and native raw durable replay:
  each1640rows, exact all-column/schema/window equality.
- SIGTERM and SIGINT: each411readable rows in2files, exit0, no current/pending TSV or
  active files left. Rotations shortened to2s/minimum1s; **not default300s proof**.
- Same-spool second native Go process fails with locked-spool error during each run.
- SIGKILL with a synced current spool:137retained rows recovered on restart, exact
  leftover line count/hash preserved, no added rows. Reference evidence retained.
- Destination obstruction causes conversion failure with unchanged source SHA256;
  removing only that test-owned obstruction retries successfully to20rows.
<!-- GROUND_TRUTH: ../Wintap-Analytics/validation/pidstat-loop/check_native_spool.py -->

| Final gate | Private evidence directory | Result |
| --- | --- | --- |
| Host26Go tests/vet/modules/static builds | `20261031T050308Z-5d649b41` | PASS |
| Host-native build | `20261031T050308Z-2ecb6764` | PASS |
| Actual Python spool/codec/durable raw differential | `20261031T050346Z-f9fc7836`, `fpc03-candidate3/spool-check` | PASS |
| Sampler/config and writer regression | `20261031T050346Z-8717d1c5`, `20261031T050346Z-e8facf77` | PASS |
|19utility regressions | `20261031T050346Z-a97a2967` | PASS |
| Native test binary build | `20261031T050346Z-185434c9` | PASS; CGO_ENABLED=0 |
| Guest directory/binary/test transfer | `20261031T050357Z-0510194e`, `20261031T050409Z-ee971422`, `20261031T050409Z-8df206aa` | PASS |
| Native26tests including fault checkpoints | `20261031T050421Z-5c802ca9` | PASS |
| Native Python/Go recovery/signals/retry | `20261031T050421Z-434b831f` | PASS; bounded private experiments |
| Hash-matched restricted-PATH help | `20261031T050421Z-0e9f7f78` | PASS; narrow startup only |
| Exact266/705/1640durable comparisons | `20261031T050421Z-98e26630`, `20261031T050421Z-753960aa`, `20261031T050421Z-56c9d384` | PASS |
| Two real raw replays plus52boundary rows | `fpc03-candidate3/other-raw-replays` | PASS |
| Both static ELF inspections | `20261031T050421Z-ab87632c` | PASS; no interpreter/DT_NEEDED |
| Native retrieval and decoded/hash inspection | `fpc03-candidate3-native-transfer`, `fpc03-final-inspection` | PASS |
| Retrieved native exact1640 comparison | `20261031T050834Z-489cf463` | PASS |
| Final cumulative tests/vet/modules/build rerun | `20261031T050834Z-59e26e21` | PASS;26tests and reproduced binary hashes |
| Original Python pytest invocation | `20261031T050455Z-4b0cbe0f` | BLOCKED: host pytest absent; no install attempted, not counted as PASS |

Key recorded commands (from Analytics; already run, reruns need new roots):

```sh
python3 validation/pidstat-loop/evidence.py record --timeout 300 -- make -C ../Lintap/pidstat-go GO=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/pidstat-fpc01-toolchain/go/bin/go test build
python3 validation/pidstat-loop/evidence.py record --timeout 300 -- python3 validation/pidstat-loop/check_spool.py --binary validation/pidstat-loop/evidence/fpc03-candidate3/pidstat-host --reference validation/pidstat-loop/evidence/20261031T042023Z-0c96a35c/reference --output validation/pidstat-loop/evidence/fpc03-candidate3/spool-check
python3 validation/pidstat-loop/evidence.py compare --reference validation/pidstat-loop/evidence/20261031T042023Z-0c96a35c/reference --candidate validation/pidstat-loop/evidence/fpc03-candidate3/spool-check/raw-durable-replay/data
python3 validation/pidstat-loop/evidence.py record --timeout 120 -- multipass exec lintap-dev -- sudo env PATH=/usr/sbin:/usr/bin:/sbin:/bin /var/tmp/pidstat-fpc03-candidate3-20261031T0504/pidstat-tests -test.v
python3 validation/pidstat-loop/evidence.py record --timeout 120 -- multipass exec lintap-dev -- sudo /var/tmp/pidstat-fpc01-reference-20261031T0413/bin/python /home/ubuntu/git/Wintap-Analytics/validation/pidstat-loop/check_native_spool.py --binary /var/tmp/pidstat-fpc03-candidate3-20261031T0504/pidstat-collector --reference /home/ubuntu/git/Wintap-Analytics/validation/pidstat-loop/evidence/20261031T042023Z-0c96a35c/reference --output /var/tmp/pidstat-fpc03-candidate3-20261031T0504/checks
```

Final binary SHA256: arm64
`224405f7d4eaf815669f2071b514967287e130002a8ef93834660bfa64f308e4`, amd64
`0dd121ce49c1e8b4c0dd48f549473d0e5224a21533e52ba5a80201809bbd1978`, host
`c691836295a077171e01a7f05b9bd430c532c08e48e78667a57e6abf3c5a303d`.
Source/module/binary/decoded/input inspection hashes and private binary copies are in
`fpc03-final-inspection/manifest.json` and `fpc03-candidate3/`; Python hash unchanged.
Candidate1/2 failed/passing runs and guest artifacts remain, not overwritten.

### Guarantee limits / review checkpoint

- Publication is atomic and source deletion follows successful close/sync/receipt.
  Process-crash transitions are tested. Full power-loss, directory-ancestor/storage/
  network-filesystem persistence is **unqualified**, not guaranteed by test fsync.
- If uploader removal races between installation and durable published receipt,
  a crash may replay a delivered window. No end-to-end exactly-once claim; see
  [[wiki/tension/pidstat-publication-versus-uploader-receipts]]. Same-spool flock is
  honored only by Go; Python does not participate. Never run both on one spool.
- TSV/meta format is compatible, but Python does not understand Go journals. Before
  rollback, use Go recovery to inspect/drain outstanding transitions. Missing meta
  inference cannot recover source-epoch precision/fold information that was lost.
- Strict retained-tail behavior deliberately rejects missing final newline rather
  than letting a CSV reader accept possibly truncated input. Empty pending files are
  cleaned up instead of Python's empty-file no-op. Invalid codec fails early; recover/
  shutdown failed conversions return nonzero rather than silently reporting success.
- Failed spools are not capped/evicted; operators must monitor persistent failures.
  Parsing is incremental but Parquet row-group buffering/throughput/RSS, sustained
  retries and default cadence remain resource/soak qualification work. No power-loss
  or shared uploader race was injected. Older diagnostics remain in-memory paths.
- Original pytest runner is missing on host, retained as blocked. Ported Go tests and
  actual Python method differentials are green, not a claim that pytest ran. Full
  original regression/race-tooling qualification remains a later environment gate.
- No service/package changes, source retirement, shared data/service operations,
  consumer edits, commits/pushes/deployment. No paired-live/DBT/RHEL/native amd64
  qualification or measured CPU/resource advantage.

**STOP: fpc-03 technical checks complete, human review/acceptance pending.** Candidate3
of3; budget began21:52PDT. No further implementation revision under this budget;
original pytest runner remains blocked as recorded. Same-session inspection only.
Packaging/fpc-04 is not started or authorized by this checkpoint.

Documentation closeout22:09PDT: approximately17/60minutes used; revisions3of3.
Time remains but the revision budget is exhausted. Source/docs/evidence snapshot and
final diff/frontmatter/wikilink checks are retained in `fpc03-closeout/`. No independent
reviewer session was run; prior evidence and unrelated working changes remain intact.

## 2026-10-30 — Authorized four-hour sensor-on VM soak (running)

Human requested a four-hour run on the existing VM before packaging, with latest
Lintap running and recurring existing smoke workloads. This authorizes isolated VM
execution, not fpc-04, a collector repair revision, or final fpc-03 acceptance.
Collector candidate remains fpc-03 candidate3; no collector/module changes.

### Environment, build and isolation

- Existing `lintap-dev`: Ubuntu24.04.5, arm64, kernel6.8.0-147-generic,4CPUs,
  8GiB RAM; about39GiB native disk free before launch. No installed `lintap` unit
  or running sensor existed. No shared service was restarted, no package installed.
- Current shared checkouts: Wintap
  `66d8297610f68ebe3a011d9ed5ab1b01a22c2508`; Lintap
  `b229a597977a2ce04820fffd86574a63f658cfcf`. “Latest” here means the current
  checkout HEAD, not a remote fetch or release-version assertion.
- Frozen Wintap `git archive HEAD` was built on the native guest filesystem with
  `make -C <archive>/wintap build_ebpf`, then
  `make -C <archive>/wintap build_dotnet WINTAP_DISABLE_MCP=true
  DOTNET_BUILD_FLAGS="-p:UseAppHost=false -p:EnableMcpServer=false"`.
  All12tracers built; SDK10.0.402 managed build:0errors,178warnings. No Wintap
  source edits were made for the run. Fresh DLL SHA256:
  `48c039ab2815bf3e8e199ca89af8eae3e9326ef3bf74b1ef2f576878486ab380`.
- **Incidental preflight mutation:** `make ... run-env` unexpectedly invoked its
  `build_dotnet` prerequisite on the shared checkout; local client timed out30s
  while guest build continued. Its restore changed the previously modified
  `shared/WintapAPI/packages.lock.json` back to the tracked version. The original
  diff was not captured, so no restoration is claimed. Subsequent build work used
  the isolated archive. Other observed checkout changes were left alone.
- Root-private native run root:
  `/var/tmp/pidstat-four-hour-20261031T0520`. Sensor data/runtime are
  `lintap-data`/`lintap-runtime`; pidstat output/spool are
  `pidstat-data`/`pidstat-spool`. Separate output prevents sensor merging, cleanup
  or upload deletion from obscuring pidstat review. No existing telemetry touched.
- Normal ETL/Esper and sensors enabled; direct Parquet, MCP and DuckDB UI disabled.
  Existing source config has all upload adapters disabled; data stays local. Only
  this isolated copied config's raw-sensor cap was raised to8GiB for retention.
  Supervisor stops the test if available disk falls below4GiB; no automatic pruning.
- Hash-matched static Go arm64 collector SHA256 remains
  `224405f7d4eaf815669f2071b514967287e130002a8ef93834660bfa64f308e4`.
  Root restricted system PATH, explicit `America/Phoenix`; default5s sampling,
  300s rotation, ZSTD,1GiB pidstat byte cap/age cap disabled. No Python collector runs.

### Supervision and stimuli

`validation/pidstat-loop/soak_vm.py` is guest test orchestration, **not** a deployed
service. It starts only its own processes, verifies required sensor registrations,
records30s `/proc` CPU ticks/RSS/HWM/threads/children/I/O and disk/load observations,
then at14400monotonic seconds stops stimuli, SIGTERMs/seals pidstat while Lintap
remains live, and stops/drains Lintap. Any early process exit aborts rather than
restarting and hiding failure. Forced shutdowns are recorded as findings.

First startup attempt at `/var/tmp/pidstat-four-hour-20261031T0518` was retained:
the harness checked console output, but registrations are in the runtime log. No
pidstat sampling or smoke round started. Stopped only this test's supervisor/sensor;
corrected log discovery and started a fresh root. This is a test-harness correction,
not a new collector candidate or budget reset.

Actual start **2026-10-31T05:18:50.564555Z**; planned stop
**2026-10-31T09:18:50.564562Z** (Oct30 22:18:50 to Oct31 02:18:50 Phoenix/PDT).
Supervisor15305 belonged to the stopped startup attempt; live supervisor15551,
Lintap15552, pidstat15606, smoke15611. Exact argv/env/config and source/binary/tracer/
runner hashes are retained in `state.json`, `preflight.json`, `inputs.sha256.json`.

Frozen existing `validation/telemetry-soak/run-smoke-soak.sh` uses the persistent
`/home/ubuntu/.venvs/lintap-dev/bin/python` (DuckDB1.5.6), archived Wintap devtools,
900s delay **after** each sequential round,120s per-workload timeout, assigned VM IPv4,
and a freshly prebuilt unchanged `clone_lifecycle_workload.c` helper. No dependency
installation. Private stimuli/manifests are outside collector data/runtime/filter
paths at `/home/ubuntu/qa/pidstat-four-hour-20261031T0520`; smoke Parquet joins
`lintap-data/raw_sensor/raw_smoke_test`. These are small canaries, not sustained
CPU pressure or a claim of complete short-lived-process visibility at5s sampling.

First round: named/process/file/clone/endpoints each exit0,`recorded` (5/5).
Execve/Clone/Exit/Network/ProcessRundown registered; FileOps registered as
`partial` because legacy open/unlink syscall tracepoints are unavailable on this
arm64 kernel. SELinux startup fails with `selinux-filesystem-absent`, expected
platform coverage limit; retained receipt is not waived as full-sensor success.

### Retrieval/review plan and preflight checks

- `inspect_soak.py` will decode **every** closed pidstat file against the physical
  and DuckDB schema of the retained actual266-row Python Parquet reference. It
  reports row/null counts, windows/partitions, duplicates, sample-time gaps,
  leftover active/spool state, resource trends, smoke outcomes and readable sensor
  file counts. No blanket live-parity tolerance or resource-improvement claim.
- Native inspector pilot used1788actual already-closed Go rows and the actual
  Python reference: all26columns and physical schema match. Incomplete-run fixture
  metadata correctly produces findings for duration, unclosed Lintap and fewer
  than3rotations; not represented as soak acceptance. Evidence retained at
  `/var/tmp/pidstat-inspector-pilot-20261031T0521`.
- Both new scripts pass `python3 -m py_compile`; `git diff --check` passes.
- Background host shell `sh_19066eede00169An86rESA2qRX` blocks on guest pidfd,
  rather than polling completion. After supervised shutdown it invokes the frozen
  inspector, archives data/logs/resources/config/inputs/smoke evidence and startup
  failure logs, transfers to
  `validation/pidstat-loop/evidence/four-hour-20261031T0520/`, verifies archive
  SHA256 and safely extracts regular files only (16GiB bound). Guest originals are
  retained; retrieval failure stops without deleting evidence or restarting work.
  Completion notification should resume review. If the client disconnects, the
  guest supervisor still owns the bounded shutdown; inspect its state before retry.

**RUNNING, not PASS.** Four-hour completion, final seal, full-file review and
resource assessment remain pending. Packaging, paired-live Python comparisons,
consumer DBT, original pytest and native RHEL/amd64 gates remain separate. No final
fpc-03 approval, independent review, commit/push or field deployment claimed.

## 2026-10-31 — Four-hour soak complete; data retrieved and reviewed

**Scoped default-cadence Ubuntu arm64 collection check passes (same-session
technical review).** Full review: [[wiki/work/fix-pidstat-collector/soak_review]].
No human fpc-03/packaging acceptance is inferred from this result.

- Actual14400.0215s; collection stopped09:18:50UTC. Smoke/pidstat/Lintap each exit0,
  no forced termination; Lintap drain finished09:19:02UTC. No restarts/early deaths.
- Every49pidstat Parquet file decoded:399312rows, all26physical/DuckDB columns
  match actual Python reference.0wrong-window/partition rows, contiguous300s windows
  across midnight,2880distinct sample times with all5s gaps. Secondary whole-dataset
  query finds0cross-file duplicate identity/time groups. Final partial window6484rows;
  no active/current/pending/journal leftovers, collector.lock alone remains.
- All fields nonnull except container_runtime/container_id (399312nulls each); this
  run had no container-ID coverage. No malformed/nonfinite row decoding failures.
- 479approximately30s independent resource observations: Go median0.465%of one core,
  peak30s0.799%, medianRSS16.97MiB/peak44.86MiB, peak10threads,0observed children,
 0read errors. Four elapsed-hour medianRSS16.70/16.96/17.03/17.03MiB. No measured
  Python comparison and no exhaustive short-lived-child/thread-event audit.
- Lintap medianCPU1.365%of one core/peak30s35.145%, medianRSS495.27MiB/peak620.23MiB.
  Decoded5s metric rows contain2880samples for both collectors: Go median/max CPU
 0.40%/1.96%, Lintap1.23%/83.00%; different interval maxima are kept distinct.
- 16five-family rounds:80/80exit0/recorded.436sensor/manifest Parquet files readable,
  including6105process,2619network increment,148670file and240smoke manifest rows.
  Stimulus completion/readability is not full capture or delivery acceptance.
- Retained sensor findings: partial arm64 FileOps hooks, absent SELinux,1disabled
  SignedS3UrlAdapter resolution error, expected plugin/UI/inference startup warnings
  and1unknown-parent warning. Reported serializer/FileOps/drop-enqueue counters have
  zero maxima; uninstrumented kernel/event completeness is not inferred. Go log has
  no failure/panic/eviction entries; final SIGTERM seal appears normally.
- Minimum observed native free disk37.76GiB; no cap/safety-floor interruption.

### Retrieval failure and bounded repair

Background wait/inspection completed; frozen inspector exit0. Initial
`multipass transfer` exit2: changing the archive owner did not make its root-private
parent traversable. Kept failed stdout/stderr, archive and original directory
permissions. Copied only the test-owned archive into
`/home/ubuntu/pidstat-evidence-transfer-20261031T0520` (Ubuntu-owned0700; archive0600),
then transferred successfully; guest originals/copy retained.

Local evidence: `validation/pidstat-loop/evidence/four-hour-20261031T0520/`.
Archive `evidence-retrieved.tar.gz`19,773,414bytes matches SHA256
`5e324a0fe0f3c8607ae8e04617ba907fc81489c49ba845668f77d0a5d0757ab1`;
safe regular-file-only extraction969files/51,538,189bytes. Read and aggregated
`retained/inspection.json`, all per-file checks/nulls, `resources.jsonl`, smoke
statuses, Go and Lintap logs; saved `review-summary.json`/`log-review.json`.

Secondary decoded query first failed because DuckDB cannot bind parameters in
CREATE VIEW. Kept `decoded-review.command.py/.stdout/.stderr`; revised only the
read-only test query to `db.from_parquet(...).create_view('soak')`, which succeeds.
Revised command/stdout/stderr and `decoded-review.json` retained. No collector
revision, altered acceptance threshold, source/module/package change or budget reset.

Packaging stays on hold for human review; paired-live Python/equivalent-load
resource comparisons, DBT, original pytest, native RHEL/amd64 and final approval
remain pending. No consumer edits, commit/push or field deployment.

## Later Entry Format

For each unit record date, revisions/working-tree scope, environment, exact commands,
exit codes/pass-fail counts, artifact hashes/evidence paths, review findings, repairs,
rerun results and remaining limitations. Keep private raw telemetry and identifiers
out of wiki commits. Mark self-review vs independent review accurately.

## Related

- [[wiki/work/fix-pidstat-collector/brief]]
- [[wiki/work/fix-pidstat-collector/implementation_plan]]
- [[wiki/work/fix-pidstat-collector/dev_handoff]]
