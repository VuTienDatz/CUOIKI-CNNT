# Bộ bài phiếu giao đề 10 MPL Logistics

Mở **01_Bao_cao_De10_MPL_theo_form_V2.docx** để đọc báo cáo chính. Bản này giữ bìa có khung, logo, học viện, giảng viên Nguyễn Xuân Dũng, lề, chữ Times New Roman và hệ tiêu đề của báo cáo V2. Bản đã kiểm tra có **16 trang tổng cộng**, gồm bìa, một trang mục lục và **14 trang nội dung chính**, đúng giới hạn 12–18 trang của phiếu và dưới 20 trang theo yêu cầu. Các chương được dàn liên tục.

## Điểm vào bộ file

| File | Nội dung |
|---|---|
| [Báo cáo theo form V2](01_Bao_cao_De10_MPL_theo_form_V2.docx) | 7 chương, đủ yêu cầu bắt buộc; có kết quả chạy thật và tài liệu tham khảo |
| [Hướng dẫn demo](02_Huong_dan_demo.docx) | 10 phần: chạy nhanh, hai container, tương tác và dựng hai VM thủ công |
| [Phân công và phiếu đóng góp](03_Phan_cong_va_phieu_dong_gop.docx) | 4 người, nhiệm vụ kỹ thuật, file phụ trách, bàn giao và phiếu cá nhân |
| [Kịch bản video](tai_lieu/Kich_ban_video.md) | 6 phút, chia cảnh theo từng người và KT1–KT3 |
| [Video minh họa 6 phút](tai_lieu/04_Video_minh_hoa_demo_6_phut.mp4) | Có phụ đề, dùng ảnh chụp demo trực tiếp và log thật; không có lời thuyết minh |
| [Đối chiếu yêu cầu](tai_lieu/Doi_chieu_yeu_cau.md) | Vị trí của mỗi yêu cầu trong báo cáo, mã và bằng chứng |
| `demo/` | Mã nguồn Python, cấu hình, hai file CMD và thư mục dữ liệu từng lần chạy |
| `thiet_ke/` | 3 sơ đồ PNG, Mermaid, bảng tài nguyên/IP/quyền và chi phí CSV |
| `minh_chung/` | Log, dữ liệu gốc, ảnh chụp và cấu hình của các lần chạy đã thực hiện |
| `bieu_mau/` | CSV kiểm thử VM sạch và phiếu đóng góp chưa xác nhận |

## Chạy lại demo

Yêu cầu Python 3.10 trở lên; không cần cài pip. Thử `python --version` hoặc `py -3 --version`. Từ thư mục `demo`:

```powershell
python demo.py
```

Để xem từng mốc và thao tác trình bày, dùng `python demo.py --interactive` hoặc nhấp `CHAY_DEMO.cmd`. URL xuyên suốt là `http://127.0.0.1:18080`. Nhấn Enter qua các mốc KT1, KT2, KT3; Enter cuối dừng các dịch vụ của lần demo.

Để chạy hai môi trường Linux cô lập, mở Docker Desktop và đợi Engine sẵn sàng, sau đó:

```powershell
docker version
docker pull python:3.12-slim
python demo.py --engine docker --interactive
```

Nếu dùng Windows Python Launcher, thay `python` bằng `py -3`. Nếu cổng bận, thêm `--base-port 19080` và dùng URL 19080. Nếu lệnh `docker` chưa có trên PATH, có thể truyền `--docker-bin "đường dẫn đầy đủ đến docker.exe"`.

Không cần thuê Cloud hoặc mua thiết bị. Script tạo 200 vận đơn giả, sao chép Web, kiểm hash, đổi route, tạo lỗi 503 và quay về nguồn. Source/target của Docker có namespace riêng; chúng cùng dùng một host và **chỉ mô phỏng Cloud**. Bản tiến trình chỉ dùng hai thư mục và hai server trên một máy. Bản hai VM có lệnh chi tiết trong hướng dẫn nhưng chưa được thực nghiệm.

## Phiên bản và khả năng tái hiện

- Bộ mã dùng Python chuẩn; lần kiểm chứng host dùng Python 3.12.14, Windows 11; phiên bản Docker và image ID chính xác nằm trong `minh_chung/demo_docker/`.
- Image đã dùng là `python:3.12-slim`; digest tải về trong lần chuẩn bị: `sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b`. Khi cần khóa phiên bản, pull digest rồi gắn lại tag cục bộ trước chạy; không tự cho tag mutable là cùng phiên bản.
- Mỗi lần thử tạo `demo/runs/<run_id>/`; `runs/latest.json` chỉ vị trí mới nhất trên máy đang chạy. Mở trực tiếp thư mục tương đối khi chuyển bộ file sang máy khác, vì đường dẫn tuyệt đối trong file cũ thuộc máy đã kiểm chứng.
- Các dữ liệu cố định luôn tạo ra 3 file, tổng 27.882 byte. Giờ chạy và số giây gián đoạn thay đổi giữa các lần.
- Tự động: đủ KT1–KT3 và 2 kiểm tra bổ sung. Xem `test_results.csv`, `summary.json`, hai manifest, dữ liệu KT1–KT3, `events.jsonl`, `probes.csv` và `rollback_timing.json`.

## Bằng chứng đã chạy

`minh_chung/demo_docker/` là lần dùng trong báo cáo: run `20261116T163608_953213Z`, KT1–KT3 PASS, 200 bản ghi khớp; gián đoạn quan sát **2,093 giây**, cận trên **2,125 giây**; có giữ lỗi chủ động khoảng 2 giây. UTC + 7 giờ là giờ Việt Nam; giữ nguyên log gốc.

`minh_chung/demo_local/` là bản kiểm tra nhanh hai tiến trình. `minh_chung/demo_video/` là lần chạy tương tác riêng dùng chụp ảnh video; run và số đo riêng nằm trong summary của thư mục đó. `minh_chung/anh_demo/` có ảnh chụp trình duyệt, metadata và console thật. Không trộn số đo giữa các run.

## Các nội dung nhóm cần điền thật

Điền lớp, số nhóm, hạn nộp và MSSV Trần Thị Lan Anh. Từng thành viên đọc, chỉnh và tự chạy phần mình, ghi file tạo/sửa, bằng chứng cùng lỗi đã xử lý rồi xác nhận phiếu cá nhân. Các ô chữ ký và đóng góp chưa được điền thay. Video minh họa không xác nhận 4 người đã trực tiếp thao tác; có thể quay lại theo kịch bản để bảo vệ.

## Giới hạn và nguồn

Web chỉ đọc, dữ liệu công khai giả; không có giao dịch mới tại đích nên quay lui không cần đồng bộ ngược. Chưa triển khai Cloud thật, HTTPS, lịch backup tự động, HA, DNS công cộng hoặc benchmark hiệu năng. Không dùng số đo lab làm SLA/RTO sản xuất.

Mọi đơn giá là giả định học tập lập ngày 16/11/2026, tỷ giá quy ước 25.000 VND/USD; chưa gồm thuế. Dự toán có compute, đĩa, backup, truyền ra, IPv4, DNS, log, nhân sự và hệ thống giữ lại. Không phải báo giá AWS. Phương án năm đầu 38.407.500 VND so với mốc giữ nội bộ 23.400.000 VND theo cùng giả định, không khẳng định tiết kiệm.

Mã demo viết cho bộ bài, dùng API thư viện chuẩn Python. Nguồn tham khảo chính: NIST SP 800-145, AWS Shared Responsibility, AWS migration strategies, Python http.server; URL và ngày truy cập trong tài liệu tham khảo báo cáo. Có dùng AI hỗ trợ soạn, viết mã và kiểm thử; nhóm phải đọc, sửa, chạy lại và chịu trách nhiệm giải thích phần nộp.
