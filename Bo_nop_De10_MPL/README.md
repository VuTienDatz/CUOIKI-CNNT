# Hồ sơ kỹ thuật MPL Logistics

Phiếu giao đề 10: thiết kế giải pháp chuyển đổi hạ tầng máy chủ doanh nghiệp lên Cloud. Mục tiêu demo là chuyển Web chỉ đọc giữa hai môi trường thử nghiệm, bảo toàn dữ liệu, đổi nơi phục vụ qua một endpoint ổn định và quay về nguồn khi đích lỗi.

## Đọc tài liệu theo vai trò

| Người đọc | Tài liệu chính |
|---|---|
| Giảng viên | [Danh mục hồ sơ đánh giá](HUONG_DAN_GIANG_VIEN.md), báo cáo chung, 4 báo cáo cá nhân, sơ đồ và minh chứng |
| Thành viên nhóm | [Hướng dẫn thực hiện](huong_dan_nhom/README.md), hướng dẫn demo Word, phân công và kịch bản video |
| Người chạy lại | Các lệnh bên dưới và mã trong `demo/` |

## Cấu trúc bộ bài

```text
01_Bao_cao_De10_MPL_theo_form_V2.docx
bao_cao_ca_nhan/       4 báo cáo theo mẫu học phần
huong_dan_nhom/        hướng dẫn thao tác và tổ chức công việc
demo/                  mã nguồn Python và cấu hình
thiet_ke/              sơ đồ, tài nguyên/IP/quyền, dự toán
minh_chung/             log, dữ liệu gốc, ảnh và archive đã kiểm chứng
tai_lieu/              đối chiếu yêu cầu và video minh họa
bieu_mau/              biểu mẫu sạch để xác nhận và chạy lại
```

## Yêu cầu môi trường

- Python 3.10 trở lên; chỉ dùng thư viện chuẩn, không cần cài pip.
- Bản hai container cần Docker Desktop với Linux Engine đang hoạt động.
- Cổng mặc định trên host: gateway 18080, nguồn 18081, đích 18082. Dùng `--base-port 19080` nếu bị chiếm.
- Toàn bộ dữ liệu là giả. Không cần thuê Cloud hoặc mua thiết bị.

## Chạy demo và kiểm thử

Từ thư mục `demo`:

```powershell
python --version
python demo.py
```

Chế độ tương tác dừng tại từng mốc để quan sát:

```powershell
python demo.py --interactive
```

Trên Windows có thể dùng `py -3` thay `python`, hoặc mở `CHAY_DEMO.cmd`. Trình duyệt giữ URL `http://127.0.0.1:18080` trong cả ba ca. Nhấn Enter lần lượt qua KT1, KT2 và KT3; Enter cuối dừng các dịch vụ do demo tạo.

Để dùng hai môi trường Linux cô lập:

```powershell
docker version
docker pull python:3.12-slim
python demo.py --engine docker --interactive
```

Nếu Docker chưa có trên PATH, thêm `--docker-bin "đường dẫn đầy đủ đến docker.exe"`. Hướng dẫn hai VM thủ công nằm trong `huong_dan_nhom/02_Huong_dan_demo.docx`; nhánh này chưa có kết quả nghiệm thu trong hồ sơ chung.

## Luồng kiểm chứng

| Ca | Nội dung | Bằng chứng chính |
|---|---|---|
| KT1 | Nguồn phục vụ và ghi baseline 200 vận đơn | `KT1_data.json`, `KT1_http.json`, `source_manifest.json` |
| KT2 | Đóng gói, nhận dữ liệu, kiểm hash và chuyển sang đích | `target_manifest.json`, `KT2_http.json`, `cutover_route.json` |
| KT3 | Gây HTTP 503, quay về nguồn, kiểm dữ liệu và đo gián đoạn | `KT3_http.json`, `rollback_timing.json`, `probes.csv` |
| KT4 bổ sung | Từ chối chuyển hướng sang đích rỗng | `events.jsonl` |
| KT5 bổ sung | Phát hiện một hash trên bản sao manifest bị sửa | `negative_manifest.json` |

Các file trên nằm trong `evidence/` của mỗi run. `test_results.csv` giữ đầu vào, thao tác, kỳ vọng, thực tế, kết luận và tên bằng chứng. Khi chạy mới, dữ liệu được tạo tại `demo/runs/<run_id>/`; `runs/latest.json` chỉ vị trí lần chạy mới nhất trên máy hiện tại. Thư mục này không được Git theo dõi.

## Bằng chứng được lưu trong repository

`minh_chung/demo_docker/` là lần dùng trong báo cáo: run `20261116T163608_953213Z`. KT1–KT3 đạt; 200 bản ghi và 3 file, tổng 27.882 byte, khớp sau chuyển và quay lui. Gián đoạn quan sát 2,093 giây, cận trên 2,125 giây; có giữ lỗi chủ động khoảng 2 giây. Thư mục này có `transfer.zip` của đúng lần chuyển đổi.

`demo_local/` giữ bằng chứng bản hai tiến trình. `demo_video/` giữ lần tương tác dùng chụp ảnh; `anh_demo/` có ảnh, metadata và console tương ứng. Không trộn số đo giữa các run. Timestamp gốc dùng UTC; cộng 7 giờ để xem theo giờ Việt Nam.

## Phiên bản và giới hạn

Lần kiểm chứng dùng host Windows 11, Python 3.12.14 và image `python:3.12-slim`; Docker version và image ID có trong hồ sơ. Digest image đã tải: `sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b`. Tag có thể thay đổi; cần khóa digest nếu muốn tái hiện đúng image.

Hai container cùng một host chỉ mô phỏng Cloud. Web chỉ đọc, không có giao dịch mới ở đích; chưa thử Cloud thật, HTTPS, DNS công cộng, lịch backup tự động, HA hay tải doanh nghiệp. Số đo lab không phải SLA hoặc RTO sản xuất.

Đơn giá ở bảng chi phí là giả định học tập ngày 16/11/2026, tỷ giá quy ước 25.000 VND/USD, trước thuế. Dự toán gồm compute, đĩa, backup, truyền ra, IPv4, DNS, log, nhân sự và dịch vụ giữ lại; không phải báo giá AWS.

## Nguồn và công cụ hỗ trợ

Nguồn chính gồm NIST SP 800-145, AWS Shared Responsibility, hướng dẫn migration của AWS và tài liệu Python. URL và ngày truy cập có trong báo cáo chung. Mã dùng thư viện chuẩn Python. AI hỗ trợ biên soạn và mã nền; từng sinh viên xác nhận phần tự chỉnh sửa, chạy lại và hỗ trợ đã nhận trong báo cáo cá nhân.

## Kiểm tra toàn vẹn bộ nộp

Từ thư mục repository chạy: `python Bo_nop_De10_MPL/demo/tools/verify_submission.py`. Công cụ kiểm SHA-256 của các file bàn giao và đối chiếu lại bằng chứng KT1–KT3. Quy tắc .gitattributes giữ nguyên byte để tránh thay đổi mã băm khi Git chuyển kiểu xuống dòng.
