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

## Giao diện web Maison

Giao diện tiếng Việt được đóng gói trong `room-service`, không cần thêm frontend service.
Mở `http://<ALB-DNS>/ui/index.html` sau khi triển khai. Đường dẫn `/` chuyển đến giao diện.

- Tổng quan dữ liệu và kết nối 3 dịch vụ.
- Xem/lọc phòng, xem chi tiết và cập nhật trạng thái với lý do, mã booking tham chiếu.
- Tạo booking với kiểm tra email/ngày lưu trú, hiển thị giá dự kiến; máy chủ tính giá chính thức.
- Xem đơn, tra cứu bằng mã booking hoặc ID, xem toàn bộ chi tiết.
- Xem và làm mới thông báo; lịch sử nằm trong bộ nhớ từng notification task, mất khi restart.
- Nhật ký HTTP, độ trễ và `X-Correlation-Id` để đối chiếu CloudWatch.

Đây là giao diện phục vụ Learner Lab trên các API hiện có, chưa có đăng nhập/phân quyền.
UI không điều khiển chaos testing, autoscaling hay teardown; các thao tác hạ tầng thực hiện trong AWS Console/script.

### Kiểm thử

```bash
npm ci --prefix frontend-tests
npm test --prefix frontend-tests
```

Bộ kiểm thử UI dùng mock API để kiểm tra luồng giao diện, lỗi, retry và escape HTML.
Kiểm thử tích hợp cần chạy thêm với 3 service thật và PostgreSQL; SNS/SQS/DynamoDB cần kiểm chứng trên AWS.
Các context test Maven cần cấu hình PostgreSQL qua `SPRING_DATASOURCE_*`.

### Triển khai từ AWS CloudShell

Sau khi clone/pull đúng commit đã kiểm thử và kiểm tra tài khoản Lab:

```bash
bash scripts/deploy-ui-cloudshell.sh
```

Script build/push cả 3 image với tag theo commit, giữ cấu hình task đang dùng, cập nhật ECS,
khởi động RDS hiện có nếu đang dừng, và thêm rule `/`, `/ui`, `/ui/*` tới room target group.
Không thay đổi dữ liệu RDS hoặc Security Groups. Các rule `/api/*` được giữ nguyên.
Script lưu ARN task cũ vào `deployment-rollback.json` (được gitignore) để rollback bằng `aws ecs update-service`.

Nếu môi trường cũ dùng bản ghi Route 53 tĩnh trỏ vào IP của task, chạy thêm:

```bash
python3 scripts/configure-room-discovery.py
```

Script đăng ký room-service với Cloud Map private namespace `hotel.internal` và cập nhật
`ROOM_SERVICE_URL` của booking sang `http://room-service.hotel.internal:8080`.
ECS tự quản lý bản ghi theo task mới, tránh IP cũ sau redeploy/self-healing; giữ nguyên zone `hotel.local` cũ.

Trong Learner Lab không được cấp `servicediscovery:CreatePrivateDnsNamespace`, script tự chuyển
sang endpoint HTTP của ALB hiện có. Booking gọi `/api/rooms*` qua ALB để theo target ECS mới,
không phụ thuộc bản ghi A tĩnh của task. Luồng này đi qua NAT/ALB và có thêm độ trễ/chi phí mạng;
không thay đổi IAM, Security Groups hoặc dữ liệu RDS.

CloudShell thiếu dung lượng build có thể dùng image đã build/test local. Build cả 3 image
`hotel-<service>:ui-week4` với label `org.opencontainers.image.revision=<full commit SHA>`,
`docker save` vào một archive và upload qua **CloudShell Actions → Upload file**. Sau `docker load`:

```bash
PREBUILT_IMAGES=1 SOURCE_REVISION=<full commit SHA> bash scripts/deploy-ui-cloudshell.sh
python3 scripts/configure-room-discovery.py
```

Script kiểm tra label của từng image trùng source revision trước khi push. Không đưa AWS credentials vào archive.
