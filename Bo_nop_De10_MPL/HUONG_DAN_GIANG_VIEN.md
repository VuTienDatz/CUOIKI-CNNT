# Danh mục hồ sơ đánh giá đề 10

Hồ sơ trình bày giải pháp chuyển Web công khai của doanh nghiệp giả định MPL Logistics, giữ dữ liệu nghiệp vụ và chia sẻ tập tin nội bộ. Báo cáo chung và báo cáo cá nhân được tách khỏi tài liệu hướng dẫn tổ chức thực hiện.

## Báo cáo

| Hồ sơ | Nội dung |
|---|---|
| [Báo cáo chung theo form V2](01_Bao_cao_De10_MPL_theo_form_V2.docx) | 7 chương, 16 trang tổng, 14 trang chính; đáp ứng yêu cầu, kiến trúc, chi phí, triển khai, kiểm thử và đánh giá |
| [SV1 Đặng Thái An](bao_cao_ca_nhan/SV1_B24DCCC002_Dang_Thai_An_Bao_cao_ca_nhan.docx) | Khảo sát, lựa chọn mô hình Cloud và đầu vào thiết kế |
| [SV2 Phạm Minh Đức](bao_cao_ca_nhan/SV2_B24DCCC071_Pham_Minh_Duc_Bao_cao_ca_nhan.docx) | Môi trường đích, gateway và kiểm tra trước chuyển hướng |
| [SV3 Vũ Tiến Đạt](bao_cao_ca_nhan/SV3_B24DCCC062_Vu_Tien_Dat_Bao_cao_ca_nhan.docx) | Dữ liệu mẫu, archive, manifest và đối chiếu toàn vẹn |
| [SV4 Trần Thị Lan Anh](bao_cao_ca_nhan/SV4_B24DCCC0_Tran_Thi_Lan_Anh_Bao_cao_ca_nhan.docx) | Chi phí, nghiệm thu, quay lui và đo gián đoạn |
| [Đối chiếu phiếu giao đề](tai_lieu/Doi_chieu_yeu_cau.md) | Vị trí từng yêu cầu trong báo cáo và file kiểm chứng |

Các báo cáo cá nhân theo đủ 10 mục của mẫu học phần. Kết quả kỹ thuật được dẫn từ lần chạy chung; phạm vi trực tiếp thực hiện và cam kết cần sinh viên xác nhận, không được suy từ việc có sẵn mã nguồn.

## Minh chứng kỹ thuật

- [Bảng kiểm thử có kết quả thực tế](minh_chung/demo_docker/test_results.csv).
- [Kết quả tổng hợp và thông tin môi trường](minh_chung/demo_docker/summary.json).
- [Manifest nguồn](minh_chung/demo_docker/source_manifest.json), [manifest đích](minh_chung/demo_docker/target_manifest.json) và [archive đã chuyển](minh_chung/demo_docker/transfer.zip).
- [Thời gian quay lui](minh_chung/demo_docker/rollback_timing.json), [chuỗi HTTP](minh_chung/demo_docker/probes.csv) và dữ liệu phản hồi KT1–KT3 trong cùng thư mục.
- [Video minh họa 6 phút](tai_lieu/04_Video_minh_hoa_demo_6_phut.mp4), dùng ảnh demo trực tiếp và log thật; có phụ đề, không có lời thuyết minh.

KT1–KT3 đã đạt trên hai container Linux riêng, cùng host. VM/container đích chỉ mô phỏng Cloud. Không kết luận SLA, HA, sức tải hoặc triển khai Cloud thật từ lần thử này. Chi phí là giả định, không phải báo giá nhà cung cấp.

## Chạy lại

Từ thư mục repository, dùng `python Bo_nop_De10_MPL/demo/demo.py` để chạy bản hai tiến trình. Bản hai container dùng thêm `--engine docker` sau khi Docker Engine hoạt động và đã tải image. Cấu hình, phiên bản và hướng dẫn tái hiện nằm trong [README kỹ thuật](README.md).

`huong_dan_nhom/` là tài liệu thao tác, phân công và chuẩn bị bảo vệ dành cho sinh viên. File tạm, cache và thư mục chạy thử được loại khỏi Git; minh chứng đánh giá vẫn được giữ đầy đủ tại `minh_chung/`.
