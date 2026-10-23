---
title: "Implementation plan: Clone default TRUE"
type: concept
confidence: high
grounded_by:
  - wiki/work/clone-default-true/verification.md
  - wiki/work/clone-default-true/dev_handoff.md
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: developer
status: draft
source_paths: ../Lintap/packaging; ../wintap/devtools
tags: [clone, feature-work, default, implementation-plan]
---

# Implementation plan: Clone default TRUE

- [x] Enable Clone in Debian/RPM env templates, retain opt-out and update package docs
- [x] Require Clone CO-RE object in native/BTF Debian and RPM payload validation
- [x] Prominent fallback thread-quality warning and missing-flags negative validation
- [x] Fresh self-contained Ubuntu arm64 package build/install
- [x] Repair startup receipt reset found by normal packaged ETL test; focused regression
- [x] Complete normal ETL manifest, bounded churn, restart, HOST and opt-out checks
- [ ] Complete separate loss-counter/resource review; no Clone-only overhead claim
- [x] Prepare RHEL dev handoff (RHEL execution belongs to user's separate environment)
- [ ] RHEL acceptance elsewhere; no Ubuntu result promoted to RHEL certification

Results and open gates: [[wiki/work/clone-default-true/verification]].
