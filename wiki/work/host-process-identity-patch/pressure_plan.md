---
title: "Controlled attribution pressure and shutdown-tail proof"
type: workflow
confidence: medium
grounded_by:
  - wiki/work/host-process-identity-patch/shutdown_delivery_results.md
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - wiki/work/host-process-identity-patch/pressure_workload.py
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../wintap/wintap/core/infrastructure; wiki/work/host-process-identity-patch
tags: [pressure, attribution, conservation, shutdown, proof]
---

# Approved scope

User approved controlled pressure/shutdown experiments on disposable AXON/CALDERA,
same qualified revision16candidate, retry1024 unchanged. Preserve installed controls,
all failed evidence, historicalDB, active lintap-dev and unrelated work. No rollout,
queue resizing, default changes or correction without demonstrated cause.

# Protocol

Synchronized tiers32/128/256 short-lived children:each four file write/read pairs,
one32-byte non-loopback TCP request/echo, independent PID/birth/port/operation receipts.
Parent server is a separate process from every client. Retain ordinary separate-
process and same-process bidirectional endpoint gates. Fork children before server
thread starts; bounded readiness60s/workload75s/socket30s. No arbitrary SQL/migration.

For each tier, fresh off/on controls on both hosts: interior stimuli after observed
start upper bounds+21s,30s settling; separate shutdown-tail round stops collector
immediately after pressure workload reaps,without additional settling. Endpoint
controls run before pressure. This is final-batch delivery,NOT generated-after-stop
or native-hook cutoff proof. Record actual workload→stop elapsed,10s primary bands
and1/5/20s sensitivity without relabeling uncertain intervals.

Keep observer budgets32768/250k/128MiB and retry1024/ten nominal1s attempts fixed.
Require complete trace before any absence/cause claim. Observe independently generated
file paths/seven normalized events per path, successful TCP exchanges and both ends;
kernel packet count is NOT inferred from syscall count. Exact observed producer→
projection→accepted→drain→enqueue→final/raw joins stay mandatory.

Preflight per host:original service inactive/no competing collector,3GiB native disk
free,available memory>=2GiB;do not delete old evidence for space. Stop escalation
on generation failure,trace refusal/error/truncation,OOM,identity/conservation deficit;
archive all evidence first,locate first stage,then repeat narrow demonstrated boundary.
No historical failure retroactively closed by a passing modern burst.

# Checklist

- [x] Qualify stimulus/oracle tests, source/package/control preflight.
 97wiki tests pass;native4child stimulus qualifies successful file/TCP manifests on
 CALDERA. Bothhosts disk/memory/service preflight passes;262tested source files match
 live revision16qualification. `pressure_preflight.json` and
 `pressure_stimulus_qualification.json` preserve receipts.
- [x] Baseline32 interior and shutdown-tail off/on dual-host controls.
 Eight rawcontrols conserve1,024paths/7,168events;complete histories and eightfresh
 fullDBTbuilds pass,256pressurelifetimes retained. Sampled pendingpeaks belowcapacity;
 no saturation/refusal/exhaustion. `pressure_baseline_results.json`.
- [x] Escalate128/256 only after complete lower-tier gates; preserve failures.
 Original20 oracle failure halted21–23. Fresh24–27 pass after exact cause proof.
- [x] Identify measured first failure or lower-bound tested envelope,not universal sizing.
 All accepted tiers pass;sampled pending max348/1024,not saturation.
- [x] Correct only demonstrated cause and regression-test if needed.
 Pressure endpoint oracle only:exact capture receipt bounds,not stimulus+2s.
 All152 original misses present in raw;deterministic test and fresh repeats pass.
- [x] Fresh canonical fullDBT builds and protected identity/counter/birth verification.
 24 accepted builds/3,328 child lifetimes;four separate20 recheck builds preserved.
- [x] Archive hashes,service/DLL/AgentId/DB/source preservation;results/log/index/checklists.
 28 archives/262 sources verified;installed controls/history unchanged,collectors idle.

Final evidence:[[wiki/work/host-process-identity-patch/pressure_results]].
No further pressure escalation or rollout launched;actual saturation remains open.
