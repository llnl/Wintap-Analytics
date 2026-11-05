---
title: "Tension: pidstat publication versus uploader receipts"
type: tension
status: open
poles:
  - "Keep the existing uploader contract and compatible filesystem publication."
  - "Exactly-once crash recovery needs durable evidence after the uploader removes a file."
resolution: null
confidence: high
grounded_by:
  - ../Lintap/pidstat-go/collector.go
  - ../Lintap/pidstat-collector.py
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
source_paths: pidstat-go/collector.go
tags: [pidstat, recovery, publication, uploader, compatibility]
---

# Tension: pidstat publication versus uploader receipts

Go fpc-03 installs completed Parquet atomically with no overwrite, then persists a
publication receipt before deleting its input. Recovery recognizes an existing
publication by its owned active inode/hash; a durable published receipt prevents
replay even if the uploader subsequently removes the completed file.
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/collector.go §convert -->

A crash after installation but before the published receipt, combined with uploader
removal in that gap, leaves no durable evidence distinguishing “never installed”
from “already delivered.” Recovery may replay that window. The unchanged Python
reference likewise publishes before source deletion without an end-to-end receipt.
**This is at-least-once behavior, not an exactly-once delivery guarantee.**
<!-- SYNTHESIS: inferred from ../Lintap/pidstat-go/collector.go §convert and ../Lintap/pidstat-collector.py §convert_spool_to_parquet -->

Do not silently claim or implement exactly-once delivery under a collector-only
compatibility rewrite. Resolving the gap would require an explicit uploader/receipt
contract decision and separate authorization. Fpc-03 tests process-crash recovery
with completed output still present and uploader deletion after a durable receipt;
real shared-uploader race/power-loss qualification remains open.

Related: [[wiki/work/fix-pidstat-collector/verification]],
[[wiki/repo/lintap-supporting-repo]].
