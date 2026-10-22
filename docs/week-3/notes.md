# Ghi Chú & Hướng Dẫn Kỹ Thuật Tuần 3

## 📌 Tổng Quan Kỹ Thuật Tuần 3
- **Trọng tâm Tuần 3:** Tích hợp nghiệp vụ hoàn chỉnh, tăng cường bảo mật thông tin nhạy cảm qua **AWS Systems Manager (SSM) Parameter Store**, thiết lập hệ thống giám sát tập trung toàn diện với **Amazon CloudWatch** (Logs Insights, Metrics, Alarms, Dashboard), và phát triển các kịch bản tự động hóa vận hành (**Automation Scripts / IaC**) giúp quản lý chi phí tài khoản AWS Academy Learner Lab.
- **Tài khoản AWS Learner Lab:** `0556-5295-1832` (Region `us-east-1`).
- **Quy định IAM Role:** `LabRole` / `LabInstanceProfile`.

---

## 🛠️ Cheat Sheet Các Câu Lệnh AWS CLI Tuần 3

### 1. Quản lý Bí mật trên AWS SSM Parameter Store

```powershell
# Tạo các tham số bảo mật (SecureString mã hóa KMS) cho thông tin kết nối RDS
aws ssm put-parameter `
    --name "/hotel/database/room_url" `
    --value "jdbc:postgresql://<rds-endpoint>:5432/room_db" `
    --type "SecureString" `
    --overwrite `
    --region us-east-1

aws ssm put-parameter `
    --name "/hotel/database/room_username" `
    --value "room_user" `
    --type "SecureString" `
    --overwrite `
    --region us-east-1

aws ssm put-parameter `
    --name "/hotel/database/room_password" `
    --value "<mat_khau_room_bi_mat>" `
    --type "SecureString" `
    --overwrite `
    --region us-east-1

aws ssm put-parameter `
    --name "/hotel/database/booking_url" `
    --value "jdbc:postgresql://<rds-endpoint>:5432/booking_db" `
    --type "SecureString" `
    --overwrite `
    --region us-east-1

aws ssm put-parameter `
    --name "/hotel/database/booking_username" `
    --value "booking_user" `
    --type "SecureString" `
    --overwrite `
    --region us-east-1

aws ssm put-parameter `
    --name "/hotel/database/booking_password" `
    --value "<mat_khau_booking_bi_mat>" `
    --type "SecureString" `
    --overwrite `
    --region us-east-1

# Kiểm tra danh sách tham số đã tạo
aws ssm describe-parameters --filters "Key=Name,Values=/hotel/" --region us-east-1
```

---

### 2. Cấu hình Retention Policy cho CloudWatch Log Groups

Để tránh tốn chi phí lưu trữ log vượt quá hạn mức của Learner Lab:

```powershell
# Đặt thời gian lưu log tối đa là 3 ngày cho cả 3 services
aws logs put-retention-policy --log-group-name "/ecs/hotel-room-service" --retention-in-days 3 --region us-east-1
aws logs put-retention-policy --log-group-name "/ecs/hotel-booking-service" --retention-in-days 3 --region us-east-1
aws logs put-retention-policy --log-group-name "/ecs/hotel-notification-service" --retention-in-days 3 --region us-east-1
```

---

### 3. Thiết lập CloudWatch Alarms & Topic Cảnh Báo

```powershell
# 1. Tạo SNS Topic nhận cảnh báo
aws sns create-topic --name hotel-system-alerts --region us-east-1

# 2. Tạo Alarm giám sát CPU của ECS Cluster
aws cloudwatch put-metric-alarm `
    --alarm-name "ECS-High-CPU-Utilization" `
    --alarm-description "Canh bao khi CPU vuot 80% trong 2 phut" `
    --metric-name CPUUtilization `
    --namespace AWS/ECS `
    --statistic Average `
    --period 60 `
    --evaluation-periods 2 `
    --threshold 80.0 `
    --comparison-operator GreaterThanOrEqualToThreshold `
    --dimensions Name=ClusterName,Value=hotel-cluster `
    --alarm-actions "arn:aws:sns:us-east-1:055652951832:hotel-system-alerts" `
    --region us-east-1

# 3. Tạo Alarm giám sát Dead Letter Queue (DLQ) có Poison Message
aws cloudwatch put-metric-alarm `
    --alarm-name "SQS-DLQ-Has-Poison-Messages" `
    --alarm-description "Canh bao ngay khi DLQ nhan it nhat 1 tin nhan loi" `
    --metric-name ApproximateNumberOfMessagesVisible `
    --namespace AWS/SQS `
    --statistic Maximum `
    --period 60 `
    --evaluation-periods 1 `
    --threshold 1.0 `
    --comparison-operator GreaterThanOrEqualToThreshold `
    --dimensions Name=QueueName,Value=booking-notification-dlq `
    --alarm-actions "arn:aws:sns:us-east-1:055652951832:hotel-system-alerts" `
    --region us-east-1
```

---

## 🔒 Cấu Hình ECS Task Definition Đọc Secrets Từ SSM

Thay vì để lộ mật khẩu dạng plaintext trong mục `environment`, chỉnh sửa JSON của Task Definition trong mục `containerDefinitions`:

```json
{
  "name": "booking-service",
  "image": "055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-booking-service:v1.1.0",
  "essential": true,
  "portMappings": [
    {
      "containerPort": 8080,
      "protocol": "tcp"
    }
  ],
  "environment": [
    { "name": "SPRING_PROFILES_ACTIVE", "value": "prod" },
    { "name": "AWS_REGION", "value": "us-east-1" },
    { "name": "AWS_DYNAMODB_TABLE", "value": "hotel-booking-audit-logs" }
  ],
  "secrets": [
    {
      "name": "SPRING_DATASOURCE_URL",
      "valueFrom": "arn:aws:ssm:us-east-1:055652951832:parameter/hotel/database/booking_url"
    },
    {
      "name": "SPRING_DATASOURCE_USERNAME",
      "valueFrom": "arn:aws:ssm:us-east-1:055652951832:parameter/hotel/database/booking_username"
    },
    {
      "name": "SPRING_DATASOURCE_PASSWORD",
      "valueFrom": "arn:aws:ssm:us-east-1:055652951832:parameter/hotel/database/booking_password"
    }
  ],
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/hotel-booking-service",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "ecs"
    }
  }
}
```

> **Lưu ý IAM:** Task Execution Role phải là **`LabRole`** để có quyền gọi `ssm:GetParameters` giải mã dữ liệu lúc khởi động container.

---

## 🔍 Hướng Dẫn Truy Vấn CloudWatch Logs Insights với Correlation ID

Khi ứng dụng đã tích hợp `CorrelationIdFilter`, mọi dòng log đều có `correlationId`. Trên giao diện **CloudWatch $\rightarrow$ Logs $\rightarrow$ Logs Insights**, chọn cả 3 log groups (`/ecs/hotel-room-service`, `/ecs/hotel-booking-service`, `/ecs/hotel-notification-service`) và thực hiện truy vấn:

### Truy vết toàn bộ luồng của 1 Transaction:
```sql
fields @timestamp, @logStream, @message
| filter @message like /corr-8f92a1b3-4c5e/
| sort @timestamp asc
| limit 200
```

### Tìm kiếm các bản ghi lỗi kèm Stack Trace:
```sql
fields @timestamp, @logStream, @message
| filter @message like /ERROR/ or @message like /Exception/
| sort @timestamp desc
| limit 50
```

---

## ⚡ Kịch Bản Tự Động Hóa Vận Hành (Scripts Tiết Kiệm Chi Phí)

### Script 1: Tắt Môi Trường (`scripts/stop-environment.ps1`)
Chạy sau mỗi buổi thực hành để tiết kiệm ngân sách:
```powershell
Write-Host "=== ĐANG TẮT MÔI TRƯỜNG HOTEL MICROSERVICES ===" -ForegroundColor Yellow

# Scale ECS Services ve 0
Write-Host "1. Scaling down ECS Services..." -ForegroundColor Cyan
aws ecs update-service --cluster hotel-cluster --service room-service --desired-count 0 --region us-east-1
aws ecs update-service --cluster hotel-cluster --service booking-service --desired-count 0 --region us-east-1
aws ecs update-service --cluster hotel-cluster --service notification-service --desired-count 0 --region us-east-1

# Dung RDS Instance
Write-Host "2. Stopping Amazon RDS Instance..." -ForegroundColor Cyan
aws rds stop-db-instance --db-instance-identifier hotel-db-instance --region us-east-1

Write-Host "=== TOÀN BỘ WORKLOAD ĐÃ ĐƯỢC TẠM DỪNG THÀNH CÔNG! ===" -ForegroundColor Green
```

### Script 2: Khởi Động Môi Trường (`scripts/start-environment.ps1`)
Chạy khi bắt đầu phiên làm việc tiếp theo:
```powershell
Write-Host "=== ĐANG KHỞI ĐỘNG MÔI TRƯỜNG HOTEL MICROSERVICES ===" -ForegroundColor Yellow

# Khoi dong RDS Instance
Write-Host "1. Starting Amazon RDS Instance..." -ForegroundColor Cyan
aws rds start-db-instance --db-instance-identifier hotel-db-instance --region us-east-1

# Cho RDS san sang
Write-Host "2. Waiting for RDS to be available (co the mat 2-3 phut)..." -ForegroundColor Cyan
aws rds wait db-instance-available --db-instance-identifier hotel-db-instance --region us-east-1

# Scale ECS Services len 1
Write-Host "3. Scaling up ECS Services to 1 task..." -ForegroundColor Cyan
aws ecs update-service --cluster hotel-cluster --service room-service --desired-count 1 --region us-east-1
aws ecs update-service --cluster hotel-cluster --service booking-service --desired-count 1 --region us-east-1
aws ecs update-service --cluster hotel-cluster --service notification-service --desired-count 1 --region us-east-1

Write-Host "=== MÔI TRƯỜNG ĐÃ SẴN SÀNG ĐỂ THỰC HÀNH & KIỂM THỬ! ===" -ForegroundColor Green
```
