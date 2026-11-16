"""Compare saved Web datasets, exact bytes, IDs and SHA-256."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--left',required=True);p.add_argument('--right',required=True);a=p.parse_args()
x=Path(a.left).read_bytes();y=Path(a.right).read_bytes()
lx=json.loads(x);ly=json.loads(y)
assert len(lx)==len(ly)==200,'Expected 200 shipments'
assert len({r['id'] for r in lx})==len({r['id'] for r in ly})==200,'IDs must be unique'
assert x==y,'FAIL: response bytes differ'
print('PASS: 200 unique IDs; exact bytes and SHA256 match',hashlib.sha256(x).hexdigest())
