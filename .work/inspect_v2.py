from pathlib import Path
from collections import Counter
from docx import Document
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'Báo Cáo BTL CNNT V2.docx';d=Document(p)
def pf(x):
 f=x.paragraph_format
 return {'style':x.style.name,'align':str(f.alignment),'before':str(f.space_before),'after':str(f.space_after),
 'line':str(f.line_spacing),'first_indent':str(f.first_line_indent),'left':str(f.left_indent),'page_break':f.page_break_before}
out={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sections':[], 'styles':[], 'paragraph_samples':[],'run_counts':[]}
for s in d.sections:
 out['sections'].append({k: str(getattr(s,k)) for k in ['page_width','page_height','top_margin','bottom_margin','left_margin','right_margin','header_distance','footer_distance','start_type','different_first_page_header_footer']})
for n in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 try:
  s=d.styles[n];out['styles'].append({'name':n,'font':s.font.name,'size':str(s.font.size),'bold':s.font.bold,'color':str(s.font.color.rgb),'format':str(s.paragraph_format._element.xml)})
 except KeyError:pass
for i,x in enumerate(d.paragraphs):
 if i<18 or x.style.name.startswith('Heading') or x.text.startswith('Hình'):
  if len(out['paragraph_samples'])<85:out['paragraph_samples'].append({'i':i,'text':x.text[:120],**pf(x),'runs':[{'font':r.font.name,'size':str(r.font.size),'bold':r.bold,'color':str(r.font.color.rgb)} for r in x.runs[:2]]})
c=Counter((r.font.name,str(r.font.size),r.bold) for p in d.paragraphs for r in p.runs if r.text)
out['run_counts']=[(str(k),v) for k,v in c.most_common(12)]
with zipfile.ZipFile(p) as z:out['parts']=[{'name':n,'size':len(z.read(n)),'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in z.namelist()]
(ROOT/'.work/v2_evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['parts','paragraph_samples','styles']},ensure_ascii=False,indent=2))
print(json.dumps(out['paragraph_samples'][:24],ensure_ascii=False,indent=2))
