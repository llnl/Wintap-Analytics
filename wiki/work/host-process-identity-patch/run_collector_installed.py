"""Approved disposable-host revision7 install and normal/restart regression suite."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    host = platform.node()
    if host not in ('axon-target', 'caldera-host'):
        raise RuntimeError('Only the two explicitly approved disposable hosts')
    state = subprocess.check_output(['systemctl', 'show', 'lintap', '--value', '-p', 'ActiveState'], text=True).strip()
    if state != 'inactive':
        raise RuntimeError('Expected previously stopped collector; refusing active-service install')
    if hashlib.sha256(args.package.read_bytes()).hexdigest() != args.sha256:
        raise RuntimeError('Package checksum mismatch')
    bundle = 'quality-installed-20261024-r7-collector'
    install_root = Path('/home/ubuntu') / (bundle + '-install')
    install_root.mkdir()
    dropin = Path('/etc/systemd/system/lintap.service.d/quality-test.conf')
    (install_root / 'previous-quality-test.conf').write_bytes(dropin.read_bytes())
    command = ['dpkg', '-i', str(args.package)]
    with (install_root / 'install.log').open('x') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    receipt = dict(package=str(args.package), package_sha256=args.sha256,
                   dll_sha256=hashlib.sha256(Path('/usr/lib/lintap/Lintap.dll').read_bytes()).hexdigest(),
                   version=subprocess.check_output(['dpkg-query', '-W', 'lintap'], text=True),
                   command=command)
    (install_root / 'receipt.json').write_text(json.dumps(receipt, indent=2))
    harness = Path(__file__).with_name('package_host_rounds.py')
    sys.path.insert(0, '/home/ubuntu/git/LLNL/wintap/devtools')
    command = [sys.executable, str(harness), '--qa-root', '/home/ubuntu/' + bundle,
               '--data-root', '/var/log/lintap/data/' + bundle + '/' + host,
               '--runtime-root', '/home/ubuntu/quality-installed-20261024-r2/native-runtime',
               '--replace-test-dropin', '--experiment-exit-recovery']
    with (install_root / 'harness.log').open('x') as log:
        # Child uses these developer helpers via PYTHONPATH; no parallel collector.
        import os
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/ubuntu/git/LLNL/wintap/devtools'
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    print(json.dumps(dict(host=host, exit_code=result.returncode, receipt=receipt)), flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
