"""Shared deterministic data, manifest, safe transfer and route functions."""
import argparse,hashlib,json,os,zipfile
from pathlib import Path
from urllib.request import build_opener,ProxyHandler

def write_json(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(tmp,path)
def seed(root):
    root=Path(root)
    if root.exists(): raise FileExistsError('Use a fresh root; existing content is never deleted')
    (root/'data').mkdir(parents=True); (root/'files').mkdir()
    rows=[{'id':f'MPL-{i:04d}','warehouse':['HN','HP','BN'][(i-1)%3],
           'status':['RECEIVED','IN_TRANSIT','DELIVERED'][(i-1)%3],
           'published_at':'2026-11-16T00:00:00+00:00'} for i in range(1,201)]
    write_json(root/'data/shipments.json',rows)
    (root/'files/readme.txt').write_text('MPL public demo dataset\n200 fictional shipments\nNo customer information\n',encoding='utf-8')
    (root/'index.html').write_text("""<!doctype html><html lang="vi"><meta charset="utf-8">
<title>MPL Logistics Demo</title><style>body{font:18px Arial;max-width:880px;margin:50px auto;background:#f5f7fa;color:#152b42}main{background:white;padding:30px;border-radius:12px}a{color:#075ca8}pre{white-space:pre-wrap}</style>
<main><h1>MPL Logistics</h1><p>Cổng dữ liệu công khai thử nghiệm</p>
<p>Dữ liệu giả định gồm 200 vận đơn không có thông tin khách hàng.</p>
<p><a href="/data/shipments.json">Mở 200 vận đơn mẫu</a> · <a href="/files/readme.txt">Tải tập tin mẫu</a></p>
<pre id="status">Đang kiểm tra dịch vụ</pre></main>
<script>fetch('/health').then(r=>r.json()).then(v=>document.getElementById('status').textContent='Dịch vụ: '+v.instance+' | '+v.status)</script></html>""",encoding='utf-8')
def manifest(root):
    root=Path(root)
    if not root.is_dir(): raise FileNotFoundError(root)
    files=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
           for p in sorted(root.rglob('*')) if p.is_file()]
    return {'files':files,'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files)}
def pack(root,archive):
    archive=Path(archive)
    if archive.exists(): raise FileExistsError(archive)
    m=manifest(root)
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for f in m['files']: z.write(Path(root)/f['path'],f['path'])
        z.writestr('_manifest.json',json.dumps(m,ensure_ascii=False))
    return m
def unpack(archive,target):
    target=Path(target)
    if target.exists(): raise FileExistsError('Use a fresh target root')
    with zipfile.ZipFile(archive) as z:
        expected=json.loads(z.read('_manifest.json'))
        for name in z.namelist():
            if name=='_manifest.json': continue
            dest=(target/name).resolve()
            if not dest.is_relative_to(target.resolve()): raise ValueError('Unsafe archive path')
            dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(z.read(name))
    actual=manifest(target)
    if actual!=expected: raise ValueError('Transfer manifest mismatch; do not cut over')
    return actual
def route(path,backend):
    # Health gate prevents a planned switch to an unavailable destination.
    opener=build_opener(ProxyHandler({}))
    with opener.open(backend.rstrip('/')+'/health',timeout=2) as r:
        if r.code!=200 or json.load(r)['status']!='ok': raise ValueError('Backend unhealthy')
    write_json(path,{'backend':backend.rstrip('/')})

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('seed'); s.add_argument('--root',required=True)
    s=sub.add_parser('manifest'); s.add_argument('--root',required=True); s.add_argument('--out',required=True)
    s=sub.add_parser('pack'); s.add_argument('--root',required=True); s.add_argument('--archive',required=True)
    s=sub.add_parser('unpack'); s.add_argument('--archive',required=True); s.add_argument('--target',required=True)
    s=sub.add_parser('compare'); s.add_argument('--left',required=True); s.add_argument('--right',required=True)
    s=sub.add_parser('route'); s.add_argument('--file',required=True); s.add_argument('--backend',required=True)
    s=sub.add_parser('fault'); s.add_argument('--root',required=True); s.add_argument('--state',choices=['on','off'],required=True)
    a=p.parse_args()
    if a.cmd=='seed': seed(a.root)
    elif a.cmd=='manifest': write_json(a.out,manifest(a.root))
    elif a.cmd=='pack': print(json.dumps(pack(a.root,a.archive)))
    elif a.cmd=='unpack': print(json.dumps(unpack(a.archive,a.target)))
    elif a.cmd=='compare':
        left=json.loads(Path(a.left).read_text(encoding='utf-8'))
        right=json.loads(Path(a.right).read_text(encoding='utf-8'))
        if left!=right: raise SystemExit('FAIL manifest mismatch')
        print('PASS exact paths, sizes, and SHA-256 match')
    elif a.cmd=='route': route(a.file,a.backend)
    elif a.cmd=='fault':
        root=Path(a.root); flag=root.parent/(root.name+'.fault')
        if a.state=='on': flag.write_text('simulated failure',encoding='utf-8')
        else: flag.unlink(missing_ok=True)
if __name__=='__main__': main()
