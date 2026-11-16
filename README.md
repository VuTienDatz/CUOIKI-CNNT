# Chuyển đổi hạ tầng máy chủ doanh nghiệp lên Cloud

Bài tập lớn học phần Nhập môn công nghệ nền tảng, phiếu giao đề 10. Tình huống MPL Logistics lựa chọn chuyển Web công khai sang IaaS theo thiết kế, giữ dữ liệu nghiệp vụ và chia sẻ tập tin nội bộ. Demo kiểm chứng di chuyển Web chỉ đọc, đối chiếu dữ liệu, chuyển hướng truy cập và quay lui khi đích lỗi.

## Tài liệu dành cho giảng viên

- [Danh mục hồ sơ và minh chứng](Bo_nop_De10_MPL/HUONG_DAN_GIANG_VIEN.md).
- [Báo cáo chung theo form V2](Bo_nop_De10_MPL/01_Bao_cao_De10_MPL_theo_form_V2.docx): 16 trang tổng, gồm 14 trang nội dung chính.
- [Bốn báo cáo cá nhân](Bo_nop_De10_MPL/bao_cao_ca_nhan/): trình bày theo mẫu 10 mục của học phần.
- [Bảng đối chiếu yêu cầu](Bo_nop_De10_MPL/tai_lieu/Doi_chieu_yeu_cau.md), [minh chứng gốc](Bo_nop_De10_MPL/minh_chung/) và [video minh họa 6 phút](Bo_nop_De10_MPL/tai_lieu/04_Video_minh_hoa_demo_6_phut.mp4).

## Tài liệu dành cho thành viên nhóm

- [Hướng dẫn thực hiện và phân vai](Bo_nop_De10_MPL/huong_dan_nhom/README.md).
- [Cách dựng lại và chạy kiểm thử](Bo_nop_De10_MPL/README.md).

## Chạy nhanh

Yêu cầu Python 3.10 trở lên, không cần gói pip bổ sung. Từ thư mục repository:

```powershell
python Bo_nop_De10_MPL/demo/demo.py
```

Để dùng hai container Linux, mở Docker Desktop, tải image bằng `docker pull python:3.12-slim`, rồi chạy:

```powershell
python Bo_nop_De10_MPL/demo/demo.py --engine docker --interactive
```

Demo ghi dữ liệu lần chạy vào `Bo_nop_De10_MPL/demo/runs/`; thư mục này được Git bỏ qua. Các bằng chứng dùng trong báo cáo được giữ riêng tại `minh_chung/`. Hai container cùng host chỉ mô phỏng Cloud; chưa triển khai Cloud thật hoặc kiểm chứng SLA.

## Thành viên

| Vai trò | Họ và tên | Mã sinh viên | Phần kỹ thuật |
|---|---|---|---|
| SV1 | Đặng Thái An | B24DCCC002 | Khảo sát và lựa chọn mô hình Cloud |
| SV2 | Phạm Minh Đức | B24DCCC071 | Môi trường đích và cấu hình truy cập |
| SV3 | Vũ Tiến Đạt | B24DCCC062 | Di chuyển và đối chiếu dữ liệu |
| SV4 | Trần Thị Lan Anh | B24DCCC0 | Chi phí, kiểm thử và quay lui |

Tài liệu đề bài và mẫu gốc được lưu tại `tai_lieu_goc/`. File tạm, cache, bản render kiểm tra và dữ liệu chạy thử không được đưa vào repository.
