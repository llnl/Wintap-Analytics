"""Fresh native build/test snapshot on lintap-dev; never overwrites prior evidence."""
import json
import argparse
import os
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', default='')
    args = parser.parse_args()
    root = Path('/home/ubuntu/quality-package-20261024-collector-telemetry' + args.attempt)
    root.mkdir()
    shutil.copytree('/home/ubuntu/git/wintap', root / 'wintap',
                    ignore=shutil.ignore_patterns('.git', 'bin', 'obj', '.fuse_hidden*'))
    shutil.copytree('/home/ubuntu/git/Lintap/packaging', root / 'packaging')
    for name in ('pidstat-collector.py', 'pidstat-collector-launch.sh', 'pidstat-collector-bootstrap.sh'):
        shutil.copy2(Path('/home/ubuntu/git/Lintap') / name, root / name)
    filters = '|'.join('FullyQualifiedName~' + name for name in [
        'CollectorProcessTelemetryTests', 'EventChannelHealthWireInTests',
        'SensorShutdownOrderTests', 'AttributionRetryQueueTests',
        'LinuxLifecycleEvidenceTests', 'IdentityContractTests', 'ProcessResolverTests',
        'NetworkEndpointNormalizationTests', 'BoundedEventTimeCacheTests'])
    commands = [
        ('focused-tests.log', ['dotnet', 'test', 'tests/Wintap.Tests/Wintap.Tests.csproj',
                              '-c', 'Release', '-p:EnableWindowsTargeting=true',
                              '--filter', filters, '--blame-hang-timeout', '45s']),
        ('build.log', ['bash', str(root / 'packaging/lintap-deb/build-deb.sh'),
                       '--version', '0.1.0~quality20261024', '--revision', '7',
                       '--skip-mcp', '--project-dir', str(root / 'wintap/wintap'),
                       '--work-root', str(root / 'build')]),
    ]
    results = []
    for name, command in commands:
        env = os.environ.copy()
        env.update(WINTAP_RUNTIME_ROOT=str(root / 'test-runtime'),
                   WINTAP_DATA_ROOT=str(root / 'test-data'),
                   LINTAP_OUTPUT_DIR=str(root / 'artifacts'))
        with (root / name).open('x') as log:
            run = subprocess.run(command, cwd=root / 'wintap', env=env,
                                 stdout=log, stderr=subprocess.STDOUT)
        results.append(dict(log=str(root / name), command=command, exit_code=run.returncode))
        (root / 'commands.json').write_text(json.dumps(results, indent=2))
        print(json.dumps(results[-1]), flush=True)
        if run.returncode:
            raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
