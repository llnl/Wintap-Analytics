# Native OpenCode pidstat loop

**fpc-01/fpc-02 human-approved; fpc-03 technical checks complete, review pending.** OpenCode owns observe → hypothesize → change → verify.
The command loads a skill; `evidence.py` runs one concrete experiment and saves
results. No external agent controller, custom agent profiles, approval tokens,
configuration template or plugin is needed. The sampler/writer diagnostics live in
`../Lintap/pidstat-go/`; explicit durable collect/recover modes now exist, but no
package/service integration or release qualification is claimed.
See [verification.md](../../wiki/work/fix-pidstat-collector/verification.md) for the
three live Python captures, exact comparisons, static builds and arm64 execution.

## Start

After explicitly authorizing the intended Lintap edits and isolated guest work,
open OpenCode in **Wintap-Analytics** and enter:

```text
/pidstat-loop fpc-01: prove static Go binaries and Parquet compatibility; stop for human review
```

The [skill](../../.opencode/skills/pidstat-loop/SKILL.md) bounds each requested unit
to **three candidate revisions or 60 minutes**, unless you specify another budget.
It requires real Python evidence, records failed attempts and remaining budget in
[verification.md](../../wiki/work/fix-pidstat-collector/verification.md), and stops
after `fpc-01`. These are agent workflow instructions, not a scheduling controller.

For fresh-context review, open a **new** OpenCode session in Analytics:

```text
/pidstat-review fpc-01; inspect the source diff and evidence directories recorded in verification.md
```

This selects Plan in that new session; it does not create a reviewer itself.
Human approval is required before resuming with `/pidstat-loop fpc-02 ...`.
Commands reload automatically; `/reload` can force discovery if needed.

## Deterministic evidence utility

Run examples from the Analytics project root. Paths below are examples: resolve
the actual guest source/interpreter and approved binary locations first. There is
no automatic VM creation, package installation, binary transfer or service restart.

### Capture actual Python output (requires guest authorization)

```sh
python3 validation/pidstat-loop/evidence.py capture-python \
  --collector /absolute/guest/path/pidstat-collector.py \
  --python /absolute/guest/path/venv/bin/python --samples 3 --interval 5
```

Targets only existing **`lintap-dev`, Ubuntu arm64**. The explicit guest interpreter
must already have DuckDB; root does not call `uv`. The helper imports the actual
Python collector, runs its sampler/writer against live `/proc`, and uses a unique
root-private `/var/tmp/pidstat-reference-*` data/spool directory, not service data.
It retains raw reads (including failures), PID enumeration, namespace links,
sample times, clock/page/memory context, normalized snapshots, actual TSV/Parquet,
source/output hashes and Python/DuckDB/platform metadata. It rejects source changes
during capture. The host receives a bounded, safely extracted archive.

Declare approved idle/CPU/memory/I/O/churn/container workloads separately. This
command does not generate them. Three samples alone do not prove workload coverage.
Keep the reference source/revision fixed through acceptance.

### Exact replay comparison

Encode the captured `golden.tsv` in fpc-01; fpc-02 replays `capture.json` through the
Go sampler using `--replay ... --output NEW_ROOT --timezone America/Phoenix` (match
the reference timezone). Replay does not use normalized snapshots/TSV. It retains
source epochs for window assignment, separately from Python-style microsecond
timestamp rounding. Retain the candidate command, binary/source
hashes and input hashes alongside its output. Then:

```sh
python3 validation/pidstat-loop/evidence.py compare \
  --reference validation/pidstat-loop/evidence/CAPTURE/reference \
  --candidate /path/to/isolated/go-output
```

The utility verifies reference file hashes/row count and compares **all 26 raw
columns**, DuckDB-visible and physical schemas, values/nulls, row multiplicity,
partition membership and filename rotation-window epoch. Collision suffixes and
file bytes may differ. Output includes `python-rows.json`, `candidate-rows.json`
and `comparison.json`, with missing/excess rows and per-column mismatch/error counts.
Identity/partition/window changes appear as unmatched rows; their field-error
counts are not fabricated by pairing unrelated identities. Inspect these reports,
not just exit zero. Manifests are provenance records, not cryptographic attestations:
review must confirm the candidate actually used the recorded inputs/reference.

This exact checker is **not paired-live qualification**. Live alignment/tolerances,
resource measurements, soak/recovery and separate/mixed Wintap-PyUtil DBT checks
remain later implementation gates in the [plan](../../wiki/work/fix-pidstat-collector/implementation_plan.md).

### Static ELF and narrow startup checks

```sh
python3 validation/pidstat-loop/evidence.py static \
  --arm64 /path/to/linux-arm64-binary --amd64 /path/to/linux-amd64-binary

python3 validation/pidstat-loop/evidence.py smoke \
  --host-binary /path/to/linux-arm64-binary \
  --guest-binary /absolute/approved/guest/path/pidstat-collector
```

`static` inspects the actual executable ELF architecture, program headers,
`PT_INTERP` and `DT_NEEDED`; record the `CGO_ENABLED=0` build command separately.
`smoke` requires a matching host/guest hash, then executes `--help` as root with a
restricted system PATH in `lintap-dev`. It does **not** prove sustained sampling,
absence of child processes, recovery, service packaging, or RHEL runtime support.

### Record one test/build command

```sh
python3 validation/pidstat-loop/evidence.py record --timeout 300 -- \
  python3 -m unittest discover -s validation/pidstat-loop -p 'test_*.py' -v
```

Argument arrays run directly, without an implicit shell. `record` reports command
success, not collector acceptance. The utility saves argv, exit status, stdout,
stderr, timing and `result.json`. Exit codes: **0 PASS, 1 FAIL, 2 INCOMPLETE**
(argument/output-directory errors also exit 2). Missing dependencies/evidence never
count as PASS. A failed assertion and an infrastructure error have different status.

Default evidence directories are unique under ignored `validation/pidstat-loop/evidence/`;
optional `--output NEW_DIRECTORY` goes **before** the subcommand. Existing output
is never overwritten. Evidence contains private host/process data: keep it local.
No automatic cleanup or uncertain retry. Timeouts kill local client process groups;
guest work may still need inspection before retrying. Preparing this workflow does
not authorize sibling edits, guest operations, commits or deployment.

## Offline utility tests

Supplement (never replace) live captures with actual Python writer edge cases:

```sh
python3 validation/pidstat-loop/evidence.py record --timeout 120 -- \
  python3 validation/pidstat-loop/check_spike.py \
  --binary /path/to/host-native/pidstat-spike --output /path/to/new/fixture-evidence
```

This uses existing host DuckDB and the unchanged live Python writer to check
duplicates, two-decimal source formatting, large integers, null/empty attribution,
sanitized Unicode text and midnight windows. Its results are explicitly labeled
controlled writer fixtures, not live proc evidence. `workload.py` is a separately
approved bounded guest CPU/memory/I/O/churn stimulus, not a sampler or parity oracle.

Actual-Python sampler/configuration differential supplement:

```sh
python3 validation/pidstat-loop/evidence.py record --timeout 120 -- \
  python3 validation/pidstat-loop/check_sampler.py \
  --binary /path/to/host-native/pidstat-spike --output /path/to/new/sampler-fixtures
```

Tests raw reads/elapsed-time replay, PID reuse/baselines, counter resets and missing
fields, cgroup variants, kernel tick/page context, decimal/path config precedence
and timestamp/window boundaries against the actual Python source. It explicitly
records Python's malformed-optional-counter exception versus Go's planned per-process
skip. These are controlled-source fixtures, not substitutes for live raw captures.

```sh
python3 -m unittest discover -s validation/pidstat-loop -p 'test_*.py' -v
```

Actual Python legacy spool/durable raw replay differential:

```sh
python3 validation/pidstat-loop/evidence.py record --timeout 300 -- \
  python3 validation/pidstat-loop/check_spool.py \
  --binary /path/to/host-native/pidstat-collector \
  --reference /path/to/actual-python-capture --output /path/to/new/spool-check
```

This drives unchanged Python Collector methods on retained real live rows/sample
epochs, recovers equivalent current/pending/missing-meta spools in Go, compares all
26columns/multiplicity/partitions/windows and tests actual codec acceptance. It also
replays the captured raw reads through Go's durable sampler/spool/writer path.
`check_native_spool.py` runs separately in the approved root-private Ubuntu arm64
guest with its reference-only interpreter: native Python legacy spools, raw replay,
SIGTERM/SIGINT, SIGKILL restart, same-spool locking and an unchanged-input filesystem
conversion retry. It never modifies shared services/data. Use a fresh output root;
keep test source, logs, hashes, failed runs and decoded output. Shortened rotations
are not default-cadence/resource/paired-live/DBT/package qualification.

Basic tests use only the standard library. Writer/comparison tests need existing
host DuckDB and read the live `../Lintap/pidstat-collector.py`; they use controlled
rows, not live `/proc` or Go output. No dependency installation occurs. These tests
validate the utility only, and cannot close the feature's real Python/Go gates.
