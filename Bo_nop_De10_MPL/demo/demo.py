"""Run KT1-KT3 locally, produce genuine timestamped evidence, then stop own servers."""
import argparse,csv,hashlib,json,platform,socket,subprocess,sys,time,urllib.request,urllib.error,zipfile,shutil
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent/'tools'))
from lab import seed,manifest,pack,unpack,write_json,route
HERE=Path(__file__).resolve().parent
def now(): return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
def main():
    p=argparse.ArgumentParser(); p.add_argument('--interactive',action='store_true')
    p.add_argument('--base-port',type=int,default=18080)
    p.add_argument('--engine',choices=['local','docker'],default='local')
    p.add_argument('--docker-bin',default='docker')
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
    routefile=run/'route.json'; processes=[]; handles=[]; rows=[]; probes=[]; events=[]; containers=[]
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
        cmd=[sys.executable,str(HERE/'app'/script),*args]
        if a.engine=='docker' and script=='service.py':
            cname='mpl-'+stamp.lower().replace('_','-')+'-'+name
            containers.append(cname)
            port=base+1 if name=='source' else base+2
            cmd=[a.docker_bin,'run','--rm','--name',cname,'--label','mpl.demo='+stamp,
                 '-p',f'127.0.0.1:{port}:8080','-v',str(HERE/'app')+':/app:ro',
                 '-v',str(run/name)+':/data:ro','python:3.12-slim','python','-u','/app/service.py',
                 '--root','/data/content','--instance',name,'--host','0.0.0.0','--port','8080']
        processes.append(subprocess.Popen(cmd,stdout=h,stderr=subprocess.STDOUT,cwd=HERE))
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
    summary={'run_id':stamp,'test_mode':('two Linux containers, separate network/process namespaces, same Docker host' if a.engine=='docker' else 'two isolated directories and server processes on one host'),
             'cloud_deployed':False,'vm_tested':False,'python':sys.version,'platform':platform.platform(),
             'client_endpoint':endpoint,'source_endpoint':source,'target_endpoint':target}
    write_json(evidence/'environment.json',summary)
    try:
        if a.engine=='docker':
            subprocess.run([a.docker_bin,'image','inspect','python:3.12-slim'],check=True,stdout=subprocess.DEVNULL)
            raw=subprocess.check_output([a.docker_bin,'version','--format','{{json .}}'],text=True)
            (evidence/'docker_version.json').write_text(raw,encoding='utf-8')
        launch('service.py',['--root',str(src),'--instance','source','--port',str(base+1)],'source')
        launch('service.py',['--root',str(dst),'--instance','target','--port',str(base+2)],'target')
        wait(source,'source'); route(routefile,source)
        if containers:
            raw=subprocess.check_output([a.docker_bin,'inspect',*containers],text=True)
            (evidence/'container_inspect.json').write_text(raw,encoding='utf-8')
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
        for cname in containers:
            subprocess.run([a.docker_bin,'stop','--time','1',cname],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
