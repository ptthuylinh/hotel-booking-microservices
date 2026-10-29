# Hệ thống đặt phòng khách sạn - Microservices trên AWS ECS

**Repository:** https://github.com/pttlinh32/hotel-booking-microservices

Đồ án Capstone - Điện toán đám mây (Cloud) - GVHD: Huỳnh Xuân Phụng

## 👥 Thành viên nhóm & Phân chia nhiệm vụ
- Chi tiết nhật ký công việc Tuần 1: xem tại [`docs/week-1/tasks.md`](docs/week-1/tasks.md) và [`docs/week-1/notes.md`](docs/week-1/notes.md).
- Chi tiết nhật ký công việc Tuần 2: xem tại [`docs/week-2/tasks.md`](docs/week-2/tasks.md) và [`docs/week-2/notes.md`](docs/week-2/notes.md).
- Chi tiết kế hoạch công việc Tuần 3: xem tại [`docs/week-3/tasks.md`](docs/week-3/tasks.md) và [`docs/week-3/notes.md`](docs/week-3/notes.md).

- **Cao Hoàng Phúc** (`24110303`): Hạ tầng AWS, Security Groups, ALB, RDS/DynamoDB/SNS/SQS, ECS Fargate, CloudWatch & Automation.
- **Phan Thị Thùy Linh** (`24110271`): Mã nguồn 3 Microservices, JPA, REST nội bộ, AWS SDK, Docker & ECR, Distributed Tracing & E2E Testing.

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
