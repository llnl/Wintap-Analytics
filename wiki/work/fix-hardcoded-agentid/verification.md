---
title: "Verification: Fix Hardcoded AgentId"
type: concept
confidence: medium
grounded_by:
  - wiki/work/fix-hardcoded-agentid/implementation_plan.md
policy: agent-editable
last_validated: 2026-10-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: network
audience: developer
status: reviewed
source_paths: wiki/work/fix-hardcoded-agentid/verification.md
tags: [feature-work, verification, agentid, tcp]
---

# Verification: Fix Hardcoded AgentId

## Current Status

Implementation and Linux VM validation complete on `lintap-dev`.

## Linux Host and Deployment

- Host: Multipass `lintap-dev`; Ubuntu 24.04.5 LTS, kernel `6.8.0-147-generic`, `aarch64`.
- Authority: `ubuntu` is in the `sudo` group; `bpftool` is installed; the package-managed `lintap` service was active.
- Deployment: rebuilt `Lintap.dll` from `/home/ubuntu/git/wintap` was copied to `/usr/lib/lintap/Lintap.dll` after preserving the prior DLL at `/var/lib/lintap/feature-backups/fix-hardcoded-agentid/Lintap.dll.pre-feature`. The service was restarted at 2026-10-20 09:02 MST. The eBPF tracer object was unchanged.

## Results

| Gate | Command / evidence | Result |
| --- | --- | --- |
| Linux build | `dotnet restore wintap/Lintap.csproj && dotnet build wintap/Lintap.csproj --no-restore` | Pass (dependency/compatibility warnings only). |
| Focused contracts | `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter FullyQualifiedName~NetworkSerializerContractTests --no-restore` | Pass: 4/4. Covers event AgentId handling, missing AgentId rejection, producer-neutral watchdog text, and shipped state template. |
| Resolver profile | `dotnet test ... --filter "Category=profile" --logger "console;verbosity=detailed"` | Pass: 1/1. 1,000 unresolved durable lookups took 621.46 ms (621.46 µs average). No negative cache added: there is no live evidence of a sustained unresolved-miss rate, while a TTL cache could conceal identity just registered out of order. |
| Static source check | `git diff --check`; no `AgentId = "grantj"` or legacy network-idle wording in active serializers; template equals `{"AgentId":""}` | Pass. |
| eBPF attachment | `sudo bpftool prog list` after restart | Pass: `trace_inet_sock_set_state`, `kprobe__tcp_v4_connect`, `kretprobe__tcp_v4_connect`, and `kprobe__tcp_close` attached. |
| Pipeline smoke | `python3 devtools/network_capture_smoke_test.py --data-root /var/log/lintap/data --timeout 180 --poll-interval 5 --rounds 2` | Pass: successful HTTP/HTTPS and UDP traffic; TCP port 443 rows observed. |
| Fresh TCP output | Fresh staging and merged raw query after restart | Pass: staging TCP file `runtime/esper_staging/tcpconnectionserializer/process_conn_incr-134369859861819287.parquet` contained 50 TCP rows, all AgentId `aa582ab7-3a2f-428b-904e-891590b2e27a`, zero `grantj`. In merged raw file `data/raw_sensor/raw_process_conn_incr/dayPK=20261020/hourPK=16/protoPK=tcp/lintap-dev+raw_tcp_process_conn_incr+134369860468586385.parquet`, post-restart (`EventTime >= 1792512135`) rows were 228 active UUID and zero `grantj`. |
| TCP lifecycle | Same fresh raw query | Pass: `TcpIpConnect` 9, `TcpIpSend` 114, `TcpIpRecv` 146, `TcpIpDisconnect` 63. |

The merged raw file also contains 104 pre-restart `grantj` rows with EventTime 1792511923–1792512086, which were queued before the replacement binary started; they are not evidence against the fixed deployment.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs §HandleSensorEvent -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/NetworkSerializerContract.cs -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §ResolveProcessAtTime -->

## Required Evidence

| Gate | Command / evidence | Result |
| --- | --- | --- |
| Build | Wintap targeted build | Pass |
| Regression tests | Focused AgentId/state/watchdog tests | Pass |
| Static source check | No hardcoded TCP AgentId; tracked state template empty | Pass |
| Resolver profiling | Repeated unresolved-owner lookup timing/counts and cache decision | Pass: no cache added |
| eBPF attachment | `sudo bpftool prog list` on matched deployment | Pass |
| Pipeline smoke | `devtools/network_capture_smoke_test.py` | Pass |
| Realistic traffic | TCP lifecycle/attribution/AgentId parquet query | Pass |

## Live Host Requirement

Record distribution, kernel, deployment method, privileges, commands, output
window, and resulting parquet paths before marking the live gate complete.
