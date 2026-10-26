"""Isolated shutdown-window A/B; never modifies the installed service.

Forks continue across SIGTERM. Conservation is NOT expected after collection
ends; instead audit identity/lifecycle for the file events actually captured.
"""
import argparse
import ctypes
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import time


def children_across_shutdown(root, collector):
    root.mkdir()
    children = []
    start = time.monotonic()
    start_unix_ns = time.time_ns()
    stop_sent = None
    while time.monotonic() - start < 3:
        if stop_sent is None and time.monotonic() - start >= .25:
            stop_sent = time.time_ns()
            collector.send_signal(signal.SIGTERM)
        pid = os.fork()
        if pid == 0:
            try:
                ctypes.CDLL(None).prctl(15, b'qa_shutdown', 0, 0, 0)
                begin = time.monotonic_ns()
                ticks = int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19])
                directory = root / 'payload' / str(os.getpid())
                directory.mkdir(parents=True)
                first = time.monotonic_ns()
                for index in range(2):
                    path = directory / f'file-{index}.txt'
                    path.write_bytes(b'shutdown-evidence')
                    path.read_bytes()
                end = time.monotonic_ns()
                (root / f'child-{os.getpid()}.json').write_text(json.dumps(dict(
                    pid=os.getpid(), parent=os.getppid(), cohort='shutdown', start_ticks=ticks,
                    clock_ticks=os.sysconf('SC_CLK_TCK'), payload_files=2,
                    callback_begin_monotonic_ns=begin, first_file_monotonic_ns=first,
                    before_exit_monotonic_ns=end, executable=str(Path('/proc/self/exe').resolve()))))
                os._exit(0)
            except BaseException:
                os._exit(1)
        children.append(pid)
        time.sleep(.01)
    records = []
    for pid in children:
        _, status = os.waitpid(pid, 0)
        if status:
            raise RuntimeError('Shutdown stimulus child failed')
        record = json.loads((root / f'child-{pid}.json').read_text())
        record.update(wait_status=status, reap_monotonic_ns=time.monotonic_ns())
        records.append(record)
    manifest = dict(children=records, expected_children=len(records),
                    expected_payload_files=len(records) * 2, sigterm_unix_ns=stop_sent,
                    start_unix_ns=start_unix_ns, end_unix_ns=time.time_ns())
    (root / 'workload.json').write_text(json.dumps(manifest, indent=2))
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--qa-root', type=Path, required=True)
    p.add_argument('--data-root', type=Path, required=True)
    p.add_argument('--baseline-bin', type=Path, required=True)
    p.add_argument('--ordered-bin', type=Path, required=True)
    args = p.parse_args()
    args.qa_root.mkdir(parents=True, exist_ok=False)
    if args.data_root.exists():
        raise RuntimeError('Refusing prior data root')
    if os.geteuid() != 0:
        raise RuntimeError('Root required for eBPF')
    boot = int(next(l.split()[1] for l in Path('/proc/stat').read_text().splitlines() if l.startswith('btime ')))
    (args.qa_root / 'host-provenance.json').write_text(json.dumps(dict(
        boot_unix_seconds=boot, hostname=platform.node(), kernel=platform.release(),
        arch=platform.machine(), os_release=Path('/etc/os-release').read_text()), indent=2))
    session = dict(rounds=[], installed_service_before=subprocess.check_output(
        ['systemctl','show','lintap','-p','MainPID','-p','NRestarts'],text=True))
    for index in range(3):
        for kind, source in [('baseline', args.baseline_bin), ('ordered', args.ordered_bin)]:
            name = f'fixed-shutdown-{kind}-{index}'
            qa = args.qa_root / name
            qa.mkdir()
            binary = qa / 'bin'
            shutil.copytree(source, binary)
            runtime = qa / 'runtime-snapshot'
            env = os.environ.copy()
            env.update(WINTAP_DATA_ROOT=str(args.data_root/name), WINTAP_RUNTIME_ROOT=str(runtime),
                       WINTAP_DISABLE_MCP='true', WINTAP_DISABLE_DUCKDB_UI='true',
                       WINTAP_ENABLE_CLONE_SENSOR='true', WINTAP_ENABLE_EXECVE_SENSOR='true',
                       WINTAP_ENABLE_EXIT_SENSOR='true', WINTAP_ENABLE_FILEOPS_SENSOR='true',
                       WINTAP_ENABLE_NETWORK_SENSOR='true', WINTAP_ENABLE_PROCESS_RUNDOWN_SENSOR='true',
                       WINTAP_ENABLE_SELINUX_SENSOR='false',
                       WINTAP_ETL_SERIALIZATION_INTERVAL_SEC='10', WINTAP_ETL_UPLOAD_INTERVAL_SEC='15',
                       WINTAP_EXPERIMENT_DRAIN_BATCH_WINDOWS='true')
            result = dict(name=name, missing_birth_injection=False, runtime_root=str(runtime),
                          binary_sha256=hashlib.sha256((binary/'Lintap.dll').read_bytes()).hexdigest(),
                          lifecycle_object_sha256={str(p.relative_to(binary)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for pattern in ('clone*.bpf.o', 'execve*.bpf.o', 'exit*.bpf.o')
                              for p in binary.rglob(pattern)},
                          env_overrides={k:v for k,v in env.items() if k.startswith('WINTAP_')})
            with (qa/'collector.log').open('x') as out:
                collector = subprocess.Popen([str(binary/'Lintap')],cwd=binary,env=env,stdout=out,stderr=subprocess.STDOUT)
                try:
                    time.sleep(20)
                    if collector.poll() is not None:
                        raise RuntimeError('Collector exited before stimulus')
                    effective = dict(part.split('=', 1) for part in Path(f'/proc/{collector.pid}/environ').read_text().split('\0') if '=' in part)
                    result['verified_process_environment'] = {k: effective.get(k) for k in result['env_overrides']}
                    if any(effective.get(k) != v for k, v in result['env_overrides'].items()):
                        raise RuntimeError('Effective collector environment differs from intended settings')
                    if not runtime.is_dir():
                        raise RuntimeError('Isolated runtime root not created')
                    result['workload'] = children_across_shutdown(qa/'workload',collector)
                    collector.wait(timeout=120)
                except Exception as exc:
                    result['error'] = str(exc)
                    if collector.poll() is None:
                        result['forced_termination'] = True
                        collector.kill()
                        collector.wait()
                result['collector_exit_code'] = collector.returncode
            session['rounds'].append(result)
            (args.qa_root/'session.json').write_text(json.dumps(session,indent=2))
            print(json.dumps({k:v for k,v in result.items() if k not in ('workload','env_overrides')}),flush=True)
            if result.get('error') or result.get('forced_termination') or result['collector_exit_code'] != 0:
                raise SystemExit(1)
    session['installed_service_after'] = subprocess.check_output(
        ['systemctl','show','lintap','-p','MainPID','-p','NRestarts'],text=True)
    (args.qa_root/'session.json').write_text(json.dumps(session,indent=2))


if __name__ == '__main__':
    main()
