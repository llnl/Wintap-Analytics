---
title: "Verification: Durable Process Entity Manager"
type: concept
confidence: medium
grounded_by:
  - wiki/work/durable-process-entity-manager/brief.md
  - wiki/work/durable-process-entity-manager/design.md
  - wiki/work/durable-process-entity-manager/implementation_plan.md
  - wiki/diagnostic/process-tree-context-completeness.md
  - wiki/workflow/process-ancestry-completeness-qa.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/tests/process_entity_context_integrity.sql
  - ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql
  - ../Wintap-PyUtil/tests/test_process_entities.py
  - ../Wintap-PyUtil/tests/test_process_entities_s3.py
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: reviewed
source_paths: wiki/work/durable-process-entity-manager
tags: [feature-work, verification, entity-state, ancestry]
---

# Verification: Durable Process Entity Manager

## Current result

### Durable processing checkpoint coverage — 2026-11-13

The hourly entity-enabled writer now maintains the dedicated sibling prefix
`<dataset>/processing_metrics/`, with one verified Parquet checkpoint per requested
UTC hour. The checkpoint schema includes operation/entity status, namespace and
expected-host count, snapshot identities, source/compacted process inventory
fingerprints, file/byte/row totals, deletion outcome and completion time. It is
separate from raw telemetry and from the durable entity snapshots.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py -->

DBT preflight now derives required hours from the selected `raw_process` raw or
compacted inputs and requires exactly one successful entity-enabled metric row for
each hour with the configured namespace and schema version. Missing, duplicate,
failed, or incompatible checkpoint coverage fails closed instead of consuming a
stale entity snapshot. A regression that removes the checkpoint files passed by
failing the DBT operation as expected.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

Focused verification after formatting/import cleanup:

* standalone compactor entity/CLI tests: **35 passed**;
* DBT durable-process-entity regression tests, including missing-checkpoint
  coverage: **12 passed**;
* changed standalone Python files pass `ruff format --check` and `ruff check`.

Commands:

```text
uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests/test_entities.py extras/raw-sensor-compact/tests/test_cli.py -q
uv run --project . --dev python -m pytest tests/test_process_entities.py tests/test_dbt_source_validation.py -q
uv run --project extras/raw-sensor-compact --locked ruff format --check <changed standalone Python files>
uv run --project extras/raw-sensor-compact --locked ruff check <changed standalone Python files>
```

A one-hour synthetic entity initialization also produced the expected fixed
Parquet schema and exclusive hour end (`00:00`–`01:00` UTC) under the local
`processing_metrics/` sibling. The opt-in S3 test was discovered and skipped
because its explicit isolated-write approval variables were not set.

The opt-in S3 qualification remains separate and was not treated as a local test
result; no live dataset or credential was written by this verification step.

### Bounded read-only on-prem fixture check — 2026-11-13

The selected `seeded_fixture_counts` test passed against the approved synthetic
one-hour fixture: **1 passed, 1 deselected in 2.18 seconds**. The expected
**24 rows** were present and the source/destination row delta was zero. A separate
read-only object listing found **24 source objects / 17,544 bytes** and **one
compacted object / 970 bytes**; neither listing was truncated. The pytest duration
includes process and test overhead and is not a pure network measurement.

The run used the approved Garage profile, endpoint and path-style access from the
on-prem development host. Only the read-only `verify` path ran; no S3 writes,
deletions, DBT, or access to preserved qualification data occurred. Dependencies
were installed into an isolated temporary environment outside the repository.
The fixture URI and profile values are intentionally omitted from this persistent
record. The archived laptop/VPN week aggregate is not an apples-to-apples baseline;
run this same bounded fixture check from the laptop before drawing a path comparison.

### Actual-data extension — run completed with failures, 2026-11-13

The human authorized several days/a week of testing after asking whether the
earlier real-data timeframe had been qualified. The earlier actual hour now passes
raw/mixed/compacted DBT and independent entity checks. The week driver completed
**168 hours: 165 successful raw compactions, 3 deletion-verification failures**.
Historical bootstrap failed identity validation; only **one combined entity/raw
hour** passed before the driver explicitly continued raw-only qualification.
This is not a successful week-long entity qualification or full historical DBT repair.

### Nov 7 compacted-only DBT build with durable enrichment — 2026-11-13

The completed mitigated Nov 7 destination was built with the repository's exact
`make dbt-build` target. The final invocation used the disposable source parent
(whose `raw_sensor` subtree was empty after successful deletion) together with the
240-file compacted destination; it did not union the immutable baseline with its
compacted copy. Durable enrichment used the retained nine-host snapshot root and
its declared identity namespace. `dbt-check-source` passed, including S3 listing,
Parquet access and schema preflight.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §dbt-build; ../Wintap-PyUtil/wintap_dbt/README.md §Durable process context -->
<!-- EVIDENCE: /tmp/opencode/dpe-nov7-mitigated/run.json; /tmp/opencode/dpe-nov7-mitigated/full-day-verify.json -->

The build materialized all **58 models** and evaluated **85 data tests**. Across
145 total DBT resources, **127 passed**, **17 were skipped**, and one errored. It
returned exit code 1 because the existing
`unique_selinux_interaction_event_id` test reported **19** duplicate rows. This
failure is unrelated to durable process context. The enabled
`process_entity_context_integrity` test passed, as did entity snapshot preflight;
no duplicate durable entity keys or invalid stored parent evidence were reported.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/tests/process_entity_context_integrity.sql; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql -->

Process-tree completeness **failed** on the retained week-limited state: the
`process_ancestry_quality` table contains **919,508** window seeds, of which only
**2** reached a root. The remaining verdicts are **908,487 missing ancestors**,
**2,861 parent conflicts**, **8,156 sentinel terminals**, and **2 missing
entities**. There were zero cycles, unresolved verdicts, or parent-PID mismatch
verdicts. The context relation independently reports 820,609 linked rows, 88,701
missing ancestors, 3,010 missing entities, 2,042 parent conflicts, 8,153
sentinels, and one root. Thus the optional enrichment executes and passes its
structural integrity gate, but this snapshot does **not** provide complete Nov 7
process trees; the previously documented stale week-limited state must not be
promoted to a production DBT input.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql -->
<!-- EVIDENCE: /tmp/opencode/dbt-nov7-mitigated/process-tree-validation-compacted-only.json -->

#### Investigation of the high missing-ancestor count — 2026-11-13

The **908,487** value is not a count of distinct missing parent processes. It is
one terminal verdict per window seed, so descendants sharing one broken ancestor
are counted repeatedly. In the direct context relation there are **88,701**
`missing_ancestor` rows but only **2,203** distinct missing parent keys. The top
one breakpoint accounts for **577,191** affected seeds; the top three account for
**800,504 (88.1%)**, and the top ten account for **876,276 (96.5%)**. This is the
same descendant-amplification pattern documented by the earlier short-window
audit; its absent-key metric explicitly was not a count of proven missing real
processes.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql; ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql -->
<!-- SYNTHESIS: wiki/diagnostic/process-tree-context-completeness.md; wiki/workflow/process-ancestry-completeness-qa.md -->

The durable cache nevertheless had **no effective coverage for this Nov 7
window**. All **33,824** loaded snapshot rows have `first_partition` and
`last_partition` equal to `2026110500`. Of **919,508** current process keys,
**zero** overlap a durable row; there are **zero** current-child-to-durable-parent
links; and the materialized `process_context` relation contains **zero**
`from_store` rows. The cache had rows, but they were stale state from the first
hour of the earlier week run, not a bootstrap/replay through Nov 7. Previous work
records that historical bootstrap failed identity validation and week maintenance
halted, and explicitly labels this nine-snapshot state stale and unsuitable for
production DBT input.
<!-- EVIDENCE: /tmp/opencode/dbt-nov7-mitigated/process-tree-investigation.json -->
<!-- SYNTHESIS: wiki/work/durable-process-entity-manager/verification.md §Completed week; wiki/work/durable-process-entity-manager/dev_handoff.md §Next, in order -->

The configured root-PID set was not the primary explanation: the current materialized
process graph contains only one self-parent root candidate (the PID-4 case) and no
PID-2 process records. The missing-root result is therefore consistent with absent
historical process context, not with counting every Linux PID-2 process as a gap.
The correct next experiment is a validated historical entity bootstrap/rebuild
covering the Nov 7 source, followed by the same direct-gap and breakpoint-impact
queries; no parent should be invented or repaired by PID alone.

### Intermediate milestone disposition — 2026-11-13

The three failed-hour partial outputs were compared with the retained immutable
local input evidence: all **25 compacted Parquet objects** match their corresponding
input rows exactly. The **142 source objects still present at final inspection**
also match their immutable copies. The three failed event/hour source prefixes were
empty on the later S3 inspection. The human accepts the failed-hour compacted data
as correct for this milestone and chooses to proceed on that assumption. This is
an operational disposition supported by the local evidence comparison; it does
not turn the three commands into successful runs, explain why immediate deletion
verification failed, or establish a reusable production deletion guarantee.

No production repair, additional mutation of qualification data, or DBT run is
authorized by this milestone. The original failure should remain visible in the
run record, while further root-cause work is optional follow-up rather than a
blocker to this intermediate handoff.

Read-only discovery located the original six-host materialized audit and its
explicit process globs for November 11 hours 08–22 (configured inclusive end 23).
An independent walk reproduces the earlier major breakpoint concentration. A
rebuild now uses a larger retained source inventory, so comparisons must distinguish
original saved populations from today's data and recorded-self-root policy from
the older PID-1/2/4 root convention.

Inventoried **71,155 objects / 5,958,506,820 bytes**: all nine available telemetry
families for **November 5–11**, plus process-only history **October 25–November 4**.
The frozen inventory excludes November 12/13 despite their discoverability.
Copying verifies each original inventory identity and SHA-256 against a full GET
of its isolated S3 copy; original keys are read-only. Planned tests cover the
earlier 08:00–09:00 hour, 168 sequential hours, historical bootstrap/default-budget
capacity, replay and DBT bronze/window/summary invariants. Failed hours/snapshots
will be retained rather than silently cleaned up or treated as passing.

Private scripts/inventories and ongoing evidence are retained at
`/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/dpe-actual-week-1vnezp50/`.
The first copy command hit its explicit two-minute harness timeout, then resumed
from already hash-verified copies without discarding data. An initial hour-harness
query referenced a nonexistent Refresh-count column; corrected to the model's
existing Start/Stop counters. These are harness repairs, not shipped-code changes.
No deployment, private environment edits, commits, pushes or output cleanup.

Human also requested compaction file-count/size metrics. The qualification harness
now aggregates validated leaf reports into overall, per-day, per-hour and per-event
input/output files and bytes, reduction percentages/factors, output-size distribution,
rows conserved, elapsed time and throughput. Entity snapshot bytes are separate.
Failed/partial outputs and untouched bootstrap copies are excluded from success
savings; byte expansion is reported as negative savings rather than hidden.
Metrics helper checks pass for reduction, expansion, grouping, throughput and
failed-command exclusion. Completed week aggregates and exclusions follow below.

#### Earlier real hour completed — November 11, 08:00–09:00 UTC

Fresh `earlier-hour` copy under the run root recorded in private `run.json`:
**399 original SHA-256 hashes unchanged**, copied sources verified before optional
deletion, all **2,668,265 rows** preserved across nine families/ten protocol leaves.
Current disabled baseline builds **54 models/140 gates**; entity-enabled raw,
mixed and compacted each build **58 models/145 gates**. Bronze/schema comparisons,
all host-level Start/Stop counts and **40,982 process/summary seeds** are preserved.
Four accepted ANY_VALUE-reachable downstream differences are recorded per migration
state, not hidden as equivalence: `file_chart`, `process_file`,
`process_file_summary`, `telemetry_event_summary`.

One-hour entity init/replay/GET verification and combined migration pass with
**40,982 entities**, **86 direct parent conflicts**, five snapshots/**3,277,708 bytes**.
Terminal QA reports 40,893 missing-ancestor seeds and 89 parent-conflict seeds
(including descendants of conflicting entities). Zero recorded-root-reached seeds:
this deliberately hour-only state is **not** a successful historical ancestry
repair, nor proof that full bootstrap would solve never-collected ancestors.
Raw and compacted-only replay are semantic no-ops. Entity init took 70.66 seconds;
raw replay 41.86 seconds, compacted replay 12.18 seconds, verify 3.88 seconds.

Measured raw compaction (decimal MB; entity storage excluded):

| Metric | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Files | 399 | 10 | 389 / 97.49% / 39.9× |
| Bytes | 35,471,263 | 32,792,809 | 2,678,454 / 7.55% |
| Rows | 2,668,265 | 2,668,265 | None; all preserved |

| Family | Files before → after | MB before → after | Byte saving |
| --- | ---: | ---: | ---: |
| pidstat | 24 → 1 | 2.339 → 7.892 | **−237.44% (expansion)** |
| host | 5 → 1 | 0.038 → 0.009 | 75.39% |
| MAC/IP | 5 → 1 | 0.010 → 0.003 | 71.67% |
| process | 114 → 1 | 5.697 → 3.292 | 42.21% |
| network (TCP/UDP) | 114 → 2 | 1.380 → 0.450 | 67.38% |
| file | 57 → 1 | 20.028 → 15.522 | 22.50% |
| SELinux AVC | 22 → 1 | 0.088 → 0.007 | 91.61% |
| SELinux interaction | 35 → 1 | 5.803 → 5.609 | 3.34% |
| SELinux transition | 23 → 1 | 0.089 → 0.008 | 91.13% |

Two successful combined commands total **238.10 seconds**, approximately 11,207
rows/second including entity no-op validation, raw validation and deletion; not a
pure writer benchmark. Source mean size 88,900 bytes; output mean 3,279,281 bytes.
Raw compacted plus entity storage is **36,070,517 bytes / 15 files**: adding the
new dimension makes this hour's combined storage 1.69% larger than raw alone,
despite the raw compaction saving. Full historical dimension growth remains separate.

#### PIDstat size diagnosis / local layout experiment

Read-only Parquet metadata shows raw pidstat: **24 row groups**, 28,005–46,335
rows/group; compacted: **426 row groups**, 424–3,745 rows/group. Both use ZSTD.
Shipping COPY requests `ROW_GROUP_SIZE 2048`; the changed layout is a credible
explanation for byte expansion, not a codec upgrade or row-count change.

A controlled **local-only DuckDB 2.0.0** rewrite of the same 897,390 pidstat rows
measured one output per candidate:

| Requested row-group size | Output bytes |
| ---: | ---: |
| 2,048 | 7,969,344 |
| 32,768 | 1,699,092 |
| 122,880 | 1,122,558 |
| 524,288 | 1,013,378 |

Counts and all-column row-hash sums match each candidate. These are local layout
measurements (input materialized once), not full multiset proof or S3 timings.
No shipping setting or S3 output was changed: larger row groups are a measured
tuning opportunity, not silently adopted during this qualification.

Private evidence: `hour-summary.json`, `hour-compaction-metrics.json`,
`hour/<state>/{snapshot,metrics,comparison}.json`, `pidstat-layout-evidence.json`
and `pidstat-layout-ab/evidence.json` under the previously recorded run directory.
At this earlier-hour checkpoint, seven-day results were pending; completed results
are recorded below.

#### Seven-day execution started / independent real-hour checks

Full copy preparation has completed: all **71,155 objects / 5,958,506,820 bytes**
have immutable inventory identity and original-versus-copy SHA-256 verification.
The resumed command took 1,628.44 seconds, in addition to the earlier timed-out
attempt; this is copy/verification time, not compaction throughput. The sequential
historical-capacity and 168-hour driver subsequently completed as recorded below.

Independent raw SQL reduction of the earlier hour's **114 physical process files**
matches the **40,982 persisted entities** exactly as a multiset over hostname/hash,
OS PID, paired parent fields/status, identity status, birth/Stop FILETIMEs,
lifetime status and Start/Refresh/Stop flags. A separate iterative Python graph walk
matches every per-host terminal ancestry-status count from DBT. Evidence:
`hour-independent-verification.json`. This verifies real evidence reduction and
QA correctness, without claiming historical ancestors exist in hour-only state.

#### Completed week — November 5–11 UTC, 2026-11-13

`qualify_week.py` completed all 168 selected UTC hours. **165 passed** their
reported schema/partition/count/inventory/deletion gates; **3 failed** immediate
source-deletion verification. Recomputed metrics match the saved final totals.
All successful leaves report `passed=true` and zero row delta. Final read-only S3
listing independently matches the **1,650 successful-hour files / 4,623,379,532
bytes**. Final full-GET reread confirms **all 71,155 original SHA-256 hashes unchanged**.

| Successful-hour raw metric | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Parquet files | 53,415 | 1,650 | 51,765 / **96.91% / 32.37×** |
| Bytes | 4,841,533,292 | 4,623,379,532 | 218,153,760 / **4.51%** |
| Rows | 360,027,830 | 360,027,830 | None; all count-preserved |

Successful command time totals **23,691.38 seconds / 6.58 hours**, including
configured validation/deletion and the first hour's entity phase: **15,197 rows/s**,
0.204 decimal MB/s. Mean hour 143.58 seconds; median 138.48; nearest-rank p95
181.11; range 119.16–192.29 seconds. All compact attempts, including the three
deletion failures and failed combined attempt, took 24,094.42 seconds. Copy,
bootstrap, initialization, DBT and final rehash time are excluded from these
compaction timings. This is sequential end-to-end test performance, not a pure
writer benchmark or production capacity certificate.

Mean file size rises from 90,640 to 2,802,048 bytes; output median 240,707 bytes,
p95 11,300,308 and maximum 17,870,355. The fixed hour/family/protocol boundaries
still produce many small files despite the 128 MiB target; no cross-hour merging.

Daily breakdown excludes each failed hour in its entirety (decimal MB):

| UTC day | Passed hours | Files before → after | MB before → after | Byte saving |
| --- | ---: | ---: | ---: | ---: |
| November 5 | 23 | 7,080 → 230 | 698.464 → 659.990 | 5.51% |
| November 6 | 24 | 7,491 → 240 | 729.302 → 690.136 | 5.37% |
| November 7 | 24 | 7,360 → 240 | 788.009 → 740.919 | 5.98% |
| November 8 | 24 | 7,147 → 240 | 739.331 → 701.433 | 5.13% |
| November 9 | 23 | 7,222 → 230 | 603.931 → 584.780 | 3.17% |
| November 10 | 24 | 7,493 → 240 | 639.417 → 630.301 | 1.43% |
| November 11 | 23 | 9,622 → 230 | 643.079 → 615.821 | 4.24% |

| Family | Files before → after | MB before → after | Byte saving |
| --- | ---: | ---: | ---: |
| pidstat | 3,960 → 165 | 467.563 → 1,395.968 | **−198.56% (expansion)** |
| host | 690 → 165 | 4.959 → 1.346 | 72.87% |
| MAC/IP | 686 → 165 | 1.441 → 0.451 | 68.67% |
| process | 15,097 → 165 | 830.075 → 482.944 | 41.82% |
| network (TCP/UDP) | 12,910 → 330 | 175.335 → 61.754 | 64.78% |
| file | 6,454 → 165 | 2,586.247 → 1,978.081 | 23.52% |
| SELinux AVC | 3,826 → 165 | 15.405 → 1.248 | 91.90% |
| SELinux interaction | 5,881 → 165 | 746.053 → 700.405 | 6.12% |
| SELinux transition | 3,911 → 165 | 14.455 → 1.183 | 91.81% |

All **165 pidstat leaves expanded**. Other families combined shrink from
4,373,969,817 to 3,227,411,221 bytes (**26.21%**). Earlier local layout evidence
identifies a tuning opportunity; no row-group setting or remote output changed.
Week gates prove row-count conservation and reported validations, not an independent
all-column multiset comparison over all 360 million rows or week-wide DBT equivalence.

#### Failure diagnosis, storage separation and remaining gates

Identity guard inspection of immutable local `raw_evidence` finds **81 negative-PID
Refresh observations** and **15 sentinel-key Stop observations with positive PIDs**
across the expanded history/week. **32 rejected observations** precede November 5;
November 5/hour 01 contains two PID −1 Refresh observations, explaining the
combined-mode stop. These match the
existing fail-closed predicate, not permission to filter evidence or repair by PID.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §unknown/load_inputs -->

Historical default bootstrap fails before publication on this identity guard,
**not demonstrated capacity exhaustion**. Independent full October 25–November 11
SQL inventory counts 13,688,390 host-scoped identities; **two hosts exceed the
one-million-row default**. This full expanded count is not
a measured initialized snapshot or the exact pre-week bootstrap cardinality.
Identity policy, large-host memory/row/byte budgets, complete historical bootstrap,
original audit-window DBT comparison and external writer/reader exclusion remain
unqualified. No silent pruning, budget increase or source-code repair was applied.

The separate week-limited init succeeds from November 5/hour 00 with **33,824
entities / nine snapshots / 2,730,739 bytes**, including five acknowledged empty
hosts. The one combined hour is a no-op update of that state; subsequent hourly
entity maintenance halted. This retained dimension is **stale, not a week-complete
snapshot** and must not be promoted to a DBT production input.

Deletion failures all report phase `delete_source` / "Source prefix remains after
deletion; manual repair required":

| UTC hour | Event whose immediate deletion check failed |
| --- | --- |
| November 5 / 06 | raw_process_conn_incr |
| November 9 / 11 | raw_selinuxtransition |
| November 11 / 20 | raw_selinuxinteraction |

All three exact failed event/hour prefixes are empty on the later read-only listing.
A transient/stale listing is possible, but **not established** from the available
request evidence. Their commands remain failed; later emptiness does not certify
the entire hour or waive manual reconciliation. Existing-output skips make a blind
rerun inappropriate. Preserved across failed hours: **25 partial compacted objects /
60,900,907 bytes** and **142 unprocessed source objects / 28,481,517 bytes**.
Remaining inputs are November 5/hour 06 file/SELinux families (118 files) and
November 11/hour 20 SELinux transition (24). November 9/hour 11 has no inputs left,
but its failed command still lacks a successful full-hour report.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py §delete_hour -->

#### Controlled Garage delete diagnostic — synthetic isolated prefixes

Two isolated synthetic runs against the current Garage S3 endpoint exercised the
real compactor at the historical input-object counts. The 72-object case retained
the 36-TCP/36-UDP shape; the other cases used 24 and 35 objects. In all three
baseline cases, `DeleteObjects` returned HTTP 200 with no per-object errors and
zero retries; the immediate prefix listing was empty. The outputs matched all
synthetic input rows exactly as multisets (72, 24 and 35 rows respectively).

A separate four-object case injected one synthetic marker **after** a successful
`DeleteObjects` response and before the compactor's immediate prefix check. The
check found exactly that marker, and the CLI returned the same
`Source prefix remains after deletion; manual repair required` error in
`delete_source`. Its four original rows still matched the compacted outputs.
This validates the failure path and shows that an object arriving in that interval
can produce the message; it does **not** show that this was the historical cause.
The ordinary cases did not reproduce an unexplained Garage deletion/listing error.

Garage's responses exposed no request ID or `x-amz` correlation header to the
client (only content/date headers). The harness cleaned its isolated prefixes;
an independent final listing found zero objects. No Garage logging configuration
was changed. The harness and detailed reports are temporary laptop artifacts,
not committed qualification data.

**Potential follow-up, not part of the accepted milestone:** if root-cause evidence
is needed later, rerun the same level of test from the on-prem development host on
a new synthetic prefix while Garage debug logging is enabled on every node. Record
server-side delete/list sequence and timing, compare any available correlation
metadata, retain the exact object found by the immediate check, and verify cleanup.
The current client response has no request ID, so server-side logs are needed for
useful correlation. Keep this distinct from a read-only performance comparison;
do not retarget the test to production or mutate the preserved qualification copy.

Final test-root storage accounting, deliberately not all claimed as compacted savings:

| Storage class | Objects | Bytes |
| --- | ---: | ---: |
| Successful week raw outputs | 1,650 | 4,623,379,532 |
| Failed-hour partial raw outputs | 25 | 60,900,907 |
| Remaining week raw inputs | 142 | 28,481,517 |
| Untouched pre-week process copies | 16,723 | 1,028,909,068 |
| Week-limited entity snapshots | 9 | 2,730,739 |
| Separate earlier-hour outputs plus entities | 15 | 36,070,517 |

Private evidence under the recorded run directory: `week-summary.json`,
`week-compaction-metrics.json` (overall/day/hour/event), `history-preflight.json`,
`week-reports/*.json`, `original-recheck.jsonl`, `week-final-object-inventory.json`
and `week-final-inspection.json`. Executed: main-env `.venv/bin/python
<run-dir>/qualify_week.py`; isolated locked writer invoked by that harness;
main-env read-only Python metric recomputation/validation and SDK final listing;
read-only DuckDB inspection of `independent-history.duckdb`. No main/standalone
runtime mixing, original mutations, private environment edits, commits, pushes,
cleanup or production deployment. Failed-hour reconciliation and identity-policy
changes require a bounded follow-up rather than relabeling this run as passing.

Final documentation checks pass: `git diff --check`; three updated frontmatters,
24 grounding paths and six wikilinks; independently summed day/event/hour metrics
all match overall file/byte/row totals, and rejection-category counts match the
read-only diagnosis. These are scoped checks, not a whole-wiki lint.

Milestone commit authorization received November 13. Fresh pre-commit targeted
checks pass: main `.venv/bin/python -m pytest -q tests/test_process_entities.py`
**11 passed (37.86 seconds)**; isolated standalone `uv run --locked pytest -q
tests/test_entities.py` **25 passed (1.06 seconds)**. No additional S3 writes or
full-suite rerun; earlier full-suite evidence remains recorded below. Handoff:
[[wiki/work/durable-process-entity-manager/dev_handoff]].

Implementation committed as Wintap-PyUtil `2cfbad1` (25 scoped files) on
`work/raw-sensor-compacted-union`; private `wintap-run.env-lintap-alpha` and
`wintap-run.env-micro-range` remain untracked/excluded. That implementation branch
is unchanged by the Garage diagnostic. The current Analytics handoff/wiki update
is a separate documentation commit; no Wintap-PyUtil commit or push is included.

First-round implementation is complete in Wintap-PyUtil following the human's
explicit "Proceed!" instruction. The standalone writer remains DuckDB 2.0.0;
DBT remains 1.5.6. Canonical facts:
[[wiki/tool/durable-process-entity-manager]]. No production bootstrap/cutover or
scheduler deployment; no original telemetry or private run-env modifications.

Current regression results: **132 passed, 2 skipped** in the standalone extra;
**310 passed, 3 skipped** in the main suite. Main collection now intentionally
excludes the isolated extra, whose dependencies/runtime must not enter DBT's env.
The previous generic root-wide collection failed for that reason; `testpaths`
now expresses the intended isolation. Optional pre-existing/live tests remain
skipped unless explicitly authorized; the entity S3 test was run separately.

Actual S3 synthetic qualification passed completed snapshot replacement, no-op
replay, full GET verification, entity-before-delete migration and compacted-only
replay/DBT. Final read-only DBT qualification passes **58 models/145 gates**, with
**33 root-reachable window seeds, 33 summaries, 36 durable entities and 2 context-only
ancestors**. Original hostname spelling is preserved in window outputs after a
new summary-population assertion exposed and fixed a normalized-host join bug.

## Research and source review (pre-implementation baseline)

Read the durable-process concept, optional process-context note, refresh tension,
anonymized ancestry audit, runtime-retention page, identity conventions and
ancestry QA. Read live PyUtil compaction, bronze process, silver process/path,
and gold process-summary SQL.

Confirmed integration boundaries:

- Raw `process_hours` skips an existing destination before source discovery and
  deletes only after its current leaf/inventory checks. State ingestion therefore
  needs a separate phase; raw skip cannot become a state completion checkpoint.
- Bronze `stg_raw_process` performs window filtering and duplicate accounting;
  historical entity rows must not be inserted there as raw observations.
- Silver `process` uses ANY_VALUE for parent/hash and metadata, and counts both
  Start and Refresh. A non-null arbitrary parent is not automatically correct.
- `process_path` currently seeds and joins only `process`, in hostname scope;
  a separate durable/context lookup is needed for out-of-window ancestors.
- Gold `process_summary` is seeded from `process`; adding all historical context
  as seeds would change summary populations and requires an explicit contract.

These facts describe the original/disabled-mode baseline. Current opt-in behavior
adds a separate entity phase/context lookup; no historical rows enter raw bronze.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql; ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql -->

## Planning and implementation verification

### Planning validation — 2026-11-12

- `git diff --check`: passed.
- Read-only `python3` scoped structural check: passed **7 frontmatters, 35 local
  grounding paths, 25 wikilinks and 4 feature index entries**. This checks required
  keys/path/link existence, not full YAML typing or whole-wiki health.
- Reviewed all four feature artifacts for consistency; added explicit cross-phase
  process inventory binding before source deletion and file metadata for typed
  empty host snapshots. These remain design requirements, not tested behavior.

No entity implementation tests or S3 qualification had been run at that planning checkpoint.

### Executed commands and evidence — 2026-11-12

- Extra: `.venv/bin/python -m pytest -q`, followed by `uv run --locked pytest -q`:
  **132 passed, 2 skipped**. Reducer permutations/duplicates/Stop replay, PID reuse,
  host isolation, empty metadata, missing-state/unknown identity, resource failures,
  cross-phase new/changed/removed input, raw COPY failure after state publication,
  partial hosts/init-resume and mocked lost-ACK/corrupt publication all pass.
- Main: `.venv/bin/python -m pytest -q`: **310 passed, 3 skipped**. Entity fixture
  tests use the nested locked UV runner, never import the writer into DBT's env.
  Full raw/mixed/compacted builds test known ancestry and preserve window counts;
  extra targeted locked tests verify the final entry point/metadata enrichment.
  Final targeted `uv run --locked --dev pytest tests/test_process_entities.py -q`:
  **11 passed**.
- Live synthetic: `RAW_ENTITY_S3_TEST_APPROVED=isolated-write`,
  `RAW_ENTITY_S3_TEST_PROFILE=lintap-alpha`, and a new
  `RAW_ENTITY_S3_TEST_ROOT` with main pytest `tests/test_process_entities_s3.py -q -s`:
  **1 passed in 67 seconds**. Completed replacement/no-op replay, fixture hashes,
  DBT builds and entity-before-delete migration verified. Initial builds had
  144 gates before the subsequently added context-integrity gate.
- Final current-code read-only build of retained S3 fixture: **58 models/145 gates**,
  33 complete seed paths and 33 summaries. Evidence/database/compiled SQL retained
  at `/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/dpe-final-s3-read-kjwzgceo/`.
- `git diff --check` passes in PyUtil and Analytics. No commits/pushes requested
  or performed for this feature; private run-env files stay untouched/untracked.
- Final scoped wiki check: **10 parsed YAML frontmatters, 61 local grounding paths,
  47 wikilinks**, all passed. Final locked reducer/store test: **25 passed**.

### Fixture model and repair iterations

Fixtures independently declare a historical root and exited bridge, 33 selected
lifecycle seeds, and one activity-only key whose lifecycle is outside the window.
Known expected chains are `[child, bridge, root]`, not derived from production SQL.
Replayed duplicates/overlapping archives add no state. In mixed raw/compacted
facts, bronze `num_dups` reflects the overlap; legacy lifecycle counts remain
counts of grouped window observations, not raw duplicate copies or entity history.
Context-only ancestors/activity-only keys do not become summary seeds.

Negative graphs cover incompatible paired parents, a never-collected ancestor,
non-root cycles and a non-root self-link. Root policy requires consistent recorded
self-parent evidence plus the declared root PID set (default 0/1/4, dataset/OS
review required). Missing nodes never appear as fabricated path steps.

During verification, corrected fixture-only physical-column casing (the shipping
schema gate properly rejected drift), corrected a duplicate-folding test expectation,
and repaired the real uppercase-output hostname/host-summary join regression by
normalizing lookups while preserving window hostname payloads. Initial Black
check reported formatting differences; no passing formatter check is claimed.

### Exact S3 scope and retained artifacts

All S3 input was generated, not copied from original telemetry. Exact root:
`s3://lintap-alpha/entity-tests/dpe-20261112-e6a7a0f0-c1b8-43c5-a4ae-5560eed3d78f`.
Verified **32 generated source hashes unchanged** before intentional migration;
the combined job then validated and deleted those **32 generated sources**.
Retained **14 compacted outputs plus 1 entity snapshot**, **48,182 bytes total**;
the 36-entity snapshot is **5,843 bytes**. Zero raw fixture objects remain.
No broader bucket operation, original key access/deletion or output cleanup.

Real endpoint qualification covered normal completed PUT replacement/GET, not
actual network-interruption atomicity or concurrent readers. Lost acknowledgment
and corrupt content were injected with mocks. External writer/reader exclusion
remains mandatory; no multi-host transaction guarantee is claimed.

| Gate | Required evidence | Status |
| --- | --- | --- |
| Schema/reducer | Cross-version Parquet, order/replay equivalence, paired conflicts/Stop/PID reuse | Passed |
| Local persistence | Fresh-worker recovery, empty/missing-state guard, no-op, init-resume and budget failures | Passed |
| S3 publisher | Actual completed replacement/GET; mocked lost response/corruption; no original access/deletion | Passed within stated limits |
| Combined job | Publication failure/input drift blocks deletion; raw failure/skip/replay contract | Passed |
| DBT | Historical/exited ancestors, context-only counters, deterministic edges, flags and disabled regressions | Passed |
| Graph QA | Independently specified bridge/root/missing/conflict/cycle fixtures | Passed; broad K95/concentration audit remains separate |
| Capacity/operations | Fixture measured; budget failures and rebuild tested; production-scale resources and schedule exclusion | Production review outstanding |

Save fixture input identities, expected semantic entities, output hashes, state
publication report, DBT schemas/rows/lineage QA and source immutability results.
Do not confuse raw row conservation with entity count conservation: this reducer
intentionally collapses repeated evidence and needs full-content/graph assertions.

## Known limitations pending review

Full retained history grows per-host snapshots. Partial/missing original archives
limit bootstrap and rebuild completeness. Fixed host files have no multi-host
transaction or historical as-of snapshot guarantee. Parent contradictions and
never-collected ancestors remain gaps. These limits must be visible to consumers.
