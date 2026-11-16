from pathlib import Path
import textwrap, json, csv, shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Bo_nop_De10_MPL'
for sub in ['demo/app', 'demo/tools', 'demo/config', 'thiet_ke', 'bieu_mau', 'tai_lieu', 'minh_chung']:
    (OUT/sub).mkdir(parents=True, exist_ok=True)

def put(path, content):
    (OUT/path).write_text(textwrap.dedent(content).lstrip(), encoding='utf-8')

put('demo/app/service.py', r'''
"""MPL read-only Web demo. Standard library only; not a production server."""
import argparse, json, mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from datetime import datetime, timezone

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--instance', required=True)
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8080)
    a=p.parse_args(); root=Path(a.root).resolve()
    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, body, kind='application/json; charset=utf-8'):
            self.send_response(code); self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-MPL-Instance', a.instance)
            self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            path=urlsplit(self.path).path
            if (root.parent/(root.name+'.fault')).exists():
                return self.reply(503,b'{"error":"simulated target failure"}')
            if not (root/'index.html').is_file():
                return self.reply(503,b'{"error":"content not deployed"}')
            if path=='/health':
                return self.reply(200,json.dumps({'status':'ok','instance':a.instance}).encode())
            names={'/':'index.html','/index.html':'index.html',
                   '/data/shipments.json':'data/shipments.json',
                   '/files/readme.txt':'files/readme.txt'}
            if path not in names: return self.reply(404,b'{"error":"not found"}')
            f=root/names[path]
            if not f.is_file(): return self.reply(404,b'{"error":"missing file"}')
            kind=mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
            return self.reply(200,f.read_bytes(),kind+'; charset=utf-8')
        def do_POST(self): self.reply(405,b'{"error":"read only"}')
        def log_message(self, fmt, *args):
            print(datetime.now(timezone.utc).isoformat(),a.instance,fmt%args,flush=True)
    server=ThreadingHTTPServer((a.host,a.port),Handler)
    print(json.dumps({'instance':a.instance,'root':str(root),'host':a.host,'port':a.port}),flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
if __name__=='__main__': main()
''')

put('demo/app/gateway.py', r'''
"""Stable lab endpoint. Atomic route file is the sole cutover control."""
import argparse, json, urllib.request, urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from datetime import datetime,timezone
def main():
    p=argparse.ArgumentParser(); p.add_argument('--route',required=True)
    p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=18080)
    a=p.parse_args(); route=Path(a.route)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                backend=json.loads(route.read_text(encoding='utf-8'))['backend'].rstrip('/')
                # Only fixed application routes are forwarded.
                if self.path.split('?')[0] not in ['/', '/index.html','/health','/data/shipments.json','/files/readme.txt']:
                    self.send_error(404); return
                try: res=opener.open(backend+self.path,timeout=1)
                except urllib.error.HTTPError as e: res=e
                with res:
                    body=res.read(); self.send_response(res.code)
                    self.send_header('Content-Type',res.headers.get('Content-Type','application/json'))
                    self.send_header('X-MPL-Instance',res.headers.get('X-MPL-Instance','unknown'))
                    self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store')
                    self.end_headers(); self.wfile.write(body)
            except Exception as e:
                body=json.dumps({'error':'backend unavailable','detail':type(e).__name__}).encode()
                self.send_response(502); self.send_header('Content-Length',str(len(body)))
                self.end_headers(); self.wfile.write(body)
        def do_POST(self): self.send_error(405,'read only')
        def log_message(self,fmt,*args):
            print(datetime.now(timezone.utc).isoformat(),'gateway',fmt%args,flush=True)
    s=ThreadingHTTPServer((a.host,a.port),Handler)
    try: s.serve_forever()
    except KeyboardInterrupt: pass
    finally: s.server_close()
if __name__=='__main__': main()
''')

put('demo/tools/lab.py', r'''
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
''')

put('demo/demo.py', r'''
"""Run KT1-KT3 locally, produce genuine timestamped evidence, then stop own servers."""
import argparse,csv,hashlib,json,platform,socket,subprocess,sys,time,urllib.request,urllib.error,zipfile
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent/'tools'))
from lab import seed,manifest,pack,unpack,write_json,route
HERE=Path(__file__).resolve().parent
def now(): return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
def main():
    p=argparse.ArgumentParser(); p.add_argument('--interactive',action='store_true')
    p.add_argument('--base-port',type=int,default=18080)
    a=p.parse_args(); base=a.base_port
    for port in [base,base+1,base+2]:
        with socket.socket() as s:
            try: s.bind(('127.0.0.1',port))
            except OSError: raise SystemExit(f'Port {port} busy; use --base-port 19080')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    run=HERE/'runs'/stamp; run.mkdir(parents=True)
    evidence=run/'evidence'; evidence.mkdir()
    src=run/'source'/'content'; dst=run/'target'/'content'
    seed(src); dst.parent.mkdir(parents=True)
    routefile=run/'route.json'; processes=[]; handles=[]; rows=[]; probes=[]; events=[]
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    source=f'http://127.0.0.1:{base+1}'; target=f'http://127.0.0.1:{base+2}'; endpoint=f'http://127.0.0.1:{base}'
    def event(kind,**values):
        v={'timestamp_utc':now(),'event':kind,**values}; events.append(v)
        print(json.dumps(v,ensure_ascii=False),flush=True)
    def request(url):
        try:
            with op.open(url,timeout=1) as r: return r.code,r.read(),dict(r.headers)
        except urllib.error.HTTPError as e: return e.code,e.read(),dict(e.headers)
        except Exception as e: return 0,str(type(e).__name__).encode(),{}
    def wait(url,instance):
        end=time.monotonic()+12
        while time.monotonic()<end:
            status,body,h=request(url+'/health')
            if status==200 and json.loads(body).get('instance')==instance:return
            time.sleep(.1)
        raise RuntimeError('Service did not start '+url)
    def launch(script,args,name):
        h=(evidence/(name+'.log')).open('w',encoding='utf-8'); handles.append(h)
        processes.append(subprocess.Popen([sys.executable,str(HERE/'app'/script),*args],stdout=h,stderr=subprocess.STDOUT,cwd=HERE))
    def snapshot(label):
        status,body,headers=request(endpoint+'/data/shipments.json')
        if status!=200: raise AssertionError((label,status))
        data=json.loads(body); assert len(data)==200 and len({x['id'] for x in data})==200
        (evidence/(label+'_data.json')).write_bytes(body)
        write_json(evidence/(label+'_http.json'),{'timestamp_utc':now(),'url':endpoint+'/data/shipments.json',
          'status':status,'instance':headers.get('X-MPL-Instance'),'records':len(data),'sha256':hashlib.sha256(body).hexdigest()})
        return body,headers.get('X-MPL-Instance')
    def pause(message):
        if a.interactive: input(message+' [Enter] ')
    def result(test,inputs,action,expected,actual,files):
        rows.append({'test_id':test,'input':inputs,'action':action,'expected':expected,'actual':actual,
                     'status':'PASS','timestamp_utc':now(),'evidence':files})
    summary={'run_id':stamp,'test_mode':'two isolated directories and server processes on one host',
             'cloud_deployed':False,'vm_tested':False,'python':sys.version,'platform':platform.platform(),
             'client_endpoint':endpoint,'source_endpoint':source,'target_endpoint':target}
    write_json(evidence/'environment.json',summary)
    try:
        launch('service.py',['--root',str(src),'--instance','source','--port',str(base+1)],'source')
        launch('service.py',['--root',str(dst),'--instance','target','--port',str(base+2)],'target')
        wait(source,'source'); route(routefile,source)
        launch('gateway.py',['--route',str(routefile),'--port',str(base)],'gateway'); wait(endpoint,'source')
        baseline,instance=snapshot('KT1'); assert instance=='source'
        m1=manifest(src); write_json(evidence/'source_manifest.json',m1)
        result('KT1','200 fictional shipments / 3 Web files','Read source through stable endpoint; save manifest',
               'HTTP 200; source; 200 unique IDs',f'HTTP 200; {instance}; 200 unique IDs; {m1["file_count"]} files',
               'KT1_data.json; KT1_http.json; source_manifest.json')
        event('KT1_PASS',records=200,files=m1['file_count'])
        pause('KT1: Open '+endpoint+' and show source, then continue migration')
        # An empty/unhealthy target must not be selected.
        rejected=False
        try: route(routefile,target)
        except Exception: rejected=True
        assert rejected and json.loads(routefile.read_text())['backend']==source
        result('KT4','Empty target','Attempt gated cutover','Reject; route remains source','Rejected; source retained','events.jsonl')
        event('unhealthy_target_cutover_rejected',route=source)
        archive=run/'transfer.zip'; pack(src,archive); unpack(archive,dst)
        m2=manifest(dst); assert m1==m2; write_json(evidence/'target_manifest.json',m2)
        # Check corruption is detectable without damaging the accepted target.
        tampered=json.loads(json.dumps(m2)); tampered['files'][0]['sha256']='0'*64
        assert tampered!=m1
        write_json(evidence/'negative_manifest.json',{'timestamp_utc':now(),'corruption_detected':tampered!=m1,
                    'method':'modify a copy of first manifest hash; preserve accepted target'})
        result('KT5','Copied manifest with one changed hash','Compare to source','Detect mismatch','Mismatch detected','negative_manifest.json')
        wait(target,'target'); route(routefile,target); wait(endpoint,'target')
        after,instance=snapshot('KT2'); assert baseline==after and instance=='target'
        write_json(evidence/'cutover_route.json',json.loads(routefile.read_text()))
        result('KT2','Source archive / manifest / stable endpoint','Transfer, compare, health gate, switch endpoint',
               'Same 200 records, all file hashes equal; target serves endpoint',
               '200 records byte-identical; all 3 file hashes equal; instance=target',
               'KT2_data.json; KT2_http.json; target_manifest.json; cutover_route.json')
        event('KT2_PASS',instance=instance,bytes=m2['total_bytes'])
        pause('KT2: Refresh '+endpoint+' and show target plus matching manifests')
        lastgood=now(); lastgood_mono=time.monotonic(); assert request(endpoint+'/health')[0]==200
        fault=dst.parent/(dst.name+'.fault'); fault.write_text('simulated failure',encoding='utf-8')
        event('target_fault_injected')
        firstbad=None; firstbad_iso=None
        end=time.monotonic()+5
        while time.monotonic()<end:
            status,body,h=request(endpoint+'/health'); t=time.monotonic()
            probes.append({'timestamp_utc':now(),'status':status,'instance':h.get('X-MPL-Instance','')})
            if status!=200: firstbad=t; firstbad_iso=now(); break
            time.sleep(.1)
        assert firstbad is not None
        event('failure_detected',http_status=status)
        # A deliberate visible hold is part of this lab, not a real DNS propagation delay.
        hold_end=time.monotonic()+2
        while time.monotonic()<hold_end:
            status,body,h=request(endpoint+'/health')
            probes.append({'timestamp_utc':now(),'status':status,'instance':h.get('X-MPL-Instance','')}); time.sleep(.1)
        route(routefile,source); wait(endpoint,'source')
        back,instance=snapshot('KT3'); assert back==baseline and instance=='source'
        restored=time.monotonic(); restored_iso=now()
        probes.append({'timestamp_utc':restored_iso,'status':200,'instance':instance})
        measure={'last_success_before_fault_utc':lastgood,'first_failure_utc':firstbad_iso,
                 'first_success_after_rollback_utc':restored_iso,
                 'observed_outage_seconds':round(restored-firstbad,4),
                 'upper_bound_seconds':round(restored-lastgood_mono,4),'probe_interval_seconds':.1,
                 'intentional_fault_hold_seconds':2,'clock':'monotonic duration; UTC wall time for evidence'}
        write_json(evidence/'rollback_timing.json',measure)
        write_json(evidence/'rollback_route.json',json.loads(routefile.read_text()))
        result('KT3','Healthy target followed by injected HTTP 503','Detect, health-check source, route back, compare',
               'Source serves endpoint; same data; outage measured',
               f'instance=source; 200 records match; observed outage={measure["observed_outage_seconds"]} s',
               'KT3_data.json; KT3_http.json; rollback_timing.json; probes.csv; rollback_route.json')
        event('KT3_PASS',**measure)
        pause('KT3: Show source after rollback; examine evidence; press Enter to stop demo servers')
        summary.update({'status':'PASS','core_tests_passed':3,'additional_tests_passed':2,
                        'records':200,'files':m1['file_count'],'total_bytes':m1['total_bytes'],**measure})
    except Exception as e:
        summary.update({'status':'FAIL','error':repr(e)})
        event('RUN_FAILED',error=repr(e))
        raise
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
        for h in handles:h.close()
        write_json(evidence/'summary.json',summary)
        (evidence/'events.jsonl').write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in events),encoding='utf-8')
        if rows:
            with (evidence/'test_results.csv').open('w',newline='',encoding='utf-8-sig') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        if probes:
            with (evidence/'probes.csv').open('w',newline='',encoding='utf-8-sig') as f:
                w=csv.DictWriter(f,fieldnames=list(probes[0]));w.writeheader();w.writerows(probes)
        print('EVIDENCE:',evidence,flush=True)
        write_json(HERE/'runs'/'latest.json',{'run_dir':str(run),'evidence_dir':str(evidence)})
if __name__=='__main__':main()
''')

put('demo/CHAY_DEMO.cmd', '''
@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python demo.py --interactive
) else (
  py -3 demo.py --interactive
)
pause
''')
put('demo/CHAY_TU_DONG.cmd', '''
@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (python demo.py) else (py -3 demo.py)
pause
''')
put('demo/config/route.source.example.json','{"backend":"http://192.168.56.11:8080"}\n')
put('demo/config/route.target.example.json','{"backend":"http://192.168.56.12:8080"}\n')
put('demo/config/requirements.txt','# Python >= 3.10. No third-party packages are required.\n')

costrows=[
 ('Compute','VM-gio',730,0.05,'USD',36.5),
 ('Luu tru khoi','GiB-thang',80,0.10,'USD',8),
 ('Backup doc lap','GiB-thang',20,0.03,'USD',0.6),
 ('Du lieu truyen ra','GB-thang',100,0.10,'USD',10),
 ('Public IPv4','IP-gio',730,0.005,'USD',3.65),
 ('DNS','goi-thang',1,1,'USD',1),
 ('Log va giam sat','goi-thang',1,5,'USD',5),
 ('Nhan su van hanh Web','gio-thang',4,100000,'VND',400000),
 ('Van hanh he thong giu lai','goi-thang',1,800000,'VND',800000)]
with (OUT/'thiet_ke/chi_phi_gia_dinh.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['hang_muc','don_vi','so_luong','don_gia_gia_dinh','tien_te','thanh_tien','co_so'])
    for r in costrows:w.writerow([*r,'Gia dinh lap ngay 2026-11-16; khong phai bao gia nha cung cap'])
with (OUT/'thiet_ke/tai_nguyen_ip_quyen.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['thanh_phan','vai_tro','cpu','ram','disk','ip_lab','cong','quyen'])
    for r in [('SOURCE','Web nguon','1 vCPU','1 GiB','10 GiB','192.168.56.11','8080','Web chi doc'),
              ('TARGET','Web dich mo phong IaaS','1 vCPU','1 GiB','10 GiB','192.168.56.12','8080','Web chi doc'),
              ('CLIENT/GATEWAY','Dau truy cap on dinh','host','host','< 1 GiB','192.168.56.1','18080','Doi route boi nguoi quan tri')]:w.writerow(r)
for name,fields in [('kiem_thu_VM.csv',['test_id','dau_vao','thao_tac','mong_doi','thuc_te','trang_thai','nguoi_chay','timestamp_UTC','bang_chung']),
 ('dong_gop_ca_nhan.csv',['vai_tro','ho_ten','ma_sv','nhiem_vu','file_tao_sua','bang_chung','loi_da_xu_ly','ngay','xac_nhan'])]:
    with (OUT/'bieu_mau'/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(fields)
        if 'kiem_thu' in name:
            for tid in ['KT1','KT2','KT3']:w.writerow([tid,'','','','','CHUA CHAY','','',''])
        else:
            for role,n,ms in [('SV1','Đặng Thái An','B24DCCC002'),('SV2','Phạm Minh Đức','B24DCCC071'),('SV3','Vũ Tiến Đạt','B24DCCC062'),('SV4','Trần Thị Lan Anh','CHUA BO SUNG')]:w.writerow([role,n,ms,'','','','','',''])
print(OUT)
