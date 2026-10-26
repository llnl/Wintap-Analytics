---
title: "RHEL 9 RPM validation: corrected telemetry bundle"
type: workflow
confidence: medium
grounded_by:
  - ../Lintap/packaging/README.md
  - ../wintap/devtools/verify_rpm_payload.py
  - validation/telemetry-soak/run-smoke-soak.sh
  - validation/telemetry-soak/validate-round.py
  - streamlit/projects/SmokeTests/analysis.py
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: packaging
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Lintap/packaging; ../wintap/devtools; validation/telemetry-soak
tags: [rhel9, rpm, qualification, telemetry-quality]
---

# Later RHEL 9 deployment validation

Prepared for the user's later native RHEL 9 x86_64 RPM deployment. Ubuntu arm64
tests qualify the source slice, not this platform/package. Packaging is owned by
Lintap, producer/helper code by Wintap, validators/wiki by Analytics. No Wintappy
change is included. Use the canonical live packaging guide for the native build,
package review and operator-directed install/start; run the commands below **after**
that installation and normal startup. They perform no service control or tracing.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §RHEL 9 prerequisites and operator-assisted qualification -->

## 1. Native build record

Retain outside Git: Wintap/packaging commits, reviewed source-diff status, exact
SDK **10.0.402**, native architecture/kernel/BTF, complete managed/eBPF build logs,
RPM SHA-256, dependency listing, and staged payload hashes. Rebuild all tracer
objects and managed assemblies from the same source snapshot. Preserve DuckDB
engine **1.5.6** and official .NET wrapper **1.5.6.1**. SDK build provenance comes
from this record, not from a running app's runtime version or a receipt marker.
Do not use Ubuntu arm64 objects/helper in the x86_64 RPM. Compile the optional
clone helper on the approved target-architecture build host and record its hash.

## 2. Verify installed payload

Set `WINTAP`, `ANALYTICS`, `PYTHON`, `RPM`, and `RPM_SHA256` to reviewed paths/hash.
`PYTHON` must be a prepared environment with DuckDB1.5.6 and the dashboard's imports
(including boto3); it is not an instruction to change the host's system Python.
Use an owned private evidence directory outside Git; no config/credentials are copied.

```bash
umask 077
mkdir -p "$EVIDENCE"
"$PYTHON" "$WINTAP/devtools/verify_rpm_payload.py" \
  --rpm "$RPM" --rpm-sha256 "$RPM_SHA256" > "$EVIDENCE/package-proof.json"
```

Proceed only with exit0 and `passed: true`. This compares the RPM to its independently
reviewed digest, installed package version, and every regular non-config payload file
against the RPM's SHA256 digests; it emits managed/core tracer hashes. It does not read
config contents, install anything, or prove which payload a running process loaded.
Wrong/missing files fail closed. Retain normal startup/service evidence separately.
<!-- GROUND_TRUTH: ../wintap/devtools/verify_rpm_payload.py -->

## 3. Run one independent round

After normal startup completes, use the already configured data root and uploader.
The evidence subtree must be writable by the generator user. Ground-truth JSON stays
under `EVIDENCE`; exported evidence parquet is the only generator data placed in the
raw smoke partition. No polling of local telemetry for stimulus success.

```bash
bash "$ANALYTICS/validation/telemetry-soak/run-smoke-soak.sh" \
  --python "$PYTHON" --devtools "$WINTAP/devtools" \
  --data-root "$DATA_ROOT" --evidence-root "$EVIDENCE/canary" \
  --rounds 1 --clone-helper "$CLONE_HELPER"
```

Inspect each `status.tsv` row and delivered manifest revision, not merely the runner
shell exit. Missing native helper remains an explicit skip if the option is omitted.
Never compile/attach the dev-time network observer on this field host. Recurring
generation remains a later operator decision, preferably in its own tmux session.

## 4. Validate delivered evidence and normal telemetry

Wait for normal upload/flush; listings are not delivery watermarks. In SmokeTests,
select the explicit round and run all validations against Garage. Check current
fingerprint, HOST context, exact paths/endpoints, and all missing/contradictory checks.
For a mounted/exported dataset (including complete preceding HOST history), this
command runs the same evaluator plus focused object/projection gates and saves only
a fingerprinted summary under sibling `analysis/smoke-tests/v1/`:

```bash
NETWORK_SHA256=$("$PYTHON" -c 'import json,sys; p=json.load(open(sys.argv[1])); assert p["passed"]; print(p["payload_sha256"]["network_ops_tracer.bpf.o"])' "$EVIDENCE/package-proof.json")
FILE_SHA256=$("$PYTHON" -c 'import json,sys; p=json.load(open(sys.argv[1])); assert p["passed"]; print(p["payload_sha256"]["file_ops_tracer.bpf.o"])' "$EVIDENCE/package-proof.json")
"$PYTHON" "$ANALYTICS/validation/telemetry-soak/validate-round.py" \
  --data-root "$DELIVERED_DATA_ROOT" --list
"$PYTHON" "$ANALYTICS/validation/telemetry-soak/validate-round.py" \
  --data-root "$DELIVERED_DATA_ROOT" --round-key "$ROUND_KEY" \
  --network-sha256 "$NETWORK_SHA256" --file-sha256 "$FILE_SHA256"
```

Select the exact listed key; multiple rounds are never combined by proximity.
The CLI requires both independently supplied hashes; passing current disk hashes
without reviewed package provenance is only local-build qualification. Receipt hashes
link the loaded object to the artifact, while startup remains temporal context rather
than continuous health or exact event ownership. Checks include network contract2/
return hooks, core file open/unlink hooks, case-only sensor keys and explicit normal
process provenance with the three recognized source values. A FileOps partial status
remains visible even if the required subset attaches; assess other failed hooks.

Exit codes: **0** all declared scoped checks observed, **1** contradiction/harness
failure, **2** incomplete/unavailable evidence. No exit code certifies full capture,
loss/count conservation or historical repair. Skips/warnings/missing tuples remain
incomplete. The Ubuntu pilot's two partial TCP provenance checks currently yield2;
do not waive them to obtain0 on RHEL. Review any known limitation explicitly when
deciding whether to proceed with a limited pilot.
<!-- GROUND_TRUTH: validation/telemetry-soak/validate-round.py; streamlit/projects/SmokeTests/queries.py -->

Repeat the identical command to check `reused: true` without another telemetry
validation scan. New delivered objects/code/settings invalidate reuse; explicitly
validate the new snapshot. `--force` deliberately rescans. Dashboard and CLI use
different validation settings/fingerprints, so their saved results are distinct.
Budgets:10000 input files,100000 selected rows,256MB DuckDB memory/no spill. These are
not network-byte/time limits. Prefer settled/scoped delivery and retain error evidence.

## Acceptance record

Record package/projection/endpoint outcomes separately from generation and upload.
Require exact relative and cwd Delete paths, all case-pair activities and distinct
sensor keys, source classification without deduplicating Starts, no contradictions,
and explicit reasons for missing/skipped checks. Check saved-summary reuse/staleness
under ongoing uploads. At a later operator-directed stop, record actual process exit
and inactivity; a timeout wrapper's124 is not a clean-shutdown proof.

Wintappy's lowercased file_id remains a separate downstream limit. Native clone,
IPv6, rapid pointer reuse, multi-host duration, historical loss, and Windows acceptance
are not inferred from a successful RHEL smoke. See
[[wiki/work/wintap-telemetry-identity-and-data-quality/advisor_review]] and
[[wiki/work/wintap-telemetry-identity-and-data-quality/verification]].
