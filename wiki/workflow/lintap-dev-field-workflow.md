---
title: "Lintap Dev/Field Split: Roles, Read-Only Policy, and Evidence Flow"
type: workflow
confidence: high
grounded_by:
  - extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh
  - wiki/work/optimize-fileops-poller/dev_handoff.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: none
audience: mixed
status: draft
source_paths: wiki/workflow/lintap-dev-field-workflow.md
tags: [lintap, dev-environment, diagnostics, workflow, field-host, git-policy]
---

# Lintap Dev/Field Split: Roles, Read-Only Policy, and Evidence Flow

How Lintap feature work moves between the development VM and the RHEL8 field
host, and the constraints each side operates under. Established during the
`optimize-fileops-poller` phase-2 work (2026-08-25).

## The two systems

- **Dev VM (`lintap-dev`, arm64 multipass):** where code is written, built,
  unit-tested, and committed on `grantj-rhel8-testing` in both `../wintap`
  and `Wintap-Analytics`. All wiki writing happens here.
- **Field host (`spk16.llnl.gov`, RHEL8 x86):** where builds are deployed,
  workloads run, and diagnostics bundles are collected.

## Field-side read-only policy (2026-08-25, human-directed)

The field host's git clones are **read-only: no commits or pushes from that
system** — a policy constraint, not a technical one. Consequences:

1. **Field reviews are transcribed dev-side.** Bundle reviews performed on
   the field host arrive as summaries; the wiki maintainer transcribes them
   into `wiki/work/<feature>/verification.md` and `wiki/log.md` here,
   clearly sourced (e.g. "recorded from implementor review summaries").
   Before any push, audit that field evidence referenced in conversation
   actually exists in this clone — it will not arrive via git.
2. **Diagnostics bundles must be self-sufficient.** Everything a review
   needs should be extracted into the
   `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` bundle
   itself, because follow-up analysis cannot be committed field-side. This
   is why the collector carries targeted triage extracts (`resolve=`,
   `agg=`, `sender=` counter sections, esper-errors grep) and
   `duckdb/fileops-parquet-sanity.txt` rather than relying on ad-hoc
   field-side queries.
3. **Deploys pull; they never commit.** Pulling code to the field host is
   allowed. The field host rebuilds its own eBPF tracer objects
   (`*.bpf.o` are gitignored and architecture-specific — never deploy
   objects built on the arm64 dev VM).

## Push mechanics

The dev VM has **no git push credentials** (HTTPS remotes, no credential
helper, no SSH keys, no `gh`). Commits are made on the dev VM; the human
pushes, e.g.:

```
! git -C /home/ubuntu/git/Wintap-Analytics push origin grantj-rhel8-testing
! git -C /home/ubuntu/git/wintap push origin grantj-rhel8-testing
```

## Agent memory policy (human-directed, 2026-08-25)

Anything the agent records in its private session memory (`~/.claude/...`)
that matters to the project **must also exist in the wiki** — the wiki is
the shared knowledge base; agent memory is a private convenience pointer,
never the sole home of project context. When a memory file is written or
updated, mirror its substance into the appropriate wiki page in the same
session.
