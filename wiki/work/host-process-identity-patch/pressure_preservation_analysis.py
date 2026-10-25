"""Read-only stopped-host/package/state/history/archive preservation audit."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time

from shutdown_delivery_experiment import HERE, TEMP, REPO


def audit(revisions):
    baseline = json.loads((HERE / 'package_r17_final_state.json').read_text())
    code = '''from pathlib import Path
import hashlib,json,subprocess,shutil
state=subprocess.check_output(['systemctl','show','lintap','-p','ActiveState','-p','MainPID','-p','NRestarts','-p','Result'],text=True)
dll=Path('/usr/lib/lintap/Lintap.dll')
agent=Path('/home/ubuntu/quality-installed-20261024-r2/native-runtime/wintapstate.json')
collectors=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit(): continue
 try:
  cmd=(p/'cmdline').read_bytes().replace(b'\\0',b' ')
  if (b'Lintap.dll' in cmd or b'/Lintap' in cmd) and b'python' not in cmd: collectors.append(int(p.name))
 except (FileNotFoundError,PermissionError,ProcessLookupError): pass
print(json.dumps(dict(service=state,installed_dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),
 agent_state=json.loads(agent.read_text()) if agent.exists() else None,
 agent_state_sha256=hashlib.sha256(agent.read_bytes()).hexdigest() if agent.exists() else None,
 collector_pids=collectors,native_free_bytes=shutil.disk_usage('/home/ubuntu').free)))
'''
    def host_state(host):
        result = json.loads(subprocess.check_output(['multipass','exec',host,'--','sudo','python3','-'],input=code,text=True))
        before = baseline['hosts'][host]
        result['preservation_gates'] = {key:result[key]==before[key] for key in (
            'service','installed_dll_sha256','agent_state_sha256','agent_state','collector_pids')}
        return host,result
    with ThreadPoolExecutor(max_workers=3) as pool:
        hosts=dict(pool.map(host_state,baseline['hosts']))
    path=Path(baseline['historical_db']['path']); stat=path.stat()
    history=dict(path=str(path),size=stat.st_size,mtime_ns=stat.st_mtime_ns,
        unchanged=stat.st_size==baseline['historical_db']['size'] and stat.st_mtime_ns==baseline['historical_db']['mtime_ns'])
    sources=json.loads((TEMP/'r16-shutdown-evidence/native-qualification/source-hashes.json').read_text())
    source_matches={name:hashlib.sha256((REPO/name).read_bytes()).hexdigest()==digest
        for name,digest in sources.items() if Path(name).suffix in ('.cs','.epl','.props','.csproj')}
    archives=[]
    for revision in revisions:
        for receipt in json.loads((TEMP/f'r{revision}-shutdown-evidence/archive-receipts.json').read_text()):
            file=Path(receipt['local_archive'])
            archives.append(dict(revision=revision,**receipt,sha256_matches=hashlib.sha256(file.read_bytes()).hexdigest()==receipt['sha256']))
    result=dict(checked_unix_ns=time.time_ns(),hosts=hosts,historical_db=history,
        tested_live_source_matches=source_matches,archives=archives,
        all_preservation_gates_passed=history['unchanged'] and all(source_matches.values()) and
        all(all(h['preservation_gates'].values()) for h in hosts.values()) and all(a['sha256_matches'] for a in archives))
    (HERE/'pressure_final_state.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(all_preservation_gates_passed=result['all_preservation_gates_passed'],
        tested_source_files=len(source_matches),verified_archives=len(archives))))
    if not result['all_preservation_gates_passed']:
        raise RuntimeError('Preservation audit failed; inspect evidence,do not reset controls')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revisions',nargs='+',type=int,required=True)
    audit(parser.parse_args().revisions)
