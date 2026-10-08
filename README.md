# Hệ thống đặt phòng khách sạn - Microservices trên AWS ECS

Đồ án Capstone - Điện toán đám mây (Cloud) - GVHD: Huỳnh Xuân Phụng

## 👥 Thành viên nhóm & Phân chia nhiệm vụ
Chi tiết nhật ký công việc (worklog) và tài liệu tuần 1: xem tại [`docs/week-1/tasks.md`](docs/week-1/tasks.md) và [`docs/week-1/notes.md`](docs/week-1/notes.md).

- **Cao Hoàng Phúc** (`24110303`): Thiết kế kiến trúc tổng thể, VPC/Subnets/Route Tables, Security Groups, ALB & CloudWatch.
- **Phan Thùy Linh** (`24110308`): Khởi tạo Source Code Skeleton, Dockerfile đa tầng, ECR Repositories, tích hợp SNS/SQS & RDS/DynamoDB.

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