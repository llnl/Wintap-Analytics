---
title: "Attribution strategy: compact retrospective and deferred research"
type: workflow
confidence: speculative
grounded_by:
  - wiki/diagnostic/sample-db-runtime-attribution-audit.md
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap; ../Wintappy; wiki/work
tags: [strategy, attribution, speculative, retrospective]
---

# Strategy retained

Prevent fabricated identities first;capture authoritative lifecycle evidence early;
then diagnose admission and delivery with bounded receipts. Identity,lifecycle
coverage,image/role classification and collection completeness are separate axes.
Classification must not invent identity,suppress evidence or imply benignness.

Implemented progress:canonical identity/kernel birth safeguards,bounded exit-only
recovery experiments,collector visibility,downstream count/precision fixes and exact
startup/shutdown ordering. Scoped verification is summarized in
[[wiki/work/wintap-telemetry-identity-and-data-quality/verification]].

## Still proposals—not implemented acceptance

- General runtime role/image timelines or short-lived classification policy.
- Grouped lifetime-qualified retry lookups,production queue sizing and broader
  cache/retention budget changes.
- Complete lifecycle/namespace/PID-reuse/suspend coverage and kernel loss accounting.
- Deterministic metadata precedence,compatible quality/capability schema extensions
  and historical dataset migration.

Prefer reproducible controls and measured lag/resource accounting to enlarged queues
or arbitrary settling sleeps. Preserve unknowns,failed traces and historical losses.
Existing Windows process-name mapping is not a trusted Linux classifier/allowlist.

Next planned phase is clean package qualification and days-long real-host collects;
see [[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]]. No new source
edits or host rollout are authorized by this strategy. Original detailed tactical
proposal:[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
