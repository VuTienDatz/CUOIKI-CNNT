# Hướng dẫn thực hiện dành cho nhóm

Thư mục này phục vụ dựng lại demo, phối hợp bốn thành viên và chuẩn bị bảo vệ. Danh mục tài liệu nộp giảng viên nằm tại [HUONG_DAN_GIANG_VIEN.md](../HUONG_DAN_GIANG_VIEN.md).

| Tài liệu | Cách dùng |
|---|---|
| [Hướng dẫn demo](02_Huong_dan_demo.docx) | Chạy tự động, hai container, chế độ tương tác và hai VM thủ công |
| [Phân công và phiếu đóng góp](03_Phan_cong_va_phieu_dong_gop.docx) | Đầu vào, đầu ra, bàn giao và xác nhận từng người |
| [Kịch bản quay 6 phút](Kich_ban_video.md) | Phân cảnh và thao tác cho từng vai trò |
| [Chương mục video minh họa](Video_chuong_muc.txt) | Tìm nhanh một cảnh trong video mẫu |

## Trình tự hoàn thiện

1. Mở báo cáo cá nhân tương ứng trong `../bao_cao_ca_nhan/`; đọc phần kỹ thuật, file và ca kiểm thử đã được phân công.
2. Dựng và chạy lại theo hướng dẫn. Mỗi lần chạy tạo thư mục mới trong `../demo/runs/`; không sửa log minh chứng cũ.
3. Ghi phạm vi tự làm, thay đổi đã thực hiện, người hỗ trợ và lỗi thực tế. Đối chiếu lại với báo cáo cá nhân trước khi ký.
4. Điền lớp, số nhóm theo danh sách học phần, ngày nộp và ngày ký. MSSV của Lan Anh đang dùng mã tạm `B24DCCC0` theo thông tin được cung cấp.
5. Quay video theo phân vai nếu cần chứng minh thao tác cá nhân; video minh họa có sẵn chỉ giúp xem trước luồng kiểm chứng.
6. Khi lưu một lần thử mới làm bằng chứng nộp, chép nguyên `evidence/` sang thư mục `minh_chung/` có tên riêng và giữ run ID. Không lấy số giây của lần khác để điền.

## Phân vai

- SV1 Đặng Thái An: khảo sát và chọn mô hình Cloud; giải thích phạm vi chuyển/giữ.
- SV2 Phạm Minh Đức: dựng đích, gateway, cổng và health gate.
- SV3 Vũ Tiến Đạt: tạo dữ liệu, chuyển archive, kiểm manifest và phản hồi HTTP.
- SV4 Trần Thị Lan Anh: dự toán, bảng kiểm, lỗi đích và quay lui có đo giờ.

Các vai trò cùng tham gia kiểm thử và nắm kiến trúc chung. Không kê khai việc chưa thực hiện, chữ ký thay hoặc lỗi không có căn cứ. Bản hai VM chưa được kiểm chứng trong hồ sơ hiện tại; cần ghi kết quả riêng nếu chọn nhánh này.
