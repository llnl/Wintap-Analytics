---
title: "Research Flexibility vs Production Hardening"
type: tension
confidence: medium
grounded_by:
  - ../wintap/README.md
  - ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs
  - ../Wintap-Analytics/2025-acme4-explore/README.md
  - ../Lintap/README.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: open
source_paths: ../wintap/README.md; ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs; ../Wintap-Analytics/2025-acme4-explore/README.md; ../Lintap/README.md
resolution: null
poles:
  - "Optimize for security research, direct telemetry access, notebooks, local DuckDB workflows, and rapid experimentation."
  - "Harden deployments with stable packaging, access controls, bounded resource use, and production-safe interfaces."
tags: [tension, research-workflows, architecture]
---

# Research Flexibility vs Production Hardening

## Tension

The Wintap README explicitly frames the platform as researcher-first and designed for security research, behavioral analysis, and exploratory investigations rather than enterprise-scale endpoint management.
<!-- GROUND_TRUTH: ../wintap/README.md §Wintap -->

This research posture appears in analytics workflows as notebook-driven ACME4 exploration over public or local Parquet files through DuckDB, and in Lintap's legacy sysdig path as a flexible playground for testing ideas quickly rather than long-term large deployments.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-acme4-explore/README.md §ACME4 Explore -->
<!-- GROUND_TRUTH: ../Lintap/README.md §Running Lintap -->

The MCP tool documentation makes the hardening gap explicit: `RunSQL` exposes arbitrary SQL with no input validation, authentication, authorization, or access control, and the code comments label the implementation research/proof-of-concept only.
<!-- GROUND_TRUTH: ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs §Security Considerations -->

## Current Holding Pattern

Preserve the research-first framing when documenting workflows, but mark unsafe or proof-of-concept interfaces clearly. Do not silently rewrite research tradeoffs into production endpoint-management assumptions.
<!-- SYNTHESIS: inferred from ../wintap/README.md and ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs -->
