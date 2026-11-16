# Kịch bản video 6 phút cho nhóm 4 người

Chạy `python demo.py --engine docker --interactive` từ thư mục `demo`. Bắt đầu quay khi đã sắp cửa sổ trình duyệt, terminal và thư mục evidence. Dùng URL gateway `http://127.0.0.1:18080` xuyên suốt. Không lấy thời lượng cảnh trong video đã dựng làm số đo gián đoạn.

| Thời gian | Thành viên | Thao tác và lời giải thích |
|---|---|---|
| 00:00–01:00 | SV1 An | Mở As-Is và To-Be. Giới thiệu ba dịch vụ; chuyển Web chỉ đọc, giữ dữ liệu nghiệp vụ và chia sẻ tập tin. Giải thích IaaS cho phép quản trị OS và ứng dụng nhưng nhóm vẫn phải vá, cấp quyền, sao lưu. |
| 01:00–02:00 | SV2 Đức | Mở container inspect hoặc `docker ps --filter label=mpl.demo`; chỉ hai môi trường riêng. Mở health qua gateway, cho thấy instance source. Giải thích địa chỉ ổn định và cổng nguồn/đích. |
| 02:00–03:20 | SV3 Đạt | Mở 200 bản ghi giả và source manifest. Nêu ba đường dẫn, số byte và SHA-256. Nhấn Enter qua KT1; chỉ archive và target manifest, cho thấy đối chiếu đầy đủ. |
| 03:20–04:20 | SV2 và SV3 | Refresh cùng URL, thấy instance target. Mở KT2_http.json và dữ liệu gốc. Giải thích đích phải khỏe và hash phải khớp trước đổi route. Nêu KT4 từ chối đích rỗng. |
| 04:20–05:30 | SV4 Lan Anh | Nhấn Enter từ KT2. Chỉ chuỗi HTTP 503 rồi route về source; mở probes.csv và rollback_timing.json. Đọc số giây của chính lần chạy. Kiểm dữ liệu KT3 bằng baseline. |
| 05:30–06:00 | SV4 và cả nhóm | Mở chi phí đủ compute, đĩa, truyền ra, backup và vận hành. Nêu đây là giá giả định; container/VM chỉ mô phỏng Cloud; chưa kiểm SLA hoặc tải thật. |

Nếu quay lỗi, giữ log và quay lại lần chạy mới, không sửa mốc giờ hoặc thay số đo. Mỗi người nên tự mở file kỹ thuật mình phụ trách, thực hiện lệnh và giải thích được kết quả. Video minh họa dựng kèm bộ file dùng ảnh demo trực tiếp và log thật; chưa thay phần chứng minh đóng góp của từng sinh viên.
