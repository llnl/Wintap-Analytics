#!/usr/bin/env python3
"""Supervise one authorized, isolated VM soak; never manage existing services.

Run as root in lintap-dev after building a frozen Wintap source archive. All
children belong to this invocation. No restarts, uploads, packages or pruning.
"""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import time


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proc_sample(pid):
    base = Path('/proc') / str(pid)
    try:
        stat = (base / 'stat').read_text().rsplit(')', 1)[1].split()
        status = dict(line.split(':', 1) for line in (base / 'status').read_text().splitlines())
        children = set()
        for task in (base / 'task').iterdir():
            try:
                children.update(map(int, (task / 'children').read_text().split()))
            except FileNotFoundError:
                pass
        return {'pid': pid, 'start_ticks': int(stat[19]), 'user_ticks': int(stat[11]),
                'system_ticks': int(stat[12]), 'rss_kib': int(status['VmRSS'].split()[0]),
                'hwm_kib': int(status['VmHWM'].split()[0]), 'threads': int(status['Threads']),
                'children': sorted(children), 'io': (base / 'io').read_text()}
    except (OSError, KeyError, ValueError) as exc:
        return {'pid': pid, 'read_error': str(exc)}


def run(args):
    assert os.geteuid() == 0 and platform.system() == 'Linux'
    assert platform.machine() in ('arm64', 'aarch64')
    root = args.root.resolve()
    assert root.parent == Path('/var/tmp') and root.name.startswith('pidstat-four-hour-')
    assert not (root / 'state.json').exists(), 'Never reuse a soak root'
    os.umask(0o077)
    build = root / 'wintap-source/wintap/bin/Debug/net10.0'
    dll = build / 'Lintap.dll'
    binary = root / 'pidstat-collector'
    assert sha(binary) == '224405f7d4eaf815669f2071b514967287e130002a8ef93834660bfa64f308e4'
    assert dll.is_file()
    config = json.loads((build / 'ETLConfig.json').read_text())
    assert all(not adapter['Enabled'] for adapter in config['Adapters'])
    # Isolated retention only. Preserve the source config and every other setting.
    (root / 'ETLConfig.original.json').write_bytes((build / 'ETLConfig.json').read_bytes())
    config['RawSensorMaxCacheSizeBytes'] = 8 * 1024**3
    write(build / 'ETLConfig.json', config)
    smoke_root = Path('/home/ubuntu/qa') / root.name
    smoke_root.mkdir(parents=True, mode=0o700, exist_ok=False)
    for folder in ('lintap-data', 'lintap-runtime', 'pidstat-data', 'pidstat-spool'):
        (root / folder).mkdir(mode=0o700)
    env = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'HOME': '/root', 'TZ': 'America/Phoenix',
           'DOTNET_ROOT': '/opt/wintap-sdk/10.0.402'}
    lintap_env = dict(env, WINTAP_DATA_ROOT=str(root / 'lintap-data'),
                      WINTAP_RUNTIME_ROOT=str(root / 'lintap-runtime'),
                      WINTAP_CONFIG_PATH=str(build / 'ETLConfig.json'),
                      WINTAP_DISABLE_MCP='true', WINTAP_DISABLE_DUCKDB_UI='true',
                      WINTAP_DISABLE_ETL='false', WINTAP_DISABLE_SENSORS='false',
                      WINTAP_ENABLE_DIRECT_PARQUET='false',
                      ASPNETCORE_URLS='http://127.0.0.1:5088')
    pidstat_env = dict(env, PIDSTAT_PARQUET_ROOT=str(root / 'pidstat-data'),
                       PIDSTAT_SPOOL_DIR=str(root / 'pidstat-spool'))
    runner = root / 'smoke-runner/run-smoke-soak.sh'
    devtools = root / 'wintap-source/devtools'
    helper = root / 'clone_lifecycle_workload'
    assert runner.is_file() and helper.is_file()
    smoke_argv = ['bash', str(runner), '--python', '/home/ubuntu/.venvs/lintap-dev/bin/python',
                  '--devtools', str(devtools), '--data-root', str(root / 'lintap-data'),
                  '--evidence-root', str(smoke_root), '--interval', '900', '--timeout', '120',
                  '--rounds', '0', '--host-ip', '192.168.252.50', '--clone-helper', str(helper)]
    commands = {'lintap': ['/opt/wintap-sdk/10.0.402/dotnet', str(dll)],
                'pidstat': [str(binary), '--collect', '--timezone', 'America/Phoenix'],
                'smoke': smoke_argv}
    state = {'status': 'starting', 'supervisor_pid': os.getpid(), 'created_utc': utc(),
             'duration_sec': args.seconds, 'smoke_root': str(smoke_root), 'commands': commands,
             'lintap_env': lintap_env, 'pidstat_env': pidstat_env,
             'binary_sha256': sha(binary), 'lintap_dll_sha256': sha(dll),
             'tracer_sha256': {p.name: sha(p) for p in sorted((build / 'tracers').glob('*.bpf.o'))},
             'clk_tck': os.sysconf('SC_CLK_TCK'), 'page_size': os.sysconf('SC_PAGE_SIZE'),
             'kernel': platform.release(), 'processes': {}, 'shutdown': {}}
    write(root / 'state.json', state)
    stopped = []
    def stop(signum, frame):
        stopped.append(signal.Signals(signum).name)
    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, stop)
    processes, logs = {}, []
    def launch(name, environment):
        log = (root / (name + '.log')).open('wb', buffering=0)
        logs.append(log)
        process = subprocess.Popen(commands[name], cwd=build if name == 'lintap' else root,
                                   env=environment, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        processes[name] = process
        state['processes'][name] = {'pid': process.pid, 'started_utc': utc()}
        write(root / 'state.json', state)
        return process
    failure = None
    started = None
    try:
        lintap = launch('lintap', lintap_env)
        deadline = time.monotonic() + 150
        required = ['ExecveProcess', 'CloneProcess', 'ExitProcess', 'Network',
                    'FileOps', 'ProcessRundown']
        while time.monotonic() < deadline:
            if stopped or lintap.poll() is not None:
                raise RuntimeError('Lintap stopped during startup')
            text = (root / 'lintap.log').read_text(errors='replace')
            runtime_log = root / 'lintap-runtime/Logs/Lintap.log'
            if runtime_log.exists():
                text += runtime_log.read_text(errors='replace')
            # Registration is separate from successful OS stimuli/capture acceptance.
            if all(name + ' sensor registered' in text for name in required):
                break
            time.sleep(1)
        else:
            raise RuntimeError('Required sensor registrations not observed within 150s')
        state['lintap_ready_utc'] = utc()
        configured = subprocess.run([str(binary), '--show-config'], env=pidstat_env,
                                    capture_output=True, text=True, timeout=10, check=True)
        state['pidstat_config'] = json.loads(configured.stdout)
        assert state['pidstat_config']['interval_sec'] == 5
        assert state['pidstat_config']['rotate_interval_sec'] == 300
        collector = launch('pidstat', pidstat_env)
        started = time.monotonic()
        state.update(status='running', started_utc=utc(),
                     planned_stop_utc=(datetime.datetime.now(datetime.timezone.utc) +
                                       datetime.timedelta(seconds=args.seconds)).isoformat())
        launch('smoke', env)
        write(root / 'state.json', state)
        with (root / 'resources.jsonl').open('a', buffering=1) as output:
            while time.monotonic() - started < args.seconds and not stopped:
                sample = {'utc': utc(), 'elapsed_sec': time.monotonic() - started,
                          'processes': {n: proc_sample(p.pid) for n, p in processes.items()},
                          'free_bytes': os.statvfs(root).f_bavail * os.statvfs(root).f_frsize,
                          'loadavg': os.getloadavg(),
                          'pidstat_files': len(list((root / 'pidstat-data').rglob('*.parquet')))}
                output.write(json.dumps(sample) + '\n')
                for name, process in processes.items():
                    if process.poll() is not None:
                        raise RuntimeError(f'{name} exited early: {process.returncode}')
                if sample['free_bytes'] < 4 * 1024**3:
                    raise RuntimeError('Disk safety floor reached; preserve data and stop')
                time.sleep(min(30, max(0, args.seconds - (time.monotonic() - started))))
        if stopped:
            raise RuntimeError('Interrupted: ' + ','.join(stopped))
        state['status'] = 'duration-complete'
    except Exception as exc:
        failure = str(exc)
        state.update(status='failed', failure=failure)
    finally:
        state['collection_stop_utc'] = utc()
        state['elapsed_sec'] = None if started is None else time.monotonic() - started
        # Stop generation first, seal pidstat while Lintap is still live, then drain Lintap.
        for name in ('smoke', 'pidstat', 'lintap'):
            process = processes.get(name)
            if process is None:
                continue
            forced = False
            if process.poll() is None:
                # Signal only this invocation's process group (including active stimuli).
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=90 if name == 'lintap' else 30)
                except subprocess.TimeoutExpired:
                    forced = True
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=10)
            state['shutdown'][name] = {'exit': process.returncode, 'forced': forced, 'utc': utc()}
        for log in logs:
            log.close()
        state['finished_utc'] = utc()
        if state['status'] == 'duration-complete':
            state['status'] = ('collected-awaiting-review' if
                               state['shutdown']['pidstat']['exit'] == 0 and
                               not any(v['forced'] for v in state['shutdown'].values())
                               else 'shutdown-failed')
        write(root / 'state.json', state)
        print(json.dumps(state, indent=2), flush=True)
    return 0 if state['status'] == 'collected-awaiting-review' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--seconds', type=int, default=14400)
    options = parser.parse_args()
    assert options.seconds > 0
    raise SystemExit(run(options))
