from pathlib import Path
from lxml import etree as E
import zipfile
R=Path(__file__).resolve().parents[1];O=R/'Bo_nop_De10_MPL'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};W='{'+NS['w']+'}'
for name in ['01_Bao_cao_De10_MPL_theo_form_V2.docx','02_Huong_dan_demo.docx','03_Phan_cong_va_phieu_dong_gop.docx']:
 p=O/name
 with zipfile.ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
 d=E.fromstring(parts['word/document.xml'])
 for t in d.xpath('//w:t',namespaces=NS):
  if t.text:t.text=t.text.replace('2.093','2,093').replace('2.125','2,125').replace('Dự phòng biến động','Tổng sau dự phòng')
 if not name.startswith('01_'):
  styles=E.fromstring(parts['word/styles.xml'])
  for tree in [d,styles]:
   for b in tree.xpath('//w:pBdr',namespaces=NS):b.getparent().remove(b)
   for f in tree.xpath('//w:rFonts',namespaces=NS):
    for a in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme','csTheme']:
     f.attrib.pop(W+a,None)
  parts['word/styles.xml']=E.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
 parts['word/document.xml']=E.tostring(d,xml_declaration=True,encoding='UTF-8',standalone=True)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in parts.items():z.writestr(n,b)
print('Display decimals, cost total label, and document title formatting corrected')
