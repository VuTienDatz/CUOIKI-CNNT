from pathlib import Path
import sys,json,re
import pdfplumber
p=Path(sys.argv[1]);result=[]
with pdfplumber.open(p) as pdf:
 for i,page in enumerate(pdf.pages,1):
  words=[w for w in page.extract_words() if w['top']<page.height-45]
  text=page.extract_text() or ''
  result.append({'page':i,'words':len(words),'body_bottom':round(max((w['bottom'] for w in words),default=0),1),
    'bottom_gap_points':round(page.height-72-max((w['bottom'] for w in words),default=0),1),
    'first':text[:100].replace('\n',' | '),'last':text[-100:].replace('\n',' | ')})
print(json.dumps(result,ensure_ascii=False,indent=2))
out=p.parent/'page_text.json'
with pdfplumber.open(p) as pdf:out.write_text(json.dumps([page.extract_text() or '' for page in pdf.pages],ensure_ascii=False,indent=2),encoding='utf-8')
