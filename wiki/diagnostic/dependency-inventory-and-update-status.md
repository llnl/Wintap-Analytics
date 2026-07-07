---
title: "Dependency Inventory and Update Status"
type: diagnostic
confidence: medium
grounded_by:
  - ../Wintap-Analytics/requirements.txt
  - ../Wintap-Analytics/Pipfile
  - ../Wintap-Analytics/2025-acme4-explore/pyproject.toml
  - ../Wintap-Analytics/2025-dmbd/requirements.txt
  - ../wintap/wintap/Wintap.Common.props
  - ../wintap/wintap/Wintap.csproj
  - ../wintap/wintap/Lintap.csproj
  - ../wintap/shared/Wintap-Workbench/package.json
  - ../wintap/shared/ai/wintap_mcp_server/wintap_mcp_server.csproj
  - ../wintap/devtools/requirements.txt
  - ../Lintap/pyproject.toml
policy: agent-editable
last_validated: 2026-06-29
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: none
audience: developer
status: draft
source_paths: ../Wintap-Analytics/requirements.txt; ../Wintap-Analytics/2025-acme4-explore/pyproject.toml; ../Wintap-Analytics/2025-dmbd/requirements.txt; ../wintap/wintap/Wintap.Common.props; ../wintap/shared/Wintap-Workbench/package.json; ../Lintap/pyproject.toml
tags: [wintap, Wintap-Analytics, Lintap, dependencies, update-status, dev-environment]
---

# Dependency Inventory and Update Status

This page records dependency manifests across the Wintap ecosystem and the update status observed on 2026-06-29. It is a diagnostic snapshot, not an upgrade plan.

## Method And Caveats

`npm outdated --all --json --long` was run in `../wintap/shared/Wintap-Workbench` and reported direct runtime dependency update status. `npm` did not report the package's `devDependencies` in this environment, so those are listed from the manifest but have no live update status here.
<!-- GROUND_TRUTH: ../wintap/shared/Wintap-Workbench/package.json §dependencies -->

`uv` is not installed in this environment, so `uv lock --upgrade --dry-run` could not be used for `../Wintap-Analytics/2025-acme4-explore` or `../Lintap`. Python update status below was produced by reading the manifests and querying PyPI JSON for the latest published version. For `>=` constraints, `current` means the lower bound, not a resolved lock version.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-acme4-explore/pyproject.toml §project.dependencies -->
<!-- GROUND_TRUTH: ../Lintap/pyproject.toml §project.dependencies -->

`dotnet` is not installed in this environment, so `dotnet list package --outdated --no-restore` could not run. .NET update status below was produced by reading `PackageReference` entries and querying the NuGet flat-container API. Treat .NET rows as registry availability, not a validated compatible restore.
<!-- GROUND_TRUTH: ../wintap/wintap/Wintap.Common.props §PackageReference -->

## Manifest Inventory

| Repo | Manifest | Ecosystem | Role |
|------|----------|-----------|------|
| Wintap-Analytics | `../Wintap-Analytics/requirements.txt` | Python/pip | Pinned baseline analytics stack. |
| Wintap-Analytics | `../Wintap-Analytics/Pipfile` | Python/pipenv | Broad unpinned analytics/dev package declaration. |
| Wintap-Analytics | `../Wintap-Analytics/2025-acme4-explore/pyproject.toml` | Python/uv | ACME4 notebook/research environment. |
| Wintap-Analytics | `../Wintap-Analytics/2025-dmbd/requirements.txt` | Python/pip | Dynamic Malware Behavioral Dataset notebook support. |
| wintap | `../wintap/wintap/Wintap.Common.props` | .NET/NuGet | Shared Wintap package references used by platform builds. |
| wintap | `../wintap/wintap/Wintap.csproj` | .NET/NuGet | Windows-specific Wintap package references. |
| wintap | `../wintap/wintap/Lintap.csproj` | .NET/NuGet | Linux-specific Wintap/Lintap package references. |
| wintap | `../wintap/shared/Wintap-Workbench/package.json` | npm | Angular Workbench frontend dependencies. |
| wintap | `../wintap/shared/ai/wintap_mcp_server/wintap_mcp_server.csproj` | .NET/NuGet | MCP server dependencies. |
| wintap | `../wintap/devtools/requirements.txt` | Python/pip | Developer analysis/smoke-test support dependencies. |
| Lintap | `../Lintap/pyproject.toml` | Python/uv | Lintap support/visualization dependencies. |

## Update Summary

| Area | Direct deps checked | Updates available | Current/no update | Not fully checked |
|------|---------------------|-------------------|-------------------|-------------------|
| Wintap-Analytics pinned `requirements.txt` | 59 | 50 | 9 | none |
| Wintap-Analytics `2025-dmbd/requirements.txt` | 6 | 5 | 1 | none |
| Wintap-Analytics ACME4 `pyproject.toml` | 23 | 17 | 6 lower bounds already at latest | lock resolution not checked because `uv` is unavailable |
| Lintap `pyproject.toml` | 5 | 5 | 0 | lock resolution not checked because `uv` is unavailable |
| wintap devtools `requirements.txt` | 4 | unknown | unknown | range-only requirements; no resolved lock version checked |
| Wintap Workbench npm runtime deps | 35 | 23 | 11 | one GitHub dependency not version-checked; npm devDependency update status not reported by `npm outdated` in this environment |
| Wintap .NET PackageReference entries | 89 package references across checked manifests | many | some | `dotnet` unavailable; NuGet registry lookup only |

## Python: Pinned Analytics Requirements

The pinned analytics stack in `../Wintap-Analytics/requirements.txt` is mostly behind current PyPI latest versions. Important analysis packages with updates include `duckdb`, `duckdb-engine`, `ipykernel`, `ipython`, `matplotlib`, `networkx`, `numpy`, `pandas`, `pillow`, `scipy`, and `sqlalchemy`.
<!-- GROUND_TRUTH: ../Wintap-Analytics/requirements.txt §requirements -->

| Dependency | Manifest version | Latest observed | Status |
|------------|------------------|-----------------|--------|
| duckdb | 0.10.1 | 1.5.4 | update available |
| duckdb-engine | 0.11.3 | 0.17.0 | update available |
| ipykernel | 6.29.4 | 7.3.0 | update available |
| ipython | 8.23.0 | 9.15.0 | update available |
| matplotlib | 3.8.4 | 3.11.0 | update available |
| networkx | 3.3 | 3.6.1 | update available |
| numpy | 1.26.4 | 2.5.0 | update available |
| pandas | 2.2.1 | 3.0.3 | update available |
| pillow | 10.3.0 | 12.2.0 | update available |
| scipy | 1.13.0 | 1.18.0 | update available |
| sqlalchemy | 2.0.29 | 2.0.51 | update available |
| appnope | 0.1.4 | 0.1.4 | current |
| cycler | 0.12.1 | 0.12.1 | current |
| ipycytoscape | 1.3.3 | 1.3.3 | current |
| nest-asyncio | 1.6.0 | 1.6.0 | current |
| pexpect | 4.9.0 | 4.9.0 | current |
| ptyprocess | 0.7.0 | 0.7.0 | current |
| python-dateutil | 2.9.0.post0 | 2.9.0.post0 | current |
| spectate | 1.0.1 | 1.0.1 | current |
| stack-data | 0.6.3 | 0.6.3 | current |

Other pinned `requirements.txt` packages with observed updates available: `asttokens`, `black`, `click`, `comm`, `contourpy`, `debugpy`, `decorator`, `executing`, `fonttools`, `ipywidgets`, `isort`, `jedi`, `jinja2`, `jupyter-client`, `jupyter-core`, `jupyterlab-widgets`, `kiwisolver`, `magic-duckdb`, `markupsafe`, `matplotlib-inline`, `mypy-extensions`, `packaging`, `parso`, `pathspec`, `platformdirs`, `prompt-toolkit`, `psutil`, `pure-eval`, `pygments`, `pyparsing`, `pytz`, `pyzmq`, `six`, `tornado`, `traitlets`, `typing-extensions`, `tzdata`, `wcwidth`, and `widgetsnbextension`.

## Python: ACME4 Explore

The ACME4 project uses lower-bound dependency ranges in `pyproject.toml`, not pinned exact versions. The observed latest versions show many newer releases, but compatibility must be tested through the ACME4 notebooks and DuckDB view construction workflow before raising lower bounds.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-acme4-explore/pyproject.toml §project.dependencies -->

| Dependency | Lower bound | Latest observed | Status |
|------------|-------------|-----------------|--------|
| bs4 | 0.0.2 | 0.0.2 | lower bound at latest |
| datamapplot | 0.6.4 | 0.7.3 | update available |
| duckdb | 1.3.2 | 1.5.4 | update available |
| fast-hdbscan | 0.2.2 | 0.3.2 | update available |
| flake8 | 7.3.0 | 7.3.0 | lower bound at latest |
| ipykernel | 6.30.1 | 7.3.0 | update available |
| ipywidgets | 8.1.7 | 8.1.8 | update available |
| jupysql | 0.11.1 | 0.11.1 | lower bound at latest |
| jupyterlab | 4.4.7 | 4.6.1 | update available |
| marimo | 0.15.2 | 0.23.11 | update available |
| mypy | 1.17.1 | 2.1.0 | update available |
| numpy | 2.2.6 | 2.5.0 | update available |
| pandas | 2.3.2 | 3.0.3 | update available |
| pytest | 8.4.2 | 9.1.1 | update available |
| python-dotenv | 1.1.1 | 1.2.2 | update available |
| python-lsp-server | 1.13.1 | 1.14.0 | update available |
| quak | 0.3.2 | 0.3.5 | update available |
| scikit-learn | 1.7.1 | 1.9.0 | update available |
| sentencepiece | 0.2.1 | 0.2.1 | lower bound at latest |
| toml | 0.10.2 | 0.10.2 | lower bound at latest |
| umap-learn | 0.5.9.post2 | 0.5.12 | update available |
| vectorizers | 0.2.2 | 0.2.2 | lower bound at latest |
| zstandard | 0.24.0 | 0.25.0 | update available |

## Python: DMBd, Lintap, And Devtools

`../Wintap-Analytics/2025-dmbd/requirements.txt` has updates available for `bokeh`, `ipykernel`, `pipdeptree`, `setuptools`, and `wheel`; `scikit-plot` was current at the observed latest.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-dmbd/requirements.txt §requirements -->

`../Lintap/pyproject.toml` lower bounds all have newer observed PyPI releases: `duckdb` 1.5.2 to 1.5.4, `marimo` 0.13.0 to 0.23.11, `pandas` 2.3.0 to 3.0.3, `plotly` 6.7.0 to 6.8.0, and `streamlit` 1.57.0 to 1.58.0.
<!-- GROUND_TRUTH: ../Lintap/pyproject.toml §project.dependencies -->

`../wintap/devtools/requirements.txt` uses range-only requirements for `sentence-transformers`, `scikit-learn`, `numpy`, and `torch`, so no resolved update status is available from the manifest alone.
<!-- GROUND_TRUTH: ../wintap/devtools/requirements.txt §requirements -->

## npm: Wintap Workbench

The Workbench is anchored to Angular 15-era packages. `npm outdated` reports newer major versions for Angular packages, PrimeNG, CodeMirror, Chart.js, jQuery, Marked, Quill, RxJS, tar, and zone.js.
<!-- GROUND_TRUTH: ../wintap/shared/Wintap-Workbench/package.json §dependencies -->

| Dependency | Wanted | Latest observed | Status |
|------------|--------|-----------------|--------|
| @angular/animations | 15.2.10 | 20.1.8 | update available |
| @angular/cdk | 15.2.9 | 22.0.2 | update available |
| @angular/common | 15.2.10 | 21.2.17 | update available |
| @angular/compiler | 15.2.10 | 21.2.17 | update available |
| @angular/core | 15.2.10 | 21.2.17 | update available |
| @angular/forms | 15.2.10 | 21.2.17 | update available |
| @angular/platform-browser | 15.2.10 | 21.2.17 | update available |
| @angular/platform-browser-dynamic | 15.2.10 | 20.0.7 | update available |
| @angular/router | 15.2.10 | 21.2.17 | update available |
| @ctrl/ngx-codemirror | 6.1.0 | 7.0.0 | update available |
| @fortawesome/fontawesome-free | 6.7.2 | 7.3.0 | update available |
| @microsoft/signalr | 8.0.17 | 10.0.0 | update available |
| chart.js | 3.9.1 | 4.5.1 | update available |
| codemirror | 5.65.21 | 6.0.2 | update available |
| jquery | 3.7.1 | 4.0.0 | update available |
| marked | 15.0.12 | 18.0.5 | update available |
| primeflex | 3.3.1 | 4.0.0 | update available |
| primeicons | 6.0.1 | 7.0.0 | update available |
| primeng | 15.4.1 | 21.1.9 | update available |
| quill | 1.3.7 | 2.0.3 | update available |
| rxjs | 7.5.7 | 7.8.2 | update available |
| tar | 6.2.1 | 7.5.19 | update available |
| zone.js | 0.11.8 | 0.16.2 | update available |

Current Workbench runtime dependencies observed by `npm outdated`: `@types/d3`, `@types/dompurify`, `@types/marked`, `@types/prismjs`, `d3`, `dompurify`, `prismjs`, `signalr`, `tslib`, `typelib`, and `web-animations-js`.

Dev dependencies declared in the manifest but not given update status by the available `npm outdated` result include Angular build tooling, Angular ESLint packages, `@types/node`, `@typescript-eslint/parser`, `eslint`, Jasmine/Karma packages, CSS/style loaders, and TypeScript.
<!-- GROUND_TRUTH: ../wintap/shared/Wintap-Workbench/package.json §devDependencies -->

## .NET: Wintap NuGet Packages

The core Wintap .NET manifests target .NET 8 in shared props and platform projects, with WintapRecorder still targeting `net6.0-windows`.
<!-- GROUND_TRUTH: ../wintap/wintap/Wintap.Common.props §TargetFramework -->
<!-- GROUND_TRUTH: ../wintap/platform/windows/WintapRecorder/WintapRecorder.csproj §TargetFramework -->

High-signal NuGet updates observed from registry lookup include these groups:

| Package family | Current examples | Latest observed | Status |
|----------------|------------------|-----------------|--------|
| DuckDB.NET.Data.Full | 1.3.2 | 1.5.3 | update available |
| NEsper.Compiler / Runtime / Compat | 8.9.0 | 8.9.1 | update available |
| Microsoft.AspNetCore.* packages | 8.0.4 | 10.0.9 stable / 11 preview | update available |
| Microsoft.Extensions.* packages | 8.0.0, 9.0.3, previews | 10.0.9 stable / 11 preview | update available |
| Microsoft.SemanticKernel core/connectors | 1.51.0-preview to 1.65.0-alpha | 1.77.0 family | update available for most |
| ModelContextProtocol | 0.2.0-preview.3 | 1.4.0 stable / 2.0 preview | update available |
| Parquet.Net | 4.24.0 | 6.0.3 stable | update available |
| Microsoft.Diagnostics.Tracing.TraceEvent | 3.1.23 | 3.2.4 | update available |
| TaskScheduler | 2.11.1 in Wintap, 2.12.2 in WintapCoreSvcMgr | 2.12.2 | update available for Wintap project only |
| Newtonsoft.Json | 13.0.3 | 13.0.4 stable | update available |
| BouncyCastle.Cryptography | 2.4.0 common, 2.7.0-beta.98 service manager | 2.6.2 stable / 2.7.0 beta | common stable update available; service manager already on beta |

NuGet packages observed as current in at least one checked manifest include `Castle.Windsor`, `Common.Logging`, `Common.Logging.Core`, `Crc32.NET`, `Microsoft.AspNet.WebApi.Client`, `Microsoft.AspNet.WebApi.OwinSelfHost`, `Microsoft.DotNet.PlatformAbstractions`, `Microsoft.NETCore.Portable.Compatibility`, `Microsoft.SemanticKernel.Connectors.Sqlite`, `Microsoft.CSharp`, `System.Data.DataSetExtensions`, `System.Security.AccessControl`, `System.ServiceModel.Duplex`, `System.ServiceModel.Security`, `XLR8.CGLib`, and `TaskScheduler` where already at `2.12.2`.

## Update Risk Notes

Angular, PrimeNG, CodeMirror, Chart.js, jQuery, Quill, and RxJS updates are mostly major-version jumps. Treat the Workbench as a coordinated frontend migration, not a set of independent patch bumps.

Many Wintap .NET packages are tied to the .NET runtime major version. Moving Microsoft.Extensions or Microsoft.AspNetCore packages from 8/9 to 10/11 should be evaluated against the target framework and deployment platform before updating.

NEsper updates are small by version number, but Esper/NEsper behavior is central to streaming semantics; validate with [[wiki/diagnostic/nesper-repro]] and the ETL EPL pages before accepting updates.

Python analytics updates include major scientific stack changes such as NumPy 1.x to 2.x and pandas 2.x to 3.x in older pinned manifests. Validate notebooks and DuckDB table/view behavior before refreshing pins.
