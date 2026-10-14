# Báo Cáo Công Việc Tuần 2 — Phan Thị Thùy Linh

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS  
**Sinh viên:** Phan Thị Thùy Linh — MSSV `24110271`  
**Học phần:** Điện toán đám mây, đợt 1 năm học 2026–2027  
**Môi trường:** Docker Desktop trên Windows & AWS Academy Learner Lab, Region `us-east-1` (Account ID: `0556-5295-1832`)  
**Repository:** https://github.com/pttlinh32/hotel-booking-microservices  
**Phân công Tuần 2:** Lập trình Backend (Spring Data JPA, REST call nội bộ, AWS SDK SNS/SQS/DynamoDB), Đóng gói Docker & Đẩy image lên Amazon ECR (`v1.0.0`), Kiểm thử thành phần. Số giờ thực hiện: 9.0 giờ.

### Bảng phân công công việc tuần 2 (Worklog)
| Thành viên | Nhiệm vụ chính | Số giờ | Trạng thái |
|---|---|---|---|
| Phan Thị Thùy Linh (`24110271`) | Lập trình Backend Spring Boot (JPA, REST, Event SDK), Build & Push ECR Images `v1.0.0`, Kiểm thử thành phần | 9.0 giờ | Đang thực hiện |
| Cao Hoàng Phúc (`24110303`) | Khởi tạo RDS (2 schemas), DynamoDB, SNS/SQS/DLQ, ALB Path-based Routing, ECS Cluster & Service | 9.0 giờ | Đang thực hiện |

---

## 1. Nâng cấp Dependencies & Cấu hình ứng dụng
- Tích hợp Spring Data JPA và Driver kết nối cơ sở dữ liệu.
- Tích hợp AWS SDK for Java v2 (SNS, SQS, DynamoDB).
- Thiết lập file `application.properties` đọc biến môi trường cho môi trường Production trên container.

---

## 2. Phát triển mã nguồn lõi cho 3 Microservices

### 2.1. `room-service`
- Xây dựng Entity `Room` và `RoomRepository`.
- Phát triển API tra cứu phòng `GET /api/rooms` và cập nhật trạng thái phòng `PUT /api/rooms/{id}/status`.

### 2.2. `booking-service`
- Xây dựng Entity `Booking` và `BookingRepository`.
- Xây dựng luồng đặt phòng `POST /api/bookings`: Gọi đồng bộ REST sang `room-service` để giữ phòng, lưu đơn vào `booking_db`, ghi audit log vào DynamoDB và phát sinh sự kiện `BookingCreatedEvent` qua SNS.

### 2.3. `notification-service`
- Triển khai SQS Consumer lắng nghe `booking-notification-queue`.
- Kiểm tra tính duy nhất (Idempotency) của `eventId`.
- Xử lý mô phỏng gửi email thông báo xác nhận và xóa message khỏi hàng đợi.

---

## 3. Đóng gói Container & Đẩy Image lên Amazon ECR
- Đóng gói JAR file với Maven Wrapper.
- Build Docker Image với tag `v1.0.0`.
- Đăng nhập và đẩy 3 image lên Amazon ECR repositories (`hotel-room-service:v1.0.0`, `hotel-booking-service:v1.0.0`, `hotel-notification-service:v1.0.0`).

---

## 4. Kết quả kiểm thử thành phần & Minh chứng thực nghiệm
*(Chèn các hình ảnh minh chứng terminal push ECR, logs container, Postman test API).*

---

## 5. Ghi nhận sử dụng AI
*(Ghi chú chi tiết các công cụ AI hỗ trợ tham khảo cú pháp SDK và gỡ lỗi).*
