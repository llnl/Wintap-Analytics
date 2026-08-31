---
title: "FileOps Event Pipeline"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/core/etl/esper/file.epl
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
policy: agent-editable
last_validated: 2026-08-31
repo_scope: wintap
implementation_area: data-pipeline
event_domain: file
audience: mixed
status: reviewed
source_paths: wiki/component/fileops-event-pipeline.md
tags: [wintap, lintap, ebpf, file-events, aggregation, esper, parquet, cross-repo]
---

# FileOps Event Pipeline

Promoted from [[wiki/work/optimize-fileops-poller/brief]] (closed
2026-08-27). Kernel-to-parquet path for Linux file events.

Owning implementation is currently on the sibling `../wintap` feature branch;
its durable commit anchors are `1db7137` and `2d3f795`. Until those
placeholder is replaced, use the live source paths above plus
[[wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31]]
for the hash-, run-, and window-qualified field evidence.

## Stages And Contracts

- **Kernel tracers** (two tiers: CO-RE + tracepoint fallback): self-PID
  filter map, regular-file filtering, batched wakeups;
  `ring_fail_total=0` is the health invariant.
- **Userspace filters** (before enqueue): pseudo paths (`/sys`, `/proc`,
  `/dev`), data-root self-feedback, `.etl`, `.parquet*`. All drops
  counted in the 60s `FileOps counters` log line.
- **Path identity**: opens store fd→path; relative/`openat` opens
  resolve to absolute pre-enqueue via opened-fd, dir-identity LRU index
  (65,536 entries, taught by DIR_OPEN records), dirfd, or cwd —
  reason-split `resolve=[...]` counters.
- **fop-11 aggregation** (default on; kill switch
  `WINTAP_FILEOPS_AGG_ENABLED=false`): emit-first per (pid, path, op),
  1s window (`WINTAP_FILEOPS_AGG_WINDOW_MS`), repeats fold into one
  summary carrying EventCount=repeats, summed bytes, first/last
  timestamps, identity stamped at first occurrence. Count AND byte
  conservation field-proven by the kill-switch A/B differential.
- **Sender queue**: bounded 524,288, drop-newest, counted.
- **Sender execution**: one `FileOps-Sender` thread dequeues one event at a time,
  then synchronously runs EventChannel attribution and Esper submission. A
  current-process cache miss can fall through to DuckDB under the resolver's
  global lock. The 2026-08-30 saturated run averaged 5.14 ms sampled send time
  and 118 cache misses/s; isolated `file.epl` itself handled about 179k events/s,
  making attribution/miss handling the leading optimization target.
- **Historical identity fast path**: a File active-cache miss now checks a
  bounded, PID-reuse-safe cache of closed process intervals before DuckDB.
  Periodic diagnostics expose its hits/misses/entries/evictions, while sampled
  sender timing separately reports average and maximum resolve, health, Esper,
  and total duration.
- **Esper composition** (`file.epl`): 10s `time_batch`, group by
  (path, PidHash, PID, activityType, ProcessName, AgentId),
  `sum(eventCount)`/`sum(bytesRequested)`, min/max first/last seen.
  **RULE: every non-aggregated select column MUST be in the group by** —
  an ungrouped column (AgentId, pre-0e01783) flips Esper to
  one-row-per-input-event output and inflates eventCount n² per
  batch-group. Same rule applies to registry.epl (fixed) and holds in
  tcp/udp (always grouped).
- **FileSerializer flush schema** (parquet columns): `File_Path`
  (lowercased), `FirstSeen`/`LastSeen` (FileTime), `ActivityType`,
  `EventCount`, `BytesRequested`, `PID`, `PidHash`, `ProcessName`,
  `AgentId`, `Hostname`, `File_Hash`, `MessageType='PROCESS_FILE'`.
  Flush every `SerializationIntervalSec` (60s) to
  `<dataroot>/parquet/fileserializer/process_file-<filetime>.parquet`;
  in-memory queue capped (`WINTAP_ETL_MAX_QUEUE_EVENTS_FILESERIALIZER`).

## Known Caveats

- ~1% of open+close pairs lost to the open path-record flake (a no_path
  open orphans its close) — phase-symmetric capture noise; the A/B
  tolerates 1% (documented 2026-08-27).
- `mmap` maps to ActivityType Read; rename is unmapped (Other).
- Parquet `eventCount` written by pre-0e01783 builds is n²-inflated
  (File/Registry, all platforms) — see the ACME-dataset check in
  [[wiki/work/extended-deployment-monitoring/brief]].
- Aggregation-OFF mode floods the serializer queue; only for short
  diagnostics (the A/B raises the cap for its run).
- NEsper `time_batch` expiration can contend with concurrent ingress at high
  cardinality, but outbound listener threading did not improve that benchmark.
  Replacing File EPL with the TCP/UDP context pattern failed an exact-count
  concurrent-boundary test and is not an accepted optimization.
- The 2026-08-30/31 overnight run showed the userspace FD-path cache growing
  `24 -> 11184` entries (about `1058/hour`) while process RSS continued rising
  post-warm-up at about `35 MB/hour`, slowing to about `19 MB/hour` over the
  final four hours. RSS/FD-entry level correlation was `0.929` overall and
  `0.938` after 22:00, while minute-delta correlation was only `0.253`.
  Conservative process-exit plus age/capacity eviction is the leading residual
  memory follow-up, but causation is not yet proven.

## Verification

Milestone tests T1-T6 in [[wiki/work/optimize-fileops-poller/test_plan]];
the kill-switch A/B (`validation/fileops-differential/run_fop11_ab.sh`)
is THE regression gate for this pipeline.

The historical-cache and long-run FileOps findings are verified in
[[wiki/work/improve-etl-and-qa/esper-sender-path-analysis-2026-08-30]] and
[[wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31]].
