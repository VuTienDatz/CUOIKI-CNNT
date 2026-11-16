"""Collect timestamped HTTP probes for manual two-VM rollback."""
import argparse,csv,json,time,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
def main():
    p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--seconds',type=float,default=60)
    p.add_argument('--interval',type=float,default=.1);p.add_argument('--out',default='probes_vm.csv');a=p.parse_args()
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[];end=time.monotonic()+a.seconds
    bad=None;recovered=None;lastgood=None
    while time.monotonic()<end:
        instance=''
        try:
            with op.open(a.url,timeout=1) as r:status=r.code;instance=r.headers.get('X-MPL-Instance','')
        except urllib.error.HTTPError as e:status=e.code
        except Exception:status=0
        mono=time.monotonic();stamp=datetime.now(timezone.utc).isoformat(timespec='milliseconds')
        row={'timestamp_utc':stamp,'monotonic_seconds':mono,'status':status,'instance':instance};rows.append(row)
        if status!=200 and bad is None:bad=row
        if bad is None and status==200:lastgood=row
        if bad and recovered is None and status==200:recovered=row
        print(stamp,status,instance,flush=True);time.sleep(a.interval)
    out=Path(a.out)
    with out.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'url':a.url,'samples':len(rows),'first_failure':bad,'first_recovery':recovered,
             'observed_outage_seconds':(recovered['monotonic_seconds']-bad['monotonic_seconds']) if bad and recovered else None,
             'upper_bound_seconds':(recovered['monotonic_seconds']-lastgood['monotonic_seconds']) if recovered and lastgood else None,
             'status':'RECOVERY_OBSERVED' if recovered else 'NOT_VERIFIED',
             'scope':'HTTP health recovery only; verify actual data separately'}
    out.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
if __name__=='__main__':main()
