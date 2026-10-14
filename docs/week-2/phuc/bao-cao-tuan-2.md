# Báo Cáo Công Việc Tuần 2 — Cao Hoàng Phúc

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS  
**Sinh viên:** Cao Hoàng Phúc — MSSV `24110303`  
**Học phần:** Điện toán đám mây, đợt 1 năm học 2026–2027  
**Môi trường:** AWS Academy Learner Lab, Region `us-east-1` (Account ID nhóm: `0556-5295-1832`)  
**Repository:** https://github.com/pttlinh32/hotel-booking-microservices  
**Phân công Tuần 2:** Hạ tầng Cloud (Amazon RDS 2 schemas, DynamoDB, SNS Topic, SQS Queue & DLQ, ALB Path-based Routing, ECS Fargate Cluster & Services). Số giờ thực hiện: 9.0 giờ.

### Bảng phân công công việc tuần 2 (Worklog)
| Thành viên | Nhiệm vụ chính | Số giờ | Trạng thái |
|---|---|---|---|
| Phan Thị Thùy Linh (`24110271`) | Lập trình Backend Spring Boot (JPA, REST, Event SDK), Build & Push ECR Images `v1.0.0`, Kiểm thử thành phần | 9.0 giờ | Đang thực hiện |
| Cao Hoàng Phúc (`24110303`) | Khởi tạo RDS (2 schemas), DynamoDB, SNS/SQS/DLQ, ALB Path-based Routing, ECS Cluster & Service | 9.0 giờ | Đang thực hiện |

---

## 1. Khởi tạo Cơ sở dữ liệu quan hệ Amazon RDS
- Tạo Subnet Group trải trên 2 Private Subnets.
- Khởi tạo 1 Database Instance loại `db.t3.micro` với security group `sg-hotel-rds`.
- Tạo 2 logical database / schema độc lập: `room_db` (user: `room_user`) và `booking_db` (user: `booking_user`).

---

## 2. Khởi tạo Amazon DynamoDB, SNS Topic và SQS Queue
- Khởi tạo bảng DynamoDB `hotel-booking-audit-logs` với Partition Key `bookingId` và Sort Key `timestamp`.
- Tạo Amazon SNS Topic `hotel-booking-events`.
- Tạo Amazon SQS Queue `booking-notification-queue` và Dead Letter Queue `booking-notification-dlq` (Redrive policy `maxReceiveCount = 3`).
- Thiết lập Subscription kết nối SNS sang SQS.

---

## 3. Cấu hình Application Load Balancer (ALB) Path-based Routing
- Tạo Application Load Balancer trên 2 Public Subnets, gán `sg-hotel-alb`.
- Tạo 3 Target Groups (loại IP, port 8080, health check path `/actuator/health`).
- Cấu hình các luật phân luồng (Path-based Routing Rules):
  - `/api/rooms*` ➡️ `tg-hotel-room-service`
  - `/api/bookings*` ➡️ `tg-hotel-booking-service`
  - `/api/notifications*` ➡️ `tg-hotel-notification-service`

---

## 4. Triển khai Cụm ECS Fargate Cluster & Services
- Tạo ECS Cluster `hotel-cluster`.
- Thiết lập 3 Task Definitions tương ứng với 3 ECR image phiên bản `v1.0.0`, sử dụng `LabRole`.
- Khởi chạy 3 ECS Services trong mạng Private Subnets, gán `sg-hotel-ecs` và liên kết với Target Groups của ALB.
- Xác nhận các tasks khởi chạy ổn định và đạt trạng thái Healthy trên Target Group.

---

## 5. Minh chứng nghiệm thu hạ tầng & Quy tắc tiết kiệm ngân sách
*(Chèn các hình ảnh chụp console RDS, DynamoDB, SNS/SQS, ALB, ECS Task status).*
- Đảm bảo thực hiện scale Task về 0 và Stop RDS sau mỗi buổi làm việc để bảo toàn ngân sách Lab.

---

## 6. Ghi nhận sử dụng AI
*(Ghi chú chi tiết các công cụ AI hỗ trợ tra cứu cú pháp và cấu hình).*
