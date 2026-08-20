---
title: "Consolidate Developer Wiki into Analytics Wiki"
type: decision
confidence: high
grounded_by:
  - ../Wintap-Analytics/AGENTS.md
  - ../Wintap-Analytics/wiki/decision/wiki-scope-cross-repo-wintap-focused.md
  - ../Wintap-Analytics/wiki/decision/feature-work-artifacts.md
  - ../wintap/CLAUDE.md
  - ../wintap/.claude/agents/engineer.md
  - ../wintap/dave-wiki/wiki/log.md
policy: agent-editable
last_validated: 2026-08-17
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: accepted
source_paths: ../Wintap-Analytics/AGENTS.md; ../Wintap-Analytics/wiki; ../wintap/CLAUDE.md; ../wintap/dave-wiki
tags: [decision, wiki, cross-repo, wintap, workflow]
---

# Consolidate Developer Wiki into Analytics Wiki

## Context

The Wintap ecosystem had two active wiki systems:

1. `../wintap/dave-wiki/`, the per-developer wiki created by the Wintap Architect / Engineer / Developer workflow, containing two ADRs under `wiki/decisions/`, `wiki/log.md`, and one scratch note under `sources/`.
2. `../Wintap-Analytics/wiki/`, the mature cross-repo Wintap ecosystem wiki with established taxonomy (`decision/`, `repo/`, `component/`, `event_type/`, `tension/`, `concept/`, `work/<feature-slug>/`), frontmatter conventions, a source policy, and the accepted decision that the wiki is cross-repo but Wintap-focused.

The `improve-windows-process-collection` feature made the split visible: design artifacts lived in `../Wintap-Analytics/wiki/work/improve-windows-process-collection/`, while Wintap-side ADR/log history lived in `../wintap/dave-wiki/` and Developer process artifacts lived under `../wintap/developer_docs/`.

## Decision

The Wintap-Analytics wiki is the single knowledge base for the Wintap ecosystem. `../wintap/dave-wiki/` is retired.

`../wintap/developer_docs/instructions/` and `../wintap/developer_docs/audits/` remain in the Wintap repository. They are process artifacts tied to code changes, approval gates, test traits, audit records, and PR/review flow in that repo. They are not the long-lived knowledge base.

Collision avoidance, the original reason for per-developer wiki directories, is handled by the existing feature-work layout. In-flight work primarily writes to `wiki/work/<feature-slug>/`, which naturally shards by feature and owner. The shared `wiki/log.md` remains the low-volume chronological operation log. Durable facts are promoted from work artifacts into canonical pages according to [[wiki/decision/feature-work-artifacts]].

Cross-repo write direction is explicitly blessed for this workflow: the Wintap repo's Engineer agent is authorized to write to `../Wintap-Analytics/wiki/` and only to `../Wintap-Analytics/wiki/`, while continuing to write Wintap process artifacts under `../wintap/developer_docs/`. This reverses the direction anticipated by the previous Analytics operating contract, which treated sibling repos as the read-only side for wiki-maintainer mode.

Both repositories are public GitHub repositories. Moving the wiki does not create a confidentiality gain or loss. The normal rule remains: do not write secrets, credentials, private host details, or other sensitive material into either repo.

## Migration Inventory

The initial consolidation migration moved the following knowledge artifacts:

- `../wintap/dave-wiki/wiki/decisions/2026-06-30-process-identity-attribution-contract.md` → `wiki/decision/process-identity-attribution-contract.md`
- `../wintap/dave-wiki/wiki/decisions/2026-06-30-test-project-structure-and-first-test.md` → `wiki/decision/test-project-structure-and-first-test.md`
- `../wintap/dave-wiki/sources/2026-08-17-wpc-01-sid-helper-notes.md` → `wiki/work/improve-windows-process-collection/sid-helper-notes-2026-08-17.md`
- the five entries from `../wintap/dave-wiki/wiki/log.md` were merged into `wiki/log.md` with `[wintap]` provenance in the entry title.

`../wintap/dave-wiki/README.md` is replaced with a tombstone. The remaining files are left in place for the Architect to remove later with git.

## Rationale

One ecosystem wiki avoids split-brain feature context. The Analytics wiki already has the cross-repo taxonomy, frontmatter conventions, feature-work structure, and accepted scope decision needed to hold Wintap design knowledge. Keeping instruction and audit documents in the Wintap repo preserves their tight relationship to code-review units, test categories, and implementation history.

The feature-work folder convention provides enough practical sharding for current LLM-assisted work without preserving an entire second wiki hierarchy. It also makes Wintap feature context easier for future agents to find because feature briefs, references, designs, implementation plans, verification records, and now scratch notes are colocated.

## Consequences

- Wintap Engineer sessions now start by reading `../Wintap-Analytics/wiki/log.md` and relevant pages under `../Wintap-Analytics/wiki/`, not `../wintap/dave-wiki/wiki/log.md`.
- New ADRs for Wintap ecosystem work are written under `../Wintap-Analytics/wiki/decision/` using Analytics frontmatter conventions.
- Scratch notes for feature work go in the relevant `../Wintap-Analytics/wiki/work/<feature-slug>/` folder, not in `dave-wiki/sources/`.
- The Wintap Developer remains read-only with respect to the wiki. It continues to write code, tests, and one audit artifact per approved instruction.
- Historical instruction and audit documents in `../wintap/developer_docs/` may retain stale `dave-wiki` references; the tombstone covers those links and they are not rewritten as part of this migration.

## Alternatives Considered

- **Keep both wikis:** rejected because it duplicates design memory and leaves cross-repo features split across multiple knowledge bases.
- **Move instructions and audits into Wintap-Analytics:** rejected because those artifacts are part of the Wintap repo's implementation approval and verification flow, not general ecosystem knowledge.
- **Use per-developer wiki directories indefinitely for collision avoidance:** superseded by the feature-work folder model plus the low-volume shared log.

## Supersedes / Superseded By

Supersedes the per-developer-wiki scheme recorded in the Wintap methodology bootstrap log entry from 2026-06-30 and in the pre-migration Wintap `CLAUDE.md` / agent files. This decision does not supersede the Wintap Architect / Engineer / Developer workflow itself; it changes the location of its wiki memory.
