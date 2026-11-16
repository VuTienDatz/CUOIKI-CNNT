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
