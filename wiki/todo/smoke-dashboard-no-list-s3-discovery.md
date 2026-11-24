---
title: "To-Do: Smoke Dashboard S3 Discovery Without List Permission"
type: diagnostic
confidence: high
grounded_by:
  - streamlit/projects/SmokeTests/s3_source.py
  - streamlit/projects/SmokeTests/main.py
  - streamlit/projects/SmokeTests/queries.py
  - streamlit/projects/SmokeTests/result_store.py
  - ../wintap/devtools/smoke_parquet.py
policy: agent-editable
last_validated: 2026-11-24
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/SmokeTests; ../wintap/devtools
tags: [todo, smoke-tests, s3, least-privilege, object-discovery, catalog]
---

# To-Do: Smoke Dashboard S3 Discovery Without List Permission

**Priority:** P3 — Low.

**State:** Open.

**Disposition:** Intake only. This note records a possible least-privilege
enhancement; it does not authorize implementation, IAM changes, uploader changes,
or new infrastructure. The immediate operational workaround is to run the dashboard
with another approved role.

## Finding

The SmokeTests dashboard does not enumerate AWS buckets, but remote discovery calls
`ListObjectsV2` beneath each configured dataset prefix. That API requires
`s3:ListBucket` on the known bucket even though it does not require
`s3:ListAllMyBuckets`. The intended production role does not have the prefix-list
permission.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/s3_source.py §discover_files/§discover_host_files -->
<!-- SOURCE: Human reported the intended production role lacks list-bucket permission and selected another role as the temporary workaround, conversation 2026-11-24. -->

Direct `GetObject` access cannot resolve an unknown key from a prefix or wildcard.
DuckDB S3 globs therefore do not remove the discovery requirement: either some
bounded listing permission or a separate catalog of exact object keys is needed.
An explicit list of every object in the local dashboard configuration would avoid
listing but would become operationally unwieldy and is not the preferred direction.
<!-- SYNTHESIS: inferred from prefix-based discovery in streamlit/projects/SmokeTests/s3_source.py and exact-file reads in streamlit/projects/SmokeTests/queries.py -->

## Candidate Directions

1. **Predictable fixed-key catalog:** Have an authorized producer publish a small,
   bounded catalog per smoke run or UTC partition at a deterministic key. The
   dashboard would fetch that known object directly, validate it, and read only the
   exact evidence and telemetry keys it names.
2. **Prefix-scoped listing:** If policy later allows it, grant only
   `s3:ListBucket` constrained to the approved dataset prefix. This is distinct from
   permission to enumerate account buckets and requires no new catalog protocol.
3. **External catalog or notification index:** Evaluate Glue/Athena, DynamoDB, or
   S3-event delivery only if those services already fit the deployment environment;
   avoid adding infrastructure solely to bypass one narrowly scoped permission.

The fixed-key catalog is the leading strict-no-list candidate, not an accepted
design. It must cover ordinary telemetry discovery, `raw_smoke_test` evidence,
HOST-history lookup, object identity used by analysis fingerprints, and late or
retried uploads. Saved analysis summaries already use predictable direct keys and
do not by themselves solve raw-object discovery.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/s3_source.py §object_identity/§discover_host_files; streamlit/projects/SmokeTests/result_store.py §location/§read_bytes -->

## Evidence

- `discover_files` first lists event prefixes and then lists each selected UTC
  partition; `discover_host_files` separately lists `raw_host` history.
- The dashboard receives only dataset roots and a date window, not exact object
  names.
- Smoke evidence filenames are deterministic after manifest publication, but the
  dashboard does not know every uploaded telemetry filename or final remote key.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/main.py §main; streamlit/projects/SmokeTests/s3_source.py §dataset_parts/§discover_files; ../wintap/devtools/smoke_parquet.py §publish -->

## Open Questions

- Which component would own catalog publication: the shared uploader, smoke
  workload, or separate indexing process?
- Should catalogs be immutable per run/partition with a predictable pointer, or a
  safely replaced bounded snapshot?
- How would a catalog represent upload-time partition rebinding, retries, late
  objects, deletions, ETags, sizes, and last-modified identity without becoming
  stale?
- Can one catalog support both selected-run evidence and the broader telemetry/HOST
  windows needed by dashboard validation?
- What read/write permissions would the producer and dashboard roles receive, and
  how would catalog tampering, path escape, excessive size, and duplicate entries be
  rejected?

## Likely Next Step

If strict no-list operation becomes a real requirement, promote this item through
the feature workflow. First freeze the target IAM constraints and trace all current
listing sites; then compare a fixed-key catalog protocol with a narrowly
prefix-scoped listing policy before changing code or producer behavior.

## Completion Criteria

- A documented, human-approved discovery contract works without `ListObjectsV2`
  when strict no-list mode is selected.
- The dashboard obtains a bounded set of exact evidence, telemetry, and HOST object
  keys without requiring operators to maintain a large per-object config.
- Synthetic tests prove the no-list path makes no listing calls, rejects untrusted
  or out-of-root catalog entries, fails closed on truncation/staleness, and does not
  expose object names or credential-bearing errors in the UI.
- Target-system verification demonstrates the approved role can load and validate a
  smoke run with direct object-read permissions only.
- Documentation preserves the existing listing mode and clearly distinguishes
  `s3:ListBucket` from account-level bucket enumeration.
