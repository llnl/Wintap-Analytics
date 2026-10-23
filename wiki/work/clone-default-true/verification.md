---
title: "Clone default-TRUE package verification"
type: diagnostic
confidence: medium
grounded_by:
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-deb/lintap.env
  - ../Lintap/packaging/lintap-rpm/lintap.env
  - ../wintap/devtools/validate_clone_package.py
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: developer
status: draft
source_paths: ../Lintap/packaging; ../wintap/devtools
tags: [clone, default, ubuntu, arm64, acceptance]
---

# Clone default-TRUE package verification

User authorized default change and Ubuntu/arm testing; RHEL runs delegated to
the user's separate environment via [[wiki/work/clone-default-true/dev_handoff]].
Source configs already had Clone=true; package environment overrides are now
true in Debian and RPM, retaining opt-out. Both existing duplicate Debian
assignments were changed rather than deleting potentially unrelated config.
Native/BTF Debian validation and the RPM CO-RE payload list now require
`clone_core_tracer.bpf.o`. Fallback logs a prominent thread-classification warning.

## Completed preparation

- Fresh self-contained Debian `0.1.0-103`, arm64, built natively from the current
  uncommitted source with `--skip-mcp`, not `--publish-dir`.
- Build command on `lintap-clone-validation`:
  `LINTAP_OUTPUT_DIR=/home/ubuntu/clone-validation/packages bash /home/ubuntu/Lintap/packaging/lintap-deb/build-deb.sh --project-dir /home/ubuntu/clone-validation/source/wintap --version 0.1.0 --revision 103 --arch arm64 --runtime linux-arm64 --skip-mcp --work-root /home/ubuntu/clone-validation/package-build`.
- Full publish, staged object validation, dependency checks and package creation
  passed; optional .NET diagnostic-provider ldd warning retained in build log.
- New disposable `lintap-clone-package`: Ubuntu 24.04 arm64,
  kernel `6.8.0-147-generic`, 2 CPUs/4 GB. Installed with apt; service initially
  inactive, packaged Clone=true and both Clone objects present. No Clone opt-in
  override or diagnostic config is added for the default capture.
- Python venv+DuckDB and manifest workload built on native storage.
- Actual fallback primary-only negative test on builder VM:
  `validate_clone_trace.py --primary-only` expected exit 1, 80 real processes
  retained but **60 false thread births**; no clone3 skips or wrong worker parents.
  Report: `/home/ubuntu/clone-validation/default-fallback-no-hooks/report.json`.
- Updated fallback with normal hooks repeated on builder VM: all 80 process
  births captured, all 60 threads excluded, correct worker parents, no duplicates/
  skips (`default-fallback-full/report.json`).
- `bash -n` on both package builders passes.
- Initial installed `0.1.0-103` receipt assertion failed before workload:
  `WINTAP_SKIP_PROCESS_RESOLVE` absent. Lazy plugin initialization unconditionally
  reset receipt settings after startup recording. Replaced reset with idempotent
  `EnsureInitialized`; added regression. This was an application receipt bug,
  not a Clone attach failure. Environment restored and service stopped.
- Rebuilt/installed self-contained `0.1.0-104` with the fix; package SHA-256:
  `14be81e1affff64dfcfff37aa98c6aae07c08ff48dfd5ece7d27a9f133ab5676`.
  Build log `/home/ubuntu/clone-validation/package-build104.log`; same native
  build command above with revision 104.
- Focused receipt/resolver/serializer schedule tests: **127 pass**, no failures/
  skips. Both source repos' `git diff --check` pass.
- Pure manifest evaluator missing-flags regression passes (zero flags admit a
  thread; CLONE_THREAD flags reject it). Twelve 5-second resource samples saved
  to `/home/ubuntu/clone-package-resource-samples.json` on the package VM; these
  are full-collector samples, not isolated Clone overhead measurements.

## Gates

- [x] Fresh native arm64 publish/package/install; true-default payload and CO-RE requirement
- [x] Fallback missing-flags negative test remains visibly unsafe, not certified
- [x] Normal packaged ETL captures manifest births/filters threads/parent TGIDs
- [ ] Bounded 100-round churn capture and loss/counter review
- [x] Published HOST receipt, same-root restart and explicit opt-out
- [x] Focused regressions and diff checks
- [ ] RHEL x86_64 fresh RPM/default/opt-out/restart/fallback acceptance elsewhere

Normal packaged acceptance completed successfully with
`sudo /home/ubuntu/receipt-venv/bin/python /home/ubuntu/wintap/devtools/validate_clone_package.py --workload /home/ubuntu/clone-workload --output /home/ubuntu/clone-package-acceptance104`.
Normal ETL captured all 80 baseline and 400 bounded-churn process births, excluded
all thread Starts, retained correct worker parents, and had no PidHash splits.
No clone3 skips. Fork+exec produced three Start rows per identity; opt-out retained
two exec observations and no fork-only births. HOST/log JSON, fresh restart run ID
and Clone running/running/disabled statuses passed. Harness restored both Clone=true
env entries and stopped the service. Full loss counter/resource review remains
separate and open. Field stimulus: [[wiki/tool/named-telemetry-smoke-workload]].
