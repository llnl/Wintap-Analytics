---
title: "Sample database QA: orphan explosion and runtime attribution theory"
type: diagnostic
confidence: high
grounded_by:
  - /Users/johnson30/git/axon-aegis-micro-range/data/lintap/duckdb/wintap.duckdb
  - wiki/work/host-process-identity-patch/sample_db_audit.py
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
  - ../Wintappy/wintap_dbt/qa/pid_hash_orphan_checks.sql
  - ../Wintappy/wintap_dbt/models/schema.yml
  - ../Wintappy/wintap_dbt/models/gold/process_file_summary.sql
  - ../Wintappy/wintap_dbt/models/gold/process_summary.sql
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs
  - ../wintap/wintap/core/infrastructure/health/DefaultHealthChecks.cs
policy: human-review-required
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/host-process-identity-patch; ../wintap/wintap/platform/linux; ../Wintappy/wintap_dbt
tags: [data-quality, attribution, orphan, linux, runtime, pid-hash, unknown-users]
---

# Outcome

<!-- REVIEW NEEDED: audit provenance updated for user-approved condensation; factual findings unchanged. Original JSON is local/uncommitted and retained in the verified external archive. -->

**The supplied historical database fails attribution and downstream aggregation QA.**
The largest defect is not a missing-value problem: apparently valid MD5 identities
were manufactured from individual file-event and exit timestamps. Process linkage
then cannot work, even when hostname/PID are known. This is independent of the
duplicate AgentId defect in [[wiki/diagnostic/duplicate-agent-id-and-os-family]].

Database owner/data location: `axon-aegis-micro-range`; Windows/Linux sensor and
runtime owner: **Wintap**; canonical downstream SQL owner: **Wintappy**;
audit artifacts: **Wintap-Analytics wiki**. Lintap supplies Linux packaging/support.

## Reproduction and scope

Run from Wintap-Analytics:

```bash
/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/smoke-dashboard-venv/bin/python \
  wiki/work/host-process-identity-patch/sample_db_audit.py
```

The successful run began at `2026-10-24T01:31:08.993732Z` (Oct 23 local;
timestamp is in the results JSON). It opens an in-memory DuckDB connection,
attaches the supplied DB **READ_ONLY**, and snapshots its existing relations in
memory. No DBT build, database write, historical repair or host/service change.
Database size/mtime remain unchanged. SQL/full returned rows remain in local,
uncommitted `sample_db_audit_results.json` and the verified archive documented in
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]]. The concise feature
record is [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]].

**98 recorded checks**, including the canonical orphan/primary-key SQL,
**38 applicable schema-test equivalents (all zero failures)**, and the current
network-name gate (zero violations). These are read-only SQL equivalents, **not**
a claim that `dbt test` or all runtime/unit tests ran against this database.

The staging views are already deduplicated: `num_dups` preserves input multiplicity.
Staging counts are 17,497 process observations, 355,566 file rows, and 28,864
network increments. Silver `process` contains exactly the same 12,643 distinct
hashes as raw process staging; there is no missing silver-process key set.

## Attribution and lifecycle results

| Check | AXON-TARGET | CALDERA-HOST |
|---|---:|---:|
| Silver process identities | 8,927 | 3,716 |
| Stop-only identities (no Start/Refresh) | 6,045 | 2,023 |
| Identities with both birth observation and Stop | 1,853 | 745 |
| Start/Refresh only | 1,029 | 948 |
| Parent hash has no same-host process entity | 4,228 | 1,279 |
| File orphan rows / total silver file rows | 26,207 / 146,182 | 63,118 / 183,411 |
| Distinct orphan file hashes | 25,635 | 55,048 |
| Network orphan rows / total silver increments | 50 / 3,783 | 0 / 3,774 |

Overall file orphan rate: **27.10%**, involving **80,683 distinct hashes**.
Stop-only identities are **63.81%** of process entities. Missing parent entities
affect **43.56%**. Missing parents are also present among processes with actual
birth observations (1,135 AXON / 403 CALDERA), not just Stop-only rows.

Orphans propagate to `process_file_summary` (80,684 rows), `process_net_conn`
(12 rows), and `process_net_summary` (6 rows). All six network orphan hashes occur
on AXON and include historical agent/capture segments. Empty registry/image models
pass only vacuously; they do not establish collection support.

No cross-host/PID collision within the audited raw hash groups, self-parent,
parent-PID disagreement on matched links, lineage cycle, negative known lifetime,
or gross activity-outside-known-lifetime violation was found. Maximum observed
lineage depth is eight. Missing parent hashes are distinct from missing entities
(four empty/null parent hashes overall).
<!-- GROUND_TRUTH: wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §archived sample_db_audit_results.json: canonical_orphan_qa_0; parents; graph_cycles; process_by_host; current_vs_raw_process_keys -->

### Exact hash evidence

The QA oracle retains integer FILETIME arithmetic and checks historical
two-stage MD5 preimages with lower-case collection hostname and recorded AgentId.
This is an independent diagnostic calculation, not another production definition.

- All **6,409 Start** and **422 Refresh** observations match the historical
  hostname/AgentId/PID/EventTime formula. For these rows EventTime is used as StartTime.
- **8,042 of 10,666 Stops** match the same formula using **exit EventTime**.
  This almost accounts for all 8,068 Stop-only identities; it proves timestamp-input
  misuse for those 8,042 rows, not that every remaining Stop-only row has that cause.
- **80,409 unknown-owner file rows** match the historical formula using
  **FirstSeen**, each with a distinct hash and no raw process entity. Of those,
  25,501 are AXON and 54,908 CALDERA. This explains the overwhelming majority of
  orphan hash cardinality directly, rather than inferring missing process records.
- CALDERA PID **16464** has **11,763 unknown file rows / 11,763 hashes** in
  **0.574 seconds** at 2026-10-23 13:13:53–13:13:54 UTC. It has a `mandb` Stop,
  but no recorded birth. Ordinary PID reuse cannot explain this explosion.
- Remaining named-owner file orphans: **10,017 raw rows / 274 hashes**. None of
  their PIDs has a recorded same-host Start/Refresh anywhere in the process table.
  Missing birth capture, unexported resolver state or a coverage boundary remains
  plausible; these are not explained by the unknown-event-hash calculation.

The table contains pre-patch identities; these results do not test `pid-v2`
deployment. Preserving distinct old/new capture boundaries remains necessary.
<!-- GROUND_TRUTH: wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §archived sample_db_audit_results.json: hash_formula; file_event_time_hash; unknown_file_hotspots; known_file_orphan_pid_coverage -->

## Unknown users, names and duplicates

`unknown-3` is a **debug fallback**, not evidence of an actual Linux user account.
Git source history (`d183e02`, ExecveSensor) introduced that literal when
`procData.Username` was null. Older ProcReader read username from `USER=` in
`/proc/<pid>/environ`; absent environment or a process exiting during enrichment
could therefore produce it. Current ExecveSensor falls back to numeric UID lookup.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; git d183e02 at the same live source path; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §ReadEnviron; §LookupUsername -->

In this DB it occurs in **six deduplicated Start observations / four hashes /
three PIDs**, all AXON, older agent `aa582ab7-3a2f-428b-904e-891590b2e27a`,
on **Oct 19**, not the newer Oct 22–23 segment. Preserved duplicate multiplicity
makes ten original observations. Two hashes for PID 36035 differ by **one 100ns
tick**, indicating a separate historical time-canonicalization split.

All raw Stops omit username; ProcessStopSerializer intentionally does not serialize
it. Thus raw null Stop users are not by themselves failed UID lookup. The **8,068
null silver users** belong exactly to Stop-only identities missing birth metadata.
Also **267 Refresh observations** use `"0"` rather than `root`: rundown allows
numeric UID fallback; mixed representation should not be mistaken for a new user.

Input has **3,820 duplicate Start observations beyond staged rows**, plus
**1,190 process identities with multiple birth observations**. Clone/exec/image
changes can legitimately produce multiple observations under one lifetime hash;
duplicate ingestion versus producer duplication needs recording/log evidence.
**567 process hashes have multiple names**, and 11 have multiple parent hashes.
`socket:[...]` process names and `/proc/self/fd/socket:[...]` process paths warrant
memfd/fexecve/symlink-context QA, not automatic classification as fake processes.
There are also **566 `kworker/dying` Stop-only identities**: possible kernel-task
or thread lifecycle coverage, not proof of 566 ordinary user processes.
<!-- GROUND_TRUTH: wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §archived sample_db_audit_results.json: unknown_user_details; numeric_uid_zero; stg_raw_process_basic; pseudo_processes; ../wintap/wintap/core/etl/extract/ProcessStopSerializer.cs -->

## Other QA defects

These describe the **unchanged supplied database and audit-time source**. Subsequent
candidate SQL projections fix file counters, the sample's summary fanout, duration
and network vocabulary without rewriting this database. New gold uniqueness tests
now detect the old fanout. See [[wiki/work/host-process-identity-patch/experiment_results]].

- **Summary fanout:** `process_summary` and `process_uber_summary` each contain
  **13,400 rows for 12,643 hashes**, or **757 extra rows**. File summaries group
  by name/agent/host/hash; network summaries also retain multiple names. Joining
  those relations only on hash is not guaranteed one-to-one. Current schema tests
  do **not** require unique hashes in the gold summaries, so they miss this defect.
- **File counters:** silver retains **344,113 Read / 99,699 Write / 136,405 Close /
  7,921 Delete events**, but corresponding gold counters and read/write bytes are
  **all zero**. Current gold SQL compares uppercase literals to title-case recorded
  names. Open events are also outside the existing gold-counter vocabulary.
- **Duration:** **195 of 3,283 terminated gold rows** differ from elapsed duration
  by more than 1ms; maximum error **41,220 seconds**. SQL uses `millisecond(interval)`
  rather than full elapsed epoch seconds. Counts are gold rows, not unique processes.
- **Network counters:** all **7,557 silver network increments** have the audited
  basic counters NULL despite nonzero events. The recorded names pass today's
  vocabulary gate; this materialized DB has older incompatible counter logic.
- **Orientation:** all **14,123 TCP receive staging rows**, plus all 60 UDP receives,
  label an IP absent from host inventory as local. Historical IP inventory is
  incomplete, but the receive-only systematic pattern supports the known reversal.
  No canonical connection hash contains multiple different unordered five-tuples.
- **Receive bytes:** TCP receive totals are about **15.45 GB** versus **12.20 MB**
  sent; all 60 UDP receive rows have zero bytes. TCP kprobe code records requested
  `tcp_recvmsg` buffer length at entry (often 262,144), not successful returned bytes,
  and rate-limits observations. These totals are **not measured wire-byte totals**;
  counter-name/endpoint fixes alone cannot repair that producer meaning.
- **Partial endpoints:** 330 UDP Send rows have zero IP and port; 15 Disconnect
  and two TCP Receive rows have zero ports. None has ports outside 0–65535,
  missing conn_id, negative byte counts, nonpositive event counts or reversed ranges.
- **Paths:** 8,988 raw file paths are not Linux-absolute; 636 contain socket/pipe/
  anon-inode markers. Separate relative-path resolution from legitimate nonregular
  descriptors. Current health `path_unqualified` check is **Windows-shaped** and
  rejects valid `/...` Linux paths too; do not report its literal result as Linux QA.
- **Metadata/observability:** both hosts share AgentId and are mislabeled Windows;
  host rows have OS `NA`, LastBoot=0, versions `0.0.0.0`, Collectors=NULL. All
  **17,497 raw process ReceiveTime values are zero**. Raw File/Network EventTime is
  Unix serialization time; FirstSeen/LastSeen carry occurrence time. Their difference
  measures event-to-serialization lag, not ring-buffer delivery or drops.
<!-- GROUND_TRUTH: wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §archived sample_db_audit_results.json; ../Wintappy/wintap_dbt/models/gold/process_file_summary.sql; ../Wintappy/wintap_dbt/models/gold/process_net_summary.sql; ../Wintappy/wintap_dbt/models/gold/process_summary.sql; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §kprobe__tcp_recvmsg; ../wintap/wintap/core/infrastructure/health/DefaultHealthChecks.cs §IsQualifiedFile; ../wintap/wintap/core/etl/extract/FileSerializer.cs -->

## Runtime theory — evidence versus inference

**High-confidence mechanism:** when an owner/birth lookup failed, old runtime
fallbacks hashed the current file/exit timestamp. That produces valid-looking but
unjoinable identity keys. DBT then faithfully preserves the orphan keys and
materializes additional counter/name-grouping defects. Duplicate AgentId is real
but does not cause thousands of same-PID hashes per second.

**Likely trigger, not proven:** short-lived package/cron/man-db workloads outlive
their `/proc` availability before independent clone/exec/file/exit callbacks can
enrich them. File serialization lag is higher for Unknown rows: CALDERA median
**70.7s**, p95 **159.9s**, max **179.8s**; AXON median **19.4s**, p95 **40.1s**.
This is consistent with backlog/amplification under bursty workloads, but includes
normal ETL windows. Without callback timestamps, active sensor receipts and
ring/queue/serializer logs, it cannot prove where backlog occurs or that drops occur.

Additional missed birth events may reflect clone/thread filtering or disabled/
unattached hooks. A same-PID birth within ten seconds exists for 1,585 Stop-only
identities, consistent with split hashes, but **not a safe automatic historical
merge rule**: Linux permits PID reuse and exec without a new process lifetime.
<!-- SYNTHESIS: exact hash evidence, lifecycle gaps, file lag distributions, and Wintap producer/resolver source; originating binary/version and runtime counters are unavailable -->

### Residual current-source gap discovered by this audit

<!-- CONTRADICTION[hard]: wiki/concept/telemetry-identity-and-endpoint-orientation.md states unresolved attribution uses an unknown sentinel instead of Stop-time hashing; Linux ExitSensor still hashes exitUtc when canonical start is unavailable — REVIEW NEEDED. Pause further semantic promotion pending review; no source fix made in this audit. -->

The shared identity formula was centralized, but **a correct formula cannot
make an exit timestamp a canonical start timestamp**. Linux `ExitSensor.cs:120–121`
at audit time hashed `exitUtc` when history, live resolver and `/proc` start time all failed.
`RegisterProcess` queues an unmatched Stop without rekeying the emitted message;
EventChannel still sends it to Esper/ProcessStopSerializer. Thus this path can
still export a fabricated Stop identity after the central identity patch.
Execve/Rundown also retain callback-now fallbacks when canonical start is unavailable;
Clone's kernel-fork-time fallback is more defensible but must agree with exec/rundown.
The focused 148-test suite and healthy endpoint/restart captures do not exercise
these missing-start Linux branches. **No source fix was made during this audit.**
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §CreateRefreshMessage; ../wintap/wintap/core/infrastructure/ProcessResolver.cs §RegisterProcess; ../wintap/wintap/core/infrastructure/EventChannel.cs §ProcessAndSend -->

**Subsequent experiment:** candidate Exit captures authoritative kernel starts and
uses the unknown sentinel when every start source is absent; initial live Stops
match canonical identity even with births deliberately disabled. This closes that
candidate branch, not complete producer-input acceptance. Execve/Rundown fallbacks,
unresolved-record semantics and package rollout are still open; retain the hard
contradiction/review record above rather than silently treating it as fully resolved.
<!-- REVIEW NEEDED: audit finding is historical; review remains for incomplete all-producer unresolved-identity contract and experimental rollout boundaries. -->
See [[wiki/work/host-process-identity-patch/experiment_results]].

## Proposed next acceptance

1. Close remaining Linux missing-start hash branches; regress unavailable `/proc`,
   Stop-before-Start ordering, and unsupported/missing kernel start fields explicitly.
2. Replay a named **burst/short-lived** workload against patched packaged code:
   preserve proc-birth/file/exit coverage, count distinct identities per lifetime,
   capture callback/queue/ring/serializer metrics, and confirm unknown attribution
   remains explicit rather than generating one process hash per file event.
3. Fix gold file vocabulary, summary one-row-per-process joins/tests, and duration;
   handle fork/exec names as observations, not extra lifetime summary keys.
4. Validate return-value TCP/UDP receive-byte semantics separately from endpoint/
   counter spelling. Add Linux-aware qualified-path QA and collection metadata.
5. Repair historical data only under an explicit event-level migration plan;
   do not infer identity from PID proximity or overwrite this supplied database.

Related: [[wiki/work/host-process-identity-patch/verification]],
[[wiki/work/improve-lintap-data-quality/clone-validation-results]],
[[wiki/diagnostic/linux-capability-data-quality-matrix]],
[[wiki/concept/telemetry-identity-and-endpoint-orientation]].
