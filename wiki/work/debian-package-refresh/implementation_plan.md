---
title: "Implementation Plan: Debian Package Refresh"
type: concept
confidence: medium
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
source_paths: wiki/work/debian-package-refresh/implementation_plan.md
tags: [feature-work, lintap-packaging, debian, implementation-plan]
---

# Implementation Plan: Debian Package Refresh

## Scope

Parity refresh of `../Lintap/packaging/lintap-deb/` against the field-proven
RPM builder, per [[wiki/work/debian-package-refresh/brief]]. Slices use the
`dpr-NN` prefix.

## Steps

### dpr-01 — build-deb.sh parity refresh

- Replace `expected_bpf_objects` with tier-aware validation:
  - Always required: `clone_tracer`, `openat_tracer`, `execve_tracepoint`,
    `exit_tracepoint`, `network_tracepoint`, `file_ops_tracepoint` (.bpf.o).
  - Required on native builds (BTF available): `execve_tracer`, `exit_tracer`,
    `network_ops_tracer`, `file_ops_tracer` (.bpf.o).
  - Opportunistic (stage if present, never fail): `selinux_tracer.bpf.o`.
- Mirror the RPM MCP approach: publish main app with `EnableMcpServer=false`
  and `DISABLE_MCP=true` plus `NativeBuildRoot`/`McpPublishTempDir`/
  `McpOutputDir` MSBuild props; publish the MCP helper separately
  (self-contained, single-file) into `/usr/lib/lintap/mcp`; add `--skip-mcp`
  (and `LINTAP_SKIP_MCP`); scrub stale `mcp`/`mcp_temp` staging on skip.
- Add `--work-root` (default `/var/tmp/lintap-deb-build`) and `--host-arch`,
  mirroring the RPM's native-filesystem work-root and cross-build messaging;
  keep final `.deb` output under `artifacts/lintap-deb/`.
- Keep: amd64/arm64 RID mapping, `~git` version format, conffiles, fakeroot,
  purge semantics, existing staging hygiene. Do NOT port: `libnironcompress.so`
  deletion, GLIBC_2.29 warning.

### dpr-02 — lintap.env field-parity sync

- Copy the RPM env's field block: `WINTAP_DISABLE_MCP=true`,
  `WINTAP_DISABLE_DUCKDB_UI=true`, `WINTAP_DISABLE_ETL=false`,
  `WINTAP_DISABLE_SENSORS=false`, the five `WINTAP_ENABLE_*` sensor flags,
  `WINTAP_ENABLE_CLONE_SENSOR=false`.
- Omit `WINTAP_PARQUET_COMPRESSION=Uncompressed` (keep Snappy); add a comment
  documenting the divergence and why.

### dpr-03 — maintainer scripts and dependency verification

- postinst/prerm/postrm: handle `upgrade`, `failed-upgrade`, `abort-install`,
  `abort-upgrade` deliberately so an in-place upgrade restarts (not disables)
  the services; follow deb-systemd-helper/invoke patterns without taking a
  hard tool dependency.
- Run `ldd` over the staged `Lintap`, bundled `*.so` (including
  `libnironcompress.so`), and the MCP binary; finalize `Depends:`
  (current guess: `libbpf1, libc6, zlib1g, libelf1, systemd`).

### dpr-04 — docs refresh

- Update `README.md` and `BUILD_AND_TEST.md` for the new flags, tier-aware
  validation, MCP behavior, and field-parity env.
- Rewrite or retire `LLM_RESTART.md` (describes the June 2026 macOS/VM/NuGet
  environment).

### dpr-05 — amd64 build + smoke

- Fresh-publish build on the amd64 Ubuntu host; run the full acceptance list
  (install, start, tracer attach, parquet readable, upgrade-in-place, remove/
  purge). Record in verification.md.

### dpr-06 — arm64 build + smoke

- Same on the native arm64 host (identity/access to be supplied at
  verification time).

### dpr-07 — closeout

- Promote durable facts to [[wiki/repo/lintap-supporting-repo]] (deb/RPM
  parity contract, compression divergence); metrics.md per
  [[wiki/concept/metrics-template]]; log entry.

## Files Likely To Change

- `../Lintap/packaging/lintap-deb/build-deb.sh`
- `../Lintap/packaging/lintap-deb/lintap.env`
- `../Lintap/packaging/lintap-deb/README.md`
- `../Lintap/packaging/lintap-deb/BUILD_AND_TEST.md`
- `../Lintap/packaging/lintap-deb/LLM_RESTART.md` (refresh or retire)
- No changes: service units, `lintap-rpm/`, `../wintap` sources.

## Tests To Add Or Update

- Script-internal `assert_exists`/`assert_not_staged` lists (the packaging
  "tests"); tier-aware assertions per dpr-01.
- Manual smoke sequences recorded in verification.md; no CI exists for
  packaging today.

## Migration Or Compatibility Notes

- Existing June 2026 arm64 deb installs: upgrade path exercised by dpr-03/05.
- Config: `/etc/lintap/lintap.env` is a conffile; dpkg will prompt on upgrade
  where locally modified — expected and acceptable.
- Snappy divergence means deb-host parquet differs from RHEL 8 RPM-host
  parquet in compression only; Wintappy reads both.

## Rollback Plan

Packaging-only change set in `../Lintap`; revert the branch commits. No
installed-host migration needed beyond reinstalling a prior .deb.

## Done Checklist

- [x] dpr-01 build-deb.sh parity refresh
- [x] dpr-02 lintap.env field-parity sync
- [x] dpr-03 maintainer scripts + ldd-verified Depends
- [x] dpr-04 docs refresh
- [x] dpr-05 amd64 build + smoke PASS
- [x] dpr-06 arm64 build + smoke PASS (sensor attach caveat recorded)
- [ ] dpr-07 closeout (promotion, metrics, log)
