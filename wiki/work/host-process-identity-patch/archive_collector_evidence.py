"""Preserve stopped installed-host QA snapshots and mounted captures with hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile


def sha256(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--data-parent', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    args.output_root.mkdir()
    bundle = 'quality-installed-20261024-r7-collector'
    receipts = []
    for host in ('axon-target', 'caldera-host'):
        state = subprocess.check_output(['multipass', 'exec', host, '--', 'systemctl', 'show',
                                         'lintap', '--value', '-p', 'ActiveState'], text=True).strip()
        if state != 'inactive':
            raise RuntimeError('Refusing live-service snapshot: ' + host)
        remote = '/home/ubuntu/' + bundle + '-qa.tar.gz'
        subprocess.run(['multipass', 'exec', host, '--', 'sudo', 'tar', '-czf', remote,
                        '-C', '/home/ubuntu', bundle, bundle + '-install'], check=True)
        qa = args.output_root / host
        qa.mkdir()
        archive = qa / (bundle + '-qa.tar.gz')
        subprocess.run(['multipass', 'transfer', host + ':' + remote, str(archive)], check=True)
        with tarfile.open(archive) as tar:
            tar.extractall(qa, filter='data')
        data_archive = qa / (bundle + '-data.tar.gz')
        with tarfile.open(data_archive, 'w:gz') as tar:
            tar.add(args.data_parent / host, arcname=host)
        receipts.append(dict(host=host, service_state=state,
                             qa_archive=str(archive), qa_sha256=sha256(archive),
                             data_archive=str(data_archive), data_sha256=sha256(data_archive)))
        args.receipt.write_text(json.dumps(receipts, indent=2) + '\n')
    print(json.dumps(receipts, indent=2))


if __name__ == '__main__':
    main()
