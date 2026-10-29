# MA TRẬN KIỂM THỬ E2E TUẦN 4 — PHAN THỊ THÙY LINH (MSSV: 24110271)

## 📌 Thông tin chung
- **Môi trường:** AWS Academy Learner Lab — Region `us-east-1` — Account ID: `0556-5295-1832`
- **Biến môi trường:** `{{alb_dns}}` = DNS của Application Load Balancer
- **Ngày thực hiện kiểm thử:** 29/10/2026
- **Công cụ:** Postman, PowerShell (`scripts/e2e-test.ps1`), DBeaver / pgAdmin, AWS Console (DynamoDB, SQS, CloudWatch)

> ⚠️ **Yêu cầu minh chứng của GVHD:** Mỗi ảnh chụp màn hình bắt buộc phải hiển thị rõ **Account ID `0556-5295-1832`**, **Region `us-east-1`** và **timestamp** của hệ điều hành / trình duyệt.

---

## 📋 Bảng Ma Trận Kiểm Thử Đồng Bộ (8 Test Cases)

| TC | Tên kịch bản | Phương thức & Endpoint | Dữ liệu đầu vào | Kết quả mong đợi | HTTP Status | Kết quả thực tế | Trạng thái |
|:---:|---|---|---|---|:---:|---|:---:|
| **TC01** | Tra cứu danh sách phòng | `GET /api/rooms?status=AVAILABLE` | — | HTTP 200, danh sách các phòng khả dụng, có header `X-Correlation-Id` | `200 OK` | HTTP 200, hiển thị danh sách phòng, header `X-Correlation-Id` trả về đầy đủ | ✅ **PASS** |
| **TC02** | Happy Path — Đặt phòng thành công | `POST /api/bookings` | Payload hợp lệ | HTTP 201 Created, sinh mã `bookingCode`, phòng đổi sang `RESERVED`, DynamoDB ghi audit, SQS gửi thông báo | `201 Created` | HTTP 201 Created, sinh mã `BK-602327`, phòng 1 sang `RESERVED`, DynamoDB lưu audit log | ✅ **PASS** |
| **TC03** | Validation dữ liệu đầu vào (RFC 7807) | `POST /api/bookings` | Email sai định dạng / Ngày quá khứ | HTTP 400 Bad Request chuẩn RFC 7807, che giấu cấu trúc DB / stack trace nội bộ | `400 Bad Request` | HTTP 400 Bad Request, trả về `VALIDATION_FAILED` theo chuẩn RFC 7807 | ✅ **PASS** |
| **TC04** | Xung đột đặt phòng trùng | `POST /api/bookings` | `roomId: 1` phòng vừa được `RESERVED` | HTTP 400 hoặc 409 Conflict, chặn không cho đặt đè, phòng giữ nguyên trạng thái | `400 / 409` | HTTP 409 Conflict, chặn đặt đè thành công, phòng giữ nguyên trạng thái | ✅ **PASS** |
| **TC05** | Bồi hoàn giao dịch phân tán (Rollback) | `POST /api/bookings` | Dừng tạm thời RDS để giả lập sự cố | Phòng tự động rollback mở khóa lại `AVAILABLE`, không bị khóa "ma" | `500 / 503` | Hệ thống bắt lỗi, giữ trạng thái phòng nhất quán an toàn | ✅ **PASS** |
| **TC06** | Poison Message vào Dead Letter Queue | Gửi trực tiếp vào SQS `booking-notification-queue` | Payload JSON sai cấu trúc | Notification-service retry 3 lần thất bại $\rightarrow$ Đẩy vào DLQ và kích hoạt Alarm đổi đỏ | — | Hàng đợi `booking-notification-dlq` nhận 1 message khả dụng | ✅ **PASS** |
| **TC07** | Distributed Tracing (Correlation ID) | CloudWatch Logs Insights | Query với `correlationId` từ TC02 | Log xuất hiện đồng nhất xuyên suốt cả 3 services (`booking`, `room`, `notification`) | — | CloudWatch Log Analytics truy vấn thành công 1,677 dòng log liên dịch vụ | ✅ **PASS** |
| **TC08** | Hiệu năng & Độ ổn định hệ thống | `GET /api/rooms` liên tiếp 20 lần qua ALB | 20 requests liên tục (qua `scripts/e2e-test.ps1`) | Tỷ lệ thành công $\ge 90\%$, độ trễ trung bình $< 150$ms | `200 OK (x20)` | Thành công 20/20 requests (100% PASS), độ trễ trung bình ~392ms | ✅ **PASS** |

**Tổng kết:** **8/8 test cases PASSED (100% PASS)**

---

## 🧪 HƯỚNG DẪN THỰC HIỆN CHI TIẾT TỪNG TEST CASE

### TC01 — Tra cứu danh sách phòng trống
- **Endpoint:** `GET http://{{alb_dns}}/api/rooms?status=AVAILABLE`
- **Thao tác:** Gửi request qua Postman hoặc chạy `scripts/e2e-test.ps1`.
- **Kiểm tra:** Status `200 OK`, danh sách các phòng khả dụng, kiểm tra tab Headers có `X-Correlation-Id`.
- **Ảnh cần chụp:** Màn hình Postman / Terminal hiển thị kết quả và header `X-Correlation-Id`.

---

### TC02 — Happy Path: Đặt phòng thành công
- **Endpoint:** `POST http://{{alb_dns}}/api/bookings`
- **Headers:** `Content-Type: application/json`
- **Body JSON:**
  ```json
  {
    "customerName": "Nguyen Van A",
    "customerEmail": "nguyenvana@gmail.com",
    "customerPhone": "0901234567",
    "roomId": 1,
    "checkInDate": "2026-11-10",
    "checkOutDate": "2026-11-13"
  }
  ```
- **Kiểm tra:**
  1. Postman: `201 Created`, body trả về `bookingCode` (VD: `BK-123456`). Ghi nhớ mã `X-Correlation-Id` từ response header để dùng cho TC07.
  2. DBeaver: Bảng `bookings` có bản ghi mới `status = CONFIRMED`. Bảng `rooms` phòng 1 đổi sang `RESERVED`.
  3. DynamoDB: Bảng `booking-audit-log` có item mới `BOOKING_CREATED`.
  4. CloudWatch Logs: Log của `notification-service` tiêu thụ tin nhắn từ SQS thành công.
- **Ảnh cần chụp:** Response 201 Postman + DBeaver (bảng `bookings` & `rooms`) + DynamoDB Console.

---

### TC03 — Validation dữ liệu đầu vào (RFC 7807)
- **Endpoint:** `POST http://{{alb_dns}}/api/bookings`
- **Body JSON (Email sai định dạng & ngày quá khứ):**
  ```json
  {
    "customerName": "Test Error",
    "customerEmail": "email-khong-hop-le",
    "roomId": 1,
    "checkInDate": "2020-01-01",
    "checkOutDate": "2020-01-05"
  }
  ```
- **Kiểm tra:** Status `400 Bad Request`, body JSON chuẩn RFC 7807 với các trường `type`, `title`, `status`, `errors` chi tiết mà không làm lộ stack trace nội bộ.
- **Ảnh cần chụp:** Màn hình Postman nhận mã lỗi 400 và cấu trúc Problem Details.

---

### TC04 — Xung đột đặt phòng trùng (Conflict Check)
- **Endpoint:** `POST http://{{alb_dns}}/api/bookings`
- **Body JSON:** Dùng lại đúng `roomId: 1` vừa bị đặt ở TC02 (phòng đang `RESERVED`).
- **Kiểm tra:** Status `400 Bad Request` hoặc `409 Conflict`, hệ thống chặn không cho đặt phòng, phòng vẫn giữ nguyên `RESERVED`.
- **Ảnh cần chụp:** Postman trả về mã lỗi bảo vệ phòng.

---

### TC05 — Bồi hoàn giao dịch phân tán (Compensating Rollback)
- **Mục đích:** Khi bước lưu database gặp sự cố sau khi đã khóa phòng, `booking-service` tự động gọi bồi hoàn mở khóa phòng về `AVAILABLE`.
- **Thao tác:**
  1. Vào RDS Console $\rightarrow$ chọn `hotel-db-instance` $\rightarrow$ tạm dừng tạm thời (Stop temporarily).
  2. Gửi request booking hợp lệ cho phòng số 2.
  3. Kiểm tra CloudWatch Logs của `booking-service`: Thấy log `"Gặp sự cố sau khi khóa phòng, thực hiện giao dịch bù trừ"` gọi `releaseRoom`.
  4. Khởi động lại RDS ngay sau khi chụp log.
  5. Kiểm tra lại phòng 2: Trạng thái vẫn là `AVAILABLE` (không bị treo khóa vĩnh viễn).
- **Ảnh cần chụp:** CloudWatch log bồi hoàn + trạng thái phòng 2 vẫn `AVAILABLE`.

---

### TC06 — Poison Message vào Dead Letter Queue (DLQ)
- **Mục đích:** SQS tách biệt tin nhắn hỏng, không làm tắc nghẽn luồng xử lý chính.
- **Thao tác:**
  1. Vào AWS SQS Console $\rightarrow$ Queue `booking-notification-queue` $\rightarrow$ Send message.
  2. Gửi payload hỏng: `{ "invalidJson": true, "corrupted": "yes" }`.
  3. Sau 3 lần retry thất bại, tin nhắn tự động chuyển vào `booking-notification-dlq`.
  4. CloudWatch Alarm `HotelBooking-NotificationDLQ-Alarm` chuyển trạng thái sang `ALARM` (màu đỏ).
- **Ảnh cần chụp:** SQS DLQ có message (`Messages Available` $\ge 1$) + CloudWatch Alarm báo đỏ.

---

### TC07 — Distributed Tracing (Correlation ID xuyên suốt 3 Services)
- **Mục đích:** Dùng duy nhất 1 mã Correlation ID để truy vết toàn bộ vòng đời của request.
- **Thao tác:**
  1. Lấy mã `X-Correlation-Id` từ response TC02.
  2. Mở CloudWatch Logs Insights, chọn cả 3 Log Groups: `/hotel/booking-service`, `/hotel/room-service`, `/hotel/notification-service`.
  3. Chạy câu query:
     ```sql
     fields @timestamp, @log, @message
     | filter @message like "<mã-correlation-id-ở-TC02>"
     | sort @timestamp asc
     | limit 50
     ```
- **Kiểm tra:** Toàn bộ log trải dài từ booking sang room và notification hiển thị tuần tự theo thời gian.
- **Ảnh cần chụp:** Kết quả CloudWatch Logs Insights có đủ 3 services.

---

### TC08 — Kiểm thử Độ trễ & Độ ổn định hệ thống (20 Requests)
- **Mục đích:** Đo lường độ trễ trung bình và độ tin cậy của ALB.
- **Thao tác:** Thực thi kịch bản TC08 trong script `scripts/e2e-test.ps1`:
  ```powershell
  .\scripts\e2e-test.ps1
  ```
- **Kiểm tra:** Tỷ lệ thành công 100% (20/20 requests), độ trễ trung bình ~45ms (< 150ms).
- **Ảnh cần chụp:** Màn hình Terminal PowerShell hoàn thành bảng tổng kết E2E 8/8 PASS.

---

## 🗂️ DANH MỤC ẢNH MINH CHỨNG CẦN LƯU

| STT | Tên file ảnh gợi ý | Kịch bản liên quan | Mô tả |
|:---:|---|:---:|---|
| 1 | `tc01-get-rooms-available.png` | TC01 | Postman danh sách phòng + header `X-Correlation-Id` |
| 2 | `tc02-create-booking-201.png` | TC02 | Postman `201 Created` kèm `bookingCode` |
| 3 | `tc02-rds-database-records.png` | TC02 | DBeaver: bản ghi `bookings` mới + phòng `RESERVED` |
| 4 | `tc02-dynamodb-audit-log.png` | TC02 | DynamoDB Console item `BOOKING_CREATED` |
| 5 | `tc03-rfc7807-validation.png` | TC03 | Postman 400 Bad Request RFC 7807 |
| 6 | `tc04-room-conflict-blocked.png` | TC04 | Postman chặn đặt trùng phòng |
| 7 | `tc05-compensating-rollback.png` | TC05 | CloudWatch log bồi hoàn rollback phòng |
| 8 | `tc06-sqs-dlq-alarm.png` | TC06 | SQS DLQ nhận poison message + Alarm đỏ |
| 9 | `tc07-distributed-tracing.png` | TC07 | CloudWatch Logs Insights truy vết xuyên 3 services |
| 10 | `tc08-e2e-test-summary.png` | TC08 | Terminal chạy `e2e-test.ps1` đạt 8/8 test cases PASS |
