"""Private qualification/captures for the approved exact shutdown-delivery gate.

Never installs, starts a service, deletes evidence, or writes live sensor sources.
Uses CALDERA's private SDK10.0.402 and archived revision11 native/runtime artifacts.
Each revision requires fresh paths. Sensor code changes are qualified separately.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3] / 'wintap'
TEMP = Path('/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode')
SDK = '/home/ubuntu/quality-r12-private-sdk-20261024/dotnet-10.0.402'
HOSTS = ('axon-target', 'caldera-host')
BASELINE = 'ad2c9dbb538ae60472bb5300be2c752f461c246650a31cd3d77787e2c9a0ed32'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exec_host(host, *command, **kwargs):
    return subprocess.run(['multipass', 'exec', host, '--', *command], check=True, **kwargs)


def transfer(source, host, destination):
    subprocess.run(['multipass', 'transfer', str(source), host + ':' + destination], check=True)


def save(path, data):
    path.write_text(json.dumps(data, indent=2))


def qualification(root, revision):
    root.mkdir(exist_ok=False)
    archive = root / 'source.tar.gz'
    excluded = {'bin', 'obj', '.git', 'node_modules', '.venv', 'dist', 'wintapstate.json'}
    manifest = {}
    with tarfile.open(archive, 'w:gz') as tar:
        paths = [p for name in ('wintap', 'shared', 'tests', 'platform') for p in (REPO / name).rglob('*')]
        paths += [p for p in REPO.iterdir() if p.is_file() and
                  (p.suffix in ('.props', '.targets', '.json') or p.name.lower() == 'nuget.config')]
        for path in paths:
            rel = path.relative_to(REPO)
            if path.is_file() and not excluded.intersection(rel.parts) and not any(
                    part.startswith('.fuse_hidden') for part in rel.parts):
                tar.add(path, arcname=str(rel), recursive=False)
                manifest[str(rel)] = sha(path)
    save(root / 'source-hashes.json', manifest)
    save(root / 'source-archive.json', dict(sha256=sha(archive), bytes=archive.stat().st_size))
    remote = f'/home/ubuntu/quality-r{revision}-staging-20261024'
    exec_host('caldera-host', 'mkdir', remote)
    transfer(archive, 'caldera-host', remote + '/source.tar.gz')
    result = subprocess.check_output(['multipass', 'exec', 'caldera-host', '--', 'sha256sum',
                                      remote + '/source.tar.gz'], text=True)
    if result.split()[0] != sha(archive):
        raise RuntimeError('Source archive transfer hash differs')
    exec_host('caldera-host', 'mkdir', remote + '/live-source')
    exec_host('caldera-host', 'tar', '-xzf', remote + '/source.tar.gz', '-C', remote + '/live-source')
    transfer(HERE / 'native_readiness_qualification.py', 'caldera-host', remote + '/qualify.py')
    cmd = ['multipass', 'exec', 'caldera-host', '--', 'env', 'PATH=' + SDK +
           ':/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'DOTNET_ROOT=' + SDK,
           'python3', remote + '/qualify.py', '--source', remote + '/live-source', '--evidence',
           f'/home/ubuntu/quality-r{revision}-readiness-20261024']
    with (root / 'qualification-driver.log').open('w') as output:
        result = subprocess.run(cmd, stdout=output, stderr=subprocess.STDOUT, timeout=900)
    save(root / 'qualification-command.json', dict(command=cmd, exit_code=result.returncode))
    print((root / 'qualification-driver.log').read_text(), flush=True)
    if result.returncode:
        raise RuntimeError('Native qualification failed; preserve evidence and do not capture')


def package(root, revision):
    if json.loads((root / 'qualification-command.json').read_text())['exit_code']:
        raise RuntimeError('Successful qualification required')
    remote = f'/home/ubuntu/quality-r{revision}-staging-20261024'
    transfer(HERE / 'repackage_managed_diagnostic.py', 'caldera-host', remote + '/repackage.py')
    cmd = ['multipass', 'exec', 'caldera-host', '--', 'python3', remote + '/repackage.py',
           '--baseline', '/home/ubuntu/quality-r12-staging-20261024/baseline-r11.deb',
           '--baseline-sha256', BASELINE, '--managed',
           f'/home/ubuntu/quality-r{revision}-readiness-20261024/source/wintap/bin/Release/net10.0',
           '--evidence', f'/home/ubuntu/quality-r{revision}-managed-package-20261024',
           '--version', f'0.1.0~quality20261024-{revision}']
    with (root / 'package.log').open('w') as output:
        result = subprocess.run(cmd, stdout=output, stderr=subprocess.STDOUT, timeout=180)
    save(root / 'package-command.json', dict(command=cmd, exit_code=result.returncode))
    if result.returncode:
        raise RuntimeError('Private repackaging failed')
    for name in ('package-receipt.json', f'lintap_0.1.0~quality20261024-{revision}_arm64.deb'):
        subprocess.run(['multipass', 'transfer',
                        f'caldera-host:/home/ubuntu/quality-r{revision}-managed-package-20261024/' + name,
                        str(root / name)], check=True)
    receipt = json.loads((root / 'package-receipt.json').read_text())
    if receipt['package_sha256'] != sha(root / Path(receipt['package']).name):
        raise RuntimeError('Managed package transfer hash differs')
    print((root / 'package.log').read_text(), flush=True)


def capture(root, revision, shutdown, stimulus_margin=0, pressure_children=None, pressure_phase='interior'):
    receipt = json.loads((root / 'package-receipt.json').read_text())
    package_path = root / Path(receipt['package']).name
    if sha(package_path) != receipt['package_sha256']:
        raise RuntimeError('Local package hash differs')
    tools = [HERE / 'diagnostic_delivery_rounds.py', HERE / 'package_host_rounds.py'] + [
        REPO / 'devtools' / name for name in ('attribution_experiment.py',
                                             'network_endpoint_smoke_test.py', 'smoke_manifest.py')]
    if pressure_children:
        tools.append(HERE / 'pressure_workload.py')
    remote = f'/home/ubuntu/quality-r{revision}-delivery-tools-20261024'
    qa = f'/home/ubuntu/quality-r{revision}-delivery-controls-20261024'
    data = f'/var/log/lintap/data/quality-r{revision}-delivery-controls-20261024'

    def run(host):
        exec_host(host, 'mkdir', remote)
        for path in [package_path] + tools:
            transfer(path, host, remote + '/' + path.name)
        expected = receipt['package_sha256']
        hashes = subprocess.check_output(['multipass', 'exec', host, '--', 'sha256sum',
                                         remote + '/' + package_path.name], text=True)
        if hashes.split()[0] != expected:
            raise RuntimeError('Host package hash differs')
        cmd = ['multipass', 'exec', host, '--', 'sudo', 'python3', remote + '/diagnostic_delivery_rounds.py',
               '--package', remote + '/' + package_path.name, '--package-sha256', expected,
               '--qa-root', qa, '--data-root', data, '--agent-state',
               '/home/ubuntu/quality-installed-20261024-r2/native-runtime/wintapstate.json',
               '--order', 'off,on' if host == 'axon-target' else 'on,off', '--etl-readiness', 'required']
        if shutdown != 'legacy':
            cmd += ['--etl-shutdown', shutdown]
        if stimulus_margin:
            cmd += ['--stimulus-margin-seconds', str(stimulus_margin)]
        if pressure_children:
            cmd += ['--pressure-children', str(pressure_children), '--pressure-phase', pressure_phase]
        log = root / (host + '-controls.log')
        with log.open('w') as output:
            result = subprocess.run(cmd, stdout=output, stderr=subprocess.STDOUT, timeout=600)
        record = dict(host=host, command=cmd, exit_code=result.returncode, log=str(log), qa=qa,
                      data=data + '/' + host, tool_hashes={p.name: sha(p) for p in tools})
        save(root / (host + '-capture-command.json'), record)
        print(json.dumps(record), flush=True)
        return record

    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(run, HOSTS))
    save(root / 'capture-commands.json', records)
    if not all(r['exit_code'] == 0 for r in records):
        raise RuntimeError('Capture failed; preserve and analyze as failure')


def archive(root, revision):
    qa = f'quality-r{revision}-delivery-controls-20261024'

    def run(host):
        dest = root / host
        dest.mkdir(exist_ok=False)
        records = []
        for kind, parent, member in [('qa', '/home/ubuntu', qa),
                                     ('data', '/var/log/lintap/data', qa + '/' + host)]:
            remote = '/home/ubuntu/' + qa + '-' + host + '-' + kind + '.tar.gz'
            exec_host(host, 'sudo', 'tar', '-czf', remote, '-C', parent, member)
            expected = subprocess.check_output(['multipass', 'exec', host, '--', 'sha256sum', remote], text=True).split()[0]
            local = dest / (kind + '.tar.gz')
            subprocess.run(['multipass', 'transfer', host + ':' + remote, str(local)], check=True)
            if sha(local) != expected:
                raise RuntimeError('Evidence archive transfer hash differs')
            extracted = dest / kind
            extracted.mkdir()
            with tarfile.open(local) as tar:
                tar.extractall(extracted, filter='data')
            records.append(dict(host=host, kind=kind, native_archive=remote,
                                local_archive=str(local), sha256=expected, bytes=local.stat().st_size))
        return records

    with ThreadPoolExecutor(max_workers=2) as pool:
        records = sum(list(pool.map(run, HOSTS)), [])
    save(root / 'archive-receipts.json', records)
    analysis = root / 'analysis'
    analysis.mkdir(exist_ok=False)
    for host in HOSTS:
        dest = analysis / host
        dest.mkdir()
        (dest / 'qa').symlink_to(root / host / 'qa' / qa, target_is_directory=True)
        (dest / 'data').symlink_to(root / host / 'data' / qa / host, target_is_directory=True)
    print(json.dumps(records), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('qualification', 'package', 'capture', 'archive'))
    parser.add_argument('--revision', type=int, required=True)
    parser.add_argument('--shutdown', choices=('legacy', 'required'), default='legacy')
    parser.add_argument('--stimulus-margin-seconds', type=int, default=0)
    parser.add_argument('--pressure-children', type=int, choices=[32, 128, 256])
    parser.add_argument('--pressure-phase', choices=['interior', 'shutdown-tail'], default='interior')
    args = parser.parse_args()
    if args.revision < 14:
        parser.error('Only fresh continuation revisions14+ allowed')
    root = TEMP / f'r{args.revision}-shutdown-evidence'
    if args.action == 'capture':
        capture(root, args.revision, args.shutdown, args.stimulus_margin_seconds,
                args.pressure_children, args.pressure_phase)
    else:
        globals()[args.action](root, args.revision)


if __name__ == '__main__':
    main()
