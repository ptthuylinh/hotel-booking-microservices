# KẾ HOẠCH & PHÂN CHIA NHIỆM VỤ TUẦN 3 (WORKLOG TUẦN 3)

## 📌 THÔNG TIN ĐỒ ÁN
- **Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS (Nhóm: Capstone)
- **Học phần:** Điện toán đám mây (Cloud) - Đợt 1 (Năm học 2026–2027)
- **Giảng viên hướng dẫn (GVHD):** Thầy Huỳnh Xuân Phụng
- **Mục tiêu Tuần 3:** Tích hợp hệ thống, tăng cường bảo mật (Secrets Management / SSM Parameter Store), giám sát tập trung toàn diện (Amazon CloudWatch Logs, Metrics, Alarms, Dashboard), tự động hóa vận hành/IaC, **chạy tải thật & quan sát co giãn Task (Auto Scaling)**, và **lập bảng theo dõi chi phí hàng ngày** (Mỗi sinh viên thực hiện $\ge$ 8.0 giờ/tuần).
- **Môi trường thực hành:** AWS Academy Learner Lab, Region `us-east-1`, Account ID: `0556-5295-1832` (Tài khoản nhóm của Phan Thị Thùy Linh).
- **Quy định IAM bắt buộc:** Sử dụng `LabRole` / `LabInstanceProfile` (Không tạo IAM User / Custom Role).

---

## 📢 PHẢN HỒI CỦA GVHD SAU TUẦN 2 & KẾ HOẠCH TIẾP THU TRONG TUẦN 3

> **Trích nhận xét của Thầy Huỳnh Xuân Phụng:**  
> *"III. Kết luận: Báo cáo tuần 2 của nhóm ĐẠT, được duyệt. Tuần 3 ngoài sáu đầu việc trong kế hoạch, nếu nhóm có thời gian thì thêm: một, chạy tải thật và ghi kết quả thay đổi số task, không chỉ demo thủ công; hai, sau mỗi buổi thực hành là một bản ghi chi phí và dọn tài nguyên, RDS và ECS về 0 — hai việc này cũng là chuẩn bị cho tuần cuối. Nhóm có đính kèm file (BaoCao_Tuan2_24110271_24110303_NPWXISy.docx), nhưng thầy chỉ xem nội dung trong phần báo cáo online trên hệ thống; file đính kèm không được tính vào đánh giá."*

### Nhóm nghiêm túc tiếp thu và bổ sung ngay vào kế hoạch Tuần 3:
1. **Chạy tải thật (Load Testing) & Ghi nhận thay đổi số Task:** Không chỉ gửi từng request đơn lẻ (thủ công) mà xây dựng kịch bản bắn tải đồng thời hàng trăm request vào ALB; cấu hình **ECS Service Auto Scaling** để ghi nhận thực tế Task Fargate tự động scale từ 1 task lên 2 tasks khi CPU/Request tăng vọt, và co về khi hết tải.
2. **Nhật ký chi phí (Billing Log) & Dọn dẹp tài nguyên về 0 sau mỗi buổi:** Lập bảng theo dõi số dư Credits còn lại trên AWS Academy Learner Lab sau từng ngày thực hành, kèm minh chứng console thực hiện lệnh tắt RDS (`hotel-db-instance` $\rightarrow$ `stopped`) và scale ECS tasks về `0`.
3. **Quy định nộp báo cáo online:** Toàn bộ nội dung báo cáo, bảng biểu, mã nguồn và hình ảnh minh chứng sẽ được định dạng chuẩn Markdown và dán trực tiếp vào khung soạn thảo **báo cáo online trên hệ thống LMS**, tuyệt đối không chỉ nộp file đính kèm `.docx`.

---

## 👥 BẢNG PHÂN CÔNG CÔNG VIỆC TUẦN 3 (WORKLOG)

| STT | Thành viên | MSSV | Vai trò chính trong Tuần 3 | Số giờ dự kiến | Trạng thái |
|:---:|---|:---:|---|:---:|:---:|
| 1 | **Cao Hoàng Phúc** | `24110303` | **Cloud Infrastructure, Security, Monitoring & Scaling (DevOps):** Quản lý bí mật qua SSM Parameter Store; cấu hình CloudWatch Centralized Logging, Metrics, Alarms & Dashboard; cấu hình **ECS Service Auto Scaling**; xây dựng kịch bản tự động hóa bật/tắt và quản lý **Nhật ký chi phí / dọn dẹp tài nguyên**. | 9.0 giờ | Đã xong Alarms & SNS (Đang tiếp tục các mục còn lại) |
| 2 | **Phan Thị Thùy Linh** | `24110271` | **Backend Integration, Tracing, Load Testing & E2E (Backend):** Triển khai cơ chế bồi hoàn giao dịch (Compensating Transaction); Distributed Tracing với Correlation ID qua MDC & Message Attributes; Bean Validation & Security Exception Handling; **viết script sinh tải thật (Load Generator Script)**; đóng gói Docker ECR `v1.1.0`. | 9.0 giờ | **Hoàn thành** |

---

## 🛠️ CHI TIẾT CÔNG VIỆC TỪNG THÀNH VIÊN

### 🔹 Thành viên 1: Cao Hoàng Phúc (MSSV: 24110303)
- **Vai trò:** Phụ trách Bảo mật Hạ tầng (SSM), Giám sát Tập trung (CloudWatch), Cấu hình ECS Auto Scaling & Quản lý Chi phí Vận hành.
- **Số giờ dự kiến:** 9.0 giờ.
- **Nhiệm vụ chi tiết:**

1. **Bảo mật dữ liệu nhạy cảm (Secrets Management & SSM Parameter Store):**
   - Khởi tạo các tham số bảo mật trên **AWS Systems Manager (SSM) Parameter Store** thuộc loại `SecureString` mã hóa KMS:
     - `/hotel/database/room_url`, `/hotel/database/room_username`, `/hotel/database/room_password`
     - `/hotel/database/booking_url`, `/hotel/database/booking_username`, `/hotel/database/booking_password`
   - Cập nhật ECS Task Definitions: Chuyển cấu hình kết nối DB từ `environment` sang `secrets` (`valueFrom`) để container đọc an toàn qua `LabRole`.
   - Rà soát Network Security Groups: ALB SG (80/443), ECS SG (8080 từ ALB và nội bộ), RDS SG (5432 từ ECS SG). Đảm bảo không lộ Public IP cho task và database.

2. **Cấu hình Giám sát tập trung (Centralized Logging với Amazon CloudWatch):**
   - Chuẩn hóa các Log Groups: `/ecs/hotel-room-service`, `/ecs/hotel-booking-service`, `/ecs/hotel-notification-service`.
   - Cấu hình **Retention Policy = 3 ngày** nhằm tiết kiệm tối đa ngân sách $100 của Learner Lab.
   - Xây dựng các mẫu truy vấn trên **CloudWatch Logs Insights** lọc theo `correlationId` và mức lỗi `ERROR`.

3. **Thiết lập CloudWatch Metrics & Cảnh báo tự động (CloudWatch Alarms):**
   - Tạo SNS Topic cảnh báo: `hotel-system-alerts`.
   - Cấu hình 4 Alarms trọng yếu:
     - **Alarm 1:** ECS High CPU Utilization ($\ge 80\%$ trong 2 phút).
     - **Alarm 2:** ECS High Memory Utilization ($\ge 85\%$).
     - **Alarm 3:** ALB 5XX Target Error Rate ($\ge 5$ lỗi/phút).
     - **Alarm 4:** SQS DLQ Poison Message Alarm ($\ge 1$ message trong `booking-notification-dlq`).

4. **Xây dựng CloudWatch Operational Dashboard:**
   - Tạo Dashboard tập trung: **`HotelBooking-System-Dashboard`**.
   - Thiết kế các widgets theo dõi CPU/Memory ECS, ALB Request Count & Target Response Time, số lượng Healthy Hosts, số lượng tin nhắn SQS/DLQ và log lỗi thời gian thực.

5. **Cấu hình ECS Service Auto Scaling (Theo yêu cầu GVHD):**
   - Thiết lập chính sách co giãn tự động (**Target Tracking Scaling Policy**) cho `booking-service` và `room-service`:
     - Minimum tasks: `1`, Maximum tasks: `3`.
     - Chỉ số theo dõi: `ECSServiceAverageCPUUtilization` (Target value: `50%`) hoặc `ALBRequestCountPerTarget`.
     - Phối hợp với Linh khi chạy tải thật để quan sát và chụp ảnh minh chứng Task tự động tăng từ 1 lên 2 tasks.

6. **Tự động hóa vận hành & Lập Nhật Ký Chi Phí (Theo yêu cầu GVHD):**
   - Xây dựng và thực thi bộ script `scripts/stop-environment.ps1` và `scripts/start-environment.ps1`.
   - Lập và duy trì **Bảng Nhật ký Chi phí & Dọn tài nguyên sau mỗi buổi thực hành** (ghi nhận ngày giờ, số dư $ còn lại, trạng thái RDS Stopped và ECS Task = 0).

---

### 🔹 Thành viên 2: Phan Thị Thùy Linh (MSSV: 24110271)
- **Vai trò:** Phụ trách Tích hợp Nghiệp vụ Phân tán, Distributed Tracing, Bảo mật Mức Ứng dụng, Script Chạy Tải Thật & Kiểm thử E2E.
- **Số giờ dự kiến:** 9.0 giờ.
- **Nhiệm vụ chi tiết:**

1. **Xử lý Bồi hoàn Giao dịch Phân tán (Compensating Transaction / Rollback Pattern):**
   - Nâng cấp luồng đặt phòng tại `booking-service`: Nếu bước lưu DB hoặc phát SNS gặp sự cố, tự động gọi REST bồi hoàn sang `room-service` (`PUT /api/rooms/{id}/status` -> `AVAILABLE`) để mở lại phòng, ngăn ngừa hiện tượng khóa phòng "ma" (Deadlock phòng).

2. **Phân phối Log Có Cấu Trúc & Truy vết Phân tán (Distributed Tracing với Correlation ID):**
   - Xây dựng bộ lọc `CorrelationIdFilter` trên cả 3 microservices:
     - Nhận hoặc tự sinh `X-Correlation-Id`, đưa vào SLF4J **MDC**.
     - Đính kèm header `X-Correlation-Id` vào HTTP Response trả về cho client.
   - Truyền header `X-Correlation-Id` qua REST nội bộ (`RoomClient`) và đính kèm vào Message Attributes của SNS Topic / SQS Queue.
   - `notification-service` trích xuất `correlationId` từ SQS và đưa vào MDC trước khi in log mô phỏng gửi email.
   - Cấu hình định dạng log chuẩn `[%X{correlationId}]` trong `application.properties` để stream lên CloudWatch.

3. **Bảo mật Ứng dụng & Chuẩn hóa Xử lý Lỗi (Application Security & Bean Validation):**
   - Bổ sung Bean Validation (`jakarta.validation-api`): `@NotNull`, `@NotBlank`, `@Email`, `@FutureOrPresent` trong `CreateBookingRequest`.
   - Xây dựng `GlobalExceptionHandler` (`@RestControllerAdvice`) chuẩn RFC 7807 (Problem Details), che giấu stack trace và mã lỗi cơ sở dữ liệu nội bộ.
   - Thêm cấu hình CORS và các Header bảo mật cơ bản.

4. **Nâng cấp Actuator Health Indicators:**
   - Cấu hình `management.endpoint.health.show-details=always`.
   - Viết Custom Health Indicators kiểm tra kết nối RDS, DynamoDB, AWS SNS/SQS.

5. **Xây dựng Script Chạy Tải Thật (Load Testing Script - Theo yêu cầu GVHD):**
   - Viết kịch bản tự động bắn tải đồng thời (bằng script PowerShell đa luồng `scripts/load-test.ps1` hoặc công cụ `ab` / `k6`):
     - Gửi 200 - 500 requests liên tục vào API tra cứu phòng `GET /api/rooms` và tạo đơn `POST /api/bookings`.
     - Đo lường thời gian phản hồi trung bình (Average Response Time), tỷ lệ thành công (Success Rate).
     - Ghi nhận và chụp ảnh minh chứng: Khi tải tăng cao, CPU vượt ngưỡng và ECS Fargate tự động scale tăng số Task từ 1 lên 2 tasks.

6. **Đóng gói Docker Image & Đẩy ECR Phiên bản `v1.1.0`:**
   - Biên dịch và đóng gói Maven: `./mvnw clean package -DskipTests`.
   - Build và push Docker Images tag `v1.1.0` lên Amazon ECR.
   - Bàn giao Image URIs cho Phúc cấu hình lên ECS Task Definition.

---

## 💰 NHẬT KÝ THEO DÕI CHI PHÍ & DỌN TÀI NGUYÊN (CHUẨN BỊ CHO TUẦN CUỐI)

Bảng ghi nhận thực tế sau mỗi phiên thực hành trên AWS Academy Learner Lab (Hạn mức cấp: **$50.00 USD**):

| Buổi làm việc | Ngày thực hiện | Số dư Credits còn lại | Chi phí đã dùng tích lũy | Trạng thái ECS Tasks | Trạng thái RDS Instance | Người thực hiện dọn dẹp | Ghi chú tiến độ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Chốt Tuần 2** | 17/10/2026 | **$43.10** | **$6.90** | Desired = 0 | `Stopped` | Phúc & Linh | Đã nghiệm thu Tuần 2 (Đạt) |
| **Buổi 1 (Tuần 3)**| 22/10/2026 | $43.10 | $6.90 | Desired = 0 | `Stopped` | Linh | Hoàn thiện Code Backend & Build Docker v1.1.0 |
| **Buổi 2 (Tuần 3)**| 23/10/2026 | TBD | TBD | Desired = 1 (khi test) | `Running` $\rightarrow$ `Stopped` | Phúc | Cấu hình SSM, CloudWatch & Auto Scaling |
| **Buổi 3 (Tuần 3)**| 24/10/2026 | TBD | TBD | Desired = 1 co giãn | `Running` $\rightarrow$ `Stopped` | Cả nhóm | Chạy tải thật & kiểm thử E2E |
| **Nghiệm thu T3** | 25/10/2026 | TBD | TBD | Desired = 0 | `Stopped` | Cả nhóm | Dọn dẹp tài nguyên & tổng kết chi phí |

---

## 🔄 QUY TRÌNH PHỐI HỢP LIÊN TỤC GIỮA 2 THÀNH VIÊN TRONG TUẦN 3

```
[BƯỚC 1 - Phúc]: Tạo SSM Parameter Store (SecureString) lưu thông tin kết nối RDS & AWS ARNs
       │
       ▼ (Bàn giao: Danh sách Parameter Keys)
[BƯỚC 2 - Linh]: Code Correlation ID, Bồi hoàn Transaction, Validation & Load Test Script
       │
       ▼ (Đóng gói JAR, Build Docker và Push ECR tag v1.1.0)
[BƯỚC 3 - Linh]: Bàn giao Image URIs v1.1.0 cho Phúc
       │
       ▼
[BƯỚC 4 - Phúc]: Cập nhật ECS Task Definitions (secrets từ SSM), cấu hình Auto Scaling (1 -> 3 tasks)
       │
       ▼ (Deploy Task v1.1.0 lên ECS Cluster)
[BƯỚC 5 - Phúc]: Cấu hình 4 CloudWatch Alarms & xây dựng Dashboard "HotelBooking-System-Dashboard"
       │
       ▼
[BƯỚC 6 - Cả hai phối hợp KIỂM THỬ TẢI & E2E]:
       ├── Linh: Chạy script bắn tải liên tục (200-500 requests) & test kịch bản DLQ
       └── Phúc: Quan sát CloudWatch Dashboard, chụp minh chứng CPU tăng và Task tự scale từ 1 -> 2 tasks
       │
       ▼ (HẾT BUỔI THỰC HÀNH - BẮT BUỘC)
[BƯỚC 7 - Cả hai]: Chạy stop-environment.ps1 (scale ECS về 0, stop RDS) & ghi số dư vào Nhật ký Chi phí!
```

---

## 📋 DANH MỤC MINH CHỨNG NGHIỆM THU TUẦN 3 (CHECKLIST ẢNH)

### 1. Minh chứng Bảo mật, Giám sát & Co giãn Hạ tầng (Phúc):
- [x] **Ảnh 1:** Danh sách các biến bí mật được mã hóa lưu trữ an toàn trong **AWS Systems Manager Parameter Store** (`/hotel/database/...`).
- [x] **Ảnh 2:** Cấu hình ECS Task Definition hiển thị trường `secrets` ánh xạ từ SSM Parameter ARN (không lộ plaintext).
- [x] **Ảnh 3:** Giao diện CloudWatch Log Groups cho 3 services với **Retention policy** được cấu hình về **3 ngày**.
- [ ] **Ảnh 4:** Kết quả truy vấn **CloudWatch Logs Insights** hiển thị toàn bộ hành trình của 1 giao dịch xuyên suốt qua `correlationId`.
- [x] **Ảnh 5:** Danh sách 4 **CloudWatch Alarms** được cấu hình đầy đủ (High CPU, High Memory, ALB 5XX, SQS DLQ Messages).
- [x] **Ảnh 6:** CloudWatch Alarm kích hoạt trạng thái **ALARM** (đỏ) khi có poison message trong DLQ hoặc khi thực hiện stress test.
- [x] **Ảnh 7:** Giao diện tổng quan **CloudWatch Dashboard** (`HotelBooking-System-Dashboard`) hiển thị đầy đủ các widget chỉ số ECS, ALB, SQS và Logs.
- [ ] **Ảnh 8 (Yêu cầu GVHD):** Cấu hình ECS Service Auto Scaling và ảnh chụp Task count tự động co giãn từ 1 lên 2 tasks khi chạy tải thật.
- [ ] **Ảnh 9 (Yêu cầu GVHD):** Bảng ghi nhận chi phí và ảnh chụp AWS Billing / Credits còn lại kèm trạng thái RDS `Stopped` và ECS Tasks = 0.

### 2. Minh chứng Ứng dụng, Tích hợp & Kiểm thử Tải (Linh):
- [x] **Ảnh 10:** Mã nguồn bộ lọc `CorrelationIdFilter` và cấu hình log xuất `correlationId`: [`10-correlation-id-filter-code.png`](linh/images/10-correlation-id-filter-code.png)
- [x] **Ảnh 11:** Mã nguồn xử lý bồi hoàn (Compensating Transaction) giải phóng phòng khi lỗi: [`11-compensating-transaction-code.png`](linh/images/11-compensating-transaction-code.png)
- [x] **Ảnh 12:** Mã nguồn `@RestControllerAdvice` xử lý validation và lỗi chuẩn RFC 7807: [`12-rfc7807-validation-exception-code.png`](linh/images/12-rfc7807-validation-exception-code.png)
- [x] **Ảnh 13:** Terminal và Amazon ECR hiển thị 3 repository có image tag mới **`v1.1.0`**: [`13-ecr-repositories-v110.png`](linh/images/13-ecr-repositories-v110.png)
- [x] **Ảnh 14:** Kiểm thử Happy Path E2E thành công (Response trả về `201 Created` kèm header `X-Correlation-Id` trên Terminal/curl): [`14-happy-path-e2e-curl.png`](linh/images/14-happy-path-e2e-curl.png)
- [x] **Ảnh 15:** Kiểm thử kịch bản Bồi hoàn (Compensating Rollback): Khi cố ý làm hỏng bước tiếp theo, phòng tự động được mở lại trạng thái `AVAILABLE`: [`15-compensating-rollback-test.png`](linh/images/15-compensating-rollback-test.png)
- [x] **Ảnh 16:** Kiểm thử kịch bản đưa tin nhắn lỗi vào SQS $\rightarrow$ sau 3 lần retry, tin nhắn vào DLQ và in log cảnh báo: [`16-sqs-dlq-retry-proof.png`](linh/images/16-sqs-dlq-retry-proof.png)
- [x] **Ảnh 17 (Yêu cầu GVHD):** Terminal thực thi kịch bản chạy tải thật (`scripts/load-test.ps1`) hiển thị 200 requests hoàn thành thành công 100%: [`17-load-test-terminal-result.png`](linh/images/17-load-test-terminal-result.png)

### Cập nhật Phúc ngày 24/10/2026

Đã tạo SNS hotel-system-alerts và bốn alarm; DLQ từng ALARM từ dữ liệu có sẵn. Ngày25/10 đã tạo6 SSM SecureString, triển khai revision2/image v1.1.0 cho3 service, kiểm tra retention3ngày, lưu2 mẫu query, tạo dashboard và chính sách scaling room/booking CPU50%,1–3task. ECS đã hạ về0/0 cuối phiên; RDS đang dừng tại thời điểm ghi nhận. Người dùng yêu cầu chỉUI, không chạy script: chưa có kiểm thử tải thật, trace giao dịch và thực thi script vận hành. SNS chưa có subscription. Chi tiết: [báo cáo Phúc](phuc/bao-cao-tuan-3.md).

### Cập nhật Linh ngày 25/10/2026

Đã hoàn thành toàn bộ mã nguồn Backend Tuần 3: Distributed Tracing với Correlation ID (Filter, MDC, SQS attributes), Giao dịch bồi hoàn (Compensating Transaction) tránh deadlock phòng, Bean Validation và xử lý ngoại lệ chuẩn RFC 7807 Problem Details. Đã build và push thành công bộ Docker Image tag `v1.1.0` lên Amazon ECR của tài khoản nhóm (`055652951832`). Đã thực hiện đầy đủ các kịch bản kiểm thử Happy Path E2E, Rollback bồi hoàn, Poison Message DLQ và xây dựng script bắn tải thật `scripts/load-test.ps1` (200 requests, concurrency 10). Chi tiết và minh chứng: [báo cáo Linh](linh/bao-cao-tuan-3.md).
