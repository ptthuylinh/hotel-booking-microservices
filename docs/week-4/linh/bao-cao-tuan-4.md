# Báo Cáo Công Việc Tuần 4 — Phan Thị Thùy Linh

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS  
**Sinh viên:** Phan Thị Thùy Linh — MSSV `24110271`  
**Học phần:** Điện toán đám mây (Cloud) — Đợt 1 năm học 2026–2027  
**Giảng viên hướng dẫn:** Thầy Huỳnh Xuân Phụng  
**Môi trường:** Docker Desktop trên Windows & AWS Academy Learner Lab, Region `us-east-1` (Account ID: `0556-5295-1832`)  
**Repository:** https://github.com/pttlinh32/hotel-booking-microservices  
**Phân công Tuần 4:** Kiểm thử toàn diện End-to-End (Ma trận 8 Test Cases), Lập kịch bản & Sản xuất Video Demo nghiệm thu ($\le 10$ phút), Soạn thảo Báo cáo Tổng kết Đồ án hoàn chỉnh trên Form Online & Repo, Thiết kế Slide thuyết trình và chuẩn bị câu hỏi vấn đáp.  
**Số giờ thực hiện:** 9.5 giờ theo worklog  
**Trạng thái:** Hoàn thành toàn diện các hạng mục kiểm thử, video demo và hồ sơ nghiệm thu  
**Ngày thực hiện:** 28/10 – 02/11/2026  

---

### Bảng phân công công việc tuần 4 (Worklog)

| STT | Thành viên | MSSV | Vai trò chính trong Tuần 4 | Số giờ | Trạng thái |
|:---:|---|:---:|---|:---:|:---:|
| 1 | **Phan Thị Thùy Linh** | `24110271` | **Backend Architecture, Comprehensive Testing, Video Demo & Final Documentation:** Xây dựng ma trận kiểm thử E2E (8 test cases) và script tự động; Biên tập và sản xuất Video Demo ($\le 10$ phút); Soạn thảo Báo cáo Tổng kết trên Form Online & Repo; Thiết kế Slide Thuyết trình và bộ câu hỏi vấn đáp. | 9.5 giờ | Hoàn thành |
| 2 | **Cao Hoàng Phúc** | `24110303` | **Cloud Infrastructure, Resilience, Cost Optimization & Teardown:** Kiểm thử chịu lỗi hạ tầng (Chaos Testing trên ECS/ALB/RDS); Phân tích chi phí & giải pháp tối ưu AWS; Hoàn thiện Sơ đồ Kiến trúc Tổng thể; Xây dựng kịch bản dọn dẹp triệt để `teardown-environment.ps1`. | 9.5 giờ | Hoàn thành |

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

## 2. Sản Xuất Video Demo Nghiệm Thu Đồ Án ($\le 10$ Phút)

Tuân thủ nghiêm ngặt quy định nghiệm thu của môn học:
- **Thời lượng:** 9 phút 45 giây ($\le 10$ phút).
- **Độ phân giải:** 1080p (Full HD, 60fps), giọng thuyết minh rõ ràng, phụ đề tóm tắt điểm nhấn công nghệ.
- **Link Video nghiệm thu:** `[Cập nhật link YouTube Unlisted / Google Drive]`
- **Kịch bản chi tiết:** Được lưu đầy đủ tại [`docs/week-4/video-demo-script.md`](file:///d:/Năm%203/Cloud/project/hotel-booking-microservices/docs/week-4/video-demo-script.md).

### Các phân đoạn chính trong Video Demo:
1. **Phần 1 (0:00 - 1:30):** Giới thiệu nhóm Capstone, bài toán thực tế và Sơ đồ Kiến trúc Microservices trên ECS Fargate.
2. **Phần 2 (1:30 - 4:30):** Trình diễn luồng nghiệp vụ chuẩn (Happy Path) qua Postman, kiểm tra dữ liệu trong PostgreSQL, DynamoDB và log SQS.
3. **Phần 3 (4:30 - 6:30):** Demo tính năng chịu lỗi nghiệp vụ: Giao dịch bồi hoàn (Rollback) giải phóng phòng và Poison Message vào SQS DLQ.
4. **Phần 4 (6:30 - 8:30):** Demo giám sát CloudWatch (Dashboard, Alarms, Logs Insights tracing Correlation ID) và bắn tải ECS Auto Scaling.
5. **Phần 5 (8:30 - 9:30):** Demo khả năng tự phục hồi (Self-healing Fargate) và thao tác dọn dẹp tài nguyên.
6. **Phần 6 (9:30 - 10:00):** Báo cáo tổng kết chi phí Lab (~$12.50/$50), bài học kinh nghiệm và lời cảm ơn GVHD.

---

## 3. Khai Báo Sử Dụng AI (Minh Bạch Theo Lưu Ý 1 Của GVHD)
- **Công cụ:** Antigravity IDE, Claude 3.5 Sonnet, ChatGPT-4o.
- **Mục đích hỗ trợ:**
  - Hỗ trợ xây dựng cấu trúc dàn ý ma trận kiểm thử E2E và kịch bản video demo.
  - Chuẩn hóa định dạng bảng biểu Markdown và rà soát cú pháp script.
- **Cam kết:** Toàn bộ mã nguồn backend Java microservices, việc triển khai trên AWS Learner Lab, video demo thực tế và nội dung phân tích chi tiết đều do nhóm tự thực hiện 100%.
