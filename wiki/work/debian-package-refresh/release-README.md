---
title: "Release README Draft: Lintap Packages"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/packaging/lintap-deb/README.md
  - ../Lintap/packaging/lintap-deb/build-deb.sh
policy: agent-editable
last_validated: 2026-10-05
repo_scope: cross-repo
implementation_area: packaging
event_domain: none
audience: mixed
status: draft
source_paths: wiki/work/debian-package-refresh/release-README.md
tags: [feature-work, lintap-packaging, debian, rpm, release-artifacts]
---

# Lintap Packages

This release provides Lintap Linux sensor packages for RHEL 8 x86_64 and
Debian/Ubuntu amd64 and arm64 systems.

## Release Assets

| Asset | Platform | Package version |
|---|---|---|
| `lintap-0.3.5-12.el8.x86_64.rpm` | RHEL 8 x86_64 | `0.3.5-12.el8` |
| `lintap_0.1.0-14_amd64.deb` | Debian/Ubuntu amd64 | `0.1.0-14` |
| `lintap_0.1.0-14_arm64.deb` | Debian/Ubuntu arm64 | `0.1.0-14` |

These assets use different package-version schemes and release revisions: the RPM is 0.3.5-12.el8, while the Debian packages are 0.1.0-14. They are based on the same core source.

## RPM Installation

Supported target: RHEL 8 x86_64 or a compatible EL8 system.

```sh
sudo dnf install ./lintap-0.3.5-12.el8.x86_64.rpm
sudo systemctl start lintap.service
sudo systemctl status lintap.service --no-pager
```

## Debian Installation

Install the asset matching the host architecture:

```sh
dpkg --print-architecture
```

Install on amd64:

```sh
sudo apt install ./lintap_0.1.0-14_amd64.deb
```

Install on arm64:

```sh
sudo apt install ./lintap_0.1.0-14_arm64.deb
```

Start and inspect the sensor:

```sh
sudo systemctl start lintap.service
systemctl status lintap.service --no-pager
sudo journalctl -u lintap.service -n 100 --no-pager
```

## Runtime Layout

Both package families use the following operational locations:

```text
/etc/lintap/lintap.env          Service configuration, high-level parameters
/usr/lib/lintap/ETLConfig.json  Detailed sensor feature configuration parameters
/usr/lib/lintap/                Published sensor application
/usr/lib/lintap/tracers/        eBPF tracer objects
/usr/lib/lintap/mcp/            Optional MCP helper, when packaged
/var/log/lintap/                Logs, Parquet, and runtime data
```

The package enables the systemd services during installation but does not
start the sensor automatically. Review `/etc/lintap/lintap.env` before
starting it.

## Configuration

The default data root is:

```text
WINTAP_DATA_ROOT=/var/log/lintap
```

The field-parity Linux sensor settings disable MCP and DuckDB UI at runtime,
enable ETL and the Linux sensor manager, enable the exec, exit, network,
FileOps, and process-rundown sensors, and keep CloneSensor opt-in.

The Debian package keeps Snappy Parquet compression. This is an intentional
Debian/Ubuntu divergence from the RHEL 8 RPM packaging, which uses the field
RHEL compatibility configuration.

To enable S3 uploads, edit the `ETLConfig.json` file.

## Upgrade and Removal

Upgrade in place with the newer package for the same packaging family. The
maintainer scripts are intended to leave an already-enabled and running
sensor enabled and running across upgrades.

Remove the package while preserving configuration and collected data:

```sh
sudo apt remove lintap
# or, on RPM systems:
sudo dnf remove lintap
```

On Debian/Ubuntu, purge removes `/etc/lintap` but preserves `/var/log/lintap`
data. Remove collected data separately only when it is no longer needed.

## Checksums

The verified checksums for the current assets are:

```text
c26c48290997a4120a18b227913722b22d288386b8abafd23c02df915325e961  lintap_0.1.0-14_arm64.deb
ea2f2659736a1f81d97ee2780315d8033ae4dcdeb7ae835f0c0bc382da8eaa2f  lintap_0.1.0-14_amd64.deb
f38209e490cb98e391216b70ed3229810c3b5e48511cac44fee7f6e54f154505  lintap-0.3.5-12.el8.x86_64.rpm
```

If these assets are accompanied by a `SHA256SUMS` file, verify each download
with:

```sh
sha256sum -c SHA256SUMS
```

The checksum file should contain the three lines above.

## Support Scope

These are research-oriented Lintap sensor packages, not Debian-policy-clean or
RPM certification artifacts. Test the package and service behavior on the
target distribution and kernel before field deployment.
