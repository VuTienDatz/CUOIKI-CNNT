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
