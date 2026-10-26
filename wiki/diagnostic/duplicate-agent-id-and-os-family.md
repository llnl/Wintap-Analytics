---
title: "Duplicate host AgentId and Linux data mislabeled as Windows"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/core/shared/StateManager.cs
  - ../wintap/wintap/core/shared/ProcessHash.cs
  - ../wintap/wintap/wintapstate.json
  - ../wintap/wintap/core/etl/shared/Utilities.cs
  - ../wintap/wintap/core/etl/extract/HostSerializer.cs
  - ../Wintappy/wintap_dbt/models/silver/host.sql
  - ../Wintappy/wintap_dbt/models/silver/host_ip.sql
  - ../Wintappy/wintap_dbt/models/silver/process.sql
  - ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintappy/wintappy/datautils/rawtostdview.sql
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/shared; ../wintap/wintap/core/etl; ../Wintappy/wintap_dbt/models/silver; ../Wintappy/wintappy/datautils/rawtostdview.sql
tags: [agentid, identity, cloned-state, linux, os-family, data-quality]
---

# Confirmed observations, unresolved remediation

**Patch follow-up:** [[wiki/work/host-process-identity-patch/verification]] records
the now-implemented shared hash and runtime host-bound agent state. The observations
below describe the pre-patch dataset/code. Existing hosts/data have not been modified;
OS-family correction remains separate and unimplemented.

**Broader read-only sample QA:** [[wiki/diagnostic/sample-db-runtime-attribution-audit]]
separates duplicate AgentId from file-event/Stop-time identity fabrication,
missing birth/parent records, unknown users, and downstream aggregation defects.

On 2026-10-23 the user reported these additional defects in
`/Users/johnson30/git/axon-aegis-micro-range/data/lintap/duckdb/wintap.duckdb`.
Opened with `duckdb.connect(path, read_only=True)`; no data or deployment changes.

| Raw host | AgentId | OS | OSVersion | Silver os_family |
|---|---|---|---|---|
| AXON-TARGET | fc3e4c62-eddf-42d0-9ab4-830773b61f6f | NA | Unix 6.8.0.147 | windows |
| CALDERA-HOST | fc3e4c62-eddf-42d0-9ab4-830773b61f6f | NA | Unix 6.8.0.147 | windows |

Reproduction queries:

```sql
select distinct hostname, agentid, os, osversion from stg_raw_host;
select hostname, agent_ids, os_family, os, os_version from host;
select hostname, agentid, count(*) from stg_raw_process_conn_incr group by all;
```

The duplicate UUID already exists in raw host telemetry; it is not introduced
by DBT grouping. Network increments also retain historical AXON-TARGET IDs
`grantj` (146 rows) and `aa582ab7-3a2f-428b-904e-891590b2e27a` (2 rows), alongside
the duplicate UUID (14,361 AXON-TARGET / 14,355 CALDERA-HOST rows). This is a
mixed-history dataset; replacing one column alone would not repair identity.

## Agent identity boundary

`StateManager` reads/writes `wintapstate.json` in the working directory. Any valid
nonempty saved UUID is accepted; a new UUID is generated only for missing,
invalid or empty IDs. No saved host binding is checked.
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/StateManager.cs §getAgentId; §readState; §writeState; §WintapState -->

The live local `../wintap/wintap/wintapstate.json` contains exactly the dataset's
duplicate UUID. `git show HEAD:wintap/wintapstate.json` instead returns
`{"AgentId":""}`. The template fix is present in the committed source, but
initialized local state remains different and must not be overwritten as if it
were merely a template. Copying initialized state through a build, install or VM
image would explain the collision; the exact deployment route is not verified.
<!-- SYNTHESIS: live ../wintap/wintap/wintapstate.json, its committed template, and the read-only dataset observations -->

The earlier [[wiki/work/fix-hardcoded-agentid/verification]] verified TCP event
AgentId propagation and an empty committed template, not clone-safe persisted
identity or uniqueness across two hosts. Those completed claims remain valid;
this finding is an additional deployment/persistence boundary.

## OS metadata boundary

Wintappy hardcodes `windows` in canonical silver `host`, `host_ip`, `process`
and `process_conn_incr`; tracked legacy `rawtostdview.sql` repeats the assumption.
Derived network/summary models propagate it. These are offline annotations, not
Windows sensor claims. Wintap separately obtains OS name from the Windows registry
only and falls back to `NA`, explaining the missing Linux name. OSVersion comes
from `Environment.OSVersion.VersionString`.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/silver/host.sql; ../Wintappy/wintap_dbt/models/silver/host_ip.sql; ../Wintappy/wintap_dbt/models/silver/process.sql; ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintappy/wintappy/datautils/rawtostdview.sql; ../wintap/wintap/core/etl/shared/Utilities.cs §Computer.Get; §GetOS; ../wintap/wintap/core/etl/extract/HostSerializer.cs §WriteHostRecordAsync -->

## Proposed correction and regression gates (not implemented here)

**Subsequent user clarification:** [[wiki/decision/process-hash-inputs-and-single-definition]]
requires `pid_hash` to depend only on hostname/PID/process-start, not agent UUID,
with one formula definition. The rotation warning below describes **pre-patch code**,
not the intended contract. The patch has consolidated the two implementations;
no agent UUID input remains in the new formula. Old binaries remain affected.

- Keep agent UUID stable across normal restarts/upgrades; ensure independent
  hosts initialize independent UUIDs. Never distribute initialized runtime state
  as a package/image template. Define clone detection/provisioning policy before
  changing persistence: hostname alone is mutable, and machine IDs can also be cloned.
- Test two independent initializations, restart persistence, package contents and
  cloned-image provisioning; add a dataset cross-host AgentId collision diagnostic
  with rename/time-context handling.
- Emit explicit platform-derived OS family in host telemetry; populate Linux OS
  name/version without Windows registry assumptions. Derive Wintappy family from
  collection-host metadata with backward-compatible handling of old schemas.
- Correlate metadata by host **and** agent (with suitable temporal/conflict handling),
  not agent alone while collisions exist. Test mixed Linux/Windows data and missing
  metadata; do not turn every `Unix` label into Linux or use the analysis OS.
- A Linux-only configured fallback is preferable to a universal `windows` label
  for this dataset, but must not relabel historical Windows data. Ambiguous metadata
  should remain unknown/flagged, not guessed.
- Plan live ID rotation/restart and historical rebuild separately. `agent_id` is
  currently part of `pid_hash` generation; rotating it midstream splits future
  identities until the clarified hash contract is implemented.
  No service restart, ID rotation, source fix or database rewrite done in this pass.

<!-- SPECULATIVE: proposed remediation, requiring implementation/deployment decisions -->

High-level contract: [[wiki/concept/telemetry-identity-and-endpoint-orientation]].
