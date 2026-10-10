# KẾ HOẠCH & PHÂN CHIA NHIỆM VỤ ĐỒ ÁN (WORKLOG)

## 📌 THÔNG TIN ĐỒ ÁN
- **Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS (Nhóm: Capstone)
- **Học phần:** Điện toán đám mây (Cloud) - Đợt 1 (Năm học 2026–2027)
- **Giảng viên hướng dẫn (GVHD):** Huỳnh Xuân Phụng
- **Công nghệ & Dịch vụ:** Java 17, Spring Boot, Docker, AWS (ECS Fargate, ECR, ALB path-based routing, RDS, DynamoDB, SNS, SQS, CloudWatch)

---

## 👥 THÀNH VIÊN NHÓM
1. **Cao Hoàng Phúc** - MSSV: `24110303` (Thành viên 1)
2. **Phan Thị Thùy Linh** - MSSV: `24110271` (Thành viên 2)

---

## 📅 PHÂN CHIA NHIỆM VỤ TUẦN 1 (DỰNG NỀN TẢNG & MÔI TRƯỜNG)

### 🔹 Thành viên 1: Cao Hoàng Phúc (MSSV: 24110303)
- **Vai trò:** Phụ trách Hạ tầng mạng (VPC/Subnets/Route Tables), Thiết kế kiến trúc & Bảo mật mạng (Security Groups).
- **Số giờ thực hiện:** 9.0 giờ
- **Trạng thái:** Hoàn thành
- **Công việc chi tiết:**
  1. Nghiên cứu tài liệu về ECS Fargate, ALB Path-based routing và CloudWatch.
  2. Thiết kế và vẽ sơ đồ kiến trúc tổng thể cho toàn bộ hệ thống microservices (Đã hoàn thành sơ đồ chi tiết bên dưới).
  3. Tạo VPC (`10.0.0.0/16`) trên AWS Learner Lab tại Region `us-east-1`.
  4. Chia 4 Subnets gồm 2 Public Subnets và 2 Private Subnets trải trên 2 Availability Zones (`us-east-1a`, `us-east-1b`).
  5. Cấu hình Internet Gateway và Route Tables tương ứng cho Public/Private Subnets.
  6. Thiết lập các Security Groups phân tầng: ALB SG mở port 80/443, ECS SG chỉ nhận kết nối nội bộ từ ALB SG.
  7. Gắn tag `Project` và `Owner` cho toàn bộ tài nguyên mạng vừa tạo.

---

### 🔹 Thành viên 2: Phan Thị Thùy Linh (MSSV: 24110271)
- **Vai trò:** Khởi tạo Source Code Skeleton, Dockerfile đa tầng & ECR Repositories.
- **Số giờ thực hiện:** 8.5 giờ
- **Trạng thái:** Hoàn thành
- **Công việc chi tiết:**
  1. Nghiên cứu tài liệu về ECR, cơ chế Event-driven qua SNS/SQS, lưu trữ với RDS và DynamoDB.
  2. Khởi tạo repository trên Git, tạo khung thư mục (skeleton) cho 3 microservices: `room-service`, `booking-service` và `notification-service`.
  3. Viết Dockerfile cơ bản (multi-stage build) và tạo endpoint health check cho từng service.
  4. Chạy thử nghiệm `docker build` và `docker run` trên môi trường máy cục bộ để đảm bảo container hoạt động.
  5. Tạo 3 kho chứa ECR Repositories trên AWS (`hotel-room-service`, `hotel-booking-service`, `hotel-notification-service`).
  6. Gắn tag `Project` và `Owner` cho các ECR Repositories.
  7. Kiểm tra quyền IAM, xác nhận sử dụng `LabRole` / `LabInstanceProfile` theo đúng quy định của AWS Learner Lab.

---

## 🏛️ SƠ ĐỒ THIẾT KẾ KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

### 1. Sơ đồ kiến trúc hạ tầng AWS (AWS Cloud Infrastructure Diagram)
Kiến trúc phân tầng bảo mật trên AWS Learner Lab (`us-east-1`), phân tách Multi-AZ Public / Private Subnets, cân bằng tải qua Application Load Balancer (ALB) Path-based Routing, các microservices chạy trên ECS Fargate trong mạng Private, lưu trữ đa tầng (RDS & DynamoDB), truyền thông điệp bất đồng bộ (SNS / SQS) và ghi log tập trung qua CloudWatch:

```mermaid
flowchart TB
    subgraph Users["Khách Hàng / Clients"]
        Client["Web / Mobile App / Postman Client"]
    end

    subgraph AWSCloud["AWS Cloud us-east-1 - AWS Learner Lab"]
        IGW["Internet Gateway IGW"]

        subgraph VPC["VPC 10.0.0.0/16 - Tag: Project=hotel-booking-microservices"]
            
            subgraph PublicSubnets["Tầng Mạng Công Khai - Public Subnets Multi-AZ"]
                PubSub1["Public Subnet 1 (us-east-1a) - 10.0.1.0/24"]
                PubSub2["Public Subnet 2 (us-east-1b) - 10.0.2.0/24"]
                
                ALB["Application Load Balancer ALB - Inbound: Port 80/443 (ALB-SG)"]
            end

            subgraph PrivateSubnets["Tầng Mạng Nội Bộ - Private Subnets Multi-AZ (ECS-SG)"]
                PrivSub1["Private Subnet 1 (us-east-1a) - 10.0.11.0/24"]
                PrivSub2["Private Subnet 2 (us-east-1b) - 10.0.12.0/24"]

                subgraph ECSFargate["AWS ECS Fargate Cluster"]
                    RoomSvc["Room Service - Port 8081 - ECR: hotel-room-service"]
                    BookingSvc["Booking Service - Port 8082 - ECR: hotel-booking-service"]
                    NotifSvc["Notification Service - Port 8083 - ECR: hotel-notification-service"]
                end

                subgraph DataLayer["Tầng Dữ Liệu và Hàng Đợi - Persistence and Messaging"]
                    RDS[("Amazon RDS PostgreSQL/MySQL - Quản lý phòng và đơn đặt")]
                    DynamoDB[("Amazon DynamoDB - Lưu trữ trạng thái và nhật ký nhanh")]
                    SNSTopic["Amazon SNS Topic - hotel-booking-events"]
                    SQSQueue["Amazon SQS Queue - booking-notification-queue"]
                end
            end
        end

        subgraph Management["Dịch Vụ Hỗ Trợ Vận Hành và Giám Sát"]
            ECR["Amazon ECR - Lưu trữ Container Images"]
            CloudWatch["Amazon CloudWatch - Logs tập trung và Metrics"]
            IAM["AWS IAM - LabRole và LabInstanceProfile"]
        end
    end

    %% Client traffic
    Client -->|"HTTP / HTTPS Requests"| IGW
    IGW --> ALB

    %% ALB Path-based routing
    ALB -->|"Route: /api/rooms*"| RoomSvc
    ALB -->|"Route: /api/bookings*"| BookingSvc
    ALB -->|"Route: /api/notifications*"| NotifSvc

    %% Service communication & persistence
    BookingSvc -->|"Giao tiếp đồng bộ REST (Kiểm tra và giữ phòng)"| RoomSvc
    RoomSvc -->|"Đọc/Ghi dữ liệu phòng"| RDS
    BookingSvc -->|"Lưu giao dịch đặt phòng"| RDS
    BookingSvc -.->|"Audit Trail / State Log"| DynamoDB

    %% Event-driven async messaging
    BookingSvc -->|"Publish Event: BookingCreated"| SNSTopic
    SNSTopic -->|"Fanout / Subscription"| SQSQueue
    SQSQueue -->|"Poll message / Consume"| NotifSvc

    %% Supporting services
    ECR -.->|"Deploy Container Task"| ECSFargate
    RoomSvc -.->|"Stream Logs & Metrics"| CloudWatch
    BookingSvc -.->|"Stream Logs & Metrics"| CloudWatch
    NotifSvc -.->|"Stream Logs & Metrics"| CloudWatch
    IAM -.->|"Cấp quyền TaskExecution"| ECSFargate
```

---

### 2. Sơ đồ luồng giao tiếp đồng bộ & bất đồng bộ (Service Communication & Event-Driven Flow)
Mô tả chi tiết 2 cơ chế giao tiếp theo yêu cầu đề tài:
- **Giao tiếp đồng bộ (Synchronous REST):** Khi Client đặt phòng, `booking-service` gọi REST trực tiếp sang `room-service` để xác nhận trạng thái phòng.
- **Giao tiếp bất đồng bộ (Asynchronous Event-Driven):** Sau khi đặt phòng thành công, `booking-service` gửi sự kiện vào `SNS Topic`, sự kiện được chuyển tiếp sang `SQS Queue`, và `notification-service` tiêu thụ hàng đợi để gửi thông báo xác nhận.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Khách hàng (Client / Frontend)
    participant ALB as Application Load Balancer
    participant Booking as Booking Service (Port 8082)
    participant Room as Room Service (Port 8081)
    participant DB as Tầng Cơ Sở Dữ Liệu (RDS / DynamoDB)
    participant SNS as Amazon SNS Topic (hotel-booking-events)
    participant SQS as Amazon SQS Queue (booking-notification-queue)
    participant Notif as Notification Service (Port 8083)
    participant CW as Amazon CloudWatch Logs

    %% Bước 1: Tra cứu phòng
    Note over Client, Room: Giai đoạn 1: Tra cứu và kiểm tra phòng (Đồng bộ - Sync REST)
    Client->>ALB: GET /api/rooms
    ALB->>Room: Path-based routing đến Room Service
    Room->>DB: Truy vấn danh sách phòng khả dụng
    DB-->>Room: Trả về dữ liệu phòng
    Room-->>ALB: HTTP 200 OK (Danh sách phòng)
    ALB-->>Client: Hiển thị thông tin phòng

    %% Bước 2: Đặt phòng
    Note over Client, SNS: Giai đoạn 2: Tạo đơn đặt phòng (Đồng bộ kết hợp Bất đồng bộ)
    Client->>ALB: POST /api/bookings (Thông tin đặt phòng)
    ALB->>Booking: Path-based routing đến Booking Service
    Booking->>Room: REST call: GET /api/rooms/{id} (Kiểm tra và khóa phòng)
    Room-->>Booking: Xác nhận phòng hợp lệ
    Booking->>DB: Ghi nhận đơn đặt phòng (Trạng thái: PENDING/CONFIRMED)
    DB-->>Booking: Ghi thành công
    Booking->>SNS: Publish Message "BookingCreatedEvent"
    SNS-->>Booking: Message Id xác nhận đã tiếp nhận
    Booking-->>ALB: HTTP 201 Created (Đã tiếp nhận đặt phòng)
    ALB-->>Client: Trả kết quả đặt phòng thành công

    %% Bước 3: Xử lý thông báo bất đồng bộ
    Note over SNS, Notif: Giai đoạn 3: Xử lý thông báo xác nhận (Bất đồng bộ - Async SQS/SNS)
    SNS->>SQS: Tự động chuyển tiếp message sang hàng đợi
    loop Polling hàng đợi định kỳ
        Notif->>SQS: Long polling kiểm tra tin nhắn mới
    end
    SQS-->>Notif: Trả về Message "BookingCreatedEvent"
    Notif->>Notif: Xử lý logic gửi thông báo (Email / SMS Mock)
    Notif->>SQS: Xóa message khỏi Queue sau khi xử lý thành công

    %% Logging tập trung
    Note over Room, CW: Giám sát tập trung (Observability)
    Room-)CW: Push log luồng xử lý phòng
    Booking-)CW: Push log luồng đặt phòng
    Notif-)CW: Push log thông báo
```

---

### 3. Bảng ánh xạ định tuyến trên ALB (Path-Based Routing Rules)

| Thứ tự ưu tiên | Đường dẫn (Path Pattern) | Cổng Service | Đích đến (Target Group) | Mục đích sử dụng |
| :---: | :--- | :---: | :--- | :--- |
| **1** | `/api/rooms*` | `8081` | `tg-hotel-room-service` | Tra cứu danh sách phòng, trạng thái phòng và quản lý phòng |
| **2** | `/api/bookings*` | `8082` | `tg-hotel-booking-service` | Tiếp nhận yêu cầu đặt phòng, quản lý lịch sử đặt chỗ |
| **3** | `/api/notifications*` | `8083` | `tg-hotel-notification-service` | Quản lý cấu hình thông báo, lịch sử thông báo đã gửi |
| **Default** | `/*` | `80` | `Default 404 / Health Check` | Trả về mã lỗi 404 hoặc trang kiểm tra trạng thái chung |

---

### 4. Bảng phân vùng mạng & Security Group (Network & Security Group Mapping)

| Tài nguyên | Định danh / Tên | CIDR / Port | Availability Zone | Mục đích & Chính sách bảo mật |
| :--- | :--- | :---: | :---: | :--- |
| **VPC** | `vpc-hotel-microservices` | `10.0.0.0/16` | Region `us-east-1` | Không gian mạng cô lập cho toàn bộ đồ án |
| **Public Subnet 1** | `subnet-public-1` | `10.0.1.0/24` | `us-east-1a` | Chứa ALB node 1, kết nối Internet qua IGW |
| **Public Subnet 2** | `subnet-public-2` | `10.0.2.0/24` | `us-east-1b` | Chứa ALB node 2, kết nối Internet qua IGW |
| **Private Subnet 1** | `subnet-private-1` | `10.0.11.0/24` | `us-east-1a` | Chứa ECS Fargate Tasks & Data layer (Nội bộ) |
| **Private Subnet 2** | `subnet-private-2` | `10.0.12.0/24` | `us-east-1b` | Chứa ECS Fargate Tasks & Data layer (Nội bộ) |
| **ALB-SG** | `sg-hotel-alb` | Inbound: `80, 443` (`0.0.0.0/0`) | - | Nhận request từ Internet và chuyển tiếp nội bộ |
| **ECS-SG** | `sg-hotel-ecs` | Inbound: `8081, 8082, 8083` (Từ `ALB-SG`) | - | Chỉ cho phép truy cập từ ALB SG, chặn hoàn toàn truy cập ngoài |

---

## 🗓️ KẾ HOẠCH CÁC TUẦN TIẾP THEO
- **Tuần 2:** Triển khai các chức năng lõi trên AWS, kiểm thử từng thành phần.
- **Tuần 3:** Tích hợp, bảo mật, giám sát (CloudWatch); tự động hóa / IaC nếu có.
- **Tuần 4:** Kiểm thử tổng thể, tối ưu chi phí, dọn dẹp tài nguyên; viết báo cáo và demo.
