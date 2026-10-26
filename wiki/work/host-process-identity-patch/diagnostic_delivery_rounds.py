"""Private extracted-package trace controls; never install or change a service.

Run as root on the two disposable hosts. Active/competing collectors are blockers.
Raw schemas, retry policy, installed files and historical databases remain untouched.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import threading
import time

from attribution_experiment import workload
from network_endpoint_smoke_test import generate_cases, host_address
from package_host_rounds import clock_receipt, collector_provenance


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def service_state():
    return command('systemctl', 'show', 'lintap', '-p', 'ActiveState', '-p',
                   'MainPID', '-p', 'NRestarts', '-p', 'Result')


def require_idle(state):
    fields = dict(line.split('=', 1) for line in state.splitlines())
    if fields.get('ActiveState') != 'inactive' or fields.get('MainPID') != '0':
        raise RuntimeError('Installed collector is not inactive; leave it untouched')
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            exe = (entry / 'exe').resolve().name
            argv = (entry / 'cmdline').read_bytes().split(b'\0')
            if exe == 'Lintap' or any(Path(a.decode()).name == 'Lintap.dll' for a in argv if a):
                raise RuntimeError(f'Competing collector PID {entry.name}; leave it untouched')
        except (FileNotFoundError, PermissionError, ProcessLookupError, UnicodeError):
            continue


def sample_resources(pid, stop, samples):
    while not stop.is_set():
        try:
            status = Path(f'/proc/{pid}/status').read_text().splitlines()
            stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
            samples.append(dict(clock=clock_receipt(),
                status={line.split(':', 1)[0]: line.split(':', 1)[1].strip()
                        for line in status if line.startswith(('VmRSS:', 'VmHWM:', 'Threads:'))},
                utime_ticks=int(stat[11]), stime_ticks=int(stat[12])))
        except (FileNotFoundError, ProcessLookupError):
            return
        stop.wait(1)


def memory_receipt():
    mem = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    vm = dict(line.split() for line in Path('/proc/vmstat').read_text().splitlines())
    return dict(clock=clock_receipt(), available_memory_kib=int(mem['MemAvailable'].split()[0]),
                oom_kill_count=int(vm['oom_kill']))


def base_environment(packaged_env):
    # The packaged file is simple systemd KEY=VALUE text, never execute it as shell.
    result = {}
    for line in packaged_env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            if key.startswith('WINTAP_'):
                result[key] = value
    return result


def round_environment(packaged_env, qa, data, runtime, mode, etl_readiness='legacy', etl_shutdown='legacy'):
    overrides = base_environment(packaged_env)
    overrides.update(WINTAP_DATA_ROOT=str(data), WINTAP_RUNTIME_ROOT=str(runtime),
        WINTAP_ETL_SERIALIZATION_INTERVAL_SEC='10', WINTAP_ETL_UPLOAD_INTERVAL_SEC='15',
        WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY='1024',
        WINTAP_EXPERIMENT_EXIT_IDENTITY_RECOVERY='true',
        WINTAP_EXPERIMENT_DRAIN_BATCH_WINDOWS='false',
        WINTAP_EXPERIMENT_LIFECYCLE_SHADOW_PATH=str(qa / 'lifetime-shadow.jsonl'))
    if etl_readiness == 'required':
        overrides['WINTAP_EXPERIMENT_ETL_READINESS'] = 'true'
    elif etl_readiness != 'legacy':
        raise ValueError('ETL readiness must be legacy or required')
    if etl_shutdown == 'required':
        overrides['WINTAP_EXPERIMENT_ETL_SHUTDOWN_BARRIER'] = 'true'
    elif etl_shutdown != 'legacy':
        raise ValueError('ETL shutdown must be legacy or required')
    if mode == 'on':
        overrides.update(WINTAP_EXPERIMENT_ATTRIBUTION_TRACE_PATH=str(qa / 'attribution.jsonl'),
            WINTAP_EXPERIMENT_TRACE_BUDGET='delivery',
            WINTAP_EXPERIMENT_TRACE_FILE_PREFIX=str(qa / 'workload'))
    elif mode != 'off':
        raise ValueError('Trace mode must be off or on')
    return overrides


def host_capture_root(parent, host):
    if not host or Path(host).name != host or host in ('.', '..'):
        raise ValueError('Host capture namespace must be a single nonempty path component')
    return parent / host


def stimulus_ready_deadline(log, utc_offset, margin_seconds):
    """Place stimulus after the latest operational start upper bound; not sensor readiness."""
    stamps = []
    for sensor in ('FileOps', 'Network'):
        matches = [line for line in log.splitlines() if line.endswith(f'{sensor} sensor started')]
        if len(matches) != 1:
            return None
        stamp = dt.datetime.strptime(matches[0][:19], '%m/%d/%Y %H:%M:%S').replace(
            tzinfo=dt.timezone(dt.timedelta(seconds=utc_offset))).timestamp()
        stamps.append(stamp + 1)  # Log precision truncates to whole seconds.
    return max(stamps) + margin_seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--package-sha256', required=True)
    parser.add_argument('--qa-root', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--agent-state', type=Path, required=True)
    parser.add_argument('--order', choices=['off,on', 'on,off'], default='off,on')
    parser.add_argument('--etl-readiness', choices=['legacy', 'required'], default='legacy')
    parser.add_argument('--etl-shutdown', choices=['legacy', 'required'], default='legacy')
    parser.add_argument('--stimulus-margin-seconds', type=int, default=0)
    parser.add_argument('--pressure-children', type=int, choices=[32, 128, 256])
    parser.add_argument('--pressure-phase', choices=['interior', 'shutdown-tail'], default='interior')
    args = parser.parse_args()
    if not 0 <= args.stimulus_margin_seconds <= 30:
        parser.error('Stimulus margin must be in0..30seconds')
    if os.geteuid() != 0:
        parser.error('Root required for eBPF; this does not authorize installation')
    before = service_state()
    require_idle(before)
    # /var/log/lintap/data is a shared mount on these hosts. Never combine captures.
    args.data_root = host_capture_root(args.data_root, platform.node())
    if sha(args.package) != args.package_sha256:
        raise RuntimeError('Package hash differs from build receipt')
    if args.qa_root.exists() or args.data_root.exists():
        raise RuntimeError('Refusing existing evidence/capture roots')
    args.qa_root.mkdir(parents=True)
    extraction = args.qa_root / 'extracted'
    subprocess.run(['dpkg-deb', '-x', str(args.package), str(extraction)], check=True)
    binary = extraction / 'usr/lib/lintap'
    runtime = args.qa_root / 'native-runtime'
    runtime.mkdir()
    shutil.copyfile(args.agent_state, runtime / 'wintapstate.json')
    hashes = {str(p.relative_to(binary)): sha(p) for p in binary.rglob('*') if p.is_file()}
    (args.qa_root / 'binary-hashes.json').write_text(json.dumps(hashes, indent=2))
    runtime_config = json.loads((binary / 'Lintap.runtimeconfig.json').read_text())
    if not all((binary / name).exists() for name in ('libcoreclr.so', 'libhostfxr.so')):
        raise RuntimeError('Private package must contain its own .NET runtime')
    ldd = subprocess.run(['ldd', str(binary / 'Lintap')], capture_output=True, text=True)
    (args.qa_root / 'apphost-ldd.txt').write_text(ldd.stdout + ldd.stderr)
    if ldd.returncode or 'not found' in ldd.stdout + ldd.stderr:
        raise RuntimeError('Apphost native dependencies unresolved')
    session = dict(hostname=platform.node(), kernel=platform.release(), clock=clock_receipt(),
        installed_service_before=before, installed_dll_sha256=sha('/usr/lib/lintap/Lintap.dll'),
        package_sha256=args.package_sha256, package_version=command('dpkg-deb', '-f', str(args.package), 'Version'),
        installed_package=command('dpkg-query', '-W', 'lintap'), runtime_config=runtime_config,
        agent_state_source=str(args.agent_state), agent_state_source_sha256=sha(args.agent_state),
        cpu_clock_ticks= os.sysconf('SC_CLK_TCK'), rounds=[])
    session_path = args.qa_root / 'session.json'
    session_path.write_text(json.dumps(session, indent=2))
    boot = int(next(line.split()[1] for line in Path('/proc/stat').read_text().splitlines() if line.startswith('btime ')))
    (args.qa_root / 'host-provenance.json').write_text(json.dumps(dict(
        boot_unix_seconds=boot, hostname=platform.node(), kernel=platform.release(),
        arch=platform.machine(), os_release=Path('/etc/os-release').read_text()), indent=2))
    for mode in args.order.split(','):
        require_idle(service_state())
        qa = args.qa_root / ('trace-' + mode)
        qa.mkdir()
        data = args.data_root / ('trace-' + mode)
        overrides = round_environment(extraction / 'etc/lintap/lintap.env', qa, data, runtime, mode,
                                      args.etl_readiness, args.etl_shutdown)
        env = {k: v for k, v in os.environ.items() if not k.startswith('WINTAP_')}
        env.update(overrides)
        result = dict(name='trace-' + mode, qa_root=str(qa), data_root=str(data),
            runtime_root=str(runtime), env_overrides=overrides, clock_start=clock_receipt(),
            identity_scheme='pid-v2',
            experiment_exit_recovery=True, shutdown_window=False, missing_birth_injection=False,
            binary_sha256=hashes['Lintap.dll'], resource_samples=[])
        session['rounds'].append(result)
        if args.pressure_children:
            result['memory_before'] = memory_receipt()
        with (qa / 'collector.log').open('w') as log:
            proc = subprocess.Popen([str(binary / 'Lintap')], cwd=binary, env=env,
                                    stdout=log, stderr=subprocess.STDOUT)
            stop = threading.Event()
            sampler = threading.Thread(target=sample_resources, args=(proc.pid, stop, result['resource_samples']))
            sampler.start()
            try:
                time.sleep(20)
                if args.stimulus_margin_seconds:
                    wait_start = clock_receipt()
                    deadline = time.monotonic() + 90
                    while True:
                        if proc.poll() is not None:
                            raise RuntimeError('Collector exited while scheduling interior stimulus')
                        logfile = runtime / 'Logs/Lintap.log'
                        target = stimulus_ready_deadline(logfile.read_text() if logfile.exists() else '',
                            wait_start['local_utc_offset_seconds'], args.stimulus_margin_seconds)
                        if target is not None and time.time() > target:
                            break
                        if time.monotonic() >= deadline:
                            raise RuntimeError('Operational sensor envelopes unavailable before bounded stimulus wait')
                        time.sleep(0.2)
                    result['stimulus_schedule'] = dict(wait_start=wait_start, wait_end=clock_receipt(),
                        target_unix_seconds=target, margin_seconds=args.stimulus_margin_seconds,
                        evidence='operational start-envelope upper bounds; not native readiness')
                if proc.poll() is not None:
                    raise RuntimeError(f'Collector exited at startup: {proc.returncode}')
                result['collector_provenance'] = collector_provenance(proc.pid)
                effective = dict(part.split('=', 1) for part in Path(f'/proc/{proc.pid}/environ')
                                 .read_text().split('\0') if '=' in part)
                result['verified_process_environment'] = {k: effective.get(k) for k in overrides}
                result['collector_TZ'] = effective.get('TZ')
                if result['verified_process_environment'] != overrides:
                    raise RuntimeError('Effective environment differs from requested control')
                if args.pressure_children:
                    result['endpoint_interval_start'] = clock_receipt()
                    result['endpoint_selectors'] = generate_cases(host_address())
                    result['endpoint_interval_end'] = clock_receipt()
                result['workload_interval_start'] = clock_receipt()
                if args.pressure_children:
                    from pressure_workload import workload as pressure_workload
                    result['pressure_phase'] = args.pressure_phase
                    result['workload'] = pressure_workload(qa / 'workload', args.pressure_children, host_address())
                    if not result['workload']['complete']:
                        raise RuntimeError('Independent pressure workload generation incomplete')
                else:
                    result['workload'] = workload(qa / 'workload', 1)
                result['workload_interval_end'] = clock_receipt()
                if args.pressure_children:
                    result['pressure_endpoint_selectors'] = result['workload']['endpoint_selectors']
                else:
                    result['endpoint_interval_start'] = clock_receipt()
                    result['endpoint_selectors'] = generate_cases(host_address())
                    result['endpoint_interval_end'] = clock_receipt()
                if not args.pressure_children or args.pressure_phase == 'interior':
                    time.sleep(30)
            except Exception as error:
                result['error'] = str(error)
            finally:
                result['stop_request_clock'] = clock_receipt()
                if proc.poll() is None:
                    proc.send_signal(signal.SIGTERM)
                    try:
                        proc.wait(timeout=120)
                    except subprocess.TimeoutExpired:
                        result['forced_termination'] = True
                        proc.kill()
                        proc.wait(timeout=15)
                stop.set()
                sampler.join(5)
                result['collector_exit_code'] = proc.returncode
                result['clock_end'] = clock_receipt()
                if args.pressure_children:
                    result['memory_after'] = memory_receipt()
                result['agent_state'] = json.loads((runtime / 'wintapstate.json').read_text())
                # The logger overwrites on restart; preserve each stopped round before the next launch.
                snapshot = qa / 'runtime-snapshot'
                snapshot.mkdir()
                shutil.copytree(runtime / 'Logs', snapshot / 'Logs')
                shutil.copyfile(runtime / 'wintapstate.json', snapshot / 'wintapstate.json')
        session_path.write_text(json.dumps(session, indent=2))
        if result.get('error') or result.get('forced_termination') or proc.returncode != 0:
            break
    session.update(installed_service_after=service_state(),
        installed_dll_sha256_after=sha('/usr/lib/lintap/Lintap.dll'),
        agent_state_source_sha256_after=sha(args.agent_state), clock_end=clock_receipt())
    session_path.write_text(json.dumps(session, indent=2))
    if session['installed_service_after'] != before or session['installed_dll_sha256_after'] != session['installed_dll_sha256']:
        raise RuntimeError('Installed control state changed')
    if session['agent_state_source_sha256_after'] != session['agent_state_source_sha256']:
        raise RuntimeError('Original runtime state changed')
    if len(session['rounds']) != 2 or any(r.get('error') or r.get('forced_termination') or r['collector_exit_code'] for r in session['rounds']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
