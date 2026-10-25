"""Installed-package test rounds on disposable axon/caldera hosts; run as root.

Preserves historical mounted data/runtime, uses fresh captures and native state.
Each round stops the actual systemd service; never launches a parallel collector.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from attribution_experiment import workload
from network_endpoint_smoke_test import generate_cases


def systemd_override(envfile):
    return '[Service]\nTimeoutStopSec=120\nKillSignal=SIGTERM\n' + f'EnvironmentFile={envfile}\n'


def clock_receipt():
    # Logging uses DateTime.Now; never assume its local offset is UTC.
    return dict(unix_ns=time.time_ns(), monotonic_ns=time.monotonic_ns(),
                local_utc_offset_seconds=int(dt.datetime.now().astimezone().utcoffset().total_seconds()),
                local_zone=time.tzname, harness_TZ=os.environ.get('TZ'),
                localtime_sha256=hashlib.sha256(Path('/etc/localtime').read_bytes()).hexdigest())


def exit_recovery_environment(enabled):
    return dict(WINTAP_EXPERIMENT_EXIT_IDENTITY_RECOVERY=str(enabled).lower(),
                WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY='1024',
                WINTAP_ENABLE_CLONE_SENSOR='false', WINTAP_ENABLE_EXECVE_SENSOR='false',
                WINTAP_ENABLE_PROCESS_RUNDOWN_SENSOR='false')


def service_stopped_cleanly(properties):
    values = dict(line.split('=', 1) for line in properties.splitlines() if '=' in line)
    return (values.get('Result') == 'success' and values.get('ExecMainCode') == '1'
            and values.get('ExecMainStatus') == '0' and values.get('ActiveState') == 'inactive'
            and values.get('NRestarts') == '0')


def command(*args):
    return subprocess.check_output(args, text=True)


def collector_provenance(pid):
    """Independent live-process evidence, not inferred capture start/end bounds."""
    proc = Path('/proc') / str(pid)
    fields = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
    return dict(pid=int(pid), start_ticks=int(fields[19]), clock_ticks=os.sysconf('SC_CLK_TCK'),
                parent_pid=int(fields[1]), executable=str((proc / 'exe').resolve()),
                commandline=(proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode().strip(),
                observed_unix_ns=time.time_ns())


def soak(qa, pid, duration):
    started = time.monotonic()
    stat_path = Path(f'/proc/{pid}/stat')
    start_ticks = stat_path.read_text().rsplit(')', 1)[1].split()[19]
    segments, selectors = [], []
    with (qa / 'monitor.jsonl').open('x') as out:
        for index in range(20):
            target = started + index * duration / 20
            while time.monotonic() < target:
                sample_service(pid, start_ticks, out)
                time.sleep(min(5, max(0, target - time.monotonic())))
            sample_service(pid, start_ticks, out)
            segments.append(workload(qa / 'workload' / f'segment-{index:02d}', 1))
            if index % 5 == 0 or index == 19:
                selectors.extend(generate_cases(command('hostname', '-I').split()[0]))
        while time.monotonic() < started + duration:
            sample_service(pid, start_ticks, out)
            time.sleep(min(5, max(0, started + duration - time.monotonic())))
    children = [child for segment in segments for child in segment['children']]
    if len({r['pid'] for r in children}) != len(children):
        raise RuntimeError('PID reuse requires instance-keyed oracle; do not combine these selectors')
    manifest = dict(start_unix_ns=segments[0]['start_unix_ns'], end_unix_ns=segments[-1]['end_unix_ns'],
                    expected_children=len(children), children=children,
                    expected_payload_files=sum(s['expected_payload_files'] for s in segments),
                    segments=segments, soak_elapsed_seconds=time.monotonic() - started)
    (qa / 'workload' / 'workload.json').write_text(json.dumps(manifest, indent=2))
    return manifest, selectors


def sample_service(pid, start_ticks, output):
    fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    if fields[19] != start_ticks:
        raise RuntimeError('Collector exited/restarted or service PID reused')
    status = dict(line.split(':', 1) for line in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line)
    output.write(json.dumps(dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                                 monotonic_ns=time.monotonic_ns(), pid=pid,
                                 rss_kib=int(status['VmRSS'].split()[0]),
                                 threads=int(status['Threads']), cpu_ticks=int(fields[11]) + int(fields[12]),
                                 native_free_bytes=shutil.disk_usage('/home/ubuntu').free)) + '\n')
    output.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--qa-root', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--replace-test-dropin', action='store_true')
    parser.add_argument('--runtime-root', type=Path, help='Existing native runtime for persistence acceptance')
    parser.add_argument('--soak-seconds', type=float, default=0)
    parser.add_argument('--shutdown-window', action='store_true',
                        help='Three installed-service rounds with fork/file activity across SIGTERM')
    parser.add_argument('--retry-capacity-ab', action='store_true',
                        help='Diagnostic 1024/4096 interleaved shutdown-window control; not release tuning')
    parser.add_argument('--exit-recovery-ab', action='store_true',
                        help='Three interleaved off/on missing-birth pairs at capacity 1024; no synthetic Start')
    parser.add_argument('--experiment-exit-recovery', action='store_true',
                         help='Enable experimental exit-only recovery during normal-birth regression rounds')
    parser.add_argument('--rounds', help='Comma-separated existing round names; preserve defaults if omitted')
    args = parser.parse_args()
    if args.exit_recovery_ab and (args.shutdown_window or args.soak_seconds or args.retry_capacity_ab):
        parser.error('Exit-recovery controls are separate from shutdown-window, soak and capacity modes')
    if args.exit_recovery_ab and args.experiment_exit_recovery:
        parser.error('Exit-recovery A/B controls choose their own off/on configuration')
    args.qa_root.mkdir(parents=True, exist_ok=False)
    if args.data_root.exists():
        raise RuntimeError('Refusing existing capture root')
    host = platform.node()
    boot = int(next(l.split()[1] for l in Path('/proc/stat').read_text().splitlines() if l.startswith('btime ')))
    (args.qa_root / 'host-provenance.json').write_text(json.dumps(dict(
        boot_unix_seconds=boot, hostname=host, kernel=platform.release(),
        arch=platform.machine(), os_release=Path('/etc/os-release').read_text()), indent=2))
    session = dict(start_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                   package=command('dpkg-query', '-W', 'lintap'), rounds=[])
    runtime = args.runtime_root or args.qa_root / 'native-runtime'
    dropin = Path('/etc/systemd/system/lintap.service.d/quality-test.conf')
    dropin.parent.mkdir(parents=True, exist_ok=True)
    if dropin.exists() and not args.replace_test_dropin:
        raise RuntimeError('Refusing existing test drop-in')
    specs = [('fixed-package-default', False, 1),
                                    ('fixed-package-drain', True, 1),
                                    ('fixed-package-burst', True, 2),
                                    ('fixed-package-restart', True, 1)]
    if args.soak_seconds:
        if args.soak_seconds < 60:
            raise RuntimeError('Soak must be at least 60 seconds')
        specs = [('fixed-package-soak', True, 1)]
    if args.shutdown_window:
        if args.soak_seconds:
            raise RuntimeError('Shutdown-window and soak modes are separate experiments')
        specs = [(f'fixed-package-shutdown-{i}', True, 1) for i in range(3)]
    if args.retry_capacity_ab:
        if not args.shutdown_window or args.soak_seconds:
            raise RuntimeError('Retry capacity A/B requires separate shutdown-window mode')
        specs = [(f'fixed-package-capacity-{capacity}-{i}', True, 1)
                  for i in range(3) for capacity in (1024, 4096)]
    if args.exit_recovery_ab:
        specs = [(f'fixed-package-exit-{enabled}-{i}', True, 1)
                  for i in range(3) for enabled in ('off', 'on')]
    if args.rounds:
        requested = args.rounds.split(',')
        if len(set(requested)) != len(requested) or not set(requested) <= {s[0] for s in specs}:
            raise RuntimeError('Requested rounds must be unique existing names for this mode')
        specs = [spec for spec in specs if spec[0] in requested]
    for name, drain, multiplier in specs:
        qa = args.qa_root / name
        qa.mkdir()
        data = args.data_root / name
        env = dict(WINTAP_DATA_ROOT=str(data), WINTAP_RUNTIME_ROOT=str(runtime),
                   WINTAP_ETL_SERIALIZATION_INTERVAL_SEC='10', WINTAP_ETL_UPLOAD_INTERVAL_SEC='15',
                   WINTAP_EXPERIMENT_DRAIN_BATCH_WINDOWS=str(drain).lower(),
                     WINTAP_EXPERIMENT_LIFECYCLE_SHADOW_PATH=str(qa / 'lifetime-shadow.jsonl'),
                    WINTAP_EXPERIMENT_EXIT_IDENTITY_RECOVERY=str(args.experiment_exit_recovery).lower(),
                    WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY='1024')
        if args.experiment_exit_recovery:
            env.update(WINTAP_ENABLE_CLONE_SENSOR='true', WINTAP_ENABLE_EXECVE_SENSOR='true',
                       WINTAP_ENABLE_PROCESS_RUNDOWN_SENSOR='true')
        if args.exit_recovery_ab:
            enabled = name.split('-')[-2] == 'on'
            env.update(exit_recovery_environment(enabled))
        if args.retry_capacity_ab:
            env['WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY'] = name.split('-')[-2]
        envfile = qa / 'quality.env'
        envfile.write_text(''.join(f'{k}={v}\n' for k, v in env.items()))
        # EnvironmentFile takes precedence over Environment. Append a later file,
        # otherwise package defaults silently win over the intended isolated roots.
        dropin.write_text(systemd_override(envfile))
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        result = dict(name=name, missing_birth_injection=args.exit_recovery_ab, env_overrides=env,
                      experiment_exit_recovery=args.experiment_exit_recovery or (args.exit_recovery_ab and enabled),
                      shutdown_window=args.shutdown_window,
                      runtime_root=str(runtime), qa_root=str(qa), data_root=str(data),
                      binary_sha256=hashlib.sha256(Path('/usr/lib/lintap/Lintap.dll').read_bytes()).hexdigest(),
                      exit_object_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                                          for p in Path('/usr/lib/lintap').rglob('exit_tracer.bpf.o')})
        journal_start = dt.datetime.now(dt.timezone.utc).isoformat()
        result['clock_start'] = clock_receipt()
        try:
            subprocess.run(['systemctl', 'start', 'lintap'], check=True, timeout=90)
            time.sleep(20)
            result['service_before'] = command('systemctl', 'show', 'lintap', '-p', 'MainPID', '-p', 'NRestarts', '-p', 'ActiveState')
            if command('systemctl', 'is-active', 'lintap').strip() != 'active':
                raise RuntimeError('Collector not active')
            service_pid = command('systemctl', 'show', 'lintap', '--value', '-p', 'MainPID').strip()
            result['collector_provenance'] = collector_provenance(service_pid)
            effective = dict(part.split('=', 1) for part in Path(f'/proc/{service_pid}/environ').read_text().split('\0') if '=' in part)
            result['collector_TZ'] = effective.get('TZ')
            result['verified_process_environment'] = {k: effective.get(k) for k in env}
            if any(effective.get(k) != v for k, v in env.items()):
                raise RuntimeError('Effective service environment differs from isolated capture settings')
            if not runtime.is_dir():
                raise RuntimeError('Expected native runtime root not created')
            if args.shutdown_window:
                from shutdown_window_experiment import children_across_shutdown
                result['endpoint_interval_start'] = clock_receipt()
                result['endpoint_selectors'] = generate_cases(command('hostname', '-I').split()[0])
                result['endpoint_interval_end'] = clock_receipt()
                time.sleep(30)
                # Signal the actual service PID while stimulus continues. The
                # final systemctl stop still checks exit status and stop budget.
                class ServiceSignal:
                    def send_signal(self, sig):
                        result['shutdown_signal_clock'] = clock_receipt()
                        result['shutdown_signal_monotonic'] = time.monotonic()
                        os.kill(int(service_pid), sig)
                result['workload'] = children_across_shutdown(qa / 'workload', ServiceSignal())
            elif args.soak_seconds:
                result['workload'], result['endpoint_selectors'] = soak(qa, service_pid, args.soak_seconds)
            else:
                result['workload'] = workload(qa / 'workload', multiplier)
                result['endpoint_interval_start'] = clock_receipt()
                result['endpoint_selectors'] = generate_cases(command('hostname', '-I').split()[0])
                result['endpoint_interval_end'] = clock_receipt()
            if not args.shutdown_window:
                time.sleep(30)
        except Exception as exc:
            result['error'] = str(exc)
        finally:
            result['stop_request_clock'] = clock_receipt()
            begin = time.monotonic()
            stopped = subprocess.run(['systemctl', 'stop', 'lintap'], timeout=150)
            result['stop_command_exit_code'] = stopped.returncode
            result['shutdown_seconds'] = time.monotonic() - begin
            if args.shutdown_window and 'shutdown_signal_monotonic' in result:
                result['shutdown_seconds'] = time.monotonic() - result['shutdown_signal_monotonic']
            result['service_after'] = command('systemctl', 'show', 'lintap', '-p', 'Result', '-p', 'ExecMainCode', '-p', 'ExecMainStatus', '-p', 'NRestarts', '-p', 'ActiveState')
            result['collector_exit_code'] = 0 if service_stopped_cleanly(result['service_after']) else -1
            result['forced_termination'] = result['collector_exit_code'] != 0
            (qa / 'collector.log').write_text(command('journalctl', '-u', 'lintap', '--since', journal_start, '--no-pager'))
            if runtime.exists():
                shutil.copytree(runtime, qa / 'runtime-snapshot')
            result['clock_end'] = clock_receipt()
            state = runtime / 'wintapstate.json'
            if state.exists():
                result['agent_state'] = json.loads(state.read_text())
            session['rounds'].append(result)
            session['end_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
            (args.qa_root / 'session.json').write_text(json.dumps(session, indent=2))
            print(json.dumps({k:v for k,v in result.items() if k not in ('workload', 'endpoint_selectors')}, default=str), flush=True)
        if result.get('error') or result['forced_termination']:
            raise SystemExit(1)
    # Leave test drop-in and service stopped for evidence review, not general rollout.


if __name__ == '__main__':
    main()
