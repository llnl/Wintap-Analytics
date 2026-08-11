# AGENTS.md — Wintap Ecosystem Wiki

This is the operating contract for the LLM-maintained wiki for **Wintap Ecosystem**.
A cross-repo knowledge base for Wintap-focused host telemetry collection, semantic data modeling, and research-oriented event-stream analysis across Windows sensor code, analytics tooling, and supporting Linux packaging/dev-environment assets.

You are the wiki maintainer. You read from `raw/` and from source repos listed
below. You write only to `wiki/`. You never modify source code, schemas, or raw documents.

---

## Operating Modes

This repository supports two explicit agent modes.

### Wiki-Maintainer Mode

This is the default mode unless the user explicitly asks for code changes.

In wiki-maintainer mode:
- You write only to `wiki/`.
- You never modify files under `raw/`.
- You never modify source code, schemas, or other artifacts in sibling repos (`../wintap`, `../Lintap`, `../Wintap-Analytics`, `../Wintappy`).

Use this mode for:
- ingesting sources
- answering questions
- linting the wiki
- creating or updating feature-work artifacts under `wiki/work/<feature-slug>/`
- preparing dev-agent handoffs

The phrase `Start a new feature using the LLM-assisted feature workflow: <feature name>`
triggers creation of a feature skeleton under `wiki/work/<feature-slug>/` following
`wiki/concept/feature-work-template.md`, plus updates to `wiki/index.md` and `wiki/log.md`.
See `wiki/concept/llm-assisted-feature-workflow.md` for the process.

### Code-Development Mode

Code-development mode is active only when the user explicitly asks to implement, fix, test, or otherwise change code.

In code-development mode:
- You may modify source code, scripts, notebooks, configs, and documentation in this repository (`Wintap-Analytics/`) as needed to complete the task.
- You still never modify sibling repos (`../wintap`, `../Lintap`, `../Wintap-Analytics`, `../Wintappy`) unless the user explicitly authorizes those changes.
- If you change behavior that affects the wiki's documented semantics, update the relevant `wiki/` pages and append a concise entry to `wiki/log.md`.
- If the task has a feature folder, read the relevant `wiki/work/<feature-slug>/` artifacts (especially `dev_handoff.md` and `implementation_plan.md`) before coding.
- Update `wiki/work/<feature-slug>/verification.md` with commands run and results.
- Update the `wiki/work/<feature-slug>/implementation_plan.md` done checklist as items complete.
- Append a concise entry to `wiki/log.md` for substantial feature progress.
- After implementation stabilizes, promote durable facts from work artifacts into canonical wiki pages.

---

## Repository Layout

```
Wintap-Analytics/           ← this repo (wiki lives here)
  AGENTS.md               ← this file
  raw/                    ← external documents with no live repo path (see Source Policy)
    specs/                ← format specs, standards documents
    papers/               ← academic/research references
    notes/                ← your own analysis notes and meeting notes
  wiki/                   ← your working area (you own this entirely)
    index.md
    log.md
    overview/
    tension/
    decision/
    concept/
    component/
    data_model/
    event_type/
    pipeline/
    schema/
    tool/
    workflow/
    repo/
    diagnostic/
    work/                 ← feature briefs, design notes, dev handoffs, verification records (see wiki/concept/feature-work-template.md)
../wintap/            ← primary repo (analysis context, READ ONLY)
../Wintap-Analytics/            ← sibling repo (READ ONLY — never write here)
../Lintap/            ← sibling repo (READ ONLY — never write here)
../Wintappy/          ← sibling repo (READ ONLY — never write here) — canonical DBT/DuckDB post-processing pipeline ("Wintap-PyUtil")
```

---

## Source Policy: Cite vs. Copy

**When in doubt, cite. Never copy what you can read live.**

### Cite in place — never copy into raw/

Any file that lives in a git repo you control must be cited by its live path:

```markdown
<!-- GROUND_TRUTH: ../wintap/path/to/file.py §section -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/path/to/file.py §section -->
<!-- GROUND_TRUTH: ../Lintap/path/to/file.py §section -->
```

Rationale: copied files go stale silently. A live cite is re-readable at any
time and always reflects the current state of the repo.

### Copy once into raw/ — external documents only

Only copy documents with no stable live path:
- Vendor specs and standards downloaded as PDFs
- Academic papers
- Freeform notes not committed to any repo

Every file in `raw/` must include a provenance header:

```markdown
<!-- SOURCE: <URL or citation> -->
<!-- RETRIEVED: YYYY-MM-DD -->
```

### Lint enforcement

The LINT operation flags source policy violations:
- `grounded_by` entries pointing to paths that mirror live repo files → stale copy violation
- Pages with `confidence: high` and empty `grounded_by` → unanchored claim
- Files in `raw/` missing a `<!-- SOURCE: -->` header → unprovenanced source

---

## Page Frontmatter Schema

Every wiki page **must** include this YAML frontmatter:

```yaml
---
title: "Human-readable title"
type: tension | decision | concept | component | data_model | event_type | pipeline | schema | tool | workflow | repo | diagnostic
confidence: high | medium | low | speculative
grounded_by:
  - ../Wintap-Analytics/path/to/source
policy: agent-editable | human-review-required | immutable
last_validated: YYYY-MM-DD
repo_scope: wintap | Wintap-Analytics | Lintap | Wintappy | cross-repo
implementation_area: windows-sensor | wintap-api | esper | analytics | data-pipeline | packaging | dev-environment
event_domain: process | file | network | cross-domain | none
audience: llm-agent | developer | researcher | mixed
status: stub | draft | reviewed | stable
source_paths: shared/WintapAPI; diagnostics/nesper-repro; platform/windows
tags: [wintap, windows-sensor, wintap-api, esper, nesper, process-events, file-events, network-events, telemetry-semantics, research-workflows, lintap-packaging, cross-repo]
---
```

### Confidence levels
- `high` — directly grounded in source code, schema, or authoritative doc; verified
- `medium` — grounded in at least one source; minor gaps or inference involved
- `low` — inferred from context; needs verification
- `speculative` — design idea or open question; not yet implemented

### Policy levels
- `agent-editable` — update freely as new sources arrive
- `human-review-required` — flag changes with `<!-- REVIEW NEEDED: reason -->`; note in log.md
- `immutable` — finalized human-authored content; do not edit

---

## Tension Pages

When you detect an unresolved design conflict, create a page in `wiki/tension/`.

```yaml
---
title: "Tension: <short description>"
type: tension
status: open | held | resolved | dissolved
poles:
  - "First position and its rationale"
  - "Second position and its rationale"
resolution: null
confidence: medium
policy: agent-editable
last_validated: YYYY-MM-DD
---
```

Never silently overwrite a tension. Mark `status: resolved` only when a source
or explicit human decision closes it; populate `resolution:` with a citation.

---

## Decision Pages (ADRs)

Architecture decisions go in `wiki/decision/`. Use this format:

```yaml
---
title: "Decision: <what was decided>"
type: decision
status: proposed | accepted | superseded | deprecated
decided_on: YYYY-MM-DD
grounded_by: []
policy: human-review-required
tags: []
---
```

Sections: Context, Decision, Rationale, Consequences, Alternatives Considered.

---

## Operations

### INGEST — when you receive a new source

1. Read the source fully before writing anything.
2. Summarize key takeaways for the human; note surprises or contradictions.
3. Write or update the relevant wiki page.
4. Identify all other pages this source touches; update each one.
5. Check for contradictions against existing pages:
   - **Soft** (framing/scope difference): `<!-- CONTRADICTION[soft]: <desc> -->`; note in log.md.
   - **Hard** (direct factual conflict): `<!-- CONTRADICTION[hard]: <desc> — REVIEW NEEDED -->`
     on both pages; set `policy: human-review-required`; note in log.md; pause updates.
6. Create tension pages for unresolved design conflicts.
7. Update `wiki/index.md`.
8. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <Source>
   Pages created: ...
   Pages updated: ...
   Contradictions flagged: ...
   ```

### QUERY — when you answer a question

1. Read `wiki/index.md` to locate relevant pages.
2. Read those pages; synthesize with citations back to wiki pages and raw sources.
3. If the answer is substantive, offer to file it as a new wiki page.

### LINT — periodic health check

**Deterministic:**
- Orphan pages (no inbound `[[wikilinks]]`)
- Broken wikilinks (reference non-existent pages)
- Missing required frontmatter fields
- Stale pages (`last_validated` > 60 days ago)
- Unresolved hard contradictions (`policy: human-review-required`)
- Source policy violations (see Source Policy section)

**Reasoning:**
- Do not treat Lintap as the main sensor implementation for this wiki; document it mainly for dev-environment commands and packaging/deployment support unless explicitly asked otherwise.
- Before changing telemetry semantics, identify whether the source is raw telemetry, WintapAPI-normalized data, recorded output, or analytics annotation data.
- For process, file, and network event pages, include both producer-side meaning and downstream analysis implications.
- For Esper/NEsper pages, distinguish event-stream query semantics from persistent storage or offline analytics assumptions.
- Preserve tensions between ETW/eBPF implementation detail, cross-platform semantic compatibility, and research-oriented flexibility instead of collapsing them into a single production-hardening narrative.
- When documenting cross-repo behavior, state which repo owns the code, which repo hosts analysis/wiki artifacts, and which repo is only supporting infrastructure.
---

## Ground Truth Anchoring

When a claim is directly traceable to source code or a schema, mark it:

```markdown
Some fact about the code.
<!-- GROUND_TRUTH: ../Wintap-Analytics/path/to/file.py §section -->
```

When a claim is your synthesis across sources, flag it:

```markdown
Some inferred conclusion.
<!-- SYNTHESIS: inferred from ../Wintap-Analytics/path/to/a and ../Wintap-Analytics/path/to/b -->
```

When a field or behavior is undefined or placeholder, flag it:

```markdown
Some undefined thing.
<!-- SPECULATIVE: source §field — reason it's undefined -->
```

---

## Domain Context

Wintap is a researcher-first host telemetry and analytics platform developed at LLNL, with the Windows sensor and shared data model as the center of gravity. The wiki exists to preserve architecture decisions, telemetry semantics, and stream-processing knowledge that are easy to lose when moving between C# sensor internals, WintapAPI abstractions, NEsper/Esper rules, and analysis repositories. Wintap-Analytics is treated as the host location and future home for experiment-analysis documentation, Wintappy ("Wintap-PyUtil") is the canonical Python/DBT/DuckDB post-processing pipeline that turns raw `raw_sensor` parquet from Wintap/Lintap into bronze/silver/gold analysis-ready models, and Lintap is documented mainly as supporting infrastructure for dev environments and packaging/deployment workflows.

### Key research/design questions to keep surfaced

- How do Windows sensor internals produce and normalize process, file, and network telemetry into the semantic Wintap data model?
- Where are the boundaries between raw host telemetry, normalized WintapAPI entities, recorded datasets, and downstream analytics artifacts?
- What NEsper/Esper event-stream processing patterns are relied on by Wintap, and what query/window/join pitfalls should future agents avoid?
- Which design choices are driven by research flexibility rather than production endpoint-management hardening?
- How should semantic compatibility be maintained between Wintap and Lintap-derived or Lintap-packaged environments?
- Which Wintap-Analytics experiment-analysis workflows should become first-class wiki topics later, including notebooks, Streamlit apps, ACME4/CALDERA annotations, schemas, and process classification JSON?
- How should Wintappy's DBT bronze/silver/gold pipeline (DuckDB-only output today) reconcile with Wintap-Analytics' and the workshop material's expectations of published `stdview-*` parquet datasets, given parquet export is not yet implemented?

---

## Session Startup

1. Read this file (AGENTS.md).
2. Read `wiki/log.md` (last 10 entries).
3. Read `wiki/index.md`.
4. Ask what to do: ingest a source, answer a question, lint, or explore.

Do not load all wiki pages at startup. Load on demand as operations require.
When referencing files in source repos, read them from their live paths directly.
Summarize and cite; never copy source code into the wiki.
