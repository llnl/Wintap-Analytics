"""One fresh default and shutdown-window rerun; no package installation.

Run as root only on the two approved disposable hosts. Existing revision7 package,
runtime identity and previous captures are protected by receipts and unique paths.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def main():
    host = platform.node()
    if host not in ('axon-target', 'caldera-host') or os.geteuid() != 0:
        raise RuntimeError('Only root on approved disposable hosts')
    before = subprocess.check_output(['systemctl','show','lintap','-p','MainPID',
                                      '-p','ActiveState','-p','NRestarts'],text=True)
    if 'MainPID=0\n' not in before or 'ActiveState=inactive\n' not in before:
        raise RuntimeError('Service must be stopped before starting')
    dll = Path('/usr/lib/lintap/Lintap.dll')
    binary_hash = hashlib.sha256(dll.read_bytes()).hexdigest()
    if binary_hash != '3df2fcdf1cc3a74710d51105ce7f01adcc687244035065e0ec0871bf2c191503':
        raise RuntimeError('Expected previously verified revision7 binary')
    base = 'quality-installed-20261024-r8-edges'
    root = Path('/home/ubuntu') / (base+'-receipts')
    root.mkdir()
    dropin = Path('/etc/systemd/system/lintap.service.d/quality-test.conf')
    (root/'previous-quality-test.conf').write_bytes(dropin.read_bytes())
    state = Path('/home/ubuntu/quality-installed-20261024-r2/native-runtime/wintapstate.json')
    (root/'previous-wintapstate.json').write_bytes(state.read_bytes())
    receipt = dict(host=host,service_before=before,dll_sha256=binary_hash,
                   package=subprocess.check_output(['dpkg-query','-W','lintap'],text=True),commands=[])
    env = os.environ.copy()
    env['PYTHONPATH'] = '/home/ubuntu/git/LLNL/wintap/devtools'
    for mode, extra in [('normal',['--rounds','fixed-package-default']),
                        ('shutdown',['--shutdown-window','--rounds','fixed-package-shutdown-0'])]:
        bundle = base+'-'+mode
        command = [sys.executable,str(Path(__file__).with_name('package_host_rounds.py')),
                   '--qa-root','/home/ubuntu/'+bundle,'--data-root',
                   '/var/log/lintap/data/'+bundle+'/'+host,'--runtime-root',str(state.parent),
                   '--replace-test-dropin','--experiment-exit-recovery']+extra
        with (root/(mode+'.log')).open('x') as output:
            run = subprocess.run(command,env=env,stdout=output,stderr=subprocess.STDOUT)
        receipt['commands'].append(dict(command=command,exit_code=run.returncode))
        receipt['service_after'] = subprocess.check_output(['systemctl','show','lintap',
            '-p','MainPID','-p','NRestarts','-p','ActiveState','-p','Result'],text=True)
        receipt['binary_unchanged'] = hashlib.sha256(dll.read_bytes()).hexdigest() == binary_hash
        receipt['agent_id_unchanged'] = json.loads(state.read_text())['AgentId'] == json.loads(
            (root/'previous-wintapstate.json').read_text())['AgentId']
        (root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt),flush=True)
        if run.returncode:
            raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
