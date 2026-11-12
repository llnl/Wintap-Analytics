---
title: "Lintap RHEL 8 SELinux Policy: S3 Upload and Cache Cleanup"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../Lintap/packaging/lintap-rpm/lintap.service
  - ../Lintap/packaging/lintap-rpm/README.md
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: packaging
event_domain: none
audience: developer
status: draft
source_paths: ../Lintap/packaging/lintap-rpm; ../wintap/wintap/core/etl/load
tags: [lintap, rhel8, selinux, s3, auditd, packaging]
---

# Lintap RHEL 8 SELinux Policy: S3 Upload and Cache Cleanup

## Incident and implemented rules

Operator-reported RHEL 8 investigation: the same Lintap RPM and `ETLConfig.json`
worked on one host but S3 uploads failed on another. On the failing host, SELinux
was enforcing; a bounded permissive test allowed uploads. The captured AVCs
identified these denials (both were recorded with `permissive=1`):

| Policy rule / label | Lintap behavior that needs it |
|---|---|
| `allow init_t lintap_s3_port_t:tcp_socket name_connect;` and TCP port 3900 labeled `lintap_s3_port_t` | S3 `PutObject` to the configured Garage endpoint. The adapter creates the S3 client and uploads through `PutObjectAsync`. <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs §PreUpload; §Upload --> |
| `allow init_t var_log_t:dir rmdir;` | Remove empty `raw_sensor` partition directories after uploaded/pruned files are deleted; the observed denied target was an `hourPK=` directory. <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §tryDeleteUploadedFile; §cleanupEmptyPartitionDirectories; §deletePrunedRawSensorFile --> |

The checked-in RPM unit runs `/usr/lib/lintap/Lintap` as root; the observed
process SELinux domain was `init_t`. The package’s durable telemetry tree is
`/var/log/lintap/data/raw_sensor/` by default. <!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/lintap.service; ../Lintap/packaging/lintap-rpm/README.md -->

The host-local module also contains earlier grants for `init_t` to write
`lib_t` files, get its process session, and create/unlink temporary `tmp_t`
FIFOs and socket files. Their originating AVCs/features were not established in
this incident. The policy source and compiled `.pp` were operator-managed under
`~/lintap-rpm/`; their integration into the checked-in Lintap RPM is not
established.

**Scope caution:** the TCP permission is limited to the custom port type, but
SELinux port labels are host-wide (not destination-host-specific), and the
source domain `init_t` is shared. The `var_log_t:dir rmdir` grant applies to
`init_t` across all directories with that type. A dedicated Lintap domain and
data-directory type would be tighter; do not broaden the network grant to all
`unreserved_port_t` ports as a shortcut.

## Detecting future denials

1. Check enforcement and audit collection before reproducing:

   ```bash
   getenforce
   systemctl is-active auditd
   auditctl -s
   ```

   If auditd is inactive, start it for the diagnostic (`service auditd start`);
   enabling it at boot is a separate host-policy decision.
2. Reproduce one failed upload under **Enforcing**, then query the executable
   rather than `comm` (the .NET worker thread name can be `.NET TP Worker`):

   ```bash
   ausearch -x /usr/lib/lintap/Lintap -m AVC,USER_AVC -ts recent -i
   ```

   Use `-ts today` or a specific date if the event is older than ten minutes.
   The audit email/sendmail warning is separate from the query result.
3. Match each AVC to its operation: `name_connect` plus `dest=3900` is the
   Garage connection; `rmdir` on `var_log_t` is empty-partition cleanup. Only
   add permissions supported by the observed AVCs. `permissive=1` means the
   denial was logged but allowed during permissive testing.
4. If a bounded permissive test is necessary, start auditd first, capture the
   AVCs, and promptly restore `setenforce 1`. Do not leave the host permissive.

## Build and deploy the local policy

Keep the existing rules in `lintap-selinux.te`; increment its module version.
For the custom port type, require `attribute port_type;` and declare
`type lintap_s3_port_t, port_type;` **outside** the `require` block. The
`require` block must also include every referenced class/permission (including
`class process getsession;` for the existing `getsession` rule).

Build and install the module from its source directory:

```bash
checkmodule -M -m -o lintap-selinux.mod lintap-selinux.te
semodule_package -o lintap-selinux.pp -m lintap-selinux.mod
semodule -i lintap-selinux.pp
```

After installing the module, map TCP 3900 to its declared type. Inspect local
port overrides first; use `-a` if none exists, or `-m` to change an existing
local mapping:

```bash
semanage port -l -C | grep -w 3900
semanage port -a -t lintap_s3_port_t -p tcp 3900
# If a local mapping already exists, use instead:
# semanage port -m -t lintap_s3_port_t -p tcp 3900
```

Verify the module and mapping, keep SELinux enforcing, and wait for a fresh
upload attempt:

```bash
semodule -l | grep lintap-selinux
semanage port -l | grep lintap_s3_port_t
getenforce
```

The policy is installed separately from the Lintap application RPM; no
application RPM rebuild is required for a local policy update. The current
host-local `.te`/`.pp` workflow is not yet documented as part of the canonical
RPM packaging or fleet deployment process.

## Related

- [[wiki/component/sensor-upload-cache-pipeline]] — upload sweep, retry, and
  delete-after-upload behavior.
- [[wiki/workflow/rhel8-rpm-build-prerequisites]] — canonical RHEL 8 application
  RPM build prerequisites (separate from this local SELinux module).
