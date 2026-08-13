---
title: "Agentic Coding Tools for eBPF Probe Development"
type: concept
confidence: medium
grounded_by:
  - raw/Agentic_Coding_for_eBPF.md
policy: agent-editable
last_validated: 2026-08-11
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: cross-domain
audience: mixed
status: draft
source_paths: raw/Agentic_Coding_for_eBPF.md
tags: [ebpf, lintap, agentic-tooling, llm-workflows, tetragon, tracee, falco, sysmon-linux, bombini, kunai, brainstorming]
---

# Agentic Coding Tools for eBPF Probe Development

## Overview

Survey of LLM/agent-assisted tooling for developing eBPF probes, plus additional reference EDR-style eBPF telemetry projects worth cross-referencing when evolving Lintap's Linux sensors. Originated from an unverified brainstorming note (`raw/Agentic_Coding_for_eBPF.md`); tool existence and top-level claims were independently verified via web research on 2026-08-11, which raised page confidence from low to medium and corrected two claims (see Verification Notes).

Motivation: writing C/Rust that passes the in-kernel eBPF verifier is tedious, and agent tooling may shorten the probe prototype loop. This is relevant to the Lintap eBPF work in `../wintap/wintap/platform/linux/sensor/ebpf/`, where verifier/CO-RE compatibility issues (e.g., `task_struct.start_time` access, program-attachment API differences) have already consumed validation effort.
<!-- SYNTHESIS: inferred from raw/Agentic_Coding_for_eBPF.md and the 2026-08-06 Lintap eBPF fixes recorded in wiki/log.md -->

## Candidate Agentic Tools (verified 2026-08-11)

| Tool | Verified status | Capability |
|---|---|---|
| MCPtrace | Active — <https://github.com/eunomia-bpf/MCPtrace> | MCP server exposing **bpftrace** kernel tracing to AI assistants; natural-language probe discovery and script execution; Rust implementation (rmcp crate); secure-gateway model where the AI never gets root |
| GPTtrace | Explicitly an experiment, **not for production** — <https://github.com/eunomia-bpf/GPTtrace> | Natural-language generation of bpftrace/eBPF programs (Kgent framework, ~2023); its own README redirects users to MCPtrace |
| eunomia-bpf / Wasm-bpf | Active — <https://github.com/eunomia-bpf> | Frameworks (not agents) that build/distribute/run CO-RE eBPF programs via JSON and WebAssembly OCI images, enabling iterative agent-driven load/test |

### Verification Notes (corrections to the brainstorming note)

- **MCPtrace is narrower than the note claimed.** The note described connecting an agent to a live kernel context to synthesize, compile, and run tracepoints/kprobes generally. In reality MCPtrace is a minimal MCP gateway to **bpftrace** — good for throwaway observational tracing and probe-point exploration, not for developing the CO-RE libbpf C tracers Lintap actually ships.
- **GPTtrace is effectively superseded.** Its README states it is an experiment unsuitable for production and points to MCPtrace as the better path. Its Kgent research reported ~80% correct eBPF generation vs a ~30% GPT-4 baseline — useful as a datapoint on LLM eBPF-generation reliability, not as a tool to adopt.
<!-- SYNTHESIS: web verification 2026-08-11 of github.com/eunomia-bpf/MCPtrace and github.com/eunomia-bpf/GPTtrace, correcting raw/Agentic_Coding_for_eBPF.md -->

### Practical implication for Lintap

The realistic near-term value of this tooling is **diagnostic, not generative**: MCPtrace-style bpftrace access could help an agent (or developer) quickly answer questions like "is `sched_process_fork` firing for this workload?" or "what does `task_struct.start_time` look like on this kernel?" during validation debugging — the exact class of question the 2026-08-06 CO-RE fixes required. Generating Lintap's production CO-RE tracers with an LLM agent remains unproven.
<!-- SYNTHESIS: inferred from verified tool scope plus the eBPF debugging history in wiki/log.md 2026-08-06 entries -->

## Additional Reference Projects for EDR-Style Telemetry (verified 2026-08-11)

The note frames these as projects to study when reproducing a clean tabular EDR stream like Wintap's data format:

- **Tracee** (Aqua Security) — already a first-class, source-inspected reference in the validation thread; see [[wiki/work/lintap-process-creation-validation/research-snapshot-2026-07-31]].
- **Falco** — the validation thread already covers Sysdig/Falco libs at source level.
- **Sysmon for Linux** — verified real and maintained: <https://github.com/microsoft/SysmonForLinux>, built on the libbpf-based SysinternalsEBPF library (<https://github.com/microsoft/SysinternalsEBPF>). Monitors process lifetime, network connections, and file writes; uses BTF for kernel offsets when available, with its own offsets auto-discovery fallback for non-BTF kernels. Directly relevant prior art for the Windows-event-semantics-on-eBPF mapping problem in [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]], and its offsets-database approach is an interesting contrast to Lintap's CO-RE approach.
- **Bombini** — verified real but very small/early-stage (~35 GitHub stars as of late 2025): <https://github.com/bombinisecurity/bombini>. Rust/Aya agent built on LSM BPF hooks with modular "Detectors". A design reference at most, not a validation-grade comparison sensor.
- **kunai** — *not in the original note; surfaced during verification.* An Aya-based Rust threat-hunting/security-monitoring tool positioned as similar to Falco or Tetragon. If a Rust-ecosystem reference is ever wanted, kunai appears more mature than Bombini and is worth evaluating first.
<!-- SYNTHESIS: web verification 2026-08-11; kunai discovered via aya-rs/awesome-aya listing -->

## Relationship to Existing Wiki Pages

- [[wiki/work/lintap-process-creation-validation/index]] — the validation thread's reference set is Tetragon, Tracee, and Sysdig (grounded in local checkouts). Sysmon for Linux is now a verified candidate fourth reference; Bombini/kunai are design references only.
- [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] — Sysmon for Linux is verified prior art for the exact Windows-semantics-on-eBPF mapping this tension preserves.
- Unlike [[wiki/work/lintap-process-creation-validation/research-snapshot-2026-07-31]], which is grounded in local source inspection of each tool, this page is grounded only in web-level verification; claims about internals remain unvetted at source level.

## Open Questions

- Should Sysmon for Linux be added as a fourth reference sensor in the process-creation validation matrix? It is verified real and maintained; adding it would require a local checkout and a source-inspection pass (process lifecycle hooks, identity strategy, loss visibility) comparable to the Tetragon/Tracee/Sysdig snapshots. Its non-BTF offsets auto-discovery is also worth comparing against Lintap's CO-RE-only posture on older kernels.
- Is MCPtrace worth wiring into the validation VM as a debugging aid for eBPF probe behavior questions, given it is bpftrace-only and cannot exercise Lintap's libbpf C tracers directly?
- Is kunai a better Rust-ecosystem reference than Bombini if that path is ever explored?
