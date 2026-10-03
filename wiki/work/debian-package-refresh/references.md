---
title: "Feature References: Debian Package Refresh"
type: concept
confidence: high
grounded_by:
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
policy: agent-editable
last_validated: 2026-10-03
repo_scope: Lintap
implementation_area: packaging
event_domain: none
audience: llm-agent
status: draft
source_paths: wiki/work/debian-package-refresh/references.md
tags: [feature-work, lintap-packaging, debian, references]
---

# Feature References: Debian Package Refresh

## Live Repo Sources

Target (to be changed):

- `../Lintap/packaging/lintap-deb/build-deb.sh` — the deb builder to refresh.
  Stale pieces: `expected_bpf_objects` list (pre-two-tier names
  `execve_tracer`/`exit_tracer`/`network_ops_tracer`, missing the four
  `*_tracepoint` objects); plain `dotnet publish` without MCP/MSBuild isolation
  props; work under repo `artifacts/` instead of a native work-root; no
  `--skip-mcp`/`--work-root`/`--host-arch` options.
- `../Lintap/packaging/lintap-deb/lintap.env` — missing the field sensor block
  (compare RPM env below).
- `../Lintap/packaging/lintap-deb/{README.md,BUILD_AND_TEST.md,LLM_RESTART.md}`
  — docs reflect the June 2026 state (macOS + `ssh lintap-dev` arm64 VM, NuGet
  outage); need refresh to current layout and workflow.
- `../Lintap/packaging/lintap-deb/{lintap.service,lintap-pidstat.service}` —
  already equivalent to the RPM units (comment wording differs only).

Parity source (read-only):

- `../Lintap/packaging/lintap-rpm/build-rpm.sh` — the field-proven builder to
  mirror: §require_cmd, §EBPF_TARGET_ARCH mapping, §MCP separate publish
  (`EnableMcpServer=false`, `DISABLE_MCP=true`, `NativeBuildRoot`,
  `McpPublishTempDir`, `McpOutputDir`, `--skip-mcp`), §staging hygiene
  (`.fuse_hidden*`, runtimes/win-osx-browser pruning), §assert_exists /
  assert_not_staged validation, §work-root under `/var/tmp`.
  NOT to mirror: `libnironcompress.so` deletion and the GLIBC_2.29 warning
  (RHEL 8-specific), `WINTAP_PARQUET_COMPRESSION=Uncompressed`.
- `../Lintap/packaging/lintap-rpm/lintap.env` — the field 0.3.4 configuration
  block to sync (minus the compression override).
- `../Lintap/packaging/PACKAGING_REVIEW.md` — 2026-06 review; §"Should do" 5
  (upgrade maintainer scripts) and 6 (binary-verified deps) are in scope here;
  "Nice to have" items remain deferred.

Build inputs (read-only):

- `../wintap/wintap/Lintap.csproj` §BuildMcpServer/CopyMcpServer — nested MCP
  publish controlled by `EnableMcpServer`/`DISABLE_MCP`; why the deb's plain
  publish currently pulls MCP in implicitly.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile` —
  `TRACEPOINT_OBJS` (clone, openat, execve_tracepoint, exit_tracepoint,
  network_tracepoint, file_ops_tracepoint) always built; `CORE_OBJS`
  (execve_tracer, exit_tracer, network_ops_tracer, file_ops_tracer,
  selinux_tracer) only when BTF/vmlinux available; `TARGET_ARCH` override.
- `../Lintap/pidstat-collector.py`, `../Lintap/pidstat-collector-launch.sh`,
  `../Lintap/pidstat-collector-bootstrap.sh` — staged into the package by both
  builders.

## External Sources

- Debian Policy / deb-systemd-helper and deb-systemd-invoke conventions for
  maintainer-script upgrade handling (apply the pattern; full policy
  compliance is a non-goal).

## Related Wiki Pages

- [[wiki/repo/lintap-supporting-repo]] — canonical home for packaging facts at
  closeout.
- [[wiki/workflow/lintap-dev-field-workflow]] — dev/field split rules if a
  field host ever receives the deb.
- [[wiki/work/selinux-monitoring/design]] — owns `selinux_tracer.bpf.o`
  semantics; this feature only packages the object opportunistically.
- [[wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31]]
  — the RPM 0.3.4 field validation that makes the RPM env the parity source.

## Libraries And APIs

- `dpkg-deb`, `fakeroot`, `dpkg --print-architecture`.
- .NET 8 `dotnet publish` with RID `linux-x64`/`linux-arm64`, self-contained.
- clang/bpftool/libbpf for the eBPF tracer build.

## Notes

- The deb builder already handles amd64/arm64 RID mapping and Debian-native
  `~git` versioning, `conffiles`, data-preserving purge, and fakeroot — keep
  all of these.
- Historical context: the June 2026 smoke test used `--publish-dir` against a
  Debug build because the VM could not reach NuGet; release builds must use a
  fresh publish.
