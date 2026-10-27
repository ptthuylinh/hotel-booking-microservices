# KỊCH BẢN CHI TIẾT VIDEO DEMO NGHIỆM THU ĐỒ ÁN (THỜI LƯỢNG $\le$ 10 PHÚT)

## 📌 THÔNG TIN CHUNG
- **Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS (Nhóm: Capstone)
- **Học phần:** Điện toán đám mây (Cloud) — Đợt 1 (2026–2027)
- **Giảng viên hướng dẫn:** Thầy Huỳnh Xuân Phụng
- **Sinh viên thực hiện:**
  - **Phan Thị Thùy Linh** — MSSV: `24110271` (Thuyết minh Tổng quan, Luồng nghiệp vụ & Bồi hoàn)
  - **Cao Hoàng Phúc** — MSSV: `24110303` (Thuyết minh Hạ tầng, Giám sát CloudWatch, Auto Scaling & Chi phí)
- **Quy định thời lượng:** $\le 10$ phút (tuyệt đối không vượt quá 10:00).
- **Độ phân giải:** 1080p (Full HD, 60fps hoặc 30fps).
- **Kênh nộp:** YouTube (Chế độ Unlisted) hoặc Google Drive mở quyền xem.

---

## ⏱️ PHÂN BỔ THỜI LƯỢNG CHI TIẾT TỪNG PHÂN ĐOẠN

| Phân đoạn | Thời gian | Thời lượng | Nội dung chính | Thao tác màn hình | Người nói |
|:---:|:---:|:---:|---|---|:---:|
| **Phần 1** | `00:00 - 01:30` | 1 phút 30s | Giới thiệu thành viên, đề tài & Sơ đồ kiến trúc tổng thể trên AWS | Slide bìa $\rightarrow$ Sơ đồ kiến trúc (Architecture Diagram) | Linh |
| **Phần 2** | `01:30 - 04:30` | 3 phút 00s | Demo luồng nghiệp vụ chuẩn (Happy Path) từ Client qua ALB vào Database & SQS | Postman $\rightarrow$ PostgreSQL console $\rightarrow$ DynamoDB $\rightarrow$ CloudWatch log | Linh |
| **Phần 3** | `04:30 - 06:30` | 2 phút 00s | Demo tính năng nâng cao: Giao dịch bồi hoàn (Rollback) & SQS Dead Letter Queue | Postman bắn lỗi $\rightarrow$ Room status revert $\rightarrow$ SQS DLQ messages | Linh |
| **Phần 4** | `06:30 - 08:30` | 2 phút 00s | Demo Giám sát CloudWatch, Truy vết Correlation ID & Bắn tải kích hoạt Auto Scaling | CloudWatch Logs Insights query $\rightarrow$ Dashboard $\rightarrow$ Terminal chạy load test $\rightarrow$ Task scale từ 1 lên 2 | Phúc |
| **Phần 5** | `08:30 - 09:30` | 1 phút 00s | Demo khả năng tự phục hồi (Self-healing Fargate) & Script dọn dẹp tài nguyên | ECS Console Stop Task $\rightarrow$ Task mới tự sinh $\rightarrow$ Chạy `teardown-environment.ps1` | Phúc |
| **Phần 6** | `09:30 - 10:00` | 30 giây | Tổng kết chi phí thực tế trên AWS Learner Lab, bài học kinh nghiệm & Lời cảm ơn | Bảng Billing/Cost Explorer ($12.50/$50) $\rightarrow$ Slide kết luận | Phúc & Linh |

---

## 🎙️ LỜI THOẠI CHI TIẾT (VOICE-OVER SCRIPT) TỪNG PHÚT

### 🎬 PHẦN 1: GIỚI THIỆU ĐỒ ÁN & KIẾN TRÚC HỆ THỐNG (00:00 – 01:30)

- **Màn hình hiển thị:**
  - `00:00 - 00:20`: Slide mở đầu hiển thị: Tên đề tài, Giảng viên hướng dẫn: Thầy Huỳnh Xuân Phụng, Nhóm Capstone (Phan Thị Thùy Linh & Cao Hoàng Phúc).
  - `00:20 - 01:30`: Sơ đồ kiến trúc hệ thống (`hotel-microservices-architecture`). Con trỏ chuột chỉ vào từng thành phần khi nhắc tới.
- **Lời thoại của Linh:**
  > *"Kính chào Thầy Huỳnh Xuân Phụng và các bạn. Hôm nay, nhóm Capstone gồm em là Phan Thị Thùy Linh và bạn Cao Hoàng Phúc xin phép trình bày và nghiệm thu đồ án: 'Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS'.*
  > 
  > *Hệ thống của tụi em được thiết kế theo chuẩn microservices hiện đại, chạy hoàn toàn không máy chủ trên nền tảng AWS ECS Fargate, phân bổ trên 2 Availability Zones của Region us-east-1. Kiến trúc bao gồm:*
  > - *Cổng vào duy nhất là Application Load Balancer (ALB) thực hiện định tuyến theo đường dẫn (Path-based routing).*
  > - *Ba microservice độc lập: room-service quản lý thông tin phòng và lưu trữ tại PostgreSQL RDS; booking-service xử lý đặt phòng, ghi nhật ký kiểm toán vào DynamoDB; và notification-service lắng nghe sự kiện để mô phỏng gửi email thông báo.*
  > - *Về giao tiếp, hệ thống kết hợp đồng bộ qua REST giữa booking và room-service, kết hợp bất đồng bộ qua Amazon SNS và Amazon SQS.*
  > - *Toàn bộ thông tin nhạy cảm được bảo mật qua SSM Parameter Store dạng SecureString, và hệ thống được giám sát tập trung toàn diện với CloudWatch Logs, Metrics, Alarms và Dashboard.*
  > *Sau đây, em xin phép demo chi tiết luồng nghiệp vụ chính của hệ thống."*

---

### 🎬 PHẦN 2: DEMO LUỒNG NGHIỆP VỤ CHUẨN (HAPPY PATH) (01:30 – 04:30)

- **Màn hình hiển thị:**
  - `01:30 - 02:15`: Giao diện Postman / Terminal gửi lệnh `GET http://<alb-dns>/api/rooms?status=AVAILABLE`.
  - `02:15 - 03:15`: Postman gửi `POST http://<alb-dns>/api/bookings` với body JSON hợp lệ. Nhận lại status `201 Created` và `bookingCode`.
  - `03:15 - 03:45`: Chuyển sang console RDS / DBeaver hiển thị bản ghi mới trong bảng `bookings` và phòng số 1 đổi trạng thái sang `RESERVED`.
  - `03:45 - 04:30`: Chuyển sang DynamoDB Console hiển thị audit log và CloudWatch Logs của `notification-service` hiển thị log tiêu thụ tin nhắn từ SQS thành công.
- **Lời thoại của Linh:**
  > *"Trước tiên, từ phía client, em gửi request tra cứu các phòng còn trống qua DNS của ALB: `GET /api/rooms?status=AVAILABLE`. ALB điều phối chính xác về cụm room-service và trả về danh sách các phòng khả dụng.*
  > 
  > *Tiếp theo, khách hàng tiến hành đặt phòng số 1 bằng request `POST /api/bookings`. Hệ thống xử lý qua chuỗi thao tác liên dịch vụ:*
  > *Thứ nhất, booking-service gọi REST sang room-service để khóa phòng sang trạng thái RESERVED.*
  > *Thứ hai, đơn đặt phòng được lưu thành công vào PostgreSQL với mã booking là BK-xxxx và trạng thái CONFIRMED.*
  > *Thứ ba, một bản ghi kiểm toán được ghi tức thì vào Amazon DynamoDB để lưu vết lịch sử giao dịch.*
  > *Và thứ tư, booking-service phát hành sự kiện BookingCreatedEvent lên SNS Topic. SNS phân phối thông điệp này vào SQS Queue.*
  > 
  > *Như thầy đang thấy trên CloudWatch Logs của notification-service: Worker đã tiếp nhận thông điệp từ SQS, giải nén đúng Correlation ID và in log mô phỏng việc gửi email xác nhận cho khách hàng trong vòng chưa đầy 1 giây."*

---

### 🎬 PHẦN 3: XỬ LÝ LỖI, BỒI HOÀN GIAO DỊCH & DEAD LETTER QUEUE (04:30 – 06:30)

- **Màn hình hiển thị:**
  - `04:30 - 05:15`: Postman gửi request sai email và ngày quá khứ $\rightarrow$ Trả về mã lỗi 400 chuẩn RFC 7807 (Problem Details).
  - `05:15 - 06:00`: Demo kịch bản Compensating Transaction: Cố tình kích hoạt lỗi ở bước lưu đơn $\rightarrow$ Kiểm tra lại phòng bên `room-service`, trạng thái phòng tự động được rollback mở lại `AVAILABLE`.
  - `06:00 - 06:30`: AWS SQS Console: Cho xem `booking-notification-dlq` nhận poison message sau 3 lần retry, kèm CloudWatch Alarm đổi sang màu đỏ.
- **Lời thoại của Linh:**
  > *"Để đảm bảo tính toàn vẹn và bảo mật dữ liệu, nhóm triển khai chuẩn hóa xử lý lỗi RFC 7807 và Bean Validation. Khi client gửi một payload không hợp lệ — ví dụ email sai định dạng — hệ thống trả về ngay mã lỗi 400 kèm chi tiết lỗi chuẩn hóa, che giấu hoàn toàn cấu trúc dữ liệu nội bộ.*
  > 
  > *Đặc biệt, trong giao dịch phân tán, nếu bước lưu DB hoặc phát SNS gặp sự cố, hệ thống sẽ tự động kích hoạt Cơ chế Bồi hoàn giao dịch (Compensating Transaction). Như thầy đang quan sát trên màn hình: Khi bước sau xảy ra lỗi, booking-service ngay lập tức gửi lệnh bồi hoàn để mở khóa lại phòng về trạng thái AVAILABLE. Nhờ đó, phòng không bao giờ bị khóa 'ma', khách hàng khác vẫn có thể tiếp tục đặt.*
  > 
  > *Đối với hàng đợi bất đồng bộ, nếu có một tin nhắn độc hại (poison message) mà notification-service không thể parse, hệ thống sẽ tự động retry 3 lần. Nếu vẫn thất bại, tin nhắn được chuyển thẳng vào Dead Letter Queue (DLQ) để bảo vệ hàng đợi chính không bị tắc nghẽn, đồng thời kích hoạt CloudWatch Alarm gửi cảnh báo về hệ thống.*
  > 
  > *Tiếp theo, bạn Phúc sẽ trình bày phần Giám sát, Khả năng tự co giãn và Tối ưu chi phí."*

---

### 🎬 PHẦN 4: GIÁM SÁT CLOUDWATCH, TRACING & AUTO SCALING (06:30 – 08:30)

- **Màn hình hiển thị:**
  - `06:30 - 07:15`: Giao diện CloudWatch Logs Insights: Chạy câu truy vấn lọc theo mã `correlationId` duy nhất, hiển thị log trải dài qua cả 3 services.
  - `07:15 - 07:45`: Giao diện CloudWatch Dashboard `HotelBooking-System-Dashboard`: Các widgets CPU, RAM, Request Count, Healthy Host, SQS visible messages.
  - `07:45 - 08:30`: Màn hình chia đôi: Một bên chạy script `load-test.ps1` (200-500 requests), một bên mở ECS Service `booking-service` quan sát Task count tự động scale từ 1 task lên 2 tasks.
- **Lời thoại của Phúc:**
  > *"Kính thưa Thầy, em xin phép tiếp tục phần giám sát và vận hành hạ tầng.*
  > 
  > *Về Distributed Tracing: Nhóm đã triển khai bộ lọc CorrelationIdFilter trên cả 3 services kết hợp cùng SLF4J MDC. Khi truy vấn trên CloudWatch Logs Insights với một mã Correlation ID duy nhất, chúng ta có thể theo dõi chính xác hành trình của request từ lúc chạm vào booking-service, gọi sang room-service cho đến khi notification-service tiêu thụ xong tin nhắn từ SQS.*
  > 
  > *Về bảng điều khiển vận hành: Tụi em đã cấu hình Dashboard tập trung 'HotelBooking-System-Dashboard' giúp theo dõi tức thời mức tiêu thụ CPU/RAM, số lượng Healthy Target của ALB, và 4 CloudWatch Alarms cảnh báo ngưỡng.*
  > 
  > *Đặc biệt, theo đúng yêu cầu kiểm thử tải thật của Thầy ở Tuần 3: Em đang thực thi script load-test.ps1 bắn 200 requests đồng thời vào ALB. Khi chỉ số CPU của booking-service tăng vượt ngưỡng 50%, chính sách ECS Service Auto Scaling đã ngay lập tức kích hoạt, tự động nâng số lượng Task từ 1 lên 2 tasks Fargate để đáp ứng tải, và sau khi hết tải sẽ tự động co về 1 task để tiết kiệm chi phí."*

---

### 🎬 PHẦN 5: CHỊU LỖI HẠ TẦNG (SELF-HEALING) & DỌN DẸP TÀI NGUYÊN (08:30 – 09:30)

- **Màn hình hiển thị:**
  - `08:30 - 09:05`: Trên ECS Console, bấm `Stop` cưỡng bức 1 task đang chạy. Fargate lập tức chuyển task sang `STOPPED` và khởi tạo ngay 1 task mới (`PROVISIONING` $\rightarrow$ `RUNNING`). ALB cập nhật lại target healthy.
  - `09:05 - 09:30`: Mở Terminal, hiển thị và giải thích script `scripts/teardown-environment.ps1` để giải phóng toàn bộ tài nguyên.
- **Lời thoại của Phúc:**
  > *"Để chứng minh độ sẵn sàng cao và khả năng tự phục hồi (Self-healing), em sẽ cố ý dừng đột ngột một container Fargate đang chạy của booking-service.*
  > 
  > *Như thầy thấy, ECS Service Scheduler ngay lập tức phát hiện số lượng task thực tế thấp hơn Desired Count = 1, và tự động spawn một container mới để thay thế trong vòng chưa đầy 15 giây. Trong suốt thời gian này, ALB tự động loại bỏ task lỗi và điều phối traffic sang task mới mà không làm gián đoạn người dùng.*
  > 
  > *Sau mỗi buổi làm việc cũng như sau khi kết thúc nghiệm thu, nhóm sử dụng bộ kịch bản tự động hóa teardown-environment.ps1 để scale toàn bộ ECS tasks về 0, dừng RDS và xóa các tài nguyên tính phí, bảo đảm không bị phát sinh chi phí ngầm."*

---

### 🎬 PHẦN 6: TỔNG KẾT CHI PHÍ & LỜI KẾT (09:30 – 10:00)

- **Màn hình hiển thị:**
  - `09:30 - 09:45`: AWS Billing / Cost Explorer Console hiển thị tổng số tiền đã dùng là ~$12.50 USD / hạn mức $50.00 USD (Credits còn dư > $37.00 USD).
  - `09:45 - 10:00`: Slide cảm ơn và thông tin liên hệ.
- **Lời thoại của Phúc & Linh:**
  > *(Phúc): "Tổng kết lại qua 4 tuần thực hiện đồ án, nhóm đã kiểm soát chi phí cực kỳ chặt chẽ: Chỉ sử dụng khoảng 12.5 đô trên tổng số 50 đô được cấp của AWS Academy Learner Lab, bảo toàn an toàn ngân sách cho đến ngày nghiệm thu cuối cùng.*
  > 
  > *(Linh): Đồ án đã giúp tụi em nắm vững toàn bộ quy trình thiết kế, triển khai, bảo mật và vận hành hệ thống Microservices chuẩn production trên AWS. Nhóm Capstone xin chân thành cảm ơn Thầy Huỳnh Xuân Phụng đã luôn tận tình hướng dẫn, góp ý sát sao để tụi em hoàn thành đề tài này. Tụi em xin cảm ơn Thầy!"*

---

## 🛠️ HƯỚNG DẪN KỸ THUẬT QUAY VIDEO (DÀNH CHO 2 BẠN)
1. **Phần mềm quay màn hình:** Dùng **OBS Studio** hoặc **Xbox Game Bar (Win + G)** tích hợp sẵn trên Windows.
2. **Cài đặt âm thanh:** Đeo tai nghe có mic, nói to, rõ ràng, dứt khoát. Trong OBS có thể bật bộ lọc *Noise Suppression* để lọc tạp âm.
3. **Thao tác chuột:** Di chuyển chuột chậm rãi, trỏ đúng vào vùng đang thuyết minh (tránh rê chuột lung tung gây rối mắt).
4. **Kiểm tra thời lượng:** Bấm đồng hồ bấm giờ trên điện thoại bên cạnh. Nếu quay đoạn nào dài quá thì ngắt ra quay lại đoạn đó, sau đó ghép lại bằng CapCut / Premiere để đảm bảo tổng video nằm trong khoảng **9 phút 30 giây đến 9 phút 50 giây**.
