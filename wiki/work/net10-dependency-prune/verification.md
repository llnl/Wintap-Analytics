---
title: ".NET10 Ubuntu package baseline: verification summary"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/global.json
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: packaging
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap; ../Lintap/packaging; streamlit/projects/SmokeTests
tags: [net10, packaging, verification, retrospective]
---

# .NET10 installed-package baseline

The supplied self-contained Debian package was installed on Ubuntu24.04 arm64
`lintap-dev` on2026-10-23. Runtime configuration reported .NET10.0 and bundled
NETCore/ASP.NET10.0.13. Initial process/file/network capture smokes passed;independent
Mac queries/dashboard confirmed published telemetry and workload evidence.

The same installed service then completed a30-minute soak:20/20runs completed,
5,000/5,000file paths retained,stable collector PID and zero restarts. Sampled
serializer drops were zero. Named server TCP Accept/UDP Receive remained missing;
named stimulus generation was not promoted to full capture acceptance. RSS/CPU
observations were diagnostic,not performance or multi-day qualification.

This is the historical baseline,not installed acceptance of later identity/ETL
changes. It did not verify DBT,pidstat,Windows live runtime,complete kernel/durable
delivery or final-package shutdown. Later work expanded beyond the upgrade scope:
[[wiki/work/wintap-telemetry-identity-and-data-quality/brief]].

Original commands,configuration,package hash,host paths and soak reports are retained
in [[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]],archive member
`wiki/work/net10-dependency-prune/verification.md`.
