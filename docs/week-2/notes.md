# Ghi Chú & Hướng Dẫn Kỹ Thuật Tuần 2

## 📌 Tổng Quan Kỹ Thuật Tuần 2
- **Mục tiêu:** Hoàn thiện hạ tầng lưu trữ (RDS, DynamoDB) và truyền thông điệp (SNS, SQS, DLQ), viết code nghiệp vụ Spring Boot, đóng gói đẩy image lên ECR, dựng cụm ECS Fargate và phân phối tải qua ALB.
- **Tài khoản AWS Learner Lab:** `0556-5295-1832` (Region `us-east-1`).
- **IAM Role:** `LabRole`.

---

## 🛠️ Cheat Sheet Các Câu Lệnh Quan Trọng Tuần 2

### 1. Đăng nhập và Đẩy Docker Image lên Amazon ECR
```powershell
# 1. Đăng nhập Docker vào kho ECR của Linh
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 055652951832.dkr.ecr.us-east-1.amazonaws.com

# 2. Gắn tag cho 3 services với phiên bản v1.0.0
docker tag hotel-room-service:v1.0.0 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-room-service:v1.0.0
docker tag hotel-booking-service:v1.0.0 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-booking-service:v1.0.0
docker tag hotel-notification-service:v1.0.0 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-notification-service:v1.0.0

# 3. Đẩy image lên kho Amazon ECR
docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-room-service:v1.0.0
docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-booking-service:v1.0.0
docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-notification-service:v1.0.0
```

---

### 2. Quy Định Bắt Buộc Dọn Dẹp / Tiết Kiệm Chi Phí Sau Buổi Học

Sau mỗi buổi thực hành, để **không bị trừ hết 100 USD trong tài khoản Learner Lab**, thực hiện lần lượt các bước:

```powershell
# 1. Scale cả 3 ECS Services về 0 (để không tốn tiền Fargate chạy ngầm)
aws ecs update-service --cluster hotel-cluster --service room-service --desired-count 0 --region us-east-1
aws ecs update-service --cluster hotel-cluster --service booking-service --desired-count 0 --region us-east-1
aws ecs update-service --cluster hotel-cluster --service notification-service --desired-count 0 --region us-east-1

# 2. Tạm dừng (Stop) RDS Database Instance (tránh phát sinh chi phí tính theo giờ)
aws rds stop-db-instance --db-instance-identifier hotel-db-instance --region us-east-1
```

*Khi bắt đầu buổi học tiếp theo:* Bấm **Start RDS Instance** trên Console và cập nhật desired-count về `1`.

---

## ⚙️ Bảng Biến Môi Trường (Environment Variables) Cho Container

Cấu hình trong phần **Environment variables** của ECS Task Definition:

| Tên biến | Giá trị mẫu | Service áp dụng |
|---|---|---|
| `SPRING_PROFILES_ACTIVE` | `prod` | Cả 3 service |
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://<rds-endpoint>:5432/room_db` | `room-service` |
| `SPRING_DATASOURCE_USERNAME` | `room_user` | `room-service` |
| `SPRING_DATASOURCE_PASSWORD` | `<mat_khau_room>` | `room-service` |
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://<rds-endpoint>:5432/booking_db` | `booking-service` |
| `SPRING_DATASOURCE_USERNAME` | `booking_user` | `booking-service` |
| `SPRING_DATASOURCE_PASSWORD` | `<mat_khau_booking>` | `booking-service` |
| `AWS_REGION` | `us-east-1` | Cả 3 service |
| `AWS_SNS_TOPIC_ARN` | `arn:aws:sns:us-east-1:055652951832:hotel-booking-events` | `booking-service` |
| `AWS_SQS_QUEUE_URL` | `https://sqs.us-east-1.amazonaws.com/055652951832/booking-notification-queue` | `notification-service` |
| `AWS_DYNAMODB_TABLE` | `hotel-booking-audit-logs` | `booking-service` |
| `INTERNAL_ROOM_SERVICE_URL`| `http://<alb-internal-dns>/api/rooms` | `booking-service` |
