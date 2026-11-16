"""Content rewrite in a byte-preserving copy of V2, with continuous flow."""
from pathlib import Path
from copy import deepcopy
import zipfile,hashlib,json,re
from lxml import etree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Bo_nop_De10_MPL'
SRC=ROOT/'Báo Cáo BTL CNNT V2.docx';CONTENT=OUT/'01_Bao_cao_De10_MPL.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'pr':'http://schemas.openxmlformats.org/package/2006/relationships'}
def w(n):return '{'+NS['w']+'}'+n
def txt(n):return ''.join(n.itertext()) if False else ''.join(n.xpath('.//w:t/text()',namespaces=NS))
def para(text,style='Normal',bold=False,break_before=False):
    pa=ET.Element(w('p'));pp=ET.SubElement(pa,w('pPr'));ET.SubElement(pp,w('pStyle')).set(w('val'),style)
    ET.SubElement(pp,w('pageBreakBefore')).set(w('val'),'1' if break_before else '0')
    if style.startswith('Heading'):ET.SubElement(pp,w('keepNext')).set(w('val'),'1')
    rr=ET.SubElement(pa,w('r'))
    if bold:rp=ET.SubElement(rr,w('rPr'));ET.SubElement(rp,w('b'))
    tt=ET.SubElement(rr,w('t'));tt.text=text;return pa
def ppr(pa):
    el=pa.find(w('pPr'))
    if el is None:el=ET.Element(w('pPr'));pa.insert(0,el)
    return el
def setstyle(pa,style):
    pp=ppr(pa);el=pp.find(w('pStyle'))
    if el is None:el=ET.SubElement(pp,w('pStyle'))
    el.set(w('val'),style)
def settext(pa,text):
    pp=pa.find(w('pPr'))
    for n in list(pa):
        if n is not pp:pa.remove(n)
    rr=ET.SubElement(pa,w('r'));tt=ET.SubElement(rr,w('t'));tt.text=text
def no_break(pa):
    pp=ppr(pa)
    for n in pp.findall(w('sectPr')):pp.remove(n)
    el=pp.find(w('pageBreakBefore'))
    if el is None:el=ET.SubElement(pp,w('pageBreakBefore'))
    el.set(w('val'),'0')

with zipfile.ZipFile(SRC) as z:parts={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(CONTENT) as z:content={n:z.read(n) for n in z.namelist()}
orig=ET.fromstring(parts['word/document.xml']);body=orig.find(w('body'));old=list(body)
sect=deepcopy(body.find(w('sectPr')))
# V2 cover ends with the paragraph containing Hanoi, followed by page break space.
cover=[]
for node in old:
    cover.append(deepcopy(node))
    if 'Hà Nội' in txt(node):break
for node in list(body):body.remove(node)
for node in cover:body.append(node)
# Keep the original cover title as Word Title while preserving its direct appearance.
for node in cover:
    if node.tag==w('p') and 'BÁO CÁO BÀI TẬP LỚN' in txt(node):
        setstyle(node,'Title');pp=ppr(node)
        for k in ['keepNext','keepLines']:
            el=pp.find(w(k))
            if el is None:el=ET.SubElement(pp,w(k))
            el.set(w('val'),'0')

mapping={1:'1.1',2:'1.2',3:'1.3',4:'2.1',5:'2.2',6:'2.3',7:'3.1',8:'4.1',9:'4.2',10:'4.3',11:'5.1',12:'5.2',13:'6.1',14:'6.2',15:'7.1'}
chapters={1:'CHƯƠNG 1  BÀI TOÁN VÀ LỰA CHỌN PHẠM VI',4:'CHƯƠNG 2  MÔ HÌNH CLOUD VÀ KIẾN TRÚC ĐỀ XUẤT',
7:'CHƯƠNG 3  DỰ TOÁN CHI PHÍ',8:'CHƯƠNG 4  KẾ HOẠCH VÀ TRIỂN KHAI DI CHUYỂN',
11:'CHƯƠNG 5  KIỂM THỬ VÀ QUAY LUI',13:'CHƯƠNG 6  KẾT QUẢ VÀ ĐÁNH GIÁ',15:'CHƯƠNG 7  PHÂN CÔNG VÀ KẾT LUẬN'}
chapter_entries=list(chapters.values())
toc=para('MỤC LỤC','Heading1',break_before=True);body.append(toc)
toc_map={}
srcbody=ET.fromstring(content['word/document.xml']).find(w('body'))
blocks={};current=None
for node in srcbody:
    t=txt(node)
    if node.tag==w('p'):
        st=node.find('w:pPr/w:pStyle',NS)
        if st is not None and st.get(w('val'))=='Heading1':
            m=re.match(r'^(\d+) ',t)
            if m:current=int(m.group(1));blocks[current]=[]
    if current is not None and node.tag!=w('sectPr'):blocks[current].append(deepcopy(node))
entries=[]
for num in range(1,16):
    if num in chapters:entries.append((chapters[num],True))
    t=txt(blocks[num][0]);entries.append((mapping[num]+' '+t.split(' ',1)[1],False))
entries.extend([('7.2 Sử dụng AI và trách nhiệm nhóm',False),('7.3 Kết luận',False),('TÀI LIỆU THAM KHẢO',True)])
(ROOT/'.work/toc_entries.json').write_text(json.dumps([x[0] for x in entries],ensure_ascii=False,indent=2),encoding='utf-8')
pagecache=ROOT/'.work/toc_pages.json'
page_values=json.loads(pagecache.read_text(encoding='utf-8')) if pagecache.exists() else {}
for i,(label,is_ch) in enumerate(entries):
    pa=para(label+'\t'+str(page_values.get(label,'…')),'Normal',is_ch)
    pp=ppr(pa);sp=ET.SubElement(pp,w('spacing'));sp.set(w('after'),'40');sp.set(w('line'),'240');sp.set(w('lineRule'),'auto')
    if not is_ch:ET.SubElement(pp,w('ind')).set(w('left'),'220')
    tabs=ET.SubElement(pp,w('tabs'));tb=ET.SubElement(tabs,w('tab'));tb.set(w('val'),'right');tb.set(w('pos'),'8300');tb.set(w('leader'),'dot')
    for rr in pa.findall(w('r')):
        rp=rr.find(w('rPr'))
        if rp is None:rp=ET.SubElement(rr,w('rPr'))
        ET.SubElement(rp,w('sz')).set(w('val'),'24')
        # Real tab node, not a tab character inside w:t.
        tt=rr.find(w('t'));first,last=tt.text.split('\t');tt.text=first;ET.SubElement(rr,w('tab'));ET.SubElement(rr,w('t')).text=last
    body.append(pa)
body.append(para('DANH MỤC HÌNH VÀ BẢNG','Normal',True))
pa=para('Hình 1 Hiện trạng  •  Hình 2 Kiến trúc mục tiêu  •  Hình 3 Luồng chuyển đổi','Normal')
body.append(pa)
body.append(para('Bảng trong báo cáo trình bày hiện trạng, quyết định, mô hình Cloud, tài nguyên, quyền, chi phí, kế hoạch, kiểm thử và kết quả.','Normal'))

# Remap new image relationships without touching reference relationships.
rels=ET.fromstring(parts['word/_rels/document.xml.rels']);newrels=ET.fromstring(content['word/_rels/document.xml.rels'])
ridmap={}
for rel in newrels:
    if rel.get('Type','').endswith('/image'):
        oldrid=rel.get('Id');newrid='rIdMPL'+str(len(ridmap)+1);ridmap[oldrid]=newrid
        orig_target=rel.get('Target');newtarget='media/mpl_'+Path(orig_target).name
        rr=deepcopy(rel);rr.set('Id',newrid);rr.set('Target',newtarget);rels.append(rr)
        parts['word/'+newtarget]=content['word/'+orig_target]

def update_crossrefs(t):
    concise={
    '01_Bao_cao_De10_MPL.docx có 16 trang nội dung chính; 02_Huong_dan_demo.docx liên kết bước chạy với mã file và ca kiểm thử; 03_Phan_cong_va_phieu_dong_gop.docx phục vụ tổ chức và xác nhận đóng góp. Thư mục demo chứa mã, cấu hình và công cụ chạy; thiet_ke chứa sơ đồ, bảng tài nguyên và chi phí; minh_chung chứa dữ liệu gốc.':
    'Bộ nộp gồm báo cáo theo form V2, hướng dẫn demo, phân công và phiếu đóng góp. Thư mục demo chứa mã và cấu hình; thiet_ke chứa sơ đồ cùng bảng tài nguyên, chi phí; minh_chung chứa dữ liệu gốc.',
    'README.md chỉ điểm vào toàn bộ bộ nộp. tai_lieu/Kich_ban_video.md phân bổ 6 phút cho 4 người; video minh họa kèm theo sử dụng ảnh và log từ demo thực. Nhóm nên quay lại theo phân vai để thể hiện thao tác cá nhân. bieu_mau giữ biểu mẫu sạch để chạy lại.':
    'README.md chỉ điểm vào bộ file. Kịch bản video 6 phút và video minh họa gắn các bước với bằng chứng. Nhóm chạy lại theo phân vai và dùng biểu mẫu sạch để ghi kết quả cá nhân.',
    'summary.json tổng hợp kết quả và giới hạn môi trường. source_manifest.json cùng target_manifest.json cho phép kiểm lại toàn bộ file. KT1_data.json, KT2_data.json, KT3_data.json là phản hồi dữ liệu gốc. probes.csv giữ chuỗi HTTP trong thời gian lỗi; events.jsonl và log từng dịch vụ giúp truy vết thao tác.':
    'Hồ sơ gốc gồm summary.json, hai manifest, dữ liệu phản hồi KT1–KT3, probes.csv, events.jsonl và log từng dịch vụ; đủ để kiểm lại dữ liệu, endpoint và chuỗi thời gian.',
    }
    t=concise.get(t,t)
    t=t.replace('Mục 2 và 3','Mục 1.2 và 1.3').replace('Mục 4 đến 6','Mục 2.1 đến 2.3').replace('Mục 8 đến 13','Mục 4.1 đến 6.1')
    t=t.replace('16 trang nội dung chính','nội dung chính trong giới hạn phiếu giao đề')
    t=t.replace('giảng viên và hạn nộp','hạn nộp').replace('lớp, nhóm, giảng viên, hạn nộp','lớp, nhóm, hạn nộp')
    t=t.replace('Báo Cáo BTL CNNT.docx','Báo Cáo BTL CNNT V2.docx')
    return re.sub(r'\b([Mm]ục|Báo cáo) (\d+)(?![\d.])',lambda m:m.group(1)+' '+mapping.get(int(m.group(2)),m.group(2)),t)

for num in range(1,16):
    if num in chapters:
        hp=para(chapters[num],'Heading1');no_break(hp)
        if num==1:
            pp=ppr(hp);pp.find(w('pageBreakBefore')).set(w('val'),'1')
        body.append(hp)
    for idx,node in enumerate(blocks[num]):
        if node.tag==w('p'):
            # Remove artificial page break paragraphs and empty spacing paragraphs.
            if node.xpath('.//w:br[@w:type="page"]',namespaces=NS):continue
            if not txt(node) and not node.xpath('.//w:drawing',namespaces=NS):continue
            no_break(node)
            st=node.find('w:pPr/w:pStyle',NS)
            if idx==0:
                settext(node,mapping[num]+' '+txt(node).split(' ',1)[1]);setstyle(node,'Heading2')
                # Reset generated paragraph typography to V2 named style.
            elif st is not None and st.get(w('val'))=='Heading2':
                text=txt(node);mm=re.match(r'^(\d+)\.(\d+)\s+(.*)',text)
                if mm:settext(node,mapping[num]+'.'+mm.group(2)+' '+mm.group(3))
                setstyle(node,'Heading3')
            for tt in node.xpath('.//w:t',namespaces=NS):tt.text=update_crossrefs(tt.text or '')
            for blip in node.xpath('.//a:blip',namespaces=NS):
                if blip.get('{'+NS['r']+'}embed') in ridmap:blip.set('{'+NS['r']+'}embed',ridmap[blip.get('{'+NS['r']+'}embed')])
            for extent in node.xpath('.//wp:extent | .//a:xfrm/a:ext',namespaces=NS):
                if extent.get('cx'):
                    extent.set('cx',str(round(int(extent.get('cx'))*14.65/16.5)))
                    extent.set('cy',str(round(int(extent.get('cy'))*14.65/16.5)))
            # Preserve figure and caption pairing.
            if node.xpath('.//w:drawing',namespaces=NS):ET.SubElement(ppr(node),w('keepNext')).set(w('val'),'1')
            # Body direct paragraph spacing from intermediate design is removed.
            if st is None or st.get(w('val'))=='Normal':
                pp=ppr(node)
                for sp in pp.findall(w('spacing')):pp.remove(sp)
            for rr in node.findall(w('r')):
                rp=rr.find(w('rPr'))
                if rp is not None:
                    # Keep code font and caption italic; normal body inherits V2 13 pt.
                    font=rp.find(w('rFonts'));is_code=font is not None and font.get(w('ascii'))=='Consolas'
                    if not is_code:
                        for z in rp.findall(w('sz'))+rp.findall(w('rFonts'))+rp.findall(w('color')):rp.remove(z)
            body.append(node)
        elif node.tag==w('tbl'):
            # Scale to V2 text area and use the reference light-grey header treatment.
            for el in node.xpath('.//w:gridCol | .//w:tcW',namespaces=NS):
                if el.get(w('w')):el.set(w('w'),str(round(int(el.get(w('w')))*14.65/16.5)))
            for sh in node.xpath('.//w:shd',namespaces=NS):sh.set(w('fill'),'E7E6E6')
            for tt in node.xpath('.//w:t',namespaces=NS):tt.text=update_crossrefs(tt.text or '')
            body.append(node)

# Place conclusion and disclosure inside chapter 7, followed by references.
tail=blocks[16];cut=next(i for i,n in enumerate(tail) if txt(n).startswith('16.1'))
for node in tail[cut:]:
    if node.tag!=w('p') or not txt(node):continue
    t=txt(node)
    if t.startswith('16.1'):settext(node,'7.2 Sử dụng AI và trách nhiệm nhóm');setstyle(node,'Heading2')
    elif t.startswith('16.2'):settext(node,'7.3 Kết luận');setstyle(node,'Heading2')
    no_break(node)
    for tt in node.xpath('.//w:t',namespaces=NS):tt.text=update_crossrefs(tt.text or '')
    body.append(node)
body.append(para('TÀI LIỆU THAM KHẢO','Heading1'))
no_break(body[-1])
for node in tail[1:cut]:
    if node.tag!=w('p') or not txt(node):continue
    if txt(node).startswith('Các nguồn trực tuyến'):continue
    no_break(node)
    for tt in node.xpath('.//w:t',namespaces=NS):tt.text=update_crossrefs(tt.text or '')
    if txt(node).startswith('[6]'):
        tt=node.xpath('.//w:t',namespaces=NS)[-1];tt.text+=' Nguồn [1]–[5] truy cập ngày 16/11/2026.'
    body.append(node)
body.append(sect)
parts['word/document.xml']=ET.tostring(orig,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['word/_rels/document.xml.rels']=ET.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
# Automatic field refresh flag; no headless save-back of the reference package.
settings=ET.fromstring(parts['word/settings.xml']);up=settings.find(w('updateFields'))
if up is None:up=ET.SubElement(settings,w('updateFields'))
up.set(w('val'),'true');parts['word/settings.xml']=ET.tostring(settings,xml_declaration=True,encoding='UTF-8',standalone=True)
for path in ['word/document.xml','word/_rels/document.xml.rels','word/settings.xml']:pass
dest=OUT/'01_Bao_cao_De10_MPL_theo_form_V2.docx'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)
inventory=json.loads((ROOT/'.work/v2_evidence.json').read_text(encoding='utf-8'))
preserve=[i for i in inventory['parts'] if i['name'] not in ['word/document.xml','word/_rels/document.xml.rels','word/settings.xml']]
assert all(hashlib.sha256(parts[i['name']]).hexdigest()==i['sha256'] for i in preserve)
contract=f'''# V2 report template contract

Reference: {SRC}
SHA256: {inventory['sha256']}
Reference render: .work/v2_render (all pages); style/package inventory: .work/v2_evidence.json.
One section, 8.268 x 11.693 in A4; margins top/bottom 1 in, left/right 1.25 in; header/footer 0.5 in. Different first-page footer, centered PAGE field on subsequent pages.
Cover: retain all source cover paragraphs through Hanoi date, floral border, both logos, institution, advisor Nguyen Xuan Dung, team, title, month, coordinates, direct typography. Cover title gets Word Title role while original direct appearance is retained.
Body: source Times New Roman 13 pt, black, 1.15 line spacing. Source Heading1 16 pt bold, Heading2 14 pt bold, Heading3 13 pt bold, same source paragraph spacing. Source footer and header parts preserved. Table header light grey, explicit grey borders, compact 11 pt text. Diagrams scale to 14.65 cm source text width.
Slots: cover preserved; obsolete editing rules and long source TOC/body replaced; seven source-derived chapter roles carry concise new content; sources last. New images have new relationship IDs and prefixed media filenames. No source image or relationship is removed.
User-authorized deviations: below 20 pages total; continuous chapter flow with pageBreakBefore false to avoid bottom gaps; one concise contents page; body sections rewritten to meet assignment 10; new diagrams and tables replace oversized old content.
Package preserve-only: all original members except word/document.xml, word/_rels/document.xml.rels (additions only), word/settings.xml (updateFields only). All retained members verified byte-for-byte. No headless LibreOffice DOCX save is used.
Fields: PAGE field is retained; contents page references are materialized after rendered pagination. updateFields=true for Word opening.
Fidelity: compare cover and body to V2 rendered patterns; check page count and all final page images; inspect content occupancy, tables and headings; final reference hash must remain unchanged.
'''
(ROOT/'.work/artifact.md').write_text(contract,encoding='utf-8')
print(dest)
