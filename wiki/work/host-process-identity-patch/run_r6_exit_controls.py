"""Native lintap-dev isolated revision-6 controls; preserves every failed run.

Run with sudo python3 via the mounted repo path. No installed-service changes.
"""
import json
import os
from pathlib import Path
import subprocess


def main():
    base = Path('/home/ubuntu/quality-isolated-20261024-r6-exit-recovery')
    base.mkdir()  # Refuse overwrite of evidence.
    script = '/home/ubuntu/quality-package-20261024-exit-recovery/wintap/devtools/attribution_experiment.py'
    binary = '/home/ubuntu/quality-package-20261024-exit-recovery/build/publish/linux-arm64'
    env = os.environ.copy()
    env['WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY'] = '1024'
    results = []
    for name, rounds, recovery in [
        ('off-missing', 'fixed-missing-birth', False),
        ('on-missing', 'fixed-missing-birth', True),
        ('on-normal', 'fixed-normal', True),
        ('on-legacy', 'fixed-legacy-exit', True),
    ]:
        command = ['python3', script, '--qa-root', str(base / name),
                   '--data-root', '/home/ubuntu/data/lintap/quality-isolated-20261024-r6-exit-recovery/' + name,
                   '--fixed-bin', binary, '--rounds', rounds, '--candidate-self-contained',
                   '--stop-signal', 'SIGTERM', '--shutdown-timeout', '120',
                   '--settle-seconds', '30', '--experiment-batch-drain']
        if recovery:
            command.append('--experiment-exit-recovery')
        with (base / (name + '-harness.log')).open('w') as log:
            run = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        results.append(dict(name=name, exit_code=run.returncode, command=command))
        (base / 'controls.json').write_text(json.dumps(results, indent=2))
        print(json.dumps(results[-1]), flush=True)


if __name__ == '__main__':
    main()
