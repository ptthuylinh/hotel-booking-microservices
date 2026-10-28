# Báo Cáo Công Việc Tuần 4 — Phan Thị Thùy Linh

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS  
**Sinh viên:** Phan Thị Thùy Linh — MSSV `24110271`  
**Học phần:** Điện toán đám mây (Cloud) — Đợt 1 năm học 2026–2027  
**Giảng viên hướng dẫn:** Thầy Huỳnh Xuân Phụng  
**Môi trường:** Docker Desktop trên Windows & AWS Academy Learner Lab, Region `us-east-1` (Account ID: `0556-5295-1832`)  
**Repository:** https://github.com/pttlinh32/hotel-booking-microservices  
**Phân công Tuần 4:** Kiểm thử toàn diện End-to-End (Ma trận 8 Test Cases) và chụp ảnh minh chứng; Soạn thảo Báo cáo Tổng kết Đồ án hoàn chỉnh trên Form Online & Repo; Push mã nguồn & tài liệu lên nhánh `week-4` và merge vào `main`.  
**Số giờ thực hiện:** 9.0 giờ theo worklog  
**Trạng thái:** Hoàn thành toàn diện các hạng mục kiểm thử E2E và hồ sơ nghiệm thu  
**Ngày thực hiện:** 28/10 – 02/11/2026  

---

### Bảng phân công công việc tuần 4 (Worklog)

| STT | Thành viên | MSSV | Vai trò chính trong Tuần 4 | Số giờ | Trạng thái |
|:---:|---|:---:|---|:---:|:---:|
| 1 | **Phan Thị Thùy Linh** | `24110271` | **Comprehensive E2E Testing & Final Documentation:** Xây dựng ma trận kiểm thử E2E (8 test cases) và chụp ảnh minh chứng; Soạn thảo Báo cáo Tổng kết Đồ án trên Form Online & Repo; Push mã nguồn & tài liệu lên nhánh `week-4` và merge vào `main`. | 9.0 giờ | Hoàn thành |
| 2 | **Cao Hoàng Phúc** | `24110303` | **Cloud Infrastructure, Video Demo, Resilience & Cost Optimization:** Toàn quyền sản xuất Video Demo ($\le 10$ phút); Kiểm thử chịu lỗi hạ tầng (Chaos Testing trên ECS/ALB/RDS); Phân tích chi phí & giải pháp tối ưu AWS; Hoàn thiện Sơ đồ Kiến trúc Tổng thể; Xây dựng kịch bản dọn dẹp triệt để `teardown-environment.ps1`. | 9.5 giờ | Hoàn thành |

---

## 1. Kết Quả Kiểm Thử Toàn Diện End-to-End (Ma Trận 8 Test Cases)

Để đảm bảo hệ thống microservices hoạt động ổn định và xử lý trơn tru mọi tình huống nghiệp vụ thực tế, em đã xây dựng kịch bản tự động hóa [`scripts/e2e-test.ps1`](file:///d:/Năm%203/Cloud/project/hotel-booking-microservices/scripts/e2e-test.ps1) kiểm thử tuần tự 8 kịch bản trọng yếu qua Application Load Balancer.

### 1.1. Ma trận kiểm thử tổng thể (E2E Test Matrix)

| Mã | Tên kịch bản kiểm thử | Mô tả chi tiết & Phương thức | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
|:---:|---|---|---|---|:---:|
| **TC01** | Tra cứu danh sách phòng | `GET /api/rooms?status=AVAILABLE` qua ALB | HTTP 200, danh sách các phòng khả dụng | HTTP 200, hiển thị danh sách phòng | **PASS** |
| **TC02** | Happy Path Đặt phòng | `POST /api/bookings` với thông tin hợp lệ | HTTP 201 Created, sinh mã `bookingCode`, phòng đổi sang `RESERVED`, DynamoDB ghi audit, SQS tiêu thụ | HTTP 201 Created, mã `BK-xxxx`, luồng chạy hoàn tất | **PASS** |
| **TC03** | Validation dữ liệu đầu vào | `POST /api/bookings` với email sai và ngày quá khứ | HTTP 400 Bad Request chuẩn RFC 7807 (Problem Details) | HTTP 400, ẩn stack trace nội bộ | **PASS** |
| **TC04** | Xung đột đặt phòng trùng | `POST /api/bookings` với phòng đang ở trạng thái `RESERVED` | HTTP 400/409 Conflict, chặn không cho đặt đè | HTTP 400, phòng được bảo vệ | **PASS** |
| **TC05** | Bồi hoàn giao dịch phân tán | Giả lập sự cố downstream sau khi khóa phòng | Phòng tự động hồi phục về `AVAILABLE` (không deadlock) | Phòng tự rollback `AVAILABLE` | **PASS** |
| **TC06** | Poison Message vào DLQ | Đẩy tin nhắn hỏng vào SQS queue | Consumer retry 3 lần, chuyển vào `booking-notification-dlq` | DLQ nhận tin, kích hoạt Alarm | **PASS** |
| **TC07** | Distributed Tracing | Gửi header `X-Correlation-Id` qua REST | Header trả về trong Response và xuất hiện trong toàn bộ log | Header echo chính xác, trace 3 services | **PASS** |
| **TC08** | Hiệu năng & Ổn định | Gửi liên tục 20 requests liên tiếp vào ALB | Tỷ lệ thành công $\ge 90\%$, độ trễ trung bình $< 150$ms | Thành công 100%, latency trung bình ~45ms | **PASS** |

---

## 2. Push Mã Nguồn & Tài Liệu Lên GitHub

Đảm bảo toàn bộ source code 3 services, scripts và tài liệu tuần 4 được commit đầy đủ và đúng quy cách:
- Commit tất cả thay đổi lên nhánh `week-4`.
- Tạo Pull Request và merge vào nhánh `main`.
- Kiểm tra repo GitHub: đủ các thư mục `booking-service/`, `room-service/`, `notification-service/`, `scripts/`, `docs/week-4/`.

---

## 3. Khai Báo Sử Dụng AI (Minh Bạch Theo Lưu Ý 1 Của GVHD)
- **Công cụ:** Antigravity IDE, Claude 3.5 Sonnet, ChatGPT-4o.
- **Mục đích hỗ trợ:**
  - Hỗ trợ xây dựng cấu trúc dàn ý ma trận kiểm thử E2E và báo cáo tuần 4.
  - Chuẩn hóa định dạng bảng biểu Markdown và rà soát cú pháp script.
- **Cam kết:** Toàn bộ mã nguồn backend Java microservices, việc triển khai trên AWS Learner Lab và nội dung phân tích chi tiết đều do nhóm tự thực hiện 100%.
