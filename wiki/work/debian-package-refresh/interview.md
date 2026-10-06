---
title: "Interview: Debian Package Refresh"
type: concept
confidence: high
grounded_by:
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Lintap/packaging/PACKAGING_REVIEW.md
policy: agent-editable
last_validated: 2026-10-03
repo_scope: Lintap
implementation_area: packaging
event_domain: none
audience: mixed
status: draft
source_paths: wiki/work/debian-package-refresh/interview.md
tags: [feature-work, lintap-packaging, debian, ubuntu, interview]
---

# Feature Interview: Debian Package Refresh

## Initial Idea

"There is packaging for an RPM for Linux. I'd like to now have a package for
debian. Scope that out for me please." (2026-10-03)

## Context Established Before Questioning

Scoping before the interview found that Debian packaging **already exists** at
`../Lintap/packaging/lintap-deb/` and was in fact the original packaging effort
(built and smoke-tested on an arm64 Ubuntu VM, June 2026); the RPM builder was
derived from it (`../Lintap/packaging/lintap-rpm/TODO.md`) and then evolved
through the RHEL 8 field deployments (0.3.4 on spk16) while the deb builder sat
still. The feature is therefore a **parity refresh**, not greenfield work.
Drift identified (taken as given, not asked):

- Stale eBPF tracer validation list: deb asserts pre-two-tier names
  (`execve_tracer`, `exit_tracer`, `network_ops_tracer`); the Makefile now
  builds `TRACEPOINT_OBJS` always and `CORE_OBJS` only when BTF is available,
  and the RPM asserts the tracepoint-tier set. Deb cross-builds fail outright.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile §CORE_OBJS/TRACEPOINT_OBJS -->
- Stale `lintap.env`: missing the field-validated sensor block
  (`WINTAP_DISABLE_MCP/DUCKDB_UI`, `WINTAP_DISABLE_ETL/SENSORS=false`, five
  `WINTAP_ENABLE_*` flags, CloneSensor opt-out) present in the RPM env.
- MCP: RPM publishes the helper separately with MSBuild isolation and
  `--skip-mcp`; deb relies on the csproj's nested MCP publish (default on).
- Work root: RPM stages under `/var/tmp` to avoid NFS/FUSE artifacts; deb
  stages under the repo `artifacts/` tree.
- `libnironcompress.so`/compression: RPM deletes the lib and forces
  Uncompressed because RHEL 8 glibc is 2.28; Ubuntu glibc is new enough.
- Review backlog still open (`PACKAGING_REVIEW.md`): upgrade-case maintainer
  scripts, dependency verification from binaries, lintian, changelog/copyright.
- New `selinux_tracer.bpf.o` in `CORE_OBJS` (sel feature, mid-flight) is
  packaged by neither builder.

## Interview Log

### Round 1

**Q:** Which Debian-family target first? (Ubuntu LTS amd64 recommended / amd64+arm64 / Debian 12)
**A:** Ubuntu amd64 + arm64.
**Outcome:** decision — both architectures are in scope and validated.

**Q:** Field deployment intent or dev smoke-test? (field-parity recommended)
**A:** Field-parity.
**Outcome:** decision — sync `lintap.env` to the RPM 0.3.4 field configuration.

**Q:** MCP helper handling? (match RPM recommended / always skip / include+enable)
**A:** Match RPM behavior.
**Outcome:** decision — separate self-contained publish into
`/usr/lib/lintap/mcp`, runtime-disabled via env, `--skip-mcp` flag.

**Q:** Package the new selinux_tracer.bpf.o? (package-if-built recommended / exclude / require)
**A:** Package if built.
**Outcome:** decision — opportunistic inclusion, never a validation failure if
absent; no coupling to the selinux-monitoring feature schedule.

### Round 2

**Q:** Native arm64 Ubuntu host available, or cross-build only? (cross-build-only recommended)
**A:** Native arm64 host available.
**Outcome:** constraint — both arches get full install + runtime smoke; host
identity/access details deferred to verification time.

**Q:** Parquet compression on Debian/Ubuntu? (keep Snappy recommended / match RPM Uncompressed / verify-then-decide)
**A:** Keep Snappy.
**Outcome:** decision — keep app-default Snappy and `libnironcompress.so`;
documented deliberate divergence from the RHEL 8 package.

**Q:** Acceptance evidence? (install + short smoke recommended / build+install only / extended gate)
**A:** Install + short smoke.
**Outcome:** decision — per-arch clean install, service start, tracer attach,
readable parquet, clean remove preserving data.

**Q:** Review-backlog scope? (deps + upgrade handling recommended / defer all / full policy pass)
**A:** Deps + upgrade handling.
**Outcome:** decision — verify `Depends:` from actual binaries via `ldd` and
handle upgrade/abort maintainer-script cases; lintian/changelog/copyright
polish deferred.

## Decisions

- Refresh existing `lintap-deb` to parity with the field-proven RPM builder.
- Targets: Ubuntu amd64 **and** arm64, both fully validated.
- Field-parity `lintap.env` (RPM 0.3.4 sensor block), except compression.
- Keep Snappy compression and `libnironcompress.so` on Debian/Ubuntu.
- MCP: match RPM builder behavior incl. `--skip-mcp`.
- `selinux_tracer.bpf.o`: package when built, never required.
- In scope: `ldd`-verified dependencies, upgrade/abort maintainer-script cases.

## Constraints

- Implementation writes only to `../Lintap/packaging/` (sibling-repo
  authorization recorded in [[wiki/work/debian-package-refresh/dev_handoff]]).
- No `../wintap` source or eBPF Makefile changes expected.
- No changes to `lintap-rpm`.

## Delegations

- Script-level details: validation lists, work-root default, flag naming.
- Final `Depends:` line, derived from `ldd` evidence on the publish output.

## Deferred / Open Questions

- arm64 host identity and access path (needed at verification time).
- Whether NuGet access limitations on build hosts persist (historical blocker;
  `--publish-dir` escape hatch exists).

## Playback Summary

Confirmed 2026-10-03: parity refresh of `../Lintap/packaging/lintap-deb/` to
the field-proven RPM builder; Ubuntu amd64 + arm64 both validated; field-parity
env except Snappy kept; MCP parity with `--skip-mcp`; selinux object
opportunistic; deps verification and upgrade-case maintainer scripts in scope;
lintian/changelog/copyright, systemd hardening, apt hosting, extended runtime
gates, and sensor code changes out of scope. Acceptance: per-arch build,
install, service start, tracer attach, readable parquet, clean remove
preserving `/var/log/lintap`, and upgrade-in-place leaving the service enabled.

## Sealed — human estimates

<!-- SEALED: any agent that will produce its own estimates must not read this
section until feature close-out. See wiki/decision/ai-velocity-roi-mini-lab
(v2.1) and wiki/concept/velocity-metric. -->

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available? (Forced counterfactual.)**
**A:** "~16 hours, ~2 weeks out" (selected from offered buckets; two focused
days of effort, realistic availability about two weeks from 2026-10-03, i.e.
approximately 2026-10-17).

**Q: With the AI workflow, on what date do you predict this feature will be
available? (Calendar prediction, open date to availability.)**
**A:** "Within 2 days (by 2026-10-05)" (selected from offered buckets).
