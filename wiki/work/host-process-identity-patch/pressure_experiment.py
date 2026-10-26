"""Fresh same-candidate pressure rounds, stopping escalation on any failed gate."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from shutdown_delivery_experiment import TEMP, HERE, capture, archive


def failed_gates(result):
    failures = []
    if not result.get('historical_db_size_mtime_unchanged'):
        failures.append(dict(stage='historical-database'))
    for host in result['hosts']:
        if not host['installed_controls_unchanged']:
            failures.append(dict(host=host['host'],stage='installed-control'))
        if len(host['rounds']) != 2:
            failures.append(dict(host=host['host'],stage='incomplete-rounds'))
        for round_ in host['rounds']:
            if round_['name'] == 'trace-on' and 'trace' not in round_:
                failures.append(dict(host=host['host'],round=round_['name'],stage='missing-trace'))
            for label, gates in [('raw', round_['gates']), ('trace', round_.get('trace', {}).get('gates', {}))]:
                failed = [name for name, value in gates.items() if not value]
                if failed:
                    failures.append(dict(host=host['host'],round=round_['name'],stage=label,gates=failed))
    return failures


def preflight(root):
    source = json.loads((TEMP / 'r16-shutdown-evidence/native-qualification/source-hashes.json').read_text())
    checks = {name:hashlib.sha256((HERE.parents[3] / 'wintap' / name).read_bytes()).hexdigest() == digest
              for name,digest in source.items() if Path(name).suffix in ('.cs','.epl','.props','.csproj')}
    if not all(checks.values()):
        raise RuntimeError('Live sources changed since candidate qualification')
    hosts = {}
    code = '''from pathlib import Path
import json,subprocess,shutil
state=subprocess.check_output(['systemctl','show','lintap','-p','ActiveState','-p','MainPID','-p','NRestarts','-p','Result'],text=True)
mem=dict(line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())
print(json.dumps(dict(service=state,free_disk=shutil.disk_usage('/home/ubuntu').free,available_memory_kib=int(mem['MemAvailable'].split()[0]))))
'''
    for host in ('axon-target','caldera-host'):
        hosts[host] = json.loads(subprocess.check_output(['multipass','exec',host,'--','python3','-'],input=code,text=True))
    (root / 'preflight.json').write_text(json.dumps(dict(hosts=hosts,tested_source_matches=checks),indent=2))
    for host,values in hosts.items():
        if ('ActiveState=inactive' not in values['service'] or 'MainPID=0' not in values['service'] or
            values['free_disk'] < 3*1024**3 or values['available_memory_kib'] < 2*1024**2):
            raise RuntimeError('Unsafe pressure preflight: ' + host)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, required=True)
    parser.add_argument('--children', type=int, required=True, choices=[32, 128, 256])
    parser.add_argument('--phase', choices=['interior', 'shutdown-tail'], required=True)
    parser.add_argument('--full-dbt', action='store_true')
    args = parser.parse_args()
    if args.revision < 18:
        parser.error('Fresh pressure evidence revisions18+ only')
    src = TEMP / 'r16-shutdown-evidence'
    root = TEMP / f'r{args.revision}-shutdown-evidence'
    root.mkdir(exist_ok=False)
    preflight(root)
    receipt = json.loads((src / 'package-receipt.json').read_text())
    package = Path(receipt['package']).name
    for name in ('package-receipt.json', package):
        shutil.copyfile(src / name, root / name)
    assert hashlib.sha256((root / package).read_bytes()).hexdigest() == receipt['package_sha256']
    (root / 'pressure-spec.json').write_text(json.dumps(dict(children=args.children,
        phase=args.phase,package_sha256=receipt['package_sha256'],retry_capacity=1024,
        source_qualification='package_r16_shutdown_qualification.json'), indent=2))
    capture_error = None
    try:
        capture(root, args.revision, 'required', 21, args.children, args.phase)
    except Exception as error:
        capture_error = str(error)
        (HERE / f'package_r{args.revision}_pressure_summary.json').write_text(json.dumps(dict(
            revision=args.revision,children=args.children,phase=args.phase,accepted=False,
            capture_error=capture_error,absence_claims_qualified=False),indent=2))
    finally:
        archive(root, args.revision)
    if capture_error:
        raise SystemExit('Capture failed; archives preserved; no escalation or absence claims: ' + capture_error)
    output = HERE / f'package_r{args.revision}_pressure_controls.json'
    command = [sys.executable, str(HERE / 'diagnostic_controls_analysis.py'),
               '--root', str(root / 'analysis'), '--output', str(output)]
    with (root / 'analysis.log').open('x') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = json.loads(output.read_text())
    failures = failed_gates(result)
    summary = dict(revision=args.revision, children=args.children,phase=args.phase,
                   output=str(output),failures=failures,accepted=not failures)
    (HERE / f'package_r{args.revision}_pressure_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary), flush=True)
    if failures:
        raise SystemExit('Failed gates: preserve, diagnose; do not escalate')
    if args.full_dbt:
        dbt_verify(root, args.revision, output)


def dbt_verify(root, revision, analysis):
    data = root / 'dbt-data'
    data.mkdir(exist_ok=False)
    for host in ('axon-target','caldera-host'):
        (data / host).symlink_to(root / 'analysis' / host / 'data',target_is_directory=True)
    output = HERE / f'package_r{revision}_pressure_dbt.json'
    command = [sys.executable,str(HERE / 'verify_collector_dbt.py'),'--analysis',str(analysis),
               '--data-parent',str(data),'--work-root',str(root / 'fresh-dbt'),
               '--output',str(output),'--full-build']
    with (root / 'dbt-driver.log').open('x') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    builds = json.loads(output.read_text())
    failed = [dict(host=b['host'],round=b['round'],exit_code=b['dbt_exit_code'],
                   failed_gates=[k for k,v in b['gates'].items() if not v])
              for b in builds if b['dbt_exit_code'] or not b['gates'] or not all(b['gates'].values())]
    if len(builds) != 4 or failed:
        raise RuntimeError('Fresh downstream verification failed; preserve/no escalation: ' + json.dumps(failed))
    print(json.dumps(dict(revision=revision,full_dbt_builds=4,downstream_gates_passed=True)),flush=True)


if __name__ == '__main__':
    main()
