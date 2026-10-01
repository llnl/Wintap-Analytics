---
title: "Analysis: FileOps Sender Path Into Esper"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/PluginManager.cs
  - ../wintap/wintap/core/etl/esper/file.epl
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/diagnostics/nesper-repro/Program.cs
  - wiki/work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30.md
  - wiki/work/improve-etl-and-qa/verification.md
policy: agent-editable
last_validated: 2026-08-31
repo_scope: wintap
implementation_area: esper
event_domain: file
audience: developer
status: draft
source_paths: wintap/platform/linux/sensor/ebpf; wintap/core/infrastructure; wintap/core/etl; diagnostics/nesper-repro
tags: [feature-work, lintap, fileops, esper, nesper, performance, backpressure, process-attribution]
---

# Analysis: FileOps Sender Path Into Esper

## Verdict

Esper is not intrinsically limited to the roughly 195 FileOps sends per second
observed in the saturated `lintap-perf-20260830-no-tenable` run. An isolated
production-shaped `file.epl` benchmark sustained about 179,000 input events per
second after warm-up with exact event-count and byte conservation.

The strongest current bottleneck is the work surrounding Esper, especially
historical process resolution on FileOps active-cache misses. The live run
recorded about 118 such misses per second while sampled end-to-end sender
latency averaged 5.14 ms, an implied serial ceiling of about 195 events per
second. Each miss can enter synchronous DuckDB lookup under the process-global
resolver lock; the single FileOps sender cannot hide that latency.

Esper still had two concrete inefficiencies: a redundant broad all-event
subscriber statement on hosts with no subscriber plugins, and costly 10-second
high-cardinality batch expiration. The former is safely removed. The latter is
real but is not safely fixed by enabling outbound threads or replacing the file
window with the existing context pattern.

## Current Path

1. One eBPF poller decodes, resolves paths, filters, stamps current process
   identity when available, applies one-second repeat aggregation, and enqueues.
2. One `FileOps-Sender` thread dequeues one row at a time.
3. `EventChannel.Send` retries process attribution when identity was not stamped.
   An active-cache miss executes synchronous historical DuckDB resolution and
   can trigger maintenance under the same `_dbLock`.
4. The same sender calls `EsperRuntime.EventService.SendEventBean` synchronously.
5. Esper evaluates every deployed `WintapMessage` statement. `file.epl` stores
   File rows in a disjoint 10-second `time_batch`, groups them, and emits the
   aggregates to `FileSerializer`.
6. FileSerializer converts aggregate rows and queues them. Parquet writing runs
   on a separate worker.

The FileOps queue adds burst capacity but no steady-state throughput. Increasing
its 524288-row cap would only defer loss and increase retained memory.

## Live Rate Arithmetic

Live-rate inputs are grounded through the hash-identified run and exact log
window in [[no-tenable-run-analysis-2026-08-30]], rather than the mutable
`/var/log` path itself. Benchmark commands and post-change test commands are
recorded in [[verification]].

For the no-Tenable hour:

| Signal | Value |
|---|---:|
| Process-cache hits | `1403289` |
| Process-cache misses | `425815` |
| Miss rate | `118.3/s` (`23.3%` of recorded resolutions) |
| Mean sampled `EventChannel.Send` duration | `5135.7 us` |
| Implied serial sender ceiling | `194.7/s` |
| Aggregation first emits | `647340` |
| Aggregation summaries produced | `281529` |
| Sender drops | `601126` |
| Summary enqueue failures | `192774` |

The cache counters span both poll-time successful identity stamping and
sender-time misses. A miss at send time is particularly costly because the
deep queue means the originating short-lived process is often already gone.

## Isolated NEsper Benchmark

The benchmark pre-creates 100,000 File `WintapMessage` objects, sends them into
a dedicated NEsper 8.9 runtime, advances external time deterministically, and
requires exact `sum(eventCount)` and `sum(bytesRequested)` output. Reported
figures are medians of three runs after including each scenario's first-run JIT
cost in the record.

| Scenario | Median input rate | Batch delivery | Fidelity | Decision |
|---|---:|---:|---|---|
| No EPL | `538882/s` | negligible | pass | Runtime API baseline |
| Current `file.epl` string casts | `178756/s` | `1.54 s` for 10k groups | pass | Keep |
| Native nested enum literals | `162381/s` | `1.84 s` | pass | No measured gain |
| File EPL plus broad all-event statement | `62785/s` | `1.70 s` | pass | Remove when no subscribers |
| File EPL plus one outbound thread | `176280/s` | `1.61 s` | pass | No meaningful gain |
| File EPL with concurrent expiration | `83925/s` | `1.75 s` | pass | Expiration contends with ingress |
| Outbound thread plus concurrent expiration | `78278/s` | `1.84 s` | pass | Does not remove contention |
| Context-based file aggregation | `51716/s` | `0.17 s` | pass without concurrent boundary | Reject |
| Context aggregation with concurrent boundary | about `48k/s` | timed out waiting for exact total | fail: duplicate counts | Reject |

The synthetic 100k-event/10k-group expiration is intentionally heavier than a
typical live 10-second batch. It demonstrates the contention mechanism, not an
estimate of each production pause. A later benchmark should sweep event and
group cardinality around observed production values.

## Esper Optimization Decisions

### Implemented: remove the empty all-event route

`PluginManager` previously deployed
`SELECT * FROM WintapMessage WHERE ... <> 'ProcessPartial'` whenever ETL was
enabled, even if there were no subscriber plugins. Its callback then iterated an
empty subscriber collection. The live host confirmed `Total plugin count: 0`
immediately after logging `Creating Subscriber EPL`.

The route is now deployed only when `subscribers.Any()`. ETL serializers are
unaffected because each deploys its own EPL statement. The benchmark shows this
removes substantial avoidable Esper work, although the roughly 10 microseconds
per synthetic event saved is far too small to explain a live 5.14 ms send.

### Fixed but not enabled: native enum rewrite

The dormant `WINTAP_DISABLE_ESPER_ENUM_CAST` rewrite used `.` for a nested enum
type and generated EPL that NEsper could not compile. Nested enums require `$`
in EPL. The generated syntax is fixed and benchmarked with exact output, but the
option remains disabled because it showed no repeatable throughput benefit.

### Rejected: outbound threading as the immediate fix

NEsper inbound, outbound, timer, and route pools are disabled by default.
Enabling one bounded outbound thread did not improve steady input throughput or
concurrent-expiration throughput. It would also add another queue and enlarge
shutdown/drain obligations. Do not enable it merely because Esper supports it.

### Rejected: switch File EPL to the TCP/UDP context pattern

The context pattern made batch delivery faster but moved more aggregation work
onto ingress, reducing steady input throughput by about 3.5x. Its concurrent
boundary stress also duplicated represented event counts. That result is enough
to reject a production switch without a redesigned context and stronger
boundary proof.

## Implemented Follow-On

The process-attribution optimization was deployed as RPM `lintap-0.3.4` on
`spk16` at `20:54:30 PDT`:

- File identity resolution checks a bounded 32,768-entry historical LRU before
  DuckDB; `WINTAP_PROCESS_HISTORICAL_IDENTITY_CACHE_ENTRIES` can tune the cap or
  set it to zero.
- Entries represent only closed process instances and include exact
  `[create_time, exit_time]` validity. Multiple instances of one PID are allowed;
  the newest matching create time wins.
- Successful durable lookups populate the cache. Retention maintenance also
  seeds identity before deleting an expired process row, and the triggering
  lookup retries the cache after maintenance.
- Normal lookup, direct Stop, pending Stop, runtime reconciliation, and startup
  reconciliation now parameterize timestamps rather than truncating them to
  whole seconds.
- FileOps summaries report `process_history_cache` hits, misses, entries, and
  evictions. The existing one-in-64 sender sample now separates average and
  maximum total, process-resolution, health-check, and Esper durations.
- Per-query ProcessResolver debug writes were removed from this hot path.

The standalone cache benchmark measured about 4.9 million cache hits/s with a
10,000-entry working set. With a simulated 5 ms durable-lookup penalty,
throughput was about `200/s`, `400/s`, `800/s`, `1995/s`, and `1.06M/s` at
`0%`, `50%`, `75%`, `90%`, and `100%` cache hits respectively. A 50,000-key
setup against the production 32,768-entry cap evicted 17,232 oldest entries and
remained bounded.

The first ten-minute live gate passed. Historical-cache hit rate was `82.7%`
(`32700/39537`), weighted sender latency fell from the prior `5135.7 us` to
`449.7 us`, resolution accounted for `445.1 us`, and Esper averaged `2.7 us`.
Queue depth stayed `0..1889` and was `152` at the tenth interval (`100` one
minute later); sender drops, summary failures, aggregation bypass, cache
evictions, serializer drops, and send errors remained zero. This validates the
short-run mechanism but not yet multi-hour cache-capacity behavior.

## Additional Fidelity Risks Found

- A failed aggregate-summary enqueue increments row failure counters but does
  not weight the global drop count by the summary's represented events/bytes.
- FileSerializer parses 10-second `sum(bytesRequested)` and `sum(eventCount)`
  through `Int32`; sufficiently large groups can overflow and discard an
  aggregate row.
- Enabling inbound Esper threading would alter ordering across all event types
  and plugins and is not justified by the current evidence.
- Shutdown does not yet prove full drain across sender, Esper, serializer, and
  Parquet queues; adding another runtime queue would increase that risk.
