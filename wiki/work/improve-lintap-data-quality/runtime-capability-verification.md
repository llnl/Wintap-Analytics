---
title: "Runtime capability receipt verification"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/tests/Wintap.Tests/RuntimeCapabilitiesTests.cs
  - ../wintap/devtools/validate_runtime_capabilities.py
  - ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap/devtools; ../wintap/tests/Wintap.Tests
tags: [runtime-capabilities, host, parquet, verification]
---

# Runtime capability receipt verification

User-authorized follow-up on current feature branches. Contract:
[[wiki/schema/runtime-capability-receipt]]. No package/default/DBT changes.

## Commands and results

- macOS `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter 'FullyQualifiedName~RuntimeCapabilities|FullyQualifiedName~ProcessResolver|FullyQualifiedName~SerializerSchedule' --no-restore -v quiet`: **126 passed**, no failures/skips (10 new receipt cases including HOST parquet round-trip, status, immutable completion/restart, object hash/history and invalid-env provenance).
- Initial macOS `dotnet build wintap/Lintap.csproj --no-restore -v quiet` blocked by absent cached AWSSDK.S3; Linux-native build used instead. Intermediate syntax errors in newly added provenance helper were fixed before final tests.
- Ubuntu VM `lintap-clone-validation`, arm64, kernel `6.8.0-147-generic`, libbpf 1.3: native `dotnet build Lintap.csproj --no-restore -v quiet` passes, zero errors. Native source copy/build is `/home/ubuntu/clone-validation/source/wintap`; final build log `runtime-receipt-build-final.log`.
- `sudo /home/ubuntu/clone-validation/venv/bin/python /home/ubuntu/wintap/devtools/validate_runtime_capabilities.py --dll /home/ubuntu/clone-validation/source/wintap/bin/Debug/net8.0/Lintap.dll --fallback-dll /home/ubuntu/clone-validation/receipt-fallback-final-app/Lintap.dll --output /home/ubuntu/clone-validation/receipt-final`: **passes**.
  Separate copied app payload omits six CO-RE objects; installed/source objects preserved.
- `sudo /home/ubuntu/clone-validation/venv/bin/python /home/ubuntu/wintap/devtools/validate_clone_pipeline.py --dll /home/ubuntu/clone-validation/source/wintap/bin/Debug/net8.0/Lintap.dll --workload /home/ubuntu/clone-validation/workload --output /home/ubuntu/clone-validation/pipeline-receipt-final2`: **passes** all 80 births, excludes 60 threads, 20 fork+exec identities each retain three Start observations; no clone3 skips.
- First concurrent clone-regression attempt (`pipeline-receipt-final`) failed before startup with Kestrel address-in-use while receipt harness ran. Sequential rerun above passed; not sensor loss. Harnesses should run sequentially.
- `git diff --check`: passes. All changes remain uncommitted; pre-existing user state/artifacts preserved.

## What the durable run established

Every tested startup published valid version-1 JSON into `raw_sensor/raw_host`
while ETL was disabled; JSON exactly equals its final startup log. Same-root
restart has a distinct run ID and retains prior published HOST. Global disable
records all seven sensors disabled. CO-RE run records Clone/Exec/Exit/Network
running, FileOps partial (arm64 legacy open/unlink hooks absent), ProcessRundown
disabled, SELinux failed due to absent SELinux filesystem. Fallback run records
Clone/FileOps/Network partial, Exec/Exit running, and clone3 flags hook attached;
selected tiers/hashes/attempt history are durable. This status is attach evidence,
not equivalent-data certification.

Shared-object ERR_PTR handling now applies to every instrumented Linux primary
and auxiliary attach path. Failed links are neither retained nor destroyed.
Null native returns store unknown errno rather than inventing a permission code.

Remaining gates: fresh Debian/RPM acceptance, RHEL/Fedora, live Windows/macOS
startup acceptance, normal ETL long-capture delivery, mixed-version HOST merge
integration, DBT retention/temporal joins, namespaces and ongoing health/change
updates. Receipt test directly validates published HOST, not downstream models.
