---
title: "Feature References: SELinux Monitoring"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/
  - ../Lintap/sql/selinux.sql
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: wiki/work/selinux-monitoring/references.md
tags: [feature-work, selinux, lintap, ebpf]
---

# Feature References: SELinux Monitoring

## Live Repo Sources

Pipeline patterns to follow (the SELinux streams slot in parallel to these):

- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/` — existing tracer
  set and the two-tier (CO-RE + tracepoint fallback) pattern:
  `file_ops_tracer.bpf.c` / `file_ops_tracepoint.bpf.c`,
  `execve_tracer.bpf.c`, `clone_tracer.bpf.c`, `network_ops_tracer.bpf.c`,
  plus `Makefile` for build integration.
- `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs` and
  `FileOpsAggregator.cs` — the reference for userspace consume, filter,
  counters logging, and the fop-11 emit-first aggregation the novel-tuple
  dedup should pattern on.
- `../wintap/wintap/core/etl/esper/file.epl` (and `tcp.epl`/`udp.epl`) —
  EPL composition patterns; every non-aggregated select column must be
  grouped (see [[wiki/component/fileops-event-pipeline]]).
- `../wintap/wintap/core/etl/extract/FileSerializer.cs` — serializer flush
  pattern to `raw_sensor`-style parquet.

Legacy POC (non-goal to change; schema/semantics reference only):

- `../Lintap/sql/selinux.sql` — context splitting
  (user:role:type:cat1:cat2), `process_selinux_contexts` ASOF-join shape,
  `SELINUX_CONTEXT` rollup view, and the Known-issues comment (TZ offset,
  ~40% unjoined rows, interval filtering).
- `../Lintap/merge_raw_tsv.sh` §`raw_selinux_contexts`/`raw_selinux_paths`
  loop — the raw column expectations of the old auditd TSVs.
- `../Lintap/README.md` §Running Lintap — declares the auditd path
  experimental/optional.
- `../Lintap/selinux.drawio`, `../Lintap/sql/selinux.drawio` — POC-era
  diagrams (uningested; consult if the old data flow needs clarifying).

## External Sources

To verify during the spike (kernel-version-sensitive; do not trust from
memory):

- Kernel `avc:selinux_audited` tracepoint (added ~5.10) — fires on audited
  AVC decisions; field set and whether context strings are exposed must be
  confirmed against the target host's kernel.
  <!-- SPECULATIVE: tracepoint availability/fields on the target RHEL 9 kernel — confirm via /sys/kernel/debug/tracing/events/avc on-host -->
- BPF LSM (`CONFIG_BPF_LSM`, `lsm=` boot parameter, kernel ~5.7+) — hook
  availability and whether RHEL 9 ships/permits it must be confirmed
  on-host.
  <!-- SPECULATIVE: RHEL 9 BPF LSM enablement — confirm via /boot/config-$(uname -r) and /sys/kernel/security/lsm on-host -->
- kprobe candidates on avc/security functions (e.g. `avc_audit`/
  `slow_avc_audit`, transition-related security hooks) — fallback tier;
  symbol presence confirmed via /proc/kallsyms on-host.
- SELinux context/SID model: SIDs are kernel-internal and not stable across
  boots; context strings are the durable representation.

## Related Wiki Pages

- [[wiki/component/fileops-event-pipeline]] — stage contracts and the EPL
  group-by invariant this feature must honor.
- [[wiki/component/process-table-retention]] — process identity/retention
  contracts if SELinux records stamp PidHash.
- [[wiki/repo/lintap-supporting-repo]] — Lintap repo orientation and the
  legacy SELinux paragraph.
- [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] — SELinux is
  Linux-only; a new pole for cross-platform semantic parity discussions.
- [[wiki/workflow/lintap-dev-field-workflow]] — dev/field split rules for
  on-host spike work.
- [[wiki/work/optimize-fileops-poller/design]] — volume-analysis and
  no-loss-argument patterns to reuse for the interaction-map dedup.

## Libraries And APIs

- libbpf CO-RE (existing tracer toolchain, clang/bpftool via the tracers
  Makefile).
- DuckDB for acceptance queries over landed parquet.
- `ausearch`/auditd on the target host — ground truth for the
  provoked-denial acceptance test only (not a capture dependency).

## Notes

- The old POC's biggest semantic lesson: joining SELinux observations to
  process identity after the fact was lossy (~40%); capturing pid/identity
  at event time in-kernel avoids the whole class of ASOF-join problems.
- Volume lesson from fop: never ship raw per-check events — `avc_has_perm`
  -level activity fires on every permission check; dedup/aggregate before
  the ring buffer or immediately after.
