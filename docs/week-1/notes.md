# Ghi Chú & Tài Liệu Triển Khai Tuần 1

## 📌 Tổng Quan Tuần 1: Dựng Nền Tảng (Infrastructure & Skeleton)
- **Mục tiêu:** Hoàn thiện kiến trúc mạng VPC, cấu hình security tầng mạng, khởi tạo repo skeleton 3 microservices, Dockerfile đa tầng và chuẩn bị các kho ECR trên AWS.
- **Môi trường:** AWS Academy Learner Lab (`us-east-1`).
- **Quy định Lab:** Sử dụng quyền `LabRole` / `LabInstanceProfile`.

---

## 🛠️ Chi Tiết Triển Khai

### 1. Hạ tầng mạng & Bảo mật (Thành viên 1 - Cao Hoàng Phúc)
- **VPC:** `10.0.0.0/16` tại `us-east-1`.
- **Subnets:**
  - `Public Subnet 1`: `us-east-1a`
  - `Public Subnet 2`: `us-east-1b`
  - `Private Subnet 1`: `us-east-1a`
  - `Private Subnet 2`: `us-east-1b`
- **Routing:** Internet Gateway kết nối Public Route Table; Private Route Table điều hướng nội bộ.
- **Security Groups:**
  - `ALB-SG`: Cho phép Inbound port 80/443 từ mọi nơi (`0.0.0.0/0`).
  - `ECS-SG`: Chỉ cho phép Inbound từ `ALB-SG` qua các cổng dịch vụ nội bộ.
- **Resource Tagging:** Tất cả tài nguyên được gán tag `Project=hotel-booking-microservices` và `Owner=phuc-linh`.

### 2. Dịch vụ & Containerization (Thành viên 2 - Phan Thùy Linh)
- **Mã nguồn:** Khung 3 services độc lập:
  - `room-service` (Port 8081 / endpoint: `/api/rooms`)
  - `booking-service` (Port 8082 / endpoint: `/api/bookings`)
  - `notification-service` (Port 8083 / endpoint: `/api/notifications`)
- **Docker:** Multi-stage build (Maven compile + Eclipse Temurin 17 JRE slim) tối ưu dung lượng image.
- **ECR Repositories:**
  - `hotel-room-service`
  - `hotel-booking-service`
  - `hotel-notification-service`
- **Kiểm thử local:** Build và chạy thử nghiệm container thành công trên máy trước khi push.
