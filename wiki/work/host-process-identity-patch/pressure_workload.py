"""Bounded Linux stimulus oracle; no sensor policy or installed state changes.

Forked children wait on a shared pipe before four write/read pairs and one
non-loopback TCP request/echo. Syscalls and bytes are stimulus evidence, NOT
predicted kernel packet counts. Native loss before callbacks remains separate.
"""
import ctypes
import datetime as dt
import json
import os
from pathlib import Path
import select
import socket
import threading
import time


def receive(sock, count):
    data = b''
    while len(data) < count:
        part = sock.recv(count - len(data))
        if not part:
            raise RuntimeError('Premature TCP EOF')
        data += part
    return data


def workload(root, children, ip):
    if children not in (4, 32, 128, 256):
        raise ValueError('Bounded qualified tiers are4/32/128/256children')
    root.mkdir(parents=True, exist_ok=False)
    ready_r, ready_w = os.pipe()
    release_r, release_w = os.pipe()
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((ip, 0))
    listener.listen(512)
    listener.settimeout(60)
    port = listener.getsockname()[1]
    started = time.time_ns()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    pids, server_rows, server_errors = [], [], []
    def serve():
        try:
            for _ in range(children):
                sock, peer = listener.accept()
                with sock:
                    sock.settimeout(30)
                    data = receive(sock, 32)
                    sock.sendall(data)
                    server_rows.append(dict(pid=os.getpid(), localPort=port, remotePort=peer[1],
                                            bytes_received=len(data), bytes_sent=len(data)))
        except Exception as error:
            server_errors.append(str(error))
    try:
        for _ in range(children):
            pid = os.fork()
            if pid == 0:
                listener.close()
                os.close(ready_r); os.close(release_w)
                record = dict(pid=os.getpid(), parent=os.getppid(), cohort='pressure', payload_files=4,
                    executable=str(Path('/proc/self/exe').resolve()), clock_ticks=os.sysconf('SC_CLK_TCK'),
                    start_ticks=int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]))
                try:
                    ctypes.CDLL(None).prctl(15, b'qa_pressure', 0, 0, 0)
                    os.write(ready_w, b'R')
                    if os.read(release_r, 1) != b'G':
                        raise RuntimeError('Missing release token')
                    record['callback_begin_monotonic_ns'] = time.monotonic_ns()
                    payload = root / 'payload' / f'pressure-{os.getpid()}'
                    payload.mkdir(parents=True)
                    for i in range(4):
                        path = payload / f'file-{i}.txt'
                        path.write_bytes(b'evidence-' * 16)
                        if path.read_bytes() != b'evidence-' * 16:
                            raise RuntimeError('File payload mismatch')
                    with socket.create_connection((ip, port), timeout=30) as sock:
                        record['tcp'] = dict(pid=os.getpid(), localPort=sock.getsockname()[1], remotePort=port)
                        sock.sendall(b'p' * 32)
                        if receive(sock, 32) != b'p' * 32:
                            raise RuntimeError('TCP echo mismatch')
                        record['tcp'].update(bytes_sent=32, bytes_received=32)
                    record['before_exit_monotonic_ns'] = time.monotonic_ns()
                    record['complete'] = True
                except BaseException as error:
                    record.update(complete=False, error=str(error))
                (root / f'child-{os.getpid()}.json').write_text(json.dumps(record))
                os._exit(0 if record['complete'] else 1)
            pids.append(pid)
        os.close(ready_w); ready_w = None
        os.close(release_r); release_r = None
        tokens = b''
        deadline = time.monotonic() + 60
        while len(tokens) < children:
            if time.monotonic() >= deadline:
                raise RuntimeError('Bounded child-ready deadline exceeded')
            if select.select([ready_r], [], [], 1)[0]:
                part = os.read(ready_r, children - len(tokens))
                if not part:
                    raise RuntimeError('Child readiness pipe closed early')
                tokens += part
        server = threading.Thread(target=serve, daemon=True)
        server.start()
        released = time.monotonic_ns()
        os.write(release_w, b'G' * children)
        os.close(release_w); release_w = None
        records = []
        deadline = time.monotonic() + 75
        remaining = set(pids)
        while remaining:
            for pid in list(remaining):
                done, status = os.waitpid(pid, os.WNOHANG)
                if done:
                    record_path = root / f'child-{pid}.json'
                    record = json.loads(record_path.read_text()) if record_path.exists() else dict(pid=pid, complete=False)
                    record.update(wait_status=status, reap_monotonic_ns=time.monotonic_ns())
                    records.append(record); remaining.remove(pid)
            if remaining and time.monotonic() >= deadline:
                raise RuntimeError('Bounded workload deadline exceeded')
            if remaining:
                time.sleep(.01)
        server.join(65)
        complete = (not server.is_alive() and not server_errors and len(server_rows) == children and
                    all(r.get('complete') and r['wait_status'] == 0 for r in records))
        completed_utc = dt.datetime.now(dt.timezone.utc).isoformat()
        selectors = []
        for record in records:
            if not record.get('complete'):
                continue
            client = record['tcp']
            matches = [s for s in server_rows if s['remotePort'] == client['localPort']]
            if len(matches) != 1:
                complete = False
                continue
            selectors.append(dict(case=f"pressure-{record['pid']}", domain='network',
                pids=[os.getpid(), record['pid']], ports=[port, client['localPort']],
                startedAtUtc=started_utc, completedAtUtc=completed_utc,
                endpointExpectations=[dict(role=role, localIp=ip, remoteIp=ip, **end)
                    for role, end in [('server', matches[0]), ('client', client)]]))
        manifest = dict(start_unix_ns=started, end_unix_ns=time.time_ns(), release_monotonic_ns=released,
            children=records, expected_children=children, expected_payload_files=children * 4,
            expected_payload_file_events=children * 4 * 7, server_rows=server_rows, server_errors=server_errors,
            endpoint_selectors=selectors, complete=complete, generation='synchronized pipe release; four file write/read pairs and32-byte TCP echo per child')
        (root / 'workload.json').write_text(json.dumps(manifest, indent=2))
        return manifest
    finally:
        for fd in (ready_r, ready_w, release_r, release_w):
            if fd is not None:
                os.close(fd)
        listener.close()
        # Only disposable stimulus children; never stop an unrelated host process.
        for pid in pids:
            try:
                done, _ = os.waitpid(pid, os.WNOHANG)
                if not done:
                    os.kill(pid, 9)
                    os.waitpid(pid, 0)
            except ChildProcessError:
                pass
