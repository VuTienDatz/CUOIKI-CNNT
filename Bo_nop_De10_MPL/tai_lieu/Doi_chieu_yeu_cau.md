# Đối chiếu phiếu giao đề 10 và hồ sơ nộp

| Yêu cầu | Báo cáo theo form V2 | File và bằng chứng |
|---|---|---|
| 12–18 trang nội dung chính | 14 trang chính, 16 trang tổng | `01_Bao_cao_De10_MPL_theo_form_V2.docx` |
| Hiện trạng và phụ thuộc 3 dịch vụ | 1.1–1.3 | Sơ đồ As-Is, bảng kiểm kê và quyết định |
| Chọn dịch vụ chuyển và giữ | 1.3 | Chuyển Web chỉ đọc; giữ DB và file; tiêu chí rõ |
| Kiến trúc trước sau | 1.2 và 2.2 | `thiet_ke/01_AsIs.png`, `02_ToBe.png`, `so_do.mmd` |
| So IaaS/PaaS/SaaS đủ 4 góc | 2.1 | Quyền kiểm soát, tài nguyên, bảo mật, vận hành |
| Tài nguyên, IP và quyền | 2.2–2.3 | `tai_nguyen_ip_quyen.csv` và ma trận quyền trong Word |
| Chi phí đủ khoản, đơn vị và giả định | 3.1 | `chi_phi_gia_dinh.csv`; toàn bộ là giả định, không dùng báo giá |
| Chuyển một dịch vụ giữa 2 môi trường | 4.1–4.3 | Hai container nguồn đích; mã `demo/`; có hướng dẫn VM |
| KT1 nguồn hoạt động, ghi nhận dữ liệu | 5.2 và 6.1 | `KT1_data.json`, `KT1_http.json`, `source_manifest.json` |
| KT2 truy cập đích và dữ liệu khớp | 5.2 và 6.1 | `KT2_data.json`, `KT2_http.json`, `target_manifest.json`, route |
| KT3 đích lỗi, quay lui, đo gián đoạn | 5.1–5.2 và 6.1 | `KT3_data.json`, timing, probes, route và log |
| Bảng kiểm đủ đầu vào đến kết luận | 5.2 | `minh_chung/demo_docker/test_results.csv` |
| Dấu thời gian, dữ liệu đo gốc | 6.1 | UTC trong events, HTTP, probes và summary; không benchmark tải |
| README, phiên bản, dựng lại, chạy test | 4.2 | README gốc bộ file; hướng dẫn Word; tools |
| Video 5–7 phút | 7.1 | MP4 minh họa 6 phút và kịch bản phân vai |
| 4 người, mỗi người kỹ thuật riêng | 7.1 | 4 báo cáo cá nhân theo mẫu; Word phân công và phiếu xác nhận trong huong_dan_nhom/ |
| Dữ liệu giả, môi trường được phép | 1.1 và 6.2 | 200 mã không có thông tin khách hàng; loopback lab |
| Nêu nguồn và cách dùng AI | 7.2 và tài liệu tham khảo | Nguồn chính thức, công bố AI, trách nhiệm chạy lại |
| Câu hỏi bảo vệ chi phí bỏ sót | 6.2 | Đĩa, truyền, backup, IPv4, log, nhân sự, chuyển một lần và phần giữ lại |

KT4 và KT5 là kiểm tra bổ sung. Phạm vi bắt buộc được nghiệm thu bằng KT1–KT3; các nội dung mở rộng không thay thế minh chứng lõi.
