---
title: "Cross-platform package release versioning"
type: workflow
confidence: medium
grounded_by:
  - ../Lintap/packaging/README.md
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../wintap/Directory.Build.props
  - ../wintap/.github/workflows/release.yml
  - ../wintap/installer/Wintap.Installer.wixproj
policy: agent-editable
last_validated: 2026-10-27
repo_scope: cross-repo
implementation_area: packaging
event_domain: none
audience: developer
status: draft
source_paths: ../Lintap/packaging; ../wintap/.github/workflows/release.yml; ../wintap/installer
tags: [release, versioning, Debian, RPM, MSI, packaging]
---

# Cross-platform package release versioning

Use **Wintap 7.0** as the product release line; keep package identities stable
(`Wintap` MSI, `lintap` Debian/RPM). The `7` is a product major version, not a
package name. This page records the current beta-round convention and a concise
release checklist; it does not imply that release automation is implemented.

## Shared release identity

Use one source release tag and build number across formats and architectures:
`v7.0.<N>[-alpha.<n>|-beta.<n>|-rc.<n>]`. Local/dev builds are not published as
releases. Final production/GA releases have no `prod` suffix. Keep architecture
in package metadata and filenames, not in the shared release number.

Wintap's current release configuration uses low build numbers for alpha, the
90s for RC, `100` for GA, and `101+` for later GA updates; MSI needs the numeric
build to increase for upgrades. The current beta round uses `7.0.1`; agree and
record the beta counter/promotion sequence before automating it. Do not assign
different upstream build numbers just because artifacts have different formats
or architectures.
<!-- GROUND_TRUTH: ../wintap/Directory.Build.props §VERSIONING; ../wintap/.github/workflows/release.yml §Version from tag; ../wintap/installer/Wintap.Installer.wixproj §VERSIONING -->

## Format-specific encoding

The formats encode the same release identity differently:

| Artifact | Beta example | Final example | Notes |
| --- | --- | --- | --- |
| Debian | `lintap_7.0.1~beta.1-1_amd64.deb` | `lintap_7.0.100-1_amd64.deb` | `~` is the Debian prerelease marker and sorts before the final version. `-1` is the Debian packaging revision. |
| RPM | `lintap-7.0.1_beta.1-1.el8.x86_64.rpm` | `lintap-7.0.100-1.el8.x86_64.rpm` | Current beta-round choice uses `_beta.1`. `el8`/`el9` identifies the target OS major, not a build counter. `Release`'s leading number is the RPM packaging revision. |
| Windows MSI | `Wintap-7.0.1-beta1-x64.msi` | `Wintap-7.0.100-release-x64.msi` | MSI `ProductVersion` remains numeric (`7.0.<N>`); channel is carried in the filename/metadata. |

For Debian, use `VERSION~beta.N` with `--revision 1`; increment the Debian
revision only when repackaging the same upstream version. For RPM, keep the
`el8`/`el9` target suffix distinct from the packaging revision. The chosen RPM
underscore spelling is not the Debian convention; verify RPM version ordering
on the target EL toolchain, especially beta-to-GA, before relying on it for
upgrade selection. Wintap's increasing numeric GA build (`100`) is intended to
keep GA above earlier prerelease builds.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/build-deb.sh §--version/--revision; ../Lintap/packaging/lintap-rpm/build-rpm.sh §--version/--release -->

## Release checklist

1. Select the release tag/build number once; record the Wintap and Lintap source
   commits. Build every supported architecture from that same source identity.
2. Use the format-specific commands and host requirements in
   `../Lintap/packaging/README.md`; RHEL 8 preparation is in
   [[wiki/workflow/rhel8-rpm-build-prerequisites]]. Do not infer target-kernel
   CO-RE validity from a cross-built Debian package.
3. Inspect package metadata, architecture, dependencies, service scripts and
   payload; record artifact SHA-256, SDK/runtime versions, source commits and
   build logs. Keep packaging revision distinct from the shared build number.
4. Install/upgrade and smoke-test on designated targets using the packaging
   guide. A successful package build alone is not installation or runtime
   acceptance. Publish the release notes, artifacts and checksums together.

Standards references: [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)
for prerelease labels; [Debian Policy, package version](https://www.debian.org/doc/debian-policy/ch-controlfields.html#version)
for Debian comparison and revision syntax. See Wintap's live release workflow
(`../wintap/.github/workflows/release.yml`) and WiX project for the current MSI
tag/channel mapping. The canonical Linux build, inspect and install guide is
`../Lintap/packaging/README.md`.
