---
title: "Validation: Historical Identity Cache Overnight Run"
type: diagnostic
confidence: high
grounded_by:
  - wiki/work/improve-etl-and-qa/verification.md
  - wiki/work/improve-etl-and-qa/esper-sender-path-analysis-2026-08-30.md
  - wiki/work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30.md
  - ../wintap/devtools/file_capture_smoke_test.py
policy: agent-editable
last_validated: 2026-08-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: file
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa; ../wintap/devtools/file_capture_smoke_test.py
tags: [feature-work, lintap, fileops, process-attribution, cache, long-run, performance, telemetry-fidelity]
---

# Validation: Historical Identity Cache Overnight Run

## Verdict

The first extended deployment of the historical identity cache passed a
10-hour-23-minute passive fidelity/performance gate and a subsequent controlled
6,000-file recovery test.

The cache remained at its configured 32,768-entry bound and churned heavily,
but hourly hit rate, sender latency, and queue behavior did not degrade with
time. No ring, sender, aggregate-summary, serializer, or File send loss was
observed. This materially raises confidence that the cache removes repeated
historical DuckDB work without trading throughput for unbounded state.

## Deployment Continuity

- RPM: `lintap-0.3.4-1.el8.x86_64`
- PID: `3322161`
- Service start: `2026-08-30 20:54:30 PDT`
- Passive observation: `20:56:03 PDT -> 07:19:33 PDT`
- FileOps summaries: `617`
- The SSH/control connection interruption did not restart or affect the sensor.

## Evidence Record

The original log, serializer directory, and retrieved `/tmp` file were host-local
working artifacts, not durable source anchors. This page preserves the evidence
needed to identify and re-run the analysis:

- installed `/usr/lib/lintap/Lintap.dll` SHA-256:
  `7bd7ab380ac07b004f04357e5bb46d23bf45f0bdca871949137b080cc7e9a235`;
- retrieved S3 aggregate SHA-256:
  `17e19df37746f2cb5f2126e79d6199c1ddecae2759e17f0c08bbc20d8b883230`;
- passive run identity: RPM `lintap-0.3.4-1.el8.x86_64`, PID `3322161`, exact
  local window `2026-08-30 20:56:03 PDT` through `2026-08-31 07:19:33 PDT`;
- pidstat passive window: `2026-08-30 20:54:36 PDT` through
  `2026-08-31 07:19:57 PDT`; controlled recovery through `07:26:57 PDT`;
- recovery command: `python3 devtools/file_capture_smoke_test.py --data-root
  /var/log/lintap --timeout 180 --poll-interval 2 --unique-file-count 6000
  --require-no-serializer-drops --serializer-observation-seconds 70`;
- integrity command: `sha256sum /usr/lib/lintap/Lintap.dll
  /tmp/spk16-lintap-pidstat-overnight-1m.parquet`;
- coverage command: `duckdb -c "select count(*) as rows, min(minute) as
  first_minute, max(minute) as last_minute from
  read_parquet('/tmp/spk16-lintap-pidstat-overnight-1m.parquet');"`;
- analysis input: that hash-identified one-minute pidstat file combined with
  log records bounded to the passive and recovery windows above for phase
  trends, slopes, correlations, queue recovery, and fidelity-counter totals.

The durable conclusions below depend on the recorded hashes and windows, not on
continued existence of those host-local paths.

## Passive Baseline

| Signal | Result |
|---|---:|
| Sender queue first / last | `1 / 10310` |
| Sender queue min / average / max | `0 / 5205.5 / 17387` |
| Maximum interval high-water | `38707` |
| Sender drops | `0` |
| Summary enqueue failures | `0` |
| Aggregation cap bypass | `0` |
| Historical-cache hits / misses | `1667417 / 542811` |
| Historical-cache hit rate | `75.4%` |
| Final cache entries | `32768` |
| Cache evictions | `394252` |
| Weighted sender average | `560.6 us` |
| Weighted resolution average | `547.1 us` |
| Weighted Esper average | `12.0 us` |
| Maximum sampled sender / resolution | `3.159 s / 3.159 s` |
| Maximum sampled Esper | `920.6 ms` |

The previous saturated run averaged `5135.7 us` per sampled send. The overnight
average remained about 89% lower despite cache saturation and eviction churn.
Rare multi-second resolution and sub-second Esper expiration stalls occurred,
but bounded queue headroom absorbed them without loss.

Hourly cache hit rate ranged `68.2%..83.0%`; full-hour sender averages ranged
`482..673 us`. There was no monotonic latency increase. Hourly average queue
depth stayed roughly `3.7k..7.2k`, with no hourly maximum above `17.4k`.

## Serializer Fidelity

Before the controlled workload, FileSerializer reported:

- `3447` non-empty flushes;
- `1260` high-water flushes;
- `11208824` rows drained;
- maximum `353` rows remaining after a drain;
- maximum drain duration `218 ms`;
- four safely skipped timer/high-water overlaps;
- zero backlog warnings, sender-worker errors, or File send errors.

Current Parquet remained readable throughout spot checks. Pidstat was uploaded
to S3 and later retrieved as 633 one-minute aggregates, closing the CPU/RSS/I/O
portion of the original logs-only limitation. GC heap/committed and process map
counts still require the privileged perf collector.

## Retrieved Pidstat Resource Analysis

The retrieved file covers 7,505 passive samples from `20:54:36` through
`07:19:57 PDT` and 84 controlled-burst samples through `07:26:57`.

Passive CPU averaged `323.8%` core-summed, or `10.12%` host-normalized on the
32-logical-CPU host. The post-22:00 CPU slope was only `+0.124` host percentage
points/hour, so the sender/cache optimization did not introduce a material CPU
ratchet. This is substantially below the saturated pre-cache run's `30.82%`
host-normalized average.

RSS did continue growing:

- full passive window: `443452 -> 1911876 kB`, dominated by startup warm-up;
- post-22:00: `1488404 -> 1911876 kB`, regression `+35157 kB/hour`;
- last four hours: `1734212 -> 1911876 kB`, regression `+18973 kB/hour`;
- last two hours: `1783928 -> 1911876 kB`, regression `+20432 kB/hour`;
- post-22 half averages: `1646991 -> 1802737 kB`.

Virtual size also continued rising post-22:00 at about `37915 kB/hour`, although
its absolute ~814 GB reservation is not resident memory.

The strongest aligned diagnostic correlate is the FileOps FD-path cache:

- PID maps: `21 -> 9921`, slope about `950/hour`;
- FD/path entries: `24 -> 11184`, slope about `1058/hour`;
- directory index: `658 -> 2137`, slope about `82/hour`;
- RSS/FD-entry level correlation: `r=0.929` overall, `r=0.938` post-22:00;
- last-four-hour level correlation: `r=0.876`;
- minute-delta correlation: only `r=0.208` overall and `r=0.253` post-22:00.

The shared long-run trend makes missing process-exit/age eviction in the FD-path
cache the leading residual memory hypothesis. The weaker delta correlation and
other time-growing runtime state mean this is not yet a per-entry causal proof.
By comparison, RSS correlation with sender queue was `r=0.130`, with CPU
`r=0.192`, and with the bounded historical identity cache `r=0.582` while that
cache had already plateaued.

## Controlled Recovery Test

After the passive cutoff, the existing high-cardinality smoke generated 6,000
unique files. It passed with recent rows for `open`, `read`, `write`, `close`,
and `delete` and observed the serializer for 70 seconds without a drop warning.

The FileOps interval high-water reached `71802`, still only about 14% of sender
capacity. Sender depth was `8590` in that interval and fell to `5416` in the
next interval, below its pre-burst `8285` value. Later natural periodic bursts
reached `16329`, still below the passive baseline maximum `17387`. Sender drops,
summary failures, cap bypass, and cache evictions attributable to the burst path
remained non-problematic; no fidelity counter increased.

Pidstat confirms that the burst did not cause a lasting resource step. Average
host CPU was `10.44%` versus passive `10.12%`; RSS was `1888276 -> 1897152 kB`
despite a transient `2209064 kB` maximum. Average write rate rose from `160` to
`206 kB/s`, while read throughput remained zero in the process-level counters.

## Remaining Risks

- Cache churn is continuous at this process-creation rate. The 32,768-entry cap
  is sufficient for this host and workload, but higher-churn hosts or deeper
  sender backlogs still need field validation.
- Average latency is stable, but rare resolution stalls reached 3.16 seconds.
  Queue age/latency percentiles would describe those outliers better than the
  current one-in-64 average/max sample.
- The retrieved pidstat supports process CPU/RSS/I/O/fault trends, but not
  anonymous-vs-file RSS, GC heap/committed, process FD count, or map count. Those
  still require the privileged perf capture.
- FileOps FD-path cache growth is now the leading residual memory hypothesis and
  needs process-exit plus conservative age/capacity eviction followed by another
  long-run comparison.
- FileSerializer's existing `Int32` aggregate parse and weighted summary-drop
  accounting gaps remain separate fidelity hardening items.
