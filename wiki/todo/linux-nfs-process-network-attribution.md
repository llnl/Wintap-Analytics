---
title: "To-Do: Qualify Linux Process Attribution on NFS Network Activity"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../Wintap-PyUtil/wintap_dbt/macros/network_keys.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_file.sql
policy: agent-editable
last_validated: 2026-11-10
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor/ebpf; ../Wintap-PyUtil/wintap_dbt/models
tags: [todo, priority, linux, network-events, process-attribution, nfs, data-quality, wintap, wintappy]
---

# To-Do: Qualify Linux Process Attribution on NFS Network Activity

**Priority:** P2 — Medium (provisional; the sample has a plausible explanation,
but process-versus-socket attribution must be explicit and validated).
**State:** Open — intake finding; no producer or model change is authorized.
**Likely next step:** Reproduce the SSH/NFS correlation while capturing process
context, socket tuple, file operations, and both `PROCESS_FILE` timestamp
fields; establish whether the deployed tracer attributes the initiating task or
the socket owner.

## Finding

Read-only inspection of `process_net_conn` in the reviewed example database
found 129 rows for one TCP five-tuple to the NFS service. The user confirms that
the destination is the NetApp NFS device and that the home directory involved
is mounted from it. The connection ID is a normalized five-tuple hash, not a
process ID: Wintappy's temporary key macro hashes protocol and endpoint address
and port pairs, while `process_net_conn` also groups by `pid_hash` and process
metadata. Thus one connection ID can legitimately appear on rows for several
process identities. Of the 129 rows, 70 have `process_name = 'exe'` across 49
distinct process hashes; that name-quality issue is tracked separately in
[[wiki/todo/linux-process-name-exe-fallback]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/network_keys.sql §temporary_five_tuple_conn_id; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql -->

One row attributes a single 264-byte TCP send on that NFS tuple to process
`ssh`. The same process also has a separate SSH connection to port 22. These
are different five-tuples, so the NFS row does not say that the SSH client
socket itself connects to the NFS server. The user confirms that the home
directory accessed by this process is NFS-mounted from the same device.
<!-- HUMAN-REPORTED: the example host's home directory is mounted from the identified NetApp NFS device. Other database values here were queried read-only from the local example database. -->

For the same SSH process, the six-minute run window contains 14
`PROCESS_FILE` rows across six home-directory paths, all within `.ssh`: four
Open rows, four Read rows, four Close rows, and two Delete rows (34 aggregated
file events). One Delete row's `first_seen` is about 1 ms after the NFS send,
consistent with an NFS metadata operation. However, that row's separate
`min_event`/`max_event` values are about five seconds later. The user-confirmed
NFS home makes this a plausible explanation, but the timestamp discrepancy
prevents a precise event-to-event conclusion.

The current Linux network tracer emits `tcp_sendmsg` observations using the
current task PID, and the managed sensor resolves process identity from that
PID. That can represent the process context causing network I/O (for example,
synchronous filesystem I/O through an NFS client), rather than an exclusive
owner of the underlying TCP socket. Confirm this semantic against the deployed
sensor/object and a controlled capture before treating the row as erroneous.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §kprobe__tcp_sendmsg; ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §HandleEvent -->

For this example, `process_name = 'ssh'` agrees with the process path and
arguments; no case mismatch is evident. There is a separate metadata caveat:
these network rows say `os_family = 'windows'`, which Wintappy's current
`process_conn_incr` SQL hardcodes. That known platform-labeling issue is tracked
in [[wiki/diagnostic/duplicate-agent-id-and-os-family]] and should not be read as
evidence that the Linux process name is wrong.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql §os_family -->

## Cursory endpoint-wide inspection

Across roughly 19 hours spanning November 9–10, the endpoint-wide query found
1,619 `process_net_conn` rows, 254 distinct five-tuple IDs, 770 distinct process
hashes, 64,773 aggregated network events, and about 9.6 MB reported. These are
model-row and aggregated-event counts, not counts of unique sockets or proof
that every event was caused by the named process.

The activity mix is broadly plausible for an NFS-backed home and a busy mounted
workload: rows include mount helpers and filesystem-inspection utilities, a
scanner workload, shells and SSH processes, plus many generic `exe` labels. The
`exe` label alone accounts for 742 rows across 211 process hashes and 32,627
events; the scanner workload accounts for 271 rows across three five-tuple IDs,
18,910 events, and about 2.4 MB. Mount helper rows account for another 310 rows.
This scale is consistent with a combination of NFS mount/metadata traffic,
filesystem scans, and application I/O, but the generic process names and
aggregation grain leave a substantial attribution-quality question; it is not
possible to validate every row as expected from these summaries alone.

Joining endpoint-attributed process hashes to `process_file` activity in the
same broad time window found 404 of 770 hashes with some file activity, and 38
with home-directory paths. Among those, seven SSH process hashes had 80 `.ssh`
file rows and 226 aggregated file events. This reverse check supports the
presence of processes interacting with NFS-backed home content, but it is a
hash-level intersection, not proof that each file operation caused a particular
network event or that the process exclusively owned the NFS socket. The large
`exe` bucket is tracked separately in
[[wiki/todo/linux-process-name-exe-fallback]].

## Validation work

1. Record the user's mount confirmation as intake context; during a controlled
   reproduction, independently capture the mount/export and correlate it with
   file and network observations.
2. Reconcile the SSH process's NFS-tuple send with its nearby file observations
   and raw network event, including event activity, PID, five-tuple, source
   tracer/object version, and the difference between first/last-seen and
   event-time columns. Check whether similar correlations occur for other
   processes accessing that mount.
3. In a controlled run, compare SSH activity with a local home directory and
   an NFS-backed home. Include metadata-only operations (open, lookup, unlink)
   and file reads/writes. Verify whether NFS transport sends are attributed to
   the initiating process, a kernel worker, or a socket owner on each supported
   tracer path.
4. Document whether `process_net_conn` means “process observed causing activity
   on this tuple” or “process owns this socket.” If both meanings are needed,
   keep them distinct in the event/model contract and downstream visualizations.
5. Validate PID/hash-to-process-name consistency using path, arguments, and
   process lifetime; do not merge names just by casing. Retain explicit
   alternatives or conflict flags where identities disagree.
6. Add a regression/data-quality fixture for one five-tuple attributed to
   multiple process contexts, and ensure consumers do not interpret
   `conn_id` alone as a process-exclusive connection.

## Related findings

- [[wiki/todo/canonical-process-owned-network-grains]] — define process-owned
  network grains and distinguish network observations from process lifecycle.
- [[wiki/todo/linux-process-name-exe-fallback]] — separately tracks the many
  `exe` process-name values in this same reviewed database.
- [[wiki/diagnostic/duplicate-agent-id-and-os-family]] — records the current
  Wintappy OS-family hardcoding issue.

## Disposition

This intake does not conclude that the SSH/NFS association is a sensor bug. The
observed tuple is NFS, SSH also has a distinct port-22 connection, and its
nearby `.ssh` file activity makes NFS-backed home access a plausible explanation.
Validate the user-reported mount details and producer attribution semantics
before changing telemetry or historical data.
