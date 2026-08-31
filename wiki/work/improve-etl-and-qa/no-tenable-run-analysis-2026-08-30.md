---
title: "Analysis: No-Tenable Lintap Performance Run"
type: diagnostic
confidence: high
grounded_by:
  - wiki/work/improve-etl-and-qa/verification.md
  - wiki/work/improve-etl-and-qa/tenable-scan-storm-response-2026-08-30.md
  - validation/perf-collection/README.md
  - wiki/concept/lintap-cpu-unit-conventions.md
policy: agent-editable
last_validated: 2026-08-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: file
audience: mixed
status: draft
source_paths: validation/perf-collection; wiki/work/improve-etl-and-qa
tags: [feature-work, lintap, performance, fileops, backpressure, memory, telemetry-fidelity]
---

# Analysis: No-Tenable Lintap Performance Run

## Verdict

`lintap-perf-20260830-no-tenable` is not the intended quiet-host, no-loss
baseline. It is a useful no-policy-hit, FileOps-saturation artifact.

The Tenable rule recorded zero matched attempts in all 60 FileOps summaries,
but the sender queue was already effectively full when capture began. The hour
recorded `601126` sender drops and `192774` aggregation-summary enqueue
failures. FileSerializer itself remained healthy, so loss occurred upstream of
serialization.

Within that bounded-saturation state, process RSS was stable rather than
ratcheting. This weakens a simple time-driven or managed-heap-leak explanation,
but the failed fidelity gate prevents treating the resource profile as a clean
production baseline.

## Capture Integrity

The host paths used during analysis were ephemeral and are not durable
`grounded_by` sources. This page is the durable evidence record. The source
files were identified by run ID, exact window, and these SHA-256 values:

| Stream | SHA-256 |
|---|---|
| `perf_dotnet_counters` | `c67cf1a602689fa801ff594145a3ac01308369c559749582c43c25a0f15c85dd` |
| `perf_proc_status` | `e007e0c28da6571cbdd422f1176ca3b53925f7d444710dda44755b0e07ba5b6e` |
| `perf_fd_map` | `49c4cab9c79ecec4a06759370b52d4dd90103bd129cfbd46f8be152bc608ca3c` |
| `perf_smaps_rollup` | `2858540273e37c8557dc16892a394efc37623d4689894de8bd55d652740c6e3f` |

The analysis used DuckDB over those four explicit files and parsed only
`/var/log/lintap/Logs/Lintap.log` records in the exact local window below. It
calculated row/time coverage, first/last/range/half averages, linear slopes,
FileOps and serializer totals, maintenance timing, and aligned queue/resource
correlations. These exact shell commands re-establish artifact identity and
stream coverage; no recursive `/tmp` glob is evidence:

```bash
sha256sum "/tmp/lintap-perf/parquet/raw_sensor/perf_dotnet_counters/dayPK=20260830/hourPK=22/perf_dotnet_counters-lintap-perf-20260830-no-tenable-2f5b321a0049.parquet" "/tmp/lintap-perf/parquet/raw_sensor/perf_proc_status/dayPK=20260830/hourPK=22/perf_proc_status-lintap-perf-20260830-no-tenable-c554209d8b48.parquet" "/tmp/lintap-perf/parquet/raw_sensor/perf_fd_map/dayPK=20260830/hourPK=22/perf_fd_map-lintap-perf-20260830-no-tenable-8599dbe67954.parquet" "/tmp/lintap-perf/parquet/raw_sensor/perf_smaps_rollup/dayPK=20260830/hourPK=22/perf_smaps_rollup-lintap-perf-20260830-no-tenable-fcac95ed47d2.parquet"
duckdb -c "select run_id, count(*) as rows, min(time) as first_time, max(time) as last_time from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_dotnet_counters/dayPK=20260830/hourPK=22/perf_dotnet_counters-lintap-perf-20260830-no-tenable-2f5b321a0049.parquet') group by run_id; select run_id, count(*) as rows, min(time) as first_time, max(time) as last_time from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_proc_status/dayPK=20260830/hourPK=22/perf_proc_status-lintap-perf-20260830-no-tenable-c554209d8b48.parquet') group by run_id; select run_id, count(*) as rows, min(time) as first_time, max(time) as last_time from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_fd_map/dayPK=20260830/hourPK=22/perf_fd_map-lintap-perf-20260830-no-tenable-8599dbe67954.parquet') group by run_id; select run_id, count(*) as rows, min(time) as first_time, max(time) as last_time from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_smaps_rollup/dayPK=20260830/hourPK=22/perf_smaps_rollup-lintap-perf-20260830-no-tenable-fcac95ed47d2.parquet') group by run_id;"
```

| Item | Result |
|---|---:|
| Run ID | `lintap-perf-20260830-no-tenable` |
| Host / PID | `spk16.llnl.gov` / `2994383` |
| UTC window | `2026-08-30T21:49:06Z` to `22:49:05Z` |
| Local window | `2026-08-30 14:49:06` to `15:49:05 PDT` |
| Procfs samples per stream | `715` |
| Runtime-counter rows | `9720` (`360` samples x `27` counters) |
| Tenable policy-hit summaries | `0/60`; every summary reported `suppressed_attempts=0` |

## Resource Profile

The `.NET System.Runtime` CPU counter is host-normalized. On this 32-logical-CPU
host, the `30.82%` average is approximately `9.86` core-summed CPUs.

| Signal | First | Last | Range | First-half avg | Second-half avg | Linear slope/hour |
|---|---:|---:|---:|---:|---:|---:|
| Host-normalized CPU | `31.10%` | `32.73%` | `18.37..35.80%` | `31.12%` | `30.52%` | `-1.07 pp` |
| Runtime working set | `2057.25 MB` | `2059.69 MB` | `1967.54..2089.53 MB` | `2057.61 MB` | `2058.42 MB` | `+5.00 MB` |
| `smaps` RSS | `2013792 kB` | `2015180 kB` | `1959768..2041840 kB` | `2011872 kB` | `2013742 kB` | `+6737 kB` |
| `smaps` anonymous | `1734528 kB` | `1735580 kB` | `1680496..1762520 kB` | `1732534 kB` | `1734147 kB` | `+6280 kB` |
| GC heap | `523.90 MB` | `765.95 MB` | `258.78..778.25 MB` | `510.26 MB` | `519.63 MB` | `+25.41 MB` |
| GC committed | `1036.02 MB` | `1049.04 MB` | `1034.90..1065.05 MB` | `1042.67 MB` | `1051.19 MB` | `+17.30 MB` |
| Open FDs | `487` | `488` | `487..490` | `488.26` | `488.26` | `+0.06` |
| Mapped regions | `4486` | `4522` | `4485..4529` | `4491.40` | `4504.19` | `+27.30` |

The GC heap's `+242 MB` first-to-last change is a sawtooth endpoint effect, not
a matching RSS rise: half-hour means differed by only `9.37 MB`, while runtime
working-set half means differed by `0.81 MB`. Generation 2 half means declined
by about `2.57 MB`; LOH half means increased by about `0.89 MB`.

`AnonHugePages` rose from `849920` to `1169408 kB`, but total anonymous memory
rose only `1052 kB` and RSS only `1388 kB`. The huge-page change is therefore
primarily promotion/reclassification inside an already resident anonymous
footprint, not `319488 kB` of additional resident memory.

The runtime allocated about `80.1 GB` across the one-hour interval, averaging
about `22.3 MB/s`. It recorded `207/202/6` generation `0/1/2` collections and
`7.30 s` total GC pause time, with thread-pool queue length zero throughout.
This is a high-allocation workload, but GC pause and thread-pool backlog were not
the dominant saturation signals.

## FileOps Fidelity And Throughput

| Signal | Result |
|---|---:|
| Sender queue first / last | `524148 / 522190` |
| Sender queue min / average / max | `513561 / 523313 / 524223` |
| Queue capacity / interval high-water | `524288 / 524288` |
| Sender drops | `601126` |
| Summary enqueue failures | `192774` |
| Aggregation cap bypass | `0` |
| Aggregation first emits / repeats folded / summaries | `647340 / 1196708 / 281529` |
| FileSerializer non-empty flushes | `385` (`359` timer, `26` high-water) |
| FileSerializer drained | `654769` rows |
| FileSerializer max remaining / max duration | `170 / 3 ms` |
| Serializer overlap / backlog warnings | `0 / 0` |

The serializer's low remaining depth, fast drains, and zero warnings establish
that it was not the bottleneck in this run. The loss boundary was the bounded
FileOps sender queue ahead of synchronous EventChannel/Esper processing.

The FileOps FD cache continued growing despite stable process FDs:

- cached PIDs: `3146 -> 4052` (`+906`, about `29%`);
- cached entries: `3890 -> 4899` (`+1009`, about `26%`);
- directory index: `9690 -> 9777` (`+87`).

This keeps conservative FileOps FD-cache eviction as an independent long-run
memory/state requirement. ProcessResolver also remained expensive: 12
maintenance cycles averaged `9.70 s` (`8.89..10.73 s`), while its active cache
rose `1807 -> 2240`. CacheManager's 12 cycles averaged `2.30 s` total and
`0.56 s` merging.

## Comparison With The Filtered Run

The filtered capture was loss-free inside its own
`2026-08-30T19:13:55Z -> 20:13:54Z` window, but it was not sustainable:

- FileOps sender depth rose from `7860` to `338592` during that hour.
- The queue continued to `401452` in the next ten-minute bucket.
- The first nonzero sender-drop summary appeared at `13:36:36 PDT`, about 23
  minutes after the filtered capture ended.
- By the no-Tenable capture, the queue had remained near capacity for more than
  an hour.

| Signal | Tenable-filtered run | No-Tenable run | Interpretation |
|---|---:|---:|---|
| Average host CPU | `22.40%` | `30.82%` | `+37.6%`; the later run was busier, not quiet |
| Average runtime working set | `1659.50 MB` | `2058.01 MB` | Later bounded-saturation footprint was about `398.5 MB` higher |
| Average `smaps` RSS | `1621354 kB` | `2012809 kB` | About `391455 kB` higher |
| Average GC heap | `311.92 MB` | `514.94 MB` | Higher managed activity/state, but no matching within-hour RSS ratchet |
| Average GC committed | `797.97 MB` | `1046.93 MB` | About `249 MB` higher |
| Open FD range | `487..495` | `487..490` | Stable process descriptors in both runs |
| Sender drops in exact window | `0` | `601126` | Later run fails telemetry-fidelity acceptance |

Across the filtered run's 60 aligned one-minute points, queue depth correlated
with RSS at `r=0.749`, anonymous memory at `r=0.748`, and runtime working set at
`r=0.583`; correlation with GC heap was only `r=0.191`. This does not prove
causality because the DBT workload was a shared confounder, but the later result
is consistent with bounded queue occupancy contributing materially to the
earlier memory climb: once queue depth was pinned near its cap, RSS also settled
into a narrow band. Correlation within the cap-bound run is not informative
because queue depth had little variance.

## Conclusions And Next Gate

1. The exact Tenable worker policy worked for its intended identity, but it did
   not make the overall FileOps pipeline sustainable under subsequent
   non-policy workload.
2. Do not use this run as a quiet-host CPU baseline or a no-loss acceptance run.
3. The hour does not show an unbounded RSS or FD leak. It does show sustained
   high CPU, a fixed large sender backlog, continued internal FD-cache growth,
   and recurring long ProcessResolver maintenance.
4. Do not run another long comparison until sender depth starts low and remains
   materially below capacity with zero drops and zero summary enqueue failures.
5. The next engineering step is a short saturated-state CPU/stack attribution
   focused on the single FileOps sender, EventChannel process attribution,
   Esper dispatch, and resolver maintenance. Any throughput change must retain
   non-policy FileOps count/byte conservation and the existing serializer
   no-drop gates.
