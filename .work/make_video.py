from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,textwrap
R=Path(__file__).resolve().parents[1];O=R/'Bo_nop_De10_MPL';V=R/'.work/video_frames';V.mkdir(exist_ok=True)
shots=O/'minh_chung/anh_demo';e=O/'minh_chung/demo_video'
s=json.loads((e/'summary.json').read_text(encoding='utf-8'));m=json.loads((e/'source_manifest.json').read_text(encoding='utf-8'))
font=lambda size,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if b else 'arial.ttf'),size)
def wrap(dr,text,f,width):
 lines=[]
 for para in text.split('\n'):
  words=para.split();line=''
  for word in words:
   trial=(line+' '+word).strip()
   if dr.textlength(trial,font=f)>width and line:lines.append(line);line=word
   else:line=trial
  lines.append(line)
 return lines
def text_card(lines):
 im=Image.new('RGB',(1160,680),'#FFFFFF');dr=ImageDraw.Draw(im);y=28
 for line in lines:
  f=font(26)
  for x in wrap(dr,line,f,1090):dr.text((30,y),x,font=f,fill='#163047');y+=37
  y+=12
 return im
scenes=[
 ('Đề 10 và mục tiêu demo',None,'Chuyển Web chỉ đọc giữa hai môi trường thử nghiệm.\n\nKiểm tra dữ liệu, giữ địa chỉ truy cập ổn định và quay lui khi đích lỗi.\n\nVideo minh họa có phụ đề từ ảnh demo trực tiếp và log thật; thời lượng dựng không phải thời gian đo.'),
 ('Ba dịch vụ trong hiện trạng','diagram1','SV1 khảo sát Web công khai, dữ liệu nghiệp vụ và chia sẻ tập tin.\n\nWeb chỉ đọc bản xuất đã lọc; không truy cập DB trực tiếp. Các thông số doanh nghiệp là giả định.'),
 ('Chọn dịch vụ chuyển và giữ','diagram2','Chuyển Web sang IaaS theo thiết kế. Giữ dữ liệu nghiệp vụ và SMB trong nội bộ.\n\nChưa triển khai Cloud thật; hai môi trường demo chỉ mô phỏng nơi chạy dịch vụ.'),
 ('Chuẩn bị hai môi trường','env','SV2 dựng hai container Linux riêng.\n\nCổng nguồn 18081, đích 18082; gateway 18080.\n\nHai container vẫn phụ thuộc cùng một Docker host.'),
 ('Điểm vào để chạy lại','commands','Mở terminal trong thư mục demo.\n\nDùng --interactive để chương trình dừng ở từng mốc và nhóm giải thích.\n\nKhông cần cài thêm gói pip hoặc thuê Cloud.'),
 ('KT1 nguồn đang hoạt động','01_nguon','Trình duyệt truy cập cùng URL gateway 18080.\n\nTrang hiển thị Dịch vụ source. Đây là nguồn phục vụ trước di chuyển.\n\nGiữ URL này cho cả KT2 và KT3.'),
 ('KT1 dữ liệu nguồn','02_du_lieu_nguon','SV3 mở 200 vận đơn giả.\n\nChỉ có mã, kho, trạng thái và thời điểm công bố. Không có thông tin khách hàng.\n\nMốc published_at cố định khác với giờ chạy thật.'),
 ('Ghi nhận manifest trước chuyển','manifest','Manifest ghi đường dẫn, số byte và SHA-256 của từng file.\n\nToàn bộ nội dung gồm 3 file, 27.882 byte.\n\nLưu baseline trước khi thay route.'),
 ('Điều kiện No-Go','nogo','KT4 thử chuyển sang đích đang rỗng.\n\nHealth không đạt thì từ chối đổi route, nguồn tiếp tục phục vụ.\n\nĐây là kiểm tra bổ sung; không thay KT1–KT3.'),
 ('Đóng gói và chuyển dữ liệu','transfer','Tạo transfer.zip kèm manifest, giải nén vào thư mục đích mới rồi so lại.\n\nKhông ghi đè một đích đã tồn tại.\n\nChỉ đổi endpoint sau khi mọi dữ liệu khớp và health đích tốt.'),
 ('KT2 đích đã phục vụ','03_dich','Refresh cùng URL 18080.\n\nTrang hiển thị Dịch vụ target.\n\nĐịa chỉ người dùng giữ nguyên, gateway đã chuyển backend.'),
 ('Xác nhận health tại đích','04_health_dich','SV2 chỉ instance target và status ok.\n\nHealth chứng minh nơi phục vụ và trạng thái dịch vụ.\n\nKiểm dữ liệu là bước độc lập, không chỉ nhìn trang chủ.'),
 ('Đối chiếu dữ liệu KT2','compare','SV3 xác nhận 200 ID duy nhất; dữ liệu HTTP bằng byte baseline; toàn bộ đường dẫn, số byte và hash khớp.\n\nKT5 thay hash trên bản sao manifest để kiểm phát hiện lệch.'),
 ('KT3 giả lập đích lỗi','05_loi_503','SV4 kích hoạt lỗi có kiểm soát.\n\nĐích trả HTTP 503; dữ liệu được giữ nguyên.\n\nMáy khách lưu mốc lỗi đầu tiên và chuỗi probe.'),
 ('Quay lui về nguồn','06_quay_ve_nguon','Kiểm nguồn còn khỏe rồi đổi route về source.\n\nCùng URL 18080 phục vụ lại từ nguồn.\n\nĐọc lại 200 bản ghi và so với KT1.'),
 ('Đo thời gian của lần quay video','timing',f'Đây là số đo riêng của run dùng quay ảnh.\n\nGián đoạn quan sát {s["observed_outage_seconds"]:.3f} giây; có giữ lỗi chủ động khoảng 2 giây.\n\nBáo cáo dùng một run khác, số đo 2,093 giây.'),
 ('Mở kết quả và bằng chứng gốc','results','Mỗi ca có đầu vào, thao tác, mong đợi, thực tế, kết luận và tên bằng chứng.\n\nCác timestamp giữ UTC. Cộng 7 giờ để xem theo giờ Việt Nam.\n\nKhông sửa số đo giữa các run.'),
 ('Chi phí đầy đủ theo giả định','cost','SV4 trình bày compute, đĩa, backup, truyền ra, IPv4, DNS, log và vận hành.\n\nGiá bài tập, không phải báo giá AWS.\n\nTheo giả định, không kết luận Cloud tiết kiệm hơn.'),
 ('Phân công bốn người','roles','SV1 khảo sát và chọn mô hình.\nSV2 dựng môi trường.\nSV3 di chuyển và kiểm dữ liệu.\nSV4 chi phí, kiểm thử và quay lui.\n\nMỗi người tự chạy, sửa và xác nhận phần kỹ thuật.'),
 ('Chạy lại và giới hạn kết luận','diagram3','KT1–KT3 đã đạt trong lab và có bằng chứng.\n\nChưa thử Cloud thật, SLA, HA, HTTPS hoặc tải doanh nghiệp.\n\nMở README và hướng dẫn Word để dựng lại, rồi quay theo phân vai của nhóm.')]

sources={
 'env':['Hai container Linux riêng; cùng Docker host','Image: python:3.12-slim',f'Run dùng chụp ảnh: {s["run_id"]}','Gateway: http://127.0.0.1:18080','Source: 127.0.0.1:18081   Target: 127.0.0.1:18082','cloud_deployed: false    vm_tested: false'],
 'commands':['python --version','docker version','docker pull python:3.12-slim','python demo.py --engine docker --interactive','Nhấn Enter lần 1: chuyển từ nguồn sang đích','Nhấn Enter lần 2: tạo lỗi và quay về nguồn','Nhấn Enter cuối: dừng dịch vụ, giữ bằng chứng'],
 'manifest':[f'{x["path"]}\n{x["bytes"]} byte\nSHA-256: {x["sha256"][:34]}…' for x in m['files']],
 'nogo':['Sự kiện từ log thật:','unhealthy_target_cutover_rejected','Đích chưa có nội dung → health 503','Không chấp nhận thay route sang đích','Route vẫn trỏ source trước khi di chuyển'],
 'transfer':['Nguồn → transfer.zip → đích mới','1. Đọc và ghi manifest nguồn','2. Đóng gói 3 file cùng _manifest.json','3. Chuyển sang môi trường đích','4. Giải nén an toàn, kiểm đủ byte và hash','5. Health đích tốt rồi thay route nguyên tử'],
 'compare':['KT2: PASS','200 bản ghi, 200 ID duy nhất','Dữ liệu qua HTTP bằng byte KT1','source_manifest.json = target_manifest.json','Header: X-MPL-Instance: target','Kiểm phụ: thay hash trên bản sao → phát hiện lệch'],
 'timing':['Trích rollback_timing.json',f'Lỗi đầu: {s["first_failure_utc"]}',f'Phục hồi: {s["first_success_after_rollback_utc"]}',f'Gián đoạn quan sát: {s["observed_outage_seconds"]:.3f} s',f'Cận trên quan sát: {s["upper_bound_seconds"]:.3f} s','Đồng hồ monotonic tính thời lượng; UTC đánh dấu log','Khoảng giữ lỗi chủ động: 2 s; chu kỳ probe: 0,1 s'],
 'results':['KT1 PASS  nguồn hoạt động, ghi dữ liệu','KT2 PASS  đích phục vụ, dữ liệu khớp','KT3 PASS  đích lỗi, quay lui, đo giờ','KT4 PASS  từ chối đích rỗng','KT5 PASS  nhận diện manifest sai','Mở test_results.csv, probes.csv và log để kiểm lại'],
 'cost':['Tổng Cloud: 64,75 USD/tháng × 25.000 = 1.618.750 VND','Vận hành Web: 400.000 VND/tháng','S2 và S3 giữ lại: 800.000 VND/tháng','Tổng có dự phòng 10%: 3.100.625 VND/tháng','Chuyển một lần: 1.200.000 VND','Năm đầu: 38.407.500 VND, trước thuế','Tất cả đơn giá là giả định học tập, không phải báo giá'],
 'roles':['SV1  Đặng Thái An  B24DCCC002','SV2  Phạm Minh Đức  B24DCCC071','SV3  Vũ Tiến Đạt  B24DCCC062','SV4  Trần Thị Lan Anh  MSSV cần bổ sung','Mở 03_Phan_cong_va_phieu_dong_gop.docx','Không xác nhận đóng góp cá nhân thay các thành viên']}

for i,(heading,key,notes) in enumerate(scenes,1):
 im=Image.new('RGB',(1920,1080),'#F2F5F8');dr=ImageDraw.Draw(im)
 dr.rectangle((0,0,1920,140),fill='#102B44');dr.text((55,42),heading,font=font(43,True),fill='white')
 if key and key.startswith('diagram'):content=Image.open(O/'thiet_ke'/['01_AsIs.png','02_ToBe.png','03_Migration.png'][int(key[-1])-1]).convert('RGB')
 elif key and (shots/(key+'.png')).exists():content=Image.open(shots/(key+'.png')).convert('RGB')
 elif key in sources:content=text_card(sources[key])
 else:content=text_card(['MPL Logistics  Phiếu giao đề 10','Chuyển Web chỉ đọc sang môi trường đích','Ghi nhận dữ liệu  Di chuyển  Đổi truy cập  Quay lui','Ảnh trình duyệt và log được tạo từ lần chạy thật','Mở README để tự chạy lại và xem hồ sơ gốc'])
 content.thumbnail((1180,740));x=40+(1180-content.width)//2;y=180+(740-content.height)//2
 im.paste(content,(x,y));dr.rectangle((x,y,x+content.width,y+content.height),outline='#B9C8D4',width=2)
 y=185
 for line in wrap(dr,notes,font(29),610):dr.text((1260,y),line,font=font(29),fill='#162C40');y+=43
 dr.line((45,965,1870,965),fill='#ABBCCA',width=2)
 dr.text((50,987),f'MPL  |  Minh họa từ demo thật  |  Cảnh {i:02d}/20',font=font(24),fill='#304C63')
 dr.text((1290,987),f'{(i-1)*18//60:02d}:{(i-1)*18%60:02d} đến {i*18//60:02d}:{i*18%60:02d}',font=font(24),fill='#304C63')
 im.save(V/f'scene_{i:02d}.png')
concat=''.join(f"file 'scene_{i:02d}.png'\nduration 18\n" for i in range(1,21))+"file 'scene_20.png'\n"
(V/'concat.txt').write_text(concat,encoding='utf-8')
(O/'tai_lieu/Video_chuong_muc.txt').write_text('\n'.join(f'{(i-1)*18//60:02d}:{(i-1)*18%60:02d} {x[0]}' for i,x in enumerate(scenes,1))+'\n',encoding='utf-8')
print('20 scenes prepared, duration 360 seconds')
