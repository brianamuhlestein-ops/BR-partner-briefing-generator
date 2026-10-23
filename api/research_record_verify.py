"""Standalone ZIP verifier: file integrity does not establish scientific validity."""
from hashlib import sha256
import json
from pathlib import Path
import re
import stat
from zipfile import ZipFile, BadZipFile


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')


def verify_package(path):
    with ZipFile(path) as archive:
        members = archive.infolist()
        names = [entry.filename for entry in members]
        if len(names) != len(set(names)) or len(names) > 134 or any(
                entry.file_size > 8_000_000 or entry.flag_bits & 1 or stat.S_ISLNK(entry.external_attr >> 16) for entry in members
        ) or sum(entry.file_size for entry in members) > 64_000_000:
            raise ValueError('Unsupported package members or size.')
        manifest = json.loads(archive.read('manifest.json'))
        if manifest['schema'] != 'swift-saved-research-export-v1' or manifest['application'] not in (
                'sunspot-classification-studio', 'cme-sa-display', 'solar-forecast-console',
                'geomagnetic-observations-monitor', 'particle-forecast-console', 'product-launcher',
                'briefing-synopsis', 'sector-risk-dashboard', 'historical-event-library', 'swift-performance-review'):
            raise ValueError('Unsupported producer/schema.')
        record = encoded(manifest['record'])
        identity = sha256(encoded(dict(application=manifest['application'], family=manifest['family'], record=manifest['record']))).hexdigest()
        if identity != manifest['capture_id'] or sha256(record).hexdigest() != manifest['record_sha256'] or archive.read('record.json') != record:
            raise ValueError('Saved record identity mismatch.')
        expected = {'manifest.json', 'viewer.html', 'verify.py', 'SHA256SUMS'}
        seen_roles, seen_paths = set(), set()
        for entry in manifest['assets']:
            name = entry['path']
            if name in seen_paths or entry['role'] in seen_roles or (name != 'record.json' and (
                    not re.fullmatch(r'files/[A-Za-z0-9_./-]+', name) or any(p in ('', '.', '..') for p in name.split('/')))):
                raise ValueError('Invalid dependency inventory.')
            seen_paths.add(name); seen_roles.add(entry['role'])
            if entry['availability'] == 'available':
                raw = archive.read(name)
                if len(raw) != entry['bytes'] or sha256(raw).hexdigest() != entry['sha256']:
                    raise ValueError('Dependency checksum mismatch.')
                expected.add(name)
            elif entry['availability'] != 'unavailable' or name in names:
                raise ValueError('Invalid missing dependency declaration.')
        if set(names) != expected or 'record' not in seen_roles:
            raise ValueError('Unexpected/missing package files.')
        sums = {}
        for line in archive.read('SHA256SUMS').decode('ascii').splitlines():
            digest, name = line.split('  ', 1)
            if name in sums or not re.fullmatch('[a-f0-9]{64}', digest):
                raise ValueError('Invalid checksum list.')
            sums[name] = digest
        if set(sums) != expected - {'SHA256SUMS'} or any(sha256(archive.read(name)).hexdigest() != digest for name, digest in sums.items()):
            raise ValueError('Package checksum mismatch.')
        return dict(application=manifest['application'], family=manifest['family'], capture_id=identity,
                    files_verified=len(sums), missing_dependencies=sum(e['availability']=='unavailable' for e in manifest['assets']))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Verify a selected saved research case ZIP without SWIFT.')
    parser.add_argument('package', type=Path)
    try:
        print(json.dumps(verify_package(parser.parse_args().package), indent=2))
    except (OSError, ValueError, KeyError, TypeError, BadZipFile) as exc:
        parser.exit(1, f'Verification failed: {exc}\n')
