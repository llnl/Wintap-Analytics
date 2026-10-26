"""Private managed-only diagnostic derivative of an archived qualified package.

This is NOT a clean native rebuild or installed-package acceptance. Preserve every
runtime/dependency/eBPF artifact; replace only the qualified Linux DLL/PDB and the
Debian version, with before/after hashes. Never install or modify a service.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--baseline-sha256', required=True)
    parser.add_argument('--managed', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    if sha(args.baseline) != args.baseline_sha256:
        raise RuntimeError('Baseline archive hash differs')
    args.evidence.mkdir(parents=True, exist_ok=False)
    extracted = args.evidence / 'extracted'
    subprocess.run(['dpkg-deb', '-R', str(args.baseline), str(extracted)], check=True)
    before = hashes(extracted)
    for name in ('Lintap.dll', 'Lintap.pdb'):
        shutil.copyfile(args.managed / name, extracted / 'usr/lib/lintap' / name)
    control = extracted / 'DEBIAN/control'
    lines = control.read_text().splitlines()
    if sum(line.startswith('Version: ') for line in lines) != 1:
        raise RuntimeError('Expected one version field')
    control.write_text('\n'.join('Version: ' + args.version if line.startswith('Version: ') else line
                                 for line in lines) + '\n')
    after = hashes(extracted)
    changed = [name for name in before if before[name] != after.get(name)]
    allowed = {'usr/lib/lintap/Lintap.dll', 'usr/lib/lintap/Lintap.pdb', 'DEBIAN/control'}
    if set(before) != set(after) or not set(changed).issubset(allowed):
        raise RuntimeError('Unexpected package content changes')
    package = args.evidence / ('lintap_' + args.version + '_arm64.deb')
    subprocess.run(['dpkg-deb', '--root-owner-group', '-b', str(extracted), str(package)], check=True)
    receipt = dict(baseline=str(args.baseline), baseline_sha256=args.baseline_sha256,
        package=str(package), package_sha256=sha(package), before=before, after=after,
        changed_files=changed, clean_native_rebuild=False, installed=False)
    (args.evidence / 'package-receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('before', 'after')}))


if __name__ == '__main__':
    main()
