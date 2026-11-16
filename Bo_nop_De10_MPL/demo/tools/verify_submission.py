"""Verify delivered files and shared KT1-KT3 evidence using the standard library."""
from pathlib import Path
import csv
import hashlib
import json


def main():
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / 'FILE_MANIFEST_SHA256.json').read_text(encoding='utf-8'))
    for entry in manifest:
        path = (root / entry['path']).resolve()
        if not path.is_relative_to(root):
            raise SystemExit('FAIL: manifest path outside submission')
        if not path.is_file():
            raise SystemExit('FAIL: missing ' + entry['path'])
        data = path.read_bytes()
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise SystemExit('FAIL: checksum mismatch ' + entry['path'])

    evidence = root / 'minh_chung' / 'demo_docker'
    summary = json.loads((evidence / 'summary.json').read_text(encoding='utf-8'))
    if summary['status'] != 'PASS' or summary['core_tests_passed'] != 3:
        raise SystemExit('FAIL: core test summary')
    source = json.loads((evidence / 'source_manifest.json').read_text(encoding='utf-8'))
    target = json.loads((evidence / 'target_manifest.json').read_text(encoding='utf-8'))
    if source != target:
        raise SystemExit('FAIL: source and target manifests differ')
    data = [(evidence / ('KT' + str(i) + '_data.json')).read_bytes() for i in [1, 2, 3]]
    if not data[0] == data[1] == data[2]:
        raise SystemExit('FAIL: KT1-KT3 response bytes differ')
    records = json.loads(data[0])
    if len(records) != 200 or len({r['id'] for r in records}) != 200:
        raise SystemExit('FAIL: expected 200 unique shipment IDs')
    with (evidence / 'test_results.csv').open(encoding='utf-8-sig', newline='') as file:
        tests = list(csv.DictReader(file))
    if not all(row['status'] == 'PASS' for row in tests):
        raise SystemExit('FAIL: test result table')
    print(f'PASS: {len(manifest)} submitted files match SHA-256; KT1-KT3 evidence verified')


if __name__ == '__main__':
    main()
