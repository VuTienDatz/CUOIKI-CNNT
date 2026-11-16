from pathlib import Path
import re,json,pdfplumber,sys
root=Path(__file__).resolve().parents[1]
entries=json.loads((root/'.work/toc_entries.json').read_text(encoding='utf-8'))
def norm(s):return re.sub(r'\s+',' ',s).strip()
with pdfplumber.open(sys.argv[1]) as pdf:texts=[norm(p.extract_text() or '') for p in pdf.pages]
out={}
for e in entries:
    for i,t in enumerate(texts[2:],3):
        if norm(e) in t:out[e]=i;break
    if e not in out:print('MISSING',e)
(root/'.work/toc_pages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOC entries',len(out),'of',len(entries))
