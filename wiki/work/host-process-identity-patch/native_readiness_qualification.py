"""Isolated native qualification, never install/start/stop a collector.

Run on lintap-dev against its read-only mounted live Wintap source. A new native
snapshot avoids shared-mount NEsper codegen and preserves previous failed evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


FILTER = '|'.join('FullyQualifiedName~' + name for name in (
    'AttributionTraceTests', 'AttributionRetryQueueTests', 'CollectorProcessTelemetryTests',
    'SensorShutdownOrderTests', 'LinuxLifecycleEvidenceTests', 'IdentityContractTests',
    'ProcessResolverTests', 'NetworkEndpointNormalizationTests', 'NetworkSerializerContractTests',
    'BoundedEventTimeCacheTests', 'TcpStartupProjectionTests', 'EtlStartupReadinessTests',
    'TcpShutdownBoundaryTests', 'EtlShutdownBarrierTests'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    # DuckDB's transitive native assets are copied for several platforms. A
    # successful source copy is not a sufficient space check for the test build.
    if shutil.disk_usage(args.evidence.parent).free < 3 * 1024**3:
        raise RuntimeError('At least 3 GiB free native disk required before qualification')
    args.evidence.mkdir(parents=True, exist_ok=False)
    snapshot = args.evidence / 'source'
    snapshot.mkdir()
    ignore = shutil.ignore_patterns('bin', 'obj', '.git', 'node_modules', '.venv',
        'dist', '.fuse_hidden*', 'wintapstate.json')
    for name in ('wintap', 'shared', 'tests', 'platform'):
        shutil.copytree(args.source / name, snapshot / name, ignore=ignore)
    for path in args.source.iterdir():
        if path.is_file() and (path.suffix in ('.props', '.targets', '.json') or
                              path.name.lower() == 'nuget.config') and path.name != 'wintapstate.json':
            shutil.copyfile(path, snapshot / path.name)
    hashes = {str(p.relative_to(snapshot)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in snapshot.rglob('*') if p.is_file()}
    (args.evidence / 'source-hashes.json').write_text(json.dumps(hashes, indent=2))
    records = []
    commands = [
        ['dotnet', 'test', 'tests/Wintap.Tests/Wintap.Tests.csproj', '-c', 'Release',
         '-p:EnableWindowsTargeting=true', '-p:RestoreLockedMode=true', '--filter', FILTER,
         '--blame-hang-timeout', '45s', '--logger', 'trx', '--results-directory',
         str(args.evidence / 'test-results')],
        ['dotnet', 'build', 'wintap/Lintap.csproj', '-c', 'Release',
         '-p:RestoreLockedMode=true', '-p:EnableMcpServer=false']]
    for index, command in enumerate(commands):
        log = args.evidence / f'qualification-{index}.log'
        with log.open('w') as output:
            try:
                result = subprocess.run(command, cwd=snapshot, stdout=output,
                                        stderr=subprocess.STDOUT, timeout=600)
                code = result.returncode
            except subprocess.TimeoutExpired:
                code = 'timeout'
        records.append(dict(command=command, cwd=str(snapshot), exit_code=code, log=str(log)))
        print(json.dumps(records[-1]), flush=True)
        (args.evidence / 'commands.json').write_text(json.dumps(records, indent=2))
        if code != 0:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
