from pathlib import Path
import json, shutil, csv, sys, textwrap
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'Bo_nop_De10_MPL'
latest=json.loads((OUT/'demo/runs/latest.json').read_text())
E=Path(latest['evidence_dir']); S=json.loads((E/'summary.json').read_text())
for folder,label in [(p,'demo_docker' if 'Linux containers' in json.loads((p/'evidence/summary.json').read_text())['test_mode'] else 'demo_local') for p in (OUT/'demo/runs').iterdir() if p.is_dir() and (p/'evidence/summary.json').exists()]:
    shutil.copytree(folder/'evidence',OUT/'minh_chung'/label,dirs_exist_ok=True)
M=json.loads((E/'source_manifest.json').read_text()); outage=S['observed_outage_seconds']; upper=S['upper_bound_seconds']

def diagram(name,kind):
    im=Image.new('RGB',(1500,690),'white'); dr=ImageDraw.Draw(im)
    fontpath='C:/Windows/Fonts/arial.ttf'; boldpath='C:/Windows/Fonts/arialbd.ttf'
    f=ImageFont.truetype(fontpath,25); b=ImageFont.truetype(boldpath,28)
    def box(x,y,w,h,title,lines,fill='#EDF2F6'):
        dr.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=fill,outline='#3E5265',width=2)
        dr.text((x+18,y+15),title,font=b,fill='#10263B')
        for i,line in enumerate(lines):dr.text((x+18,y+58+i*34),line,font=f,fill='#142B40')
    def arrow(a,z,label=''):
        dr.line((a,z),fill='#395D7E',width=4)
        import math
        angle=math.atan2(z[1]-a[1],z[0]-a[0]); L=16
        p1=(z[0]-L*math.cos(angle-.5),z[1]-L*math.sin(angle-.5));p2=(z[0]-L*math.cos(angle+.5),z[1]-L*math.sin(angle+.5))
        dr.polygon([z,p1,p2],fill='#395D7E')
        if label:dr.text(((a[0]+z[0])/2-65,(a[1]+z[1])/2-35),label,font=f,fill='#10263B')
    if kind=='asis':
        dr.text((35,20),'HIỆN TRẠNG GIẢ ĐỊNH CỦA MPL',font=b,fill='black')
        box(40,95,370,140,'Người dùng công khai',['Trình duyệt Internet'])
        box(650,95,750,170,'S1 Web công khai tại trụ sở',['Nội dung tĩnh và bản trích xuất đã loại thông tin nhạy cảm','HTTP HTTPS theo thiết kế'])
        box(40,410,370,150,'Nhân viên 3 kho',['HN  HP  BN','Truy cập nội bộ qua VPN'])
        box(520,410,420,170,'S2 Dữ liệu nghiệp vụ',['MySQL và ứng dụng nội bộ','Không mở trực tiếp ra Internet'])
        box(1010,410,420,170,'S3 Chia sẻ tập tin',['SMB chứng từ nội bộ','Backup tách bản vận hành'])
        arrow((410,165),(650,165),'Truy cập')
        arrow((410,480),(520,480),'VPN')
        arrow((940,490),(1010,490),'Tập tin')
        arrow((735,410),(900,265),'Xuất bản đã lọc')
        dr.text((550,620),'S2 và S3 có quan hệ nghiệp vụ  Web không truy vấn DB trực tiếp',font=f,fill='black')
    elif kind=='tobe':
        dr.text((35,20),'KIẾN TRÚC ĐỀ XUẤT SAU CHUYỂN ĐỔI',font=b,fill='black')
        box(30,110,320,140,'Người dùng Internet',['Tên truy cập Web ổn định'])
        box(570,100,850,185,'Cloud IaaS theo thiết kế',['1 VM Web  2 vCPU  4 GiB RAM  80 GiB đĩa','HTTPS 443  quyền đọc nội dung  giám sát dịch vụ','Backup độc lập 20 GiB  chưa triển khai Cloud thật'])
        box(30,420,400,150,'Nhân viên 3 kho',['VPN về trụ sở','Nghiệp vụ và chia sẻ nội bộ'])
        box(560,410,430,170,'Giữ tại trụ sở',['S2 dữ liệu nghiệp vụ','S3 chia sẻ tập tin nội bộ'])
        box(1070,410,350,170,'Nguồn Web cũ',['Giữ trong kỳ quay lui','Đóng thay đổi xuất bản'])
        arrow((350,175),(570,175),'DNS HTTPS')
        arrow((430,490),(560,490),'VPN')
        arrow((820,410),(900,285),'Xuất bản qua SSH')
        dr.text((560,620),'Không mở DB hoặc SMB giữa Internet và mạng nội bộ',font=f,fill='black')
    else:
        dr.text((35,20),'LUỒNG DEMO VÀ ĐIỂM QUAY LUI',font=b,fill='black')
        box(40,100,390,150,'KT1 Nguồn hoạt động',['200 bản ghi  3 tập tin','Lưu manifest SHA 256'])
        box(555,100,390,150,'Đóng gói và đối chiếu',['transfer.zip sang đích','Sai dữ liệu thì dừng chuyển'])
        box(1070,100,390,150,'KT2 Chuyển hướng',['Đích khỏe và dữ liệu khớp','route.json chọn target'])
        box(1070,430,390,150,'Giả lập đích lỗi',['Đích trả HTTP 503','Ghi mốc phát hiện lỗi'])
        box(555,430,390,150,'KT3 Quay về nguồn',['Kiểm tra nguồn còn khỏe','Đổi route  đối chiếu  đo giờ'])
        box(40,430,390,150,'Kết thúc và lưu bằng chứng',['CSV kiểm thử  log có giờ','Dừng các tiến trình của demo'])
        arrow((430,175),(555,175));arrow((945,175),(1070,175));arrow((1260,250),(1260,430))
        arrow((1070,505),(945,505));arrow((555,505),(430,505))
    im.save(OUT/'thiet_ke'/name)
diagram('01_AsIs.png','asis');diagram('02_ToBe.png','tobe');diagram('03_Migration.png','flow')
(OUT/'thiet_ke/so_do.mmd').write_text('''flowchart LR
 U[Người dùng] --> G[Đầu truy cập ổn định]
 G -->|trước chuyển đổi hoặc quay lui| S[Web nguồn]
 G -->|sau chuyển đổi| T[Web đích mô phỏng IaaS]
 DB[Dữ liệu nghiệp vụ giữ nội bộ] -->|bản xuất đã lọc| S
 S -->|archive và SHA256| T
 DB --- F[Chia sẻ tập tin giữ nội bộ]
''',encoding='utf-8')

def setup():
    d=Document(); sec=d.sections[0]; sec.page_width=Cm(21);sec.page_height=Cm(29.7)
    sec.top_margin=Cm(2);sec.bottom_margin=Cm(2);sec.left_margin=Cm(2.3);sec.right_margin=Cm(2)
    sec.header_distance=Cm(.8);sec.footer_distance=Cm(.8)
    for sn,size in [('Normal',12),('Title',23),('Subtitle',13),('Heading 1',16),('Heading 2',13),('Heading 3',12)]:
        st=d.styles[sn]; st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
        st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Times New Roman')
        pf=st.paragraph_format;pf.space_after=Pt(6);pf.line_spacing=1.12
        if sn.startswith('Heading'):pf.space_before=Pt(10);pf.keep_with_next=True
    d.styles['Normal'].paragraph_format.widow_control=True
    return d
def p(d,text,bold=False):
    pa=d.add_paragraph();r=pa.add_run(text);r.bold=bold;return pa
def h(d,text,level=2):return d.add_paragraph(text,'Heading '+str(level))
def title(d,text):return d.add_paragraph(text,'Title')
def page(d,name):
    d.add_page_break();h(d,name,1)
def table(d,headers,rows,widths=None,size=11):
    t=d.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths:
        for c,w in zip(t.columns,widths):c.width=Cm(w)
    for c,tx in zip(t.rows[0].cells,headers):c.text=tx
    for row in rows:
        cells=t.add_row().cells
        for c,tx in zip(cells,row):c.text=str(tx)
    for i,row in enumerate(t.rows):
        trPr=row._tr.get_or_add_trPr()
        cant=OxmlElement('w:cantSplit');trPr.append(cant)
        if i==0:repeat=OxmlElement('w:tblHeader');trPr.append(repeat)
        for j,c in enumerate(row.cells):
            if widths:c.width=Cm(widths[j])
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcPr=c._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:w'),'85');el.set(qn('w:type'),'dxa');mar.append(el)
            tcPr.append(mar)
            borders=OxmlElement('w:tcBorders')
            for side in ['top','left','bottom','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
            tcPr.append(borders)
            if i==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E7EDF3');tcPr.append(sh)
            for pa in c.paragraphs:
                pa.paragraph_format.space_after=Pt(2);pa.paragraph_format.line_spacing=1.05
                for r in pa.runs:r.font.size=Pt(size);r.bold=i==0;r.font.color.rgb=RGBColor(0,0,0)
    d.add_paragraph().paragraph_format.space_after=Pt(1)
    return t
def pic(d,name,caption):
    pa=d.add_paragraph();pa.add_run().add_picture(str(OUT/'thiet_ke'/name),width=Cm(16.5));pa.paragraph_format.space_after=Pt(2)
    cap=p(d,caption);cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in cap.runs:r.italic=True;r.font.size=Pt(10)
def code(d,txt):
    for line in textwrap.dedent(txt).strip().splitlines():
        pa=d.add_paragraph();pa.paragraph_format.space_after=Pt(2);pa.paragraph_format.line_spacing=1.0
        r=pa.add_run(line);r.font.name='Consolas';r.font.size=Pt(9)
def footer(section,start=None):
    section.footer.is_linked_to_previous=False
    pa=section.footer.paragraphs[0];pa.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=pa.add_run();field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');r._r.addnext(field)
    if start:
        el=OxmlElement('w:pgNumType');el.set(qn('w:start'),str(start));section._sectPr.append(el)

R=setup()
pa=p(R,'BÁO CÁO BÀI TẬP LỚN',True);pa.alignment=1
p(R,'').paragraph_format.space_after=Pt(35)
for tx in ['Thiết kế giải pháp chuyển đổi','hạ tầng máy chủ doanh nghiệp lên Cloud']:
    pa=title(R,tx);pa.alignment=1
pa=p(R,'Phiếu giao đề 10   Doanh nghiệp giả định MPL Logistics');pa.alignment=1
p(R,'').paragraph_format.space_after=Pt(30)
table(R,['Vai trò','Thành viên','Mã sinh viên'],[
 ('SV1','Đặng Thái An','B24DCCC002'),('SV2','Phạm Minh Đức','B24DCCC071'),
 ('SV3','Vũ Tiến Đạt','B24DCCC062'),('SV4','Trần Thị Lan Anh','[Bổ sung]')],[2,8,6.5],12)
p(R,'Lớp  [Bổ sung]                       Nhóm  [Bổ sung]')
p(R,'Giảng viên  [Bổ sung]                 Hạn nộp  [Bổ sung]')
p(R,'Tháng 11 năm 2026').alignment=1
page(R,'Mục lục')
outline=[
 'Bài toán và yêu cầu của phiếu giao đề','Hiện trạng và phụ thuộc giữa ba dịch vụ','Lựa chọn dịch vụ chuyển đổi và giữ lại',
 'So sánh IaaS PaaS và SaaS','Kiến trúc mục tiêu và tài nguyên','Thiết kế mạng quyền truy cập và sao lưu',
 'Dự toán chi phí và các giả định','Kế hoạch chuyển đổi và điều kiện quyết định','Triển khai hai môi trường thử nghiệm',
 'Di chuyển và đối chiếu dữ liệu','Chuyển hướng truy cập và quay lui','Kịch bản kiểm thử nghiệm thu',
 'Kết quả thực nghiệm và bằng chứng','Đánh giá giải pháp và giới hạn','Phân công và hồ sơ bàn giao','Tài liệu tham khảo và kết luận']
for i,tx in enumerate(outline,1):p(R,f'{i:02d}   {tx}    {i}')
sec=R.add_section(WD_SECTION_START.NEW_PAGE);footer(sec,1)
h(R,'1 Bài toán và yêu cầu của phiếu giao đề',1)
p(R,'MPL Logistics là doanh nghiệp giả định có Web công khai, dịch vụ chia sẻ tập tin và dữ liệu nghiệp vụ trên máy chủ tại trụ sở. Giải pháp đề xuất chuyển Web lên IaaS, giữ hai dịch vụ nội bộ và kiểm chứng quy trình chuyển đổi bằng hai môi trường thử nghiệm. Mục tiêu là bảo toàn dữ liệu, đổi nơi phục vụ truy cập và quay lui được khi đích lỗi.')
h(R,'1.1 Phạm vi và giả định')
p(R,'Ba kho HN, HP, BN và 80 nhân viên là bối cảnh giả định kế thừa từ báo cáo tham khảo. Phạm vi được thu gọn về một Web chỉ đọc, không triển khai WMS hoàn chỉnh, không chuyển cơ sở dữ liệu nghiệp vụ và không xây dựng dự phòng nhiều vùng. Thông số doanh nghiệp và dự toán là giả định thiết kế; kết quả ở mục 13 là số đo của demo đã chạy.')
h(R,'1.2 Đối chiếu yêu cầu bắt buộc')
table(R,['Yêu cầu','Nội dung đáp ứng','Vị trí'],[
 ('YC1','Hiện trạng 3 dịch vụ, phụ thuộc, chọn chuyển và giữ lại','Mục 2 và 3'),
 ('YC2','Sơ đồ trước sau; so sánh 3 mô hình theo 4 tiêu chí','Mục 4 đến 6'),
 ('YC3','Bảng chi phí có đơn vị, giả định, đủ lưu trữ, truyền, backup và vận hành','Mục 7'),
 ('YC4','Demo nguồn sang đích, dữ liệu, đổi truy cập, quay lui','Mục 8 đến 13'),
 ('Hồ sơ chung','Mã nguồn, README, hướng dẫn, bảng kiểm thử, video và phiếu đóng góp','Mục 15 và bộ file kèm theo')],[1.7,11.6,3.2])
p(R,'Chỉ dùng dữ liệu tổng hợp và dịch vụ cục bộ. Hai container hoặc hai VM đích trong thực hành đều chỉ mô phỏng nơi đặt dịch vụ; không được diễn giải thành triển khai Cloud thật. Bản chạy nhanh bằng hai tiến trình giúp tập thao tác trước khi chạy hai môi trường cô lập.')

page(R,'2 Hiện trạng và phụ thuộc giữa ba dịch vụ')
table(R,['Dịch vụ','Hiện trạng giả định','Phụ thuộc và dữ liệu'],[
 ('S1 Web công khai','4 lõi CPU, 8 GiB RAM, 120 GiB đĩa; nội dung Web tĩnh','Đọc bản xuất đã lọc từ S2; không gọi trực tiếp DB'),
 ('S2 Dữ liệu nghiệp vụ','8 lõi CPU, 16 GiB RAM, 400 GiB đĩa; MySQL và nghiệp vụ nội bộ','Nhân viên qua VPN; liên kết mã chứng từ với S3'),
 ('S3 Chia sẻ tập tin','4 lõi CPU, 8 GiB RAM, 1 TiB đĩa; SMB và chứng từ','Tài khoản nội bộ; phục vụ S2 và nhân viên')],[3.2,6.1,7.2])
pic(R,'01_AsIs.png','Hình 1  Kiến trúc trước chuyển đổi  Các thông số là giả định')
p(R,'Luồng xuất bản chỉ chọn trường mã vận đơn, kho, trạng thái và thời điểm công bố. Web không chứa tên khách hàng, địa chỉ, tài khoản hay thông tin thanh toán. Bản xuất là dữ liệu công khai tách khỏi dữ liệu nghiệp vụ; không sao chép toàn bộ MySQL lên Web.')
p(R,'Điểm yếu hiện trạng là Web phụ thuộc phòng máy và đường truyền trụ sở; một sự cố nguồn hoặc mạng tại đây có thể làm Web ngừng phục vụ. S2 và S3 vẫn có rủi ro riêng, cần tiếp tục sao lưu và quản trị dù Web được chuyển đi.')

page(R,'3 Lựa chọn dịch vụ chuyển đổi và giữ lại')
h(R,'3.1 Tiêu chí quyết định')
p(R,'Nhóm ưu tiên dịch vụ có ít phụ thuộc thời gian thực, dữ liệu có thể công khai, dễ kiểm tra tính toàn vẹn và dễ quay lui. Đồng thời xét mức thay đổi ứng dụng, công sức quản trị, băng thông và chi phí vận hành đầy đủ. Không coi yêu cầu dùng Cloud là lý do để di chuyển mọi dịch vụ.')
table(R,['Dịch vụ','Quyết định','Căn cứ và điều kiện'],[
 ('Web công khai','Chuyển sang IaaS','Nội dung chỉ đọc; độc lập DB; đóng gói được; kiểm tra bằng hash; giữ nguồn cũ để quay lui'),
 ('Dữ liệu nghiệp vụ','Giữ tại trụ sở','Dữ liệu hạn chế, có giao dịch ghi; chuyển đòi hỏi kiểm soát nhất quán và đồng bộ ngoài phạm vi demo'),
 ('Chia sẻ tập tin','Giữ tại trụ sở','Nhân viên dùng nội bộ; liên kết chứng từ với nghiệp vụ; tránh công khai SMB hoặc đổi quy trình người dùng')],[3.2,3.4,9.9])
h(R,'3.2 Chiến lược áp dụng')
p(R,'Dùng Rehost ở phạm vi dịch vụ Web: giữ nội dung và hành vi HTTP, dựng lại cấu hình phục vụ ở đích rồi chuyển đường truy cập. Demo không chuyển nguyên ảnh đĩa máy vật lý; nó kiểm chứng việc chuyển một dịch vụ giữa hai môi trường. Retain áp dụng cho S2 và S3. Cách lựa chọn này phù hợp hướng dẫn phân loại chiến lược của AWS [3].')
h(R,'3.3 Rủi ro cần xử lý trước khi chuyển')
p(R,'Nếu Web phát sinh API ghi hoặc phải gọi DB nội bộ, quyết định này phải đánh giá lại. Nếu manifest lệch, đích chưa khỏe hoặc nguồn không còn phục vụ được thì chưa cho chuyển hướng. Trong thời gian thử và quay lui, đóng thay đổi bản xuất để tránh hai bản Web mang dữ liệu khác nhau.')
p(R,'Chủ trì khảo sát bàn giao danh mục phụ thuộc cho người dựng đích và người di chuyển. Khi thay tên tệp, đường dẫn hay cổng, phải cập nhật đồng thời bảng tài nguyên, cấu hình, hướng dẫn và ca kiểm thử.')

page(R,'4 So sánh IaaS PaaS và SaaS')
p(R,'Theo NIST SP 800-145 [1], ba mô hình khác nhau ở năng lực cung cấp và phần người dùng kiểm soát. So sánh dưới đây áp dụng cho Web của MPL, không mặc định một mô hình luôn tốt hơn các mô hình còn lại.')
table(R,['Tiêu chí','IaaS','PaaS','SaaS'],[
 ('Quyền kiểm soát','Quản trị OS, Web server, thư mục và một phần cấu hình mạng','Quản trị mã, nội dung và cấu hình ứng dụng; nền tảng quản lý OS','Cấu hình người dùng và tính năng do sản phẩm cho phép'),
 ('Tài nguyên','Chọn vCPU, RAM, đĩa và mạng; tự đo để cấp phát phù hợp','Chọn gói hoặc mức chạy; chịu giới hạn runtime, storage','Dùng hạn mức tài khoản, dung lượng hoặc nghiệp vụ'),
 ('Bảo mật','Tự vá OS, cấp quyền, cấu hình firewall, TLS và backup','Tự bảo vệ mã, dữ liệu, định danh; nhà cung cấp quản nền','Quản trị người dùng, chia sẻ, dữ liệu và cấu hình thuê bao'),
 ('Vận hành','Công sức lớn hơn; tự giám sát, phục hồi và cập nhật','Giảm quản trị nền; phụ thuộc giao diện và khả năng nền tảng','Ít quản trị hạ tầng; phụ thuộc tính năng và xuất dữ liệu')],[2.5,4.7,4.7,4.6],10.5)
h(R,'4.1 Lựa chọn IaaS có điều kiện')
p(R,'IaaS giúp nhóm thể hiện rõ cấp tài nguyên, quyền OS, chuyển tập tin và cấu hình Web trong phạm vi học phần. Đánh đổi là MPL vẫn phải vận hành và sao lưu máy ảo. PaaS là lựa chọn hợp lý khi Web tương thích nền tảng và muốn giảm công việc quản trị; SaaS cần xem xét nếu có sản phẩm thay thế đúng nhu cầu.')
p(R,'Nhà cung cấp bảo vệ phần hạ tầng do họ quản lý; doanh nghiệp vẫn chịu trách nhiệm dữ liệu, tài khoản và cấu hình thuộc quyền mình. Với EC2, khách hàng còn quản lý hệ điều hành và ứng dụng [2]. Chuyển lên IaaS không tự tạo HA hoặc tự bảo vệ dữ liệu.')

page(R,'5 Kiến trúc mục tiêu và tài nguyên')
pic(R,'02_ToBe.png','Hình 2  Kiến trúc mục tiêu  Cloud là phương án thiết kế chưa triển khai')
table(R,['Thành phần','Tài nguyên đề xuất','Lý do và cách xác nhận'],[
 ('VM Web IaaS','1 VM; 2 vCPU; 4 GiB RAM; 80 GiB đĩa','Cấu hình khởi điểm cho Web tĩnh; đo CPU RAM dung lượng trước tăng cấp'),
 ('Lưu trữ Web','OS 20 GiB; nội dung 10 GiB; log tạm 10 GiB; dự phòng 40 GiB','Tổng 80 GiB; dữ liệu thật phải đo riêng'),
 ('Backup độc lập','20 GiB lưu trữ bản sao theo giả định chi phí','Nội dung cộng cấu hình nén; xác nhận đủ lịch giữ bằng dung lượng thực tế'),
 ('Hai môi trường lab','Mỗi VM 1 vCPU, 1 GiB RAM, 10 GiB đĩa hoặc hai container','Dữ liệu chỉ 27.882 byte; không đại diện tải sản xuất')],[3.3,6.3,6.9])
p(R,'Theo giả định, Web có 10 GiB dữ liệu và tăng 0,5 GiB/tháng. Sau 12 tháng: 10 + 12 × 0,5 = 16 GiB; phần dự phòng đĩa vẫn cần kiểm tra cùng log và OS. Dung lượng backup không suy từ dung lượng đĩa đã cấp; cần tính số phiên bản và tỷ lệ thay đổi.')
p(R,'Một VM là điểm lỗi đơn, chấp nhận trong phạm vi bài. Chưa có load balancer, nhiều AZ hay cam kết SLA. Cần bổ sung thiết kế và chi phí khi yêu cầu sẵn sàng thay đổi.')

page(R,'6 Thiết kế mạng quyền truy cập và sao lưu')
table(R,['Thành phần lab','Hai VM thủ công','Bản tự động trên cùng máy'],[
 ('CLIENT và gateway','192.168.56.1:18080','127.0.0.1:18080'),
 ('SOURCE','192.168.56.11:8080','127.0.0.1:18081'),
 ('TARGET','192.168.56.12:8080','127.0.0.1:18082'),
 ('Mạng','Host-only 192.168.56.0/24; NAT riêng nếu cần cài gói','Hai container có namespace riêng; cổng công bố chỉ trên loopback')],[3.3,6.2,7])
table(R,['Chủ thể','Quyền cho phép','Quyền từ chối'],[
 ('Người xem Web','GET nội dung, dữ liệu công khai và health trong lab','Ghi dữ liệu; đọc file ngoài danh sách URL'),
 ('Tiến trình Web','Đọc thư mục nội dung; ghi log stdout','Sửa nội dung khi chạy container volume chỉ đọc'),
 ('Người triển khai','Đóng gói, kiểm hash, thay route qua quyền quản trị máy lab','Không nhận thông tin nghiệp vụ nhạy cảm để đưa lên Web'),
 ('Nhân viên nội bộ','S2 S3 theo tài khoản và VPN hiện hữu','Internet không được truy cập trực tiếp DB hoặc SMB')],[3.3,6.8,6.4])
p(R,'Phương án thực tế mở HTTPS 443 cho người xem, chỉ cho IP quản trị truy cập SSH, dùng khóa và tài khoản riêng. Lab dùng HTTP trên mạng được phép để quan sát; máy chủ Python là công cụ học tập, không phải cấu hình đưa thẳng lên Internet [4].')
p(R,'Đề xuất backup nội dung và cấu hình hằng ngày, giữ 7 bản ngày và 4 bản tuần trong kho tách nơi vận hành; thử phục hồi định kỳ. Demo transfer.zip chỉ chứng minh bản sao cho lần chuyển đổi. Lịch backup tự động, mã hóa và chính sách giữ bản là thiết kế chưa được kiểm chứng ở lab.')

page(R,'7 Dự toán chi phí và các giả định')
p(R,'Dự toán cho Web IaaS một VM hoạt động 730 giờ/tháng và hai dịch vụ giữ nội bộ. Toàn bộ đơn giá dưới đây là giả định bài tập lập ngày 16/11/2026, không phải báo giá AWS. Quy ước 1 USD = 25.000 VND chỉ để tính toán; trước triển khai cần thay bằng báo giá đúng vùng, cấu hình và ngày. [5] chỉ tham khảo cấu trúc khoản phí.')
table(R,['Hạng mục','Lượng mỗi tháng','Đơn giá giả định','Thành tiền'],[
 ('Compute','730 VM giờ','0,05 USD/VM giờ','36,50 USD'),
 ('Đĩa khối','80 GiB tháng','0,10 USD/GiB tháng','8,00 USD'),
 ('Backup độc lập','20 GiB tháng','0,03 USD/GiB tháng','0,60 USD'),
 ('Truyền ra Internet','100 GB','0,10 USD/GB','10,00 USD'),
 ('Public IPv4','730 IP giờ','0,005 USD/IP giờ','3,65 USD'),
 ('DNS','1 gói tháng','1 USD/gói','1,00 USD'),
 ('Log và giám sát','1 gói tháng','5 USD/gói','5,00 USD'),
 ('Tổng dịch vụ Cloud','64,75 USD','25.000 VND/USD','1.618.750 VND'),
 ('Vận hành Web','4 giờ','100.000 VND/giờ','400.000 VND'),
 ('Hệ thống giữ lại','1 gói tháng','800.000 VND/gói','800.000 VND'),
 ('Cộng trước dự phòng','','','2.818.750 VND'),
 ('Dự phòng biến động','10% cộng trước','281.875 VND','3.100.625 VND')],[4.5,3.7,4.5,3.8],10.5)
p(R,'Chi phí chuyển một lần 1.200.000 VND gồm 8 giờ kỹ thuật × 100.000 = 800.000; chạy song song 300.000; quỹ truyền một lần 100.000. Tổng năm đầu = 12 × 3.100.625 + 1.200.000 = 38.407.500 VND, trước thuế. Không cộng lại 8 giờ này vào 4 giờ vận hành định kỳ.')
p(R,'Mốc giữ nguyên nội bộ giả định: Web 1.150.000 + S2 S3 800.000 = 1.950.000 VND/tháng, hay 23.400.000 VND/năm. Phương án Cloud cao hơn 15.007.500 VND trong năm đầu theo giả định này. Không kết luận tiết kiệm. Chưa gồm VAT, hỗ trợ trả phí, HA, giấy phép thương mại và nâng cấp WAN; lab chạy cục bộ không phát sinh hóa đơn Cloud.')

page(R,'8 Kế hoạch chuyển đổi và điều kiện quyết định')
pic(R,'03_Migration.png','Hình 3  Luồng di chuyển và quay lui gắn với KT1 KT2 KT3')
table(R,['Giai đoạn','Đầu ra và người phụ trách','Điều kiện chuyển tiếp'],[
 ('Chuẩn bị','SV1 chốt phạm vi; SV2 dựng đích và mạng','Nguồn khỏe; đích đúng phiên bản; chưa đổi route'),
 ('KT1','SV3 ghi dữ liệu nguồn; SV4 xác nhận baseline','200 ID duy nhất; manifest 3 file; mốc giờ lưu được'),
 ('Di chuyển','SV3 tạo archive và kiểm toàn bộ hash','Mọi file khớp; đích trả health 200'),
 ('KT2','SV2 SV3 chuyển route; SV4 truy cập từ gateway','Instance target; dữ liệu đúng baseline'),
 ('KT3 và kết thúc','SV4 tạo lỗi, quay lui; cả nhóm kiểm tra và lưu log','Instance source; dữ liệu khớp; có thời gian gián đoạn')],[2.7,7.5,6.3])
p(R,'Go khi dữ liệu khớp toàn bộ, đích khỏe, đường truy cập đã kiểm tra và nguồn còn có thể quay lui. No-Go khi thiếu tệp, sai hash, sai số bản ghi, lỗi HTTP hoặc thiếu người xử lý. Không dùng việc trang chủ hiển thị được để thay thế kiểm toàn bộ dữ liệu.')
p(R,'Khi đích lỗi sau chuyển đổi, ưu tiên xác nhận nguồn khỏe rồi đổi route. Vì demo là chỉ đọc và đóng thay đổi xuất bản, không có giao dịch ghi mới ở đích cần đồng bộ ngược. Nếu xuất hiện ghi mới, phải dừng và thiết kế hòa giải dữ liệu trước khi quay lui.')

page(R,'9 Triển khai hai môi trường thử nghiệm')
p(R,'Mã dùng Python 3 và thư viện chuẩn, không cần viết ứng dụng logistics hoàn chỉnh. service.py phục vụ các URL cố định; gateway.py giữ địa chỉ truy cập của máy khách. tools/lab.py dùng chung cho tạo dữ liệu, manifest, đóng gói, kiểm tra và thay route. demo.py điều phối đúng các ca trong phiếu.')
h(R,'9.1 Bản đã thực nghiệm')
p(R,'Nguồn và đích là hai container Linux riêng dùng image python:3.12-slim; gateway và máy khách kiểm thử ở host Windows. Mỗi container có tiến trình và namespace mạng riêng, nội dung được gắn chỉ đọc. Hai container cùng một Docker host nên không đại diện hai máy vật lý hoặc hai Availability Zone.')
code(R,'python demo.py --engine docker')
p(R,'Lệnh chạy trong thư mục demo sau khi Docker Desktop hoạt động và đã docker pull python:3.12-slim. Nếu chỉ muốn tập thao tác không cần Docker, chạy python demo.py hoặc CHAY_DEMO.cmd. Bản tiến trình cục bộ có log riêng, không được gắn nhãn thành kiểm thử hai VM.')
h(R,'9.2 Bản thao tác chi tiết')
p(R,'Hướng dẫn 02_Huong_dan_demo.docx chỉ rõ đường chạy tự động, đường quay video tương tác và đường dựng hai VM thủ công. Trong hai VM, giữ IP tĩnh nguồn .11 và đích .12, chạy service.py ở cổng 8080, chuyển archive bằng scp rồi đổi route ở máy khách. Không tự sửa DNS hoặc tệp hosts của máy người dùng.')
h(R,'9.3 Khả năng chạy lại')
p(R,'Mỗi lần chạy tạo demo/runs/<mốc UTC>/ mới, không xóa dữ liệu lần trước. Nếu cổng 18080–18082 bị chiếm thì dùng --base-port 19080. Script chỉ dừng các tiến trình hoặc container đã tự tạo; log và dữ liệu vẫn giữ nguyên. Bản README ghi phiên bản đã dùng và cách tìm lần chạy mới nhất.')

page(R,'10 Di chuyển và đối chiếu dữ liệu')
h(R,'10.1 Bộ dữ liệu đầu vào')
p(R,'Bộ mẫu cố định gồm 200 vận đơn MPL-0001 đến MPL-0200. Mỗi bản ghi chỉ có id, warehouse, status, published_at; đây là dữ liệu công khai giả, không phải đơn hàng nghiệp vụ hoặc bản sao MySQL. Các giá trị không phụ thuộc đồng hồ khi tạo nên có thể tạo lại cùng bộ byte.')
table(R,['Đối tượng','Số lượng','Cách kiểm tra'],[
 ('index.html','1 file','SHA-256 và số byte'),
 ('data/shipments.json','200 bản ghi trong 1 file','Hash byte; đếm 200 ID duy nhất'),
 ('files/readme.txt','1 file','SHA-256 và số byte'),
 ('Toàn bộ nội dung','3 file; 27.882 byte','Đúng danh sách đường dẫn, dung lượng và hash')],[5.1,4.4,7])
h(R,'10.2 Quy trình bảo toàn dữ liệu')
p(R,'Đầu tiên lưu phản hồi nguồn và source_manifest.json. Tiếp theo pack tạo transfer.zip kèm manifest; unpack tại một thư mục đích mới, kiểm đường dẫn an toàn và so lại manifest. File cấu hình gateway không nằm trong nội dung Web nên không được chuyển lẫn với dữ liệu công khai.')
code(R,'''
python tools/lab.py pack --root content --archive transfer.zip
python tools/lab.py unpack --archive transfer.zip --target content
''')
p(R,'Hai lệnh trên thực hiện lần lượt ở nguồn và đích. Đích đã có thư mục content sẽ bị từ chối để tránh ghi đè. Muốn thử lại, dùng thư mục mới và cập nhật --root của tiến trình; không xóa bừa thư mục chứa dữ liệu khác.')
h(R,'10.3 Tiêu chí đối chiếu')
p(R,'Kết quả chỉ đạt khi mọi đường dẫn, số byte và hash đều bằng nhau, không thiếu và không thừa file; phản hồi dữ liệu qua gateway cũng phải bằng byte baseline. Kiểm tra ID loại trừ trường hợp dữ liệu JSON không đúng cấu trúc mẫu. Các bản manifest và phản hồi nguồn/đích được giữ cùng lần chạy để tránh so nhầm.')

page(R,'11 Chuyển hướng truy cập và quay lui')
h(R,'11.1 Cơ chế chuyển hướng')
p(R,'Máy khách luôn dùng http://127.0.0.1:18080 trong bản tự động. Gateway đọc route.json cho từng yêu cầu và chuyển tiếp đến nguồn hoặc đích. lab.route kiểm /health trước rồi thay tệp route bằng thao tác nguyên tử. Đây là mô phỏng đổi endpoint bằng reverse proxy; không đo thời gian lan truyền DNS của Internet.')
h(R,'11.2 Các bước quay lui')
for tx in [
 '1. Tạo cờ content.fault tại vùng đích. service.py trả HTTP 503 cho các yêu cầu mới và giữ nguyên dữ liệu.',
 '2. Máy khách kiểm /health qua gateway; lưu mốc lỗi đầu tiên và chuỗi probe có thời gian UTC.',
 '3. Kiểm nguồn còn khỏe. Đổi route.json về nguồn bằng cùng cơ chế có kiểm health.',
 '4. Đọc lại 200 vận đơn qua địa chỉ ổn định, so byte với KT1 và xác nhận X-MPL-Instance là source.',
 '5. Lưu rollback_timing.json, probes.csv và rollback_route.json; chỉ sau đó kết thúc demo.']:p(R,tx)
h(R,'11.3 Cách đo gián đoạn')
p(R,'Khoảng gián đoạn quan sát = thời điểm đọc dữ liệu thành công sau quay lui − mốc HTTP lỗi đầu tiên. Đồng hồ monotonic tính thời lượng, đồng hồ UTC đánh dấu log. Cận trên quan sát lấy từ lần thành công cuối trước lỗi đến lần thành công xác nhận sau quay lui; không coi đây là phép đo chính xác tuyệt đối của thời điểm bắt đầu mất dịch vụ.')
p(R,f'Lần chạy hai container ghi {outage:.3f} giây gián đoạn quan sát, cận trên {upper:.3f} giây. Có chủ động giữ lỗi khoảng 2 giây để nhìn thấy tình huống, khoảng probe mục tiêu 0,1 giây. Số đo là kiểm chứng cơ chế quay lui trong lab, không phải RTO cam kết cho hệ thống thật.')
p(R,'Vì không cho ghi nghiệp vụ, dữ liệu của snapshot đã kiểm tra không mất trong lần quay lui này. Kết luận đó không áp dụng cho dịch vụ có giao dịch mới hoặc xuất bản đang thay đổi.')

page(R,'12 Kịch bản kiểm thử nghiệm thu')
p(R,'Các ca dưới đây chạy cùng bộ dữ liệu, cùng endpoint và cùng lần thử. Bảng kết quả chi tiết có đủ đầu vào, thao tác, kỳ vọng, thực tế, kết luận và đường dẫn bằng chứng trong minh_chung/demo_docker/test_results.csv. Mốc giờ UTC có hậu tố +00:00.')
table(R,['Mã','Đầu vào và thao tác','Kỳ vọng','Bằng chứng'],[
 ('KT1','Nguồn có 200 vận đơn; đọc qua gateway và lập manifest','HTTP 200, instance source, 200 ID duy nhất','KT1_data.json; KT1_http.json; source_manifest.json'),
 ('KT2','Đóng gói, chuyển, kiểm hash, đổi route sang đích','HTTP 200 từ target, toàn bộ nội dung khớp nguồn','KT2_http.json; target_manifest.json; cutover_route.json'),
 ('KT3','Cho đích trả 503, quay route về nguồn, đọc lại','Nguồn phục vụ lại; dữ liệu khớp; đo được gián đoạn','KT3_http.json; rollback_timing.json; probes.csv'),
 ('KT4 bổ sung','Đích chưa có nội dung; thử chuyển hướng','Từ chối chuyển; giữ route nguồn','events.jsonl'),
 ('KT5 bổ sung','Thay 1 hash trên bản sao manifest rồi so','Phát hiện không khớp; không làm hỏng đích đã nhận','negative_manifest.json')],[1.4,5.4,4.7,5],10.5)
h(R,'12.1 Cách kết luận')
p(R,'PASS chỉ khi lệnh kiểm và dữ liệu bằng chứng cùng xác nhận; nếu script lỗi phải ghi FAIL và giữ log. KT4 và KT5 là kiểm tra bổ sung, không thay KT1–KT3. KT5 kiểm cơ chế so manifest với một hash giả bị sửa, chưa phải thử làm hỏng archive thật.')
h(R,'12.2 Kiểm thử hai VM')
p(R,'Biểu mẫu bieu_mau/kiem_thu_VM.csv để riêng trạng thái Chưa chạy. Nhóm dùng khi thực hiện nhánh hai VM trong hướng dẫn. Không chuyển kết quả hai container sang hai VM hoặc tự điền thời gian gián đoạn chưa đo. Mỗi người phải mở được bằng chứng và thực hiện lại phần kỹ thuật của mình khi bảo vệ.')

page(R,'13 Kết quả thực nghiệm và bằng chứng')
p(R,f'Run ID {S["run_id"]}. Bản kiểm chứng dùng hai container Linux riêng, image python:3.12-slim; môi trường host và phiên bản Docker/Python được lưu trong environment.json, docker_version.json và container_inspect.json. Ngày và giờ trong hồ sơ bằng chứng dùng UTC, đổi sang giờ Việt Nam bằng cách cộng 7 giờ.')
table(R,['Ca','Kết quả thực tế','Kết luận'],[
 ('KT1','Nguồn trả 200; 200 ID duy nhất; 3 file; tổng 27.882 byte','PASS'),
 ('KT2','Dữ liệu HTTP bằng byte nguồn; manifest khớp; instance target','PASS'),
 ('KT3',f'Quay về source; 200 bản ghi khớp; gián đoạn quan sát {outage:.3f} s','PASS'),
 ('KT4','Đích rỗng bị từ chối; route nguồn giữ nguyên','PASS'),
 ('KT5','Bản sao manifest bị đổi hash được nhận diện không khớp','PASS')],[2,12.4,2.1])
h(R,'13.1 Chuỗi mốc quay lui từ log thực tế')
for label,key in [('Thành công cuối trước lỗi','last_success_before_fault_utc'),('Lỗi đầu tiên quan sát','first_failure_utc'),('Thành công xác nhận sau quay lui','first_success_after_rollback_utc')]:p(R,label+'  '+S[key])
h(R,'13.2 Hồ sơ để kiểm tra kết luận')
p(R,'summary.json tổng hợp kết quả và giới hạn môi trường. source_manifest.json cùng target_manifest.json cho phép kiểm lại toàn bộ file. KT1_data.json, KT2_data.json, KT3_data.json là phản hồi dữ liệu gốc. probes.csv giữ chuỗi HTTP trong thời gian lỗi; events.jsonl và log từng dịch vụ giúp truy vết thao tác.')
p(R,'Các file nằm tại minh_chung/demo_docker/ trong bộ nộp. Chúng là kết quả kiểm chứng kỹ thuật của bộ demo, chưa phải xác nhận mỗi sinh viên đã trực tiếp hoàn thành nhiệm vụ. Phiếu cá nhân cần từng thành viên chạy lại, ghi phần sửa và xác nhận thật.')

page(R,'14 Đánh giá giải pháp và giới hạn')
h(R,'14.1 Những điểm đã kiểm chứng')
p(R,'Quy trình có thể chuyển Web chỉ đọc giữa hai môi trường thử nghiệm, nhận diện nơi phục vụ mà không đổi địa chỉ người dùng, đối chiếu byte và hash, phát hiện đích lỗi rồi quay về nguồn. Mã và dữ liệu giữ theo từng run nên có thể chạy lại và kiểm toán kết quả.')
h(R,'14.2 Những nội dung còn ở mức thiết kế')
p(R,'Cloud IaaS thật, DNS công cộng, HTTPS, backup định kỳ, firewall doanh nghiệp, hoạt động qua WAN, tải lớn và HA chưa được thực hiện. Hai container chung host không tạo dự phòng độc lập; host lỗi làm cả nguồn và đích ngừng. Bản hai VM trong hướng dẫn cũng chưa có bằng chứng nghiệm thu.')
p(R,'Bộ dữ liệu 27.882 byte chỉ dùng kiểm tính đúng của migration. Không từ đó suy ra băng thông truyền 10 GiB, sức tải 80 nhân viên hoặc chi phí thực. Không có bài đo hiệu năng nên không công bố throughput hay p95. probes.csv là số đo gián đoạn cho KT3, không là benchmark tải.')
h(R,'14.3 Rủi ro và phương án xử lý')
table(R,['Tình huống','Ảnh hưởng','Xử lý'],[
 ('Đích chưa sẵn sàng','Đổi endpoint có thể gây gián đoạn','Health gate trước khi thay route'),
 ('Nội dung không khớp','Thiếu hoặc sai thông tin công khai','Dừng chuyển; xem manifest; tạo archive mới'),
 ('Nguồn không còn hoạt động','Không quay lui được theo quy trình','Xác nhận nguồn trước cutover; giữ bản sao riêng'),
 ('Có ghi mới sau chuyển','Quay lui có thể mất thay đổi','Đóng xuất bản trong kỳ thử; thiết kế đồng bộ ngược nếu có ghi'),
 ('Chi phí truyền hoặc log tăng','Dự toán bị vượt','Giới hạn log; theo dõi lượng dùng; cập nhật bảng chi phí')],[4.3,5.2,7])
p(R,'Câu hỏi bảo vệ của phiếu: chỉ so giá thuê máy chủ sẽ dễ bỏ sót đĩa, backup, truyền ra, IPv4, DNS, log, hỗ trợ, giấy phép, nhân sự, chạy song song, chuyển một lần và chi phí các dịch vụ vẫn giữ lại.')

page(R,'15 Phân công và hồ sơ bàn giao')
table(R,['Vai trò và thành viên','Phần kỹ thuật phải tự làm','Sản phẩm và bằng chứng'],[
 ('SV1 Đặng Thái An','Khảo sát 3 dịch vụ, phụ thuộc; chọn Cloud và phạm vi','Sơ đồ, bảng tài nguyên; giải thích quyết định; kiểm baseline KT1'),
 ('SV2 Phạm Minh Đức','Dựng nguồn đích, gateway, mạng; thao tác health và đổi route','service.py, gateway.py, cấu hình; container inspect hoặc ảnh VM; KT4'),
 ('SV3 Vũ Tiến Đạt','Seed, archive, manifest; chuyển và đối chiếu dữ liệu','lab.py; transfer.zip; source/target manifest; KT1 KT2 KT5'),
 ('SV4 Trần Thị Lan Anh','Chi phí; điều phối kiểm thử; lỗi đích và quay lui; đo giờ','chi_phi_gia_dinh.csv; demo.py; test_results.csv; KT3 log và timing')],[4.2,6,6.3])
p(R,'Tất cả cùng kiểm thử kiến trúc chung; không thành viên nào chỉ làm Word hoặc slide. Tài liệu 03_Phan_cong_va_phieu_dong_gop.docx có đầu vào, đầu ra, bàn giao giữa vai trò, lịch tương đối và phiếu cá nhân. Họ tên và ba MSSV được giữ từ báo cáo cũ; MSSV Lan Anh cần bổ sung.')
h(R,'15.1 Danh mục sản phẩm')
p(R,'01_Bao_cao_De10_MPL.docx có 16 trang nội dung chính; 02_Huong_dan_demo.docx liên kết bước chạy với mã file và ca kiểm thử; 03_Phan_cong_va_phieu_dong_gop.docx phục vụ tổ chức và xác nhận đóng góp. Thư mục demo chứa mã, cấu hình và công cụ chạy; thiet_ke chứa sơ đồ, bảng tài nguyên và chi phí; minh_chung chứa dữ liệu gốc.')
p(R,'README.md chỉ điểm vào toàn bộ bộ nộp. tai_lieu/Kich_ban_video.md phân bổ 6 phút cho 4 người; video minh họa kèm theo sử dụng ảnh và log từ demo thực. Nhóm nên quay lại theo phân vai để thể hiện thao tác cá nhân. bieu_mau giữ biểu mẫu sạch để chạy lại.')
h(R,'15.2 Các việc trước khi nộp')
p(R,'Điền lớp, nhóm, giảng viên, hạn nộp và MSSV còn thiếu; mỗi thành viên chạy lại và ghi đóng góp thực tế, không xác nhận thay. Đối chiếu quy định giảng viên về định dạng nộp. Rubric trong tài liệu giao đề là đề xuất chờ giảng viên chốt, không tự coi là thang điểm đã phê duyệt.')

page(R,'16 Tài liệu tham khảo và kết luận')
refs=[
 '[1] NIST. SP 800-145 The NIST Definition of Cloud Computing. https://csrc.nist.gov/pubs/sp/800/145/final',
 '[2] AWS. Shared Responsibility Model. https://aws.amazon.com/compliance/shared-responsibility-model/',
 '[3] AWS Prescriptive Guidance. About the migration strategies. https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html',
 '[4] Python Software Foundation. http.server HTTP servers. https://docs.python.org/3/library/http.server.html',
 '[5] AWS. EC2 On-Demand Pricing và Amazon EBS Pricing. https://aws.amazon.com/ec2/pricing/on-demand/ và https://aws.amazon.com/ebs/pricing/',
 '[6] Tài liệu học phần do nhóm cung cấp. Phieu giao de tai.docx, phần hồ sơ chung và phiếu giao đề 10; Báo Cáo BTL CNNT.docx, tài liệu tham khảo bối cảnh MPL.']
for tx in refs:p(R,tx)
p(R,'Các nguồn trực tuyến được đối chiếu ngày 16/11/2026. Đơn giá ở mục 7 do bài tập giả định, không trích làm báo giá từ các trang nhà cung cấp. Mã demo viết riêng cho bộ bài, dùng API thư viện chuẩn Python và không sao chép mã nghiệp vụ của tổ chức khác.')
h(R,'16.1 Sử dụng AI và trách nhiệm nhóm')
p(R,'Có sử dụng AI để hỗ trợ thu gọn báo cáo, đề xuất mã/cấu hình demo, biên soạn hướng dẫn và kiểm tra đối chiếu yêu cầu. Bằng chứng trong bộ nộp được tạo từ lần chạy công cụ trên môi trường thử nghiệm; không tạo giả kết quả. Mỗi thành viên chịu trách nhiệm đọc, chỉnh sửa, chạy lại và giải thích phần mình nhận trước khi xác nhận phiếu đóng góp.')
h(R,'16.2 Kết luận')
p(R,'Giải pháp chọn chuyển Web lên IaaS và giữ dữ liệu nghiệp vụ cùng chia sẻ tập tin trong mạng nội bộ. Bộ demo đã kiểm chứng KT1–KT3 trên hai container và lưu dữ liệu gốc, mốc giờ cùng kết quả đối chiếu. Chi phí đầy đủ trong tình huống giả định cao hơn giữ nội bộ; lợi ích chính là tách Web công khai khỏi nơi vận hành nghiệp vụ và có quy trình chuyển đổi kiểm tra được. Triển khai Cloud thật cần xác nhận sizing, giá, bảo mật và khả năng phục hồi trước khi vận hành.')
R.core_properties.title='Chuyển đổi hạ tầng máy chủ doanh nghiệp lên Cloud theo phiếu 10'
R.core_properties.author='Nhóm MPL Logistics'
R.save(OUT/'01_Bao_cao_De10_MPL.docx')

# Detailed demo guide with both tested and manual paths.
G=setup();footer(G.sections[0],1)
title(G,'Hướng dẫn demo chuyển Web và quay lui')
p(G,'Phiếu giao đề 10  Bộ MPL Logistics  Dùng cùng báo cáo và mã nguồn trong thư mục demo')
h(G,'1 Chọn cách chạy và chuẩn bị',1)
p(G,'Bắt đầu bằng bản tự động để hiểu luồng, sau đó dùng chế độ tương tác để thuyết trình. Nếu muốn thực hành hai VM, dùng từ bước 7. Bản hai container và bản tiến trình đã có log chạy; nhánh hai VM cần nhóm tự dựng và kiểm thử.')
table(G,['Cách chạy','Chuẩn bị','Lệnh tại thư mục demo'],[
 ('Nhanh trên một máy','Python 3.10 trở lên; không cần gói pip','python demo.py'),
 ('Hai container Linux','Docker Desktop đang chạy; có image Python','python demo.py --engine docker'),
 ('Dừng từng mốc để quay','Như một trong hai dòng trên','python demo.py --engine docker --interactive'),
 ('Hai VM thủ công','2 Linux VM; Python; IP host-only','Làm bước 7 đến 10')],[3.6,6.1,6.8])
p(G,'Mở Terminal tại thư mục Bo_nop_De10_MPL/demo. Windows có thể dùng py -3 thay python nếu Python chưa có trên PATH. Kiểm bằng python --version hoặc py -3 --version. Với Docker: docker version phải có phần Server. Chạy docker pull python:3.12-slim trước lần đầu; đây là tải image, không thuê Cloud.')
code(G,'''
python --version
docker version
docker pull python:3.12-slim
python demo.py --engine docker --interactive
''')
p(G,'Nếu chưa dùng Docker thì nhấp CHAY_DEMO.cmd. Bản tự động không cần quyền quản trị, không sửa DNS hệ thống, không cài thêm pip. Nguồn và đích chỉ nghe localhost ở các cổng 18081, 18082; gateway là 18080. Đóng chương trình đang chiếm cổng hoặc dùng --base-port 19080.')

page(G,'2 Cấu trúc file và liên kết với báo cáo')
table(G,['File hoặc thư mục','Dùng để làm gì','Đối chiếu'],[
 ('demo.py','Điều phối nguồn đích, KT1–KT5, log và dọn tiến trình','Báo cáo 9 và 12'),
 ('app/service.py','Phục vụ Web chỉ đọc; trả instance; giả lập lỗi 503','Báo cáo 9 và 11'),
 ('app/gateway.py','Đầu truy cập cố định; đọc route.json','Báo cáo 11'),
 ('tools/lab.py','seed, manifest, pack, unpack, compare, route, fault','Báo cáo 10'),
 ('runs/<run>/source và target','Nội dung thực của hai môi trường','KT1 KT2 KT3'),
 ('runs/<run>/evidence','Dữ liệu gốc và kết quả theo lần chạy','Báo cáo 13'),
 ('../minh_chung/demo_docker','Bản bằng chứng hai container đã đóng gói','So đối chiếu tham khảo'),
 ('../bieu_mau/kiem_thu_VM.csv','Ghi lần thử thủ công hai VM','Bước 10 của hướng dẫn')],[5.3,7.6,3.6])
p(G,'Dùng runs/latest.json để tìm lần chạy mới nhất; đây là tệp thông tin, không phải lệnh cần thực thi. Muốn xem bằng PowerShell: Get-Content runs/latest.json. Khi chia sẻ bộ file sang máy khác, dùng đường dẫn tương đối runs/<run>/ thay cho đường dẫn tuyệt đối ghi trong latest.json của máy cũ.')
h(G,'Quy ước dữ liệu và giờ')
p(G,'ID MPL-0001 đến MPL-0200 là dữ liệu giả. published_at là mốc dữ liệu cố định, không phải thời gian thực hiện demo. Thời gian chạy thật nằm trong file evidence có trường timestamp_utc, first_failure_utc và sự kiện log. UTC + 7 giờ là giờ Việt Nam; không sửa số giờ trong log gốc.')
p(G,'Mỗi lần chạy dùng thư mục mới. Không sửa minh_chung đã bàn giao để làm như kết quả tự chạy của nhóm. Tạo lần chạy riêng rồi sao chép nguyên evidence đó vào thư mục minh chứng mới có tên người thực hiện.')

page(G,'3 KT1 ghi nhận nguồn đang hoạt động')
p(G,'Trong chế độ tương tác, script dừng ở thông báo KT1. Chưa nhấn Enter. Mở trình duyệt http://127.0.0.1:18080; trang phải hiện Dịch vụ source. Mở liên kết 200 vận đơn mẫu và tập tin tải xuống. Chụp ảnh có URL và đồng hồ hệ thống nếu nhóm cần bằng chứng màn hình.')
code(G,'''
curl.exe -i http://127.0.0.1:18080/health
curl.exe http://127.0.0.1:18080/data/shipments.json
''')
p(G,'Kỳ vọng: HTTP 200, JSON health có instance source, header X-MPL-Instance: source. Dữ liệu có 200 phần tử và 200 ID khác nhau. Script đồng thời lưu dữ liệu phản hồi, mã băm và manifest trước di chuyển.')
table(G,['Bằng chứng KT1','Nội dung cần mở'],[
 ('KT1_http.json','status 200; instance source; records 200; hash phản hồi'),
 ('KT1_data.json','Toàn bộ dữ liệu nhận từ Web'),
 ('source_manifest.json','3 đường dẫn, số byte, SHA-256'),
 ('source.log và gateway.log','Các yêu cầu thực tế với thời gian UTC')],[5.8,10.7])
p(G,'Người trình bày SV1 giải thích phụ thuộc giữa Web và bản xuất; SV3 mở manifest và giải thích vì sao không dùng bản sao MySQL làm dữ liệu công khai. SV2 chỉ vị trí hai tiến trình/container và endpoint. Khi đã lưu ảnh, nhấn Enter ở cửa sổ demo để bắt đầu di chuyển.')
p(G,'Trước khi chuyển thật, KT4 tự thử chọn đích đang rỗng. Chuyển hướng phải bị từ chối và route vẫn là nguồn; sự kiện unhealthy_target_cutover_rejected được ghi trong events.jsonl. Đây là minh chứng điều kiện No-Go, không thay KT1.')

page(G,'4 KT2 di chuyển dữ liệu và đổi nơi phục vụ')
p(G,'Sau Enter, script tạo transfer.zip từ nội dung nguồn, chứa cả _manifest.json; unpack vào đích mới rồi kiểm danh sách đường dẫn, kích thước và hash. Nguồn vẫn phục vụ trong lúc copy. Chỉ sau khi đích khỏe, script thay route.json nguyên tử và dừng ở thông báo KT2.')
code(G,'''
curl.exe -i http://127.0.0.1:18080/health
curl.exe -i http://127.0.0.1:18082/health
''')
p(G,'Giữ nguyên URL 18080 và refresh trang, phải thấy Dịch vụ target. Mở hai manifest; file_count cùng là 3, total_bytes cùng 27882, từng hash bằng nhau. Mở KT1_data.json và KT2_data.json; script kiểm bằng byte, không chỉ so số dòng.')
table(G,['Bằng chứng KT2','Ý nghĩa'],[
 ('target_manifest.json','Nội dung thực sau giải nén'),
 ('KT2_http.json và KT2_data.json','Máy khách qua gateway đọc từ target, dữ liệu đúng'),
 ('cutover_route.json','Bản route tại mốc đã chuyển hướng'),
 ('negative_manifest.json','KT5 đổi hash trên một bản sao và phát hiện lệch'),
 ('container_inspect.json','Hai container riêng trong lần chạy Docker')],[6.3,10.2])
p(G,'SV3 giải thích SHA-256 là phép kiểm nội dung; SV2 giải thích route và health gate. Hash bằng nhau không chứng minh phân quyền hoặc bảo mật Internet, nên không dùng kết quả này để kết luận các tính năng đó đạt.')
p(G,'Nếu muốn thu cảnh lỗi HTTP 503 khi quay video, mở thêm cửa sổ chạy vòng curl kiểm /health trước khi nhấn Enter. Bản tự động giữ lỗi khoảng 2 giây, sau đó tự quay lui. Không dừng hoặc đóng cửa sổ demo giữa hai mốc.')

page(G,'5 KT3 tạo lỗi đích và quay về nguồn')
p(G,'Tại mốc KT2, nhấn Enter. Script tạo cờ content.fault tại đích, gateway nhận HTTP 503, lưu thời điểm lỗi đầu tiên, giữ lỗi khoảng 2 giây rồi kiểm nguồn và đổi route về nguồn. Dữ liệu không bị xóa. Chương trình dừng tại mốc KT3 để nhóm quan sát.')
code(G,'''
curl.exe -i http://127.0.0.1:18080/health
''')
p(G,'Kỳ vọng sau quay lui: HTTP 200, instance source; 200 vận đơn và mọi byte dữ liệu bằng baseline. Đích vẫn ở trạng thái lỗi cho đến khi kết thúc lần chạy. Mở probes.csv để thấy chuỗi 503 chuyển về 200; mở rollback_route.json để kiểm địa chỉ nguồn.')
table(G,['Tệp','Trường cần giải thích'],[
 ('rollback_timing.json','first_failure_utc; first_success_after_rollback_utc; observed_outage_seconds'),
 ('probes.csv','Mã HTTP theo chuỗi thời gian'),
 ('KT3_http.json','instance source; hash dữ liệu'),
 ('test_results.csv','Đủ đầu vào, thao tác, kỳ vọng, thực tế, PASS và bằng chứng'),
 ('summary.json','Kết quả cả lần chạy và giới hạn cloud_deployed=false; vm_tested=false')],[6,10.5])
p(G,'Lần hai container tham khảo đo '+f'{outage:.3f}'+' giây gián đoạn quan sát. Không thay giá trị đó vào lần chạy mới: số giờ phụ thuộc máy và thời điểm thực hiện. Có khoảng giữ lỗi chủ động 2 giây nên không so số này với SLA Cloud.')
p(G,'SV4 giải thích cách tính, mở file đo và cho thấy nguồn còn đủ dữ liệu. Sau khi lưu ảnh và bảng, nhấn Enter lần cuối để dừng các tiến trình/container của demo. Kiểm tra mã thoát 0 và summary PASS; nếu có traceback, giữ nguyên log và ghi FAIL để chẩn đoán.')

page(G,'6 Lưu hồ sơ và xử lý lỗi thường gặp')
table(G,['Triệu chứng','Nguyên nhân có thể','Cách xử lý'],[
 ('python không nhận','Chưa cài hoặc PATH chưa có','Thử py -3; dùng Python 3.10+; mở terminal mới'),
 ('Port busy','Cổng 18080–18082 đã được dùng','Dùng --base-port 19080; cập nhật URL trình duyệt tương ứng'),
 ('Docker thiếu Server','Docker Desktop chưa sẵn sàng','Mở Docker Desktop, chờ Engine chạy, kiểm docker version'),
 ('Không thấy image','Chưa pull hoặc thiếu Internet lúc tải','docker pull python:3.12-slim; chạy lại'),
 ('Đích chưa sẵn sàng','Thiếu nội dung hoặc tiến trình lỗi','Mở target.log; chưa đổi route; chạy lại bằng run mới'),
 ('Manifest không khớp','Khác dữ liệu hoặc sửa nhầm file','Dừng cutover; so từng đường dẫn; tạo archive mới'),
 ('VM không truy cập được','Sai IP, listener, host-only hoặc firewall','Kiểm ip a, cổng 8080, bind 0.0.0.0 và luật firewall'),
 ('Trang không đổi instance','Sai URL hoặc chưa Enter qua mốc','Dùng gateway 18080; kiểm /health và route.json')],[4.3,5.1,7.1],10.5)
p(G,'Hồ sơ một lần thử gồm nguyên thư mục evidence, archive transfer.zip, ảnh màn hình nhóm tự chụp và phiếu cá nhân đã điền. Giữ run ID trong mọi tên minh chứng. Nén nguyên thư mục cùng README, tránh chỉ nộp ảnh PASS thiếu dữ liệu gốc.')
p(G,'Muốn dọn container còn lại sau khi buộc tắt chương trình, trước hết chạy docker ps --filter label=mpl.demo để xác nhận đúng tên của run. Chỉ docker stop <tên-cụ-thể> của demo; không dùng lệnh dọn toàn bộ Docker vì có thể ảnh hưởng dự án khác.')
p(G,'Bản Windows dùng hai file CMD để tiện chạy. Các lệnh Python còn dùng được trên Linux/macOS với python3 thay python. Thư mục đường dẫn có khoảng trắng cần đặt trong dấu nháy kép khi gõ lệnh.')

page(G,'7 Dựng hai VM để thao tác thủ công')
p(G,'Nhánh này tùy chọn môi trường thay cho hai container; không phải kiểm thử đã chạy trong bộ bằng chứng hiện tại. Dùng 2 VM Linux và máy host làm client/gateway. Đề không bắt buộc thuê Cloud. Có thể chọn phần mềm ảo hóa được phép và ghi đúng phiên bản thực tế vào README của nhóm.')
table(G,['Máy','Cấu hình lab đề xuất','Mạng host-only'],[
 ('SOURCE','1 vCPU; 1 GiB RAM; đĩa 10 GiB; Python 3.10+','192.168.56.11/24'),
 ('TARGET','1 vCPU; 1 GiB RAM; đĩa 10 GiB; Python 3.10+','192.168.56.12/24'),
 ('HOST','Máy khách, gateway; có Python và đủ tài nguyên cho 2 VM','192.168.56.1/24')],[3,8,5.5])
p(G,'Gán IP host-only cố định bằng công cụ mạng của hệ điều hành guest, kiểm ip a. Hai VM cùng subnet không cần default gateway trên card host-only. Nếu cài gói cần Internet, thêm card NAT riêng. Kiểm không trùng với dải mạng đang dùng. Guest phải có Python; chỉ cần SSH nếu muốn truyền archive bằng scp.')
p(G,'Chép thư mục demo vào ~/mpl-demo trên cả hai VM. Lệnh dưới giả định đang đứng tại ~/mpl-demo, và mỗi VM chưa có thư mục content. Với scp cần cài và bật SSH trên guest theo hướng dẫn chính thức của OS; có thể thay bằng shared folder/USB được phép, ghi lại cách đã dùng.')
code(G,'''
python3 --version
ip a
# SOURCE: tao du lieu nguon, luu manifest
python3 tools/lab.py seed --root content
python3 tools/lab.py manifest --root content --out source_manifest.json
# SOURCE: giu cua so nay chay
python3 app/service.py --root content --instance source --host 0.0.0.0 --port 8080
''')
p(G,'Trên TARGET, mở terminal riêng và chạy service.py với instance target, root content cùng cổng 8080. Khi chưa có content, health trả 503 là đúng. Nếu firewall đang bật, chỉ cho host-only client và IP nguồn cần thiết vào 8080; không mở cổng ra mạng công cộng.')

page(G,'8 KT1 và KT2 trên hai VM')
p(G,'Tại thư mục demo trên HOST, chạy các lệnh sau trong hai terminal. Các file route.vm.json chỉ ở host; không chép vào thư mục Web công khai.')
code(G,'''
# HOST terminal 1
python tools/lab.py route --file route.vm.json --backend http://192.168.56.11:8080
python app/gateway.py --route route.vm.json --port 18080
# HOST terminal 2
curl.exe -i http://127.0.0.1:18080/health
curl.exe http://127.0.0.1:18080/data/shipments.json -o KT1_data.json
''')
p(G,'KT1: chụp health source, lưu dữ liệu và manifest nguồn. Sau đó dùng terminal mới trên SOURCE tạo archive và chuyển đến TARGET. Thay demo_user bằng tài khoản lab thực, không ghi mật khẩu vào lệnh hoặc báo cáo.')
code(G,'''
# SOURCE
python3 tools/lab.py pack --root content --archive transfer.zip
scp transfer.zip demo_user@192.168.56.12:~/mpl-demo/
# TARGET
python3 tools/lab.py unpack --archive transfer.zip --target content
python3 tools/lab.py manifest --root content --out target_manifest.json
''')
p(G,'Chép source_manifest.json và target_manifest.json về cùng một máy để đối chiếu. Nếu archive đã tồn tại hoặc content đã có, dùng một tên run/thư mục mới; không ghi đè dữ liệu mà chưa rõ nguồn.')
code(G,'''
# HOST, sau khi da chep hai manifest ve thu muc hien tai
python tools/lab.py compare --left source_manifest.json --right target_manifest.json
python tools/lab.py route --file route.vm.json --backend http://192.168.56.12:8080
curl.exe -i http://127.0.0.1:18080/health
curl.exe http://127.0.0.1:18080/data/shipments.json -o KT2_data.json
''')
p(G,'KT2: instance phải là target; cả hai manifest khớp, 200 bản ghi nhận ở gateway khớp baseline. Lưu mốc giờ và kết luận thực tế vào biểu mẫu VM. Không dùng file kết quả hai container thay kết quả đang thao tác.')

page(G,'9 KT3 thủ công đo gián đoạn và quay lui')
p(G,'Chạy công cụ theo dõi dưới đây trên HOST trước khi tạo lỗi. Nó lưu chuỗi HTTP vào probes_vm.csv và tự dừng sau 60 giây; đổi tham số nếu cần. Mở terminal HOST thứ hai sẵn lệnh chuyển route về nguồn.')
code(G,'''
python tools/monitor.py --url http://127.0.0.1:18080/health --seconds 60 --out probes_vm.csv
# TARGET: gia lap dich loi
python3 tools/lab.py fault --root content --state on
# HOST: sau khi quan sat HTTP 503, quay lui
python tools/lab.py route --file route.vm.json --backend http://192.168.56.11:8080
curl.exe -i http://127.0.0.1:18080/health
curl.exe http://127.0.0.1:18080/data/shipments.json -o KT3_data.json
''')
p(G,'Công cụ monitor tính thời gian từ lỗi đầu đến health thành công đầu sau lỗi bằng monotonic, đồng thời ghi các mốc UTC. Mở probes_vm.summary.json. Sau đó phải kiểm dữ liệu KT3 riêng, vì health 200 một mình chưa chứng minh dữ liệu khớp. Đối chiếu hash bằng công cụ trong tools/verify_http.py.')
code(G,'''
python tools/verify_http.py --left KT1_data.json --right KT2_data.json
python tools/verify_http.py --left KT1_data.json --right KT3_data.json
# TARGET: chi xoa co loi sau khi da luu bang chung
python3 tools/lab.py fault --root content --state off
''')
p(G,'Điền thời gian, kết quả và tên người thực hiện vào bieu_mau/kiem_thu_VM.csv. Nếu không thấy lỗi trong thời gian monitor thì ca chưa đủ bằng chứng; chạy lại với cửa sổ giám sát bao trùm toàn bộ thao tác. Dừng các terminal dịch vụ bằng Ctrl+C sau khi đã lưu hồ sơ.')
p(G,'Trường hợp nguồn cũng lỗi: không chuyển route về nguồn chưa khỏe. Giữ trạng thái lỗi và ghi nhận chưa phục hồi, sau đó sửa nguồn hoặc dùng bản sao độc lập. Không đánh dấu KT3 đạt chỉ vì đã sửa file route.')

page(G,'10 Quay video và đối chiếu trước khi nộp')
p(G,'Kịch bản 6 phút nằm tại tai_lieu/Kich_ban_video.md. Chuẩn bị terminal, trình duyệt gateway, evidence và bảng chi phí trước khi quay. Chạy --interactive để không bỏ lỡ mốc KT1, KT2, KT3. Mỗi người có thao tác kỹ thuật và giải thích riêng.')
table(G,['Thời lượng','Người và nội dung','Cảnh cần thấy'],[
 ('00:00–01:00','SV1 phạm vi 3 dịch vụ, chọn Web và IaaS','Sơ đồ trước sau, lý do giữ DB và file'),
 ('01:00–02:00','SV2 nguồn đích, gateway và mạng','Container/VM; /health; URL ổn định'),
 ('02:00–03:20','SV3 KT1 và archive/hash','200 ID; manifest; transfer.zip'),
 ('03:20–04:20','SV2 SV3 KT2 đổi route','URL giữ nguyên; instance target; dữ liệu khớp'),
 ('04:20–05:30','SV4 KT3 lỗi và quay lui','503; source phục hồi; timing và probes'),
 ('05:30–06:00','SV4 chi phí, cả nhóm chốt giới hạn','Bảng phí đủ khoản; kết quả và phần chưa thử')],[3,7.8,5.7])
p(G,'Video minh họa dựng kèm bộ bài từ ảnh chụp demo trực tiếp và log thật giúp nhóm xem trước luồng. Các đoạn giải thích được kéo dài khi dựng, không thể dùng độ dài cảnh làm số đo gián đoạn. Khi nộp cá nhân, nhóm quay lại để chứng minh chính mình thao tác và giải thích.')
h(G,'Danh sách kiểm cuối')
for tx in ['Báo cáo giữ 12–18 trang nội dung chính và đủ YC1–YC4.',
 'KT1–KT3 có dữ liệu thực tế, thời gian, kết luận và bằng chứng gốc.',
 'Đủ README, mã nguồn, cấu hình, sơ đồ, bảng tài nguyên/IP/quyền và chi phí.',
 'Video 5–7 phút đọc rõ; không lộ mật khẩu; không gọi VM/container là Cloud thật.',
 'Cả 4 người có file kỹ thuật, lỗi đã xử lý và phiếu đóng góp xác nhận thực tế.',
 'Bổ sung MSSV Lan Anh cùng lớp, nhóm, giảng viên và hạn nộp.']:p(G,'☐ '+tx)
G.core_properties.title='Hướng dẫn demo chuyển Web và quay lui theo phiếu 10';G.save(OUT/'02_Huong_dan_demo.docx')

P=setup();footer(P.sections[0],1);title(P,'Phân công nhóm và phiếu đóng góp cá nhân')
p(P,'Đề 10  Chuyển đổi hạ tầng máy chủ doanh nghiệp lên Cloud  Nhóm 4 thành viên')
h(P,'1 Phân công kỹ thuật',1)
table(P,['Thành viên','Nhiệm vụ theo phiếu','File phụ trách'],[
 ('SV1 Đặng Thái An\nB24DCCC002','Khảo sát, phụ thuộc, chọn mô hình Cloud; xác nhận baseline','thiet_ke/01_AsIs.png; 02_ToBe.png; so_do.mmd; tai_nguyen_ip_quyen.csv'),
 ('SV2 Phạm Minh Đức\nB24DCCC071','Dựng đích, mạng, service và gateway; health gate','demo/app/service.py; gateway.py; demo/config/'),
 ('SV3 Vũ Tiến Đạt\nB24DCCC062','Dữ liệu giả, đóng gói, di chuyển và so toàn vẹn','demo/tools/lab.py; verify_http.py; manifest; transfer.zip'),
 ('SV4 Trần Thị Lan Anh\nMSSV [Bổ sung]','Chi phí, kiểm thử, lỗi đích, quay lui và đo giờ','demo/demo.py; tools/monitor.py; chi_phi_gia_dinh.csv; probes.csv')],[4.2,6.1,6.2],10.5)
p(P,'Đây là phân công đề xuất và biểu mẫu để nhóm thực hiện, không phải xác nhận các cá nhân đã hoàn thành. Bộ mã nền có thể dùng chung; mỗi người phải đọc, sửa hoặc cấu hình phần nhận, tự chạy và giải thích. Không nhận vai trò chỉ làm báo cáo hoặc chỉ quay video.')
h(P,'Bàn giao giữa các vai trò')
p(P,'SV1 bàn giao sơ đồ, URL/cổng và chính sách dữ liệu → SV2 dựng môi trường. SV2 bàn giao endpoint nguồn đích cùng log health → SV3 chuyển dữ liệu. SV3 bàn giao manifest khớp và baseline → SV4 tổ chức KT3, tính thời gian, tổng hợp bảng kiểm. Tất cả cùng xem lại sai khác và chạy lại phần bị ảnh hưởng.')
h(P,'Quy tắc hồ sơ cá nhân')
p(P,'Giữ run ID, tên file tạo/sửa và vị trí bằng chứng. Ghi lỗi thực đã gặp, cách chẩn đoán và kiểm lại; nếu không gặp lỗi, ghi rõ chưa phát sinh, không bịa lỗi. Các file chung không được coi là 4 sản phẩm cá nhân giống nhau chỉ bằng cách đổi tên.')

page(P,'2 Kế hoạch thực hiện và tiêu chí bàn giao')
table(P,['Mốc tương đối','Chủ trì','Đầu ra phải kiểm được'],[
 ('Buổi 1','SV1 và SV2','Chốt 3 dịch vụ; sơ đồ; bảng IP; Web nguồn chạy'),
 ('Buổi 2','SV2 và SV3','Đích khỏe sau chuyển nội dung; manifest; KT1 KT2'),
 ('Buổi 3','SV3 và SV4','KT3 quay lui; dữ liệu gốc; đo giờ; bảng chi phí'),
 ('Buổi 4','Cả nhóm','Chạy lại chéo phần việc; hoàn thiện báo cáo; quay 6 phút'),
 ('Trước hạn nộp','Cả nhóm','Điền thông tin; ký phiếu; kiểm mở ZIP và README')],[3.6,4.5,8.4])
h(P,'Tiêu chí cho từng vai trò')
p(P,'SV1 phải giải thích được vì sao Web chuyển còn DB và SMB giữ lại, điểm khác của IaaS/PaaS/SaaS và rủi ro khi Web cần ghi. SV2 phải đổi được cổng hoặc IP rồi cập nhật đúng route, nhận biết source/target qua health và không chuyển sang đích chưa khỏe.')
p(P,'SV3 phải tạo được bộ dữ liệu giống nhau, chỉ ra từng file trong manifest, chạy so hash và phát hiện một sai lệch. SV4 phải tạo lỗi có kiểm soát, quay lui, mở log đo thực tế, tính đầy đủ phí và phân biệt chi phí giả định với báo giá.')
h(P,'Minh chứng khi bảo vệ')
table(P,['Người','Thao tác trực tiếp gợi ý','Minh chứng mở kèm'],[
 ('SV1','Thay giả định Web cần ghi; giải thích tác động lựa chọn','Sơ đồ phụ thuộc và quyết định'),
 ('SV2','Thử chuyển route sang đích rỗng rồi sang đích khỏe','health và events'),
 ('SV3','So manifest có hash bị thay đổi','manifest và negative_manifest'),
 ('SV4','Gây 503 rồi quay route về nguồn','probes, timing và kết quả KT3')],[2.2,8.8,5.5])
p(P,'Mỗi người còn có thể được hỏi kiến trúc chung. Kế hoạch theo buổi không ấn định ngày thay giảng viên; nhóm điền ngày thực tế theo hạn nộp được thông báo. Tất cả tham gia kiểm thử và đọc lại báo cáo trước khi nộp.')

for ix,(role,name,ms) in enumerate([('SV1','Đặng Thái An','B24DCCC002'),('SV2','Phạm Minh Đức','B24DCCC071'),('SV3','Vũ Tiến Đạt','B24DCCC062'),('SV4','Trần Thị Lan Anh','[Bổ sung]')]):
    if ix in [0,2]:page(P,'3 Phiếu đóng góp cá nhân' if ix==0 else '4 Phiếu đóng góp cá nhân tiếp theo')
    h(P,f'{role} {name}')
    p(P,f'Mã sinh viên  {ms}       Ngày thực hiện  ........................')
    for tx in ['Nhiệm vụ đã thực hiện và phạm vi tự làm', 'File tạo hoặc chỉnh sửa cùng mô tả thay đổi',
               'Ca kiểm thử và đường dẫn minh chứng có mốc giờ', 'Lỗi đã gặp cách xử lý và kết quả kiểm lại']:
        p(P,tx+'  ........................................................................')
        p(P,'........................................................................................................')
    p(P,'Tự xác nhận đã đọc sửa chạy lại và giải thích được phần nhận  ........................')
    p(P,'Chữ ký thành viên  ........................    Người kiểm tra chéo  ........................')
P.core_properties.title='Phân công nhóm và phiếu đóng góp cá nhân đề 10';P.save(OUT/'03_Phan_cong_va_phieu_dong_gop.docx')
print('Created report, demo guide, contribution forms; Docker outage',outage)
