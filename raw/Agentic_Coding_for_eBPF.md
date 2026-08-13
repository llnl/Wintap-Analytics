<!-- SOURCE: Internal brainstorming note, "Initial brainstorming: Using an agentic coding tool for developing eBPF probes". Exact origin unrecorded; frontmatter tag `confluence-mcp-access` suggests it was retrieved from Confluence, and the citation style suggests AI-assistant output. Bracketed reference URLs in the footer are unresolved domain-level links. -->
<!-- RETRIEVED: 2026-07-17 -->

---
title: "Initial brainstorming: Using an agentic coding tool for developing eBPF probes"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-07-16
tags: [feature-work, confluence-mcp-access]
---


Generating raw C or Rust code that satisfies the strict in-kernel eBPF verifier is notoriously tedious. Below are the AI agentic coding tools designed specifically to help you build those probes, followed by established EDR-like infrastructure projects to cross-reference with Tetragon.
These tools use LLMs to automate the generation and compilation of eBPF programs, specifically tailored to handle system tracing and telemetry.
MCPtrace: This is a Model Context Protocol (MCP) server designed for eBPF tracing. Instead of just spitting out code snippets, it allows you to connect an AI agent (like Claude Desktop or any MCP-compatible IDE assistant) directly to a Linux kernel context. The agent can synthesize, compile, and run tracepoints or kprobes to experiment with retrieving process and file telemetry in real time. [2, 3] 
GPTtrace: Developed by the Eunomia-bpf team, this tool uses natural language prompts to generate functional bpftrace programs and libbpf-based C code. For your EDR model, you can prompt it with things like: "Generate an eBPF script to trace sys_enter_openat2 and return the calling PID, PPID, and the absolute filename string," and it handles the boilerplates and verifier-compliant pointer arithmetic. [2] 
eunomia-bpf & Wasm-bpf Frameworks: While not standalone agents, these lightweight development frameworks are heavily utilized by coding agents (like Copilot SWE-agents) to distribute eBPF. They compile eBPF code into JSON metadata or WebAssembly modules. If you are building an LLM agent script to prototype probes iteratively, hooking it into Eunomia's runtime allows your agent to load and test bytecode without full system recompilations. [4, 5, 6] 
Tetragon is powerful because of its smart, in-kernel filtering and CRD-driven runtime enforcement. However, if your primary goal is reproducing a clean, tabular EDR stream (like Wintap's data format), these projects offer excellent telemetry collection pipelines to study or build upon: [7, 8] 
Aqua Security Tracee: Tracee is a robust runtime security and forensics tool for Linux built entirely on eBPF. Unlike Tetragon, which focuses heavily on enforcement (blocking/killing processes inline), Tracee focuses aggressively on deep kernel tracing and behavioral patterns. It exposes comprehensive events for file reads/writes, code injections, and network payloads, outputting them in structured JSON—making it a close open-source equivalent to ETW-based telemetry infrastructure.
Falco: The CNCF-graduated classic. Falco uses a modern eBPF driver to tap into the Linux system call stream. It maps these streams into a high-performance userspace rules engine. While Tetragon hooks deeply into inner kernel functions (kprobes/LSM), Falco provides an incredibly mature map of how to translate raw syscall activity into structured, security-relevant events.
Sysmon for Linux: An official Microsoft port of Windows Sysmon to Linux. It uses eBPF as its underlying engine to collect telemetry. Because you are migrating from a Windows data model mindset, looking at Sysmon for Linux's open-source eBPF implementation is invaluable. It shows exactly how Microsoft engineers chose to map native Windows event concepts (Process Creation, Network Connection, FileCreateTime) onto Linux eBPF hooks.
Bombini: If you are writing your Linux EDR version in Rust, Bombini is a reference architecture. It is an eBPF security agent written entirely in Rust utilizing the Aya library and Linux Security Module (LSM) BPF hooks. [8, 9, 10, 11] 
If you are using a specific framework for your new Linux telemetry agent (such as pure C with libbpf, Rust with Aya, or Go with cilium/ebpf), let me know. I can tailor code-generation strategies or agent prompts specifically to that toolchain.

[1] https://eunomia.dev
[2] https://github.com
[3] https://eunomia.dev
[4] https://eunomia.dev
[5] https://github.com
[6] https://www.alibabacloud.com
[7] https://ebpf.io
[8] https://kubernetes.ae
[9] https://www.armosec.io
[10] https://github.com
[11] https://betterstack.com