# BỘ CÂU HỎI & CÂU TRẢ LỜI VẤN ĐÁP BẢO VỆ ĐỒ ÁN (Q&A DEFENSE PREPARATION)

**Học phần:** Điện toán đám mây (Cloud) — Đợt 1 (2026–2027)  
**Giảng viên hướng dẫn:** Thầy Huỳnh Xuân Phụng  
**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS (Nhóm: Capstone)  
**Sinh viên:** Phan Thị Thùy Linh (`24110271`) & Cao Hoàng Phúc (`24110303`)  

---

### ❓ Câu 1: Tại sao nhóm chọn triển khai trên AWS ECS Fargate thay vì ECS EC2 Launch Type hay Kubernetes (EKS)?
- **Trả lời:**
  - **Fargate là Serverless Container:** Nhóm không phải quản lý, vá lỗi hay cấu hình hệ điều hành cho các EC2 instances chạy ngầm. Fargate tự động cấp phát tài nguyên tính toán (vCPU/RAM) chính xác theo nhu cầu của container.
  - **Phù hợp với giới hạn AWS Learner Lab:** Hạn mức EC2 của Learner Lab rất giới hạn ($\le 9$ instances, $\le 32$ vCPUs). Dùng Fargate giúp nhóm tránh việc vượt quá quota EC2 và không bị lãng phí chi phí khi máy ảo chạy không tải.
  - **Khởi động nhanh & Scaling mượt mà:** Fargate tích hợp trực tiếp với Application Load Balancer và Application Auto Scaling, cho phép co giãn số lượng task tức thì dựa trên CPU/Request Count mà không cần chờ cụm EC2 scale-out trước.
  - **So với EKS:** EKS có chi phí quản lý control plane cố định ($0.10/giờ $\approx$ $72/tháng), vượt quá hạn mức $50 của Lab, trong khi ECS là miễn phí control plane, chỉ tính phí tài nguyên Fargate thực tế tiêu thụ.

---

### ❓ Câu 2: Trong kiến trúc microservices của nhóm, tại sao lại tách thành 3 dịch vụ (`room`, `booking`, `notification`)?
- **Trả lời:**
  - Nhóm áp dụng nguyên lý **Single Responsibility Principle** và **Domain-Driven Design (DDD)**:
    1. **`room-service` (Quản lý Phòng):** Đặc thù là tần suất đọc (Read) cực kỳ cao do người dùng liên tục tra cứu, tìm kiếm phòng trống. Service này cần scale độc lập về số lượng đọc mà không ảnh hưởng đến việc ghi giao dịch.
    2. **`booking-service` (Giao dịch Đặt phòng):** Đặc thù là tác vụ ghi (Write-heavy) đòi hỏi tính nhất quán giao dịch, tính toán giá tiền, ghi audit log và phát hành sự kiện.
    3. **`notification-service` (Gửi Thông báo):** Là tác vụ phụ trợ, tốn thời gian I/O (gọi SMTP/SES hoặc API gửi tin nhắn). Việc tách service này giúp cô lập độ trễ, nếu dịch vụ gửi mail bị chậm hoặc sập thì luồng đặt phòng của khách hàng vẫn thành công bình thường.

---

### ❓ Câu 3: Giao tiếp giữa các services: Khi nào nhóm dùng REST đồng bộ, khi nào dùng SNS/SQS bất đồng bộ?
- **Trả lời:**
  - **Dùng REST đồng bộ (`booking-service` $\rightarrow$ `room-service`):**
    - Khi đặt phòng, `booking-service` **bắt buộc phải biết ngay lập tức** phòng đó có tồn tại và còn trống hay không để khóa phòng (`PUT /api/rooms/{id}/status`). Đây là giao dịch cốt lõi mang tính tức thời, client không thể chờ xử lý bất đồng bộ.
  - **Dùng Amazon SNS/SQS bất đồng bộ (`booking-service` $\rightarrow$ `notification-service`):**
    - Áp dụng mô hình **Event-Driven Architecture (Pub/Sub)**. Khi đơn đặt phòng được tạo, `booking-service` phát sự kiện `BookingCreatedEvent` lên SNS Topic rồi phản hồi ngay cho người dùng (`201 Created`).
    - Việc gửi email thông báo không cần trả kết quả ngay cho người dùng. SQS hoạt động như một bộ đệm (Buffer): Nếu lưu lượng đặt phòng tăng vọt, tin nhắn xếp hàng an toàn trong SQS và `notification-service` tiêu thụ dần mà không làm sập ứng dụng.

---

### ❓ Câu 4: Nhóm giải quyết bài toán giao dịch phân tán (Distributed Transaction) như thế nào khi không dùng 2-Phase Commit (2PC)?
- **Trả lời:**
  - Trong môi trường microservices đám mây, 2PC gây khóa tài nguyên (blocking) và làm giảm nghiêm trọng hiệu năng cũng như tính sẵn sàng của hệ thống.
  - Nhóm áp dụng mô hình **Compensating Transaction (Giao dịch bồi hoàn/bù trừ)** theo mẫu Saga:
    1. Bước 1: `booking-service` gọi REST khóa phòng bên `room-service` (`status = RESERVED`).
    2. Bước 2: `booking-service` tiến hành lưu đơn vào DB và phát SNS.
    3. **Xử lý sự cố:** Nếu bước 2 xảy ra lỗi (DB sập hoặc mạng đứt), khối `catch` trong `BookingService.java` ngay lập tức kích hoạt giao dịch bồi hoàn: tự động gọi REST sang `room-service` (`releaseRoom`) để đổi trạng thái phòng trở lại `AVAILABLE`.
    - Nhờ đó, loại bỏ triệt để hiện tượng khóa phòng "ma" (deadlock tài nguyên), đảm bảo tính nhất quán cuối cùng (**Eventual Consistency**).

---

### ❓ Câu 5: Dead Letter Queue (DLQ) trong hệ thống hoạt động ra sao và giải quyết vấn đề gì?
- **Trả lời:**
  - Khi một thông điệp trong SQS bị lỗi định dạng (Poison Message) hoặc `notification-service` bị lỗi logic không thể xử lý:
    - Consumer ném ra ngoại lệ, SQS sẽ không xóa tin nhắn và đưa tin nhắn quay lại hàng đợi sau khoảng thời gian `VisibilityTimeout`.
    - Nhóm đã cấu hình `maxReceiveCount = 3`. Nếu tin nhắn bị lỗi liên tiếp 3 lần, Amazon SQS sẽ tự động tách tin nhắn đó ra khỏi hàng đợi chính và chuyển vào **`booking-notification-dlq`**.
  - **Lợi ích:**
    - Ngăn chặn tin nhắn lỗi làm tắc nghẽn toàn bộ hàng đợi, giúp các đơn đặt phòng hợp lệ tiếp theo được xử lý thông suốt.
    - CloudWatch Alarm `SQS-DLQ-Has-Poison-Messages` sẽ kích hoạt báo động để kỹ sư vận hành vào điều tra nguyên nhân.

---

### ❓ Câu 6: Distributed Tracing với Correlation ID được triển khai cụ thể thế nào?
- **Trả lời:**
  - Nhóm xây dựng bộ lọc `CorrelationIdFilter` áp dụng trên cả 3 services:
    1. Tiếp nhận header `X-Correlation-Id` từ client (hoặc tự sinh UUID nếu client không truyền).
    2. Nạp ID vào SLF4J **Mapped Diagnostic Context (MDC)**. Mọi dòng log xuất ra đều tự động có tiền tố `[%X{correlationId}]`.
    3. Gắn `X-Correlation-Id` vào header của REST call nội bộ (`RoomClient`).
    4. Gắn `correlationId` vào Message Attributes của Amazon SNS/SQS.
    5. Tại `notification-service`, worker đọc Message Attribute và nạp vào MDC trước khi xử lý.
  - **Kết quả:** Trên **CloudWatch Logs Insights**, chỉ cần gõ `filter correlationId = '...'` là có thể truy vết toàn bộ hành trình của một request qua cả 3 services trên một màn hình duy nhất.

---

### ❓ Câu 7: Nhóm bảo mật thông tin nhạy cảm (Credentials, DB URL) trên ECS như thế nào?
- **Trả lời:**
  - Nhóm **tuyệt đối không** hardcode mật khẩu trong mã nguồn hay để lộ plaintext trong biến môi trường `environment` của Docker.
  - Nhóm lưu trữ toàn bộ mật khẩu kết nối cơ sở dữ liệu trên **AWS Systems Manager (SSM) Parameter Store** dưới dạng **`SecureString`** (được mã hóa tự động bằng AWS KMS).
  - Trong ECS Task Definition, nhóm cấu hình trường `secrets` với thuộc tính `valueFrom` trỏ tới ARN của Parameter Store.
  - Khi khởi chạy container, ECS Agent sẽ sử dụng quyền của `LabRole` để giải mã và inject trực tiếp biến môi trường vào trong container lúc runtime.

---

### ❓ Câu 8: Cơ chế Auto Scaling của ECS được cấu hình thế nào và hoạt động ra sao?
- **Trả lời:**
  - Nhóm cấu hình **Application Auto Scaling** theo chính sách **Target Tracking Scaling Policy** cho `booking-service` và `room-service`.
  - **Thông số:** Minimum tasks = `1`, Maximum tasks = `3`.
  - **Chỉ số theo dõi (Metric):** `ECSServiceAverageCPUUtilization` với ngưỡng mục tiêu là **50%**.
  - **Nguyên lý:** Khi chạy script bắn tải thật (`scripts/load-test.ps1`) với hàng trăm requests đồng thời, CPU container tăng vượt ngưỡng 50%, CloudWatch Alarm kích hoạt Auto Scaling nâng số Task từ 1 lên 2 tasks. Khi hết tải, hệ thống tự động co về 1 task để tối ưu chi phí.

---

### ❓ Câu 9: Nhóm đã quản lý chi phí như thế nào để không bị âm tài khoản Learner Lab ($50)?
- **Trả lời:**
  - Sau mỗi buổi thực hành, nhóm luôn chạy script `scripts/stop-environment.ps1` để scale toàn bộ ECS tasks về `0` và tạm dừng (`Stop`) RDS PostgreSQL Instance.
  - Log Retention của CloudWatch được giới hạn ở mức **3 ngày** thay vì Never Expire để tránh phát sinh chi phí lưu trữ log.
  - Định kỳ theo dõi số dư Credits trên AWS Billing Dashboard: Tính đến cuối Tuần 3, nhóm chỉ mới sử dụng **$10.20 USD / $50.00 USD** (còn dư gần $40 USD).
  - Cuối kỳ, nhóm chuẩn bị sẵn script `scripts/teardown-environment.ps1` để giải phóng toàn bộ tài nguyên có phí về mức $0.

---

### ❓ Câu 10: Khi một container Fargate bị sập bất ngờ (Crash/Kill), hệ thống tự phục hồi thế nào?
- **Trả lời:**
  - **Tự chữa lành (Self-healing):** Trong cấu hình ECS Service, nhóm thiết lập `Desired Count = 1`. Nếu container bị crash (hoặc bị dừng bằng tay), ECS Service Scheduler sẽ ngay lập tức nhận diện trạng thái và khởi tạo một Task Fargate mới để thay thế trong vòng 10–15 giây.
  - **Khử đăng ký tại ALB:** ALB liên tục gửi Health Check (`GET /actuator/health`). Khi container sập, ALB lập tức chuyển target sang trạng thái `Unhealthy` và ngừng gửi traffic vào đó. Khi task mới đạt trạng thái `Healthy`, ALB mới bắt đầu định tuyến lưu lượng vào task mới, đảm bảo tính liên tục của dịch vụ.

---

### ❓ Câu 11: Chuẩn lỗi RFC 7807 (Problem Details) mang lại lợi ích gì cho hệ thống?
- **Trả lời:**
  - **Tính chuẩn hóa:** Cung cấp định dạng JSON báo lỗi đồng nhất theo chuẩn quốc tế RFC 7807 (`type`, `title`, `status`, `detail`, `instance`).
  - **Bảo mật ứng dụng (Security):** Che giấu hoàn toàn các thông tin nhạy cảm của hệ thống backend như tên bảng cơ sở dữ liệu, câu lệnh SQL, stack trace nội bộ khi xảy ra lỗi. Client chỉ nhận được thông báo lỗi thân thiện mà không thể khai thác lỗ hổng từ thông báo lỗi.

---

### ❓ Câu 12: Đồ án còn những hạn chế gì và nếu triển khai môi trường thực tế (Production) nhóm sẽ nâng cấp những gì?
- **Trả lời:**
  - **Hạn chế do môi trường Lab:** Vì dùng AWS Learner Lab nên không thể tạo Custom IAM Roles riêng lẻ cho từng service (phải dùng chung `LabRole`), và RDS chỉ chạy Single-AZ để tiết kiệm tiền.
  - **Hướng nâng cấp thực tế (Production):**
    1. Triển khai **API Gateway** ở tầng trước ALB để hỗ trợ Rate Limiting, xác thực JWT / OAuth2 và bảo vệ chống tấn công DDoS qua AWS WAF.
    2. Nâng cấp RDS sang mô hình **Multi-AZ** với Read Replica để tăng cường độ sẵn sàng và chịu lỗi thảm họa.
    3. Áp dụng **AWS Fargate Spot** cho các worker phi trạng thái (`notification-service`) để giảm tới 70% chi phí điện toán đám mây.
    4. Xây dựng đường ống **CI/CD hoàn chỉnh** qua GitHub Actions / AWS CodePipeline để tự động build, test và deploy image lên ECR/ECS mỗi khi merge code.
