# Hệ thống đặt phòng khách sạn - Microservices trên AWS ECS

**Repository:** https://github.com/pttlinh32/hotel-booking-microservices

Đồ án Capstone - Điện toán đám mây (Cloud) - GVHD: Huỳnh Xuân Phụng

## 👥 Thành viên nhóm & Phân chia nhiệm vụ
Chi tiết nhật ký công việc (worklog) và tài liệu tuần 1: xem tại [`docs/week-1/tasks.md`](docs/week-1/tasks.md) và [`docs/week-1/notes.md`](docs/week-1/notes.md).

- **Cao Hoàng Phúc** (`24110303`): Thiết kế kiến trúc tổng thể, VPC/Subnets/Route Tables, Security Groups, ALB & CloudWatch. (Xem [`báo cáo tuần 1`](docs/week-1/phuc/bao-cao-tuan-1.md))
- **Phan Thị Thùy Linh** (`24110271`): Khởi tạo Source Code Skeleton, Dockerfile đa tầng, ECR Repositories, tích hợp SNS/SQS & RDS/DynamoDB. (Xem [`báo cáo tuần 1`](docs/week-1/linh/bao-cao-tuan-1.md))

---

## 📌 Quy ước chung
- **AWS Region:** `us-east-1` (US East - N. Virginia).
- **Cổng Container:** Cổng `8080` cho cả 3 microservices bên trong container.
- **ALB Path-based Routing:**
  - `/api/rooms` → `room-service`
  - `/api/bookings` → `booking-service`
  - `/api/notifications` → `notification-service`
- **Health Check Endpoint:** `/actuator/health` (Spring Boot Actuator probe `liveness` & `readiness`).
- **AWS Resource Tagging:**
  - `Project=hotel-booking-microservices`
  - `Owner=<MSSV từng người>` (ví dụ: `24110303` cho Phúc, `24110271` cho Linh).

---

## 🏗️ Các microservices
- **`room-service`**: Quản lý phòng & trạng thái phòng.
- **`booking-service`**: Đặt phòng & xử lý luồng đặt phòng.
- **`notification-service`**: Gửi thông báo qua Event-driven (SNS / SQS).

---

## 🛠️ Công nghệ & Hạ tầng
- **Backend:** Java 17, Spring Boot, Maven Wrapper.
- **Containerization:** Docker (multi-stage build).
- **AWS Cloud (Learner Lab):** ECS Fargate, ECR, ALB (path-based routing), RDS, DynamoDB, SNS, SQS, CloudWatch.