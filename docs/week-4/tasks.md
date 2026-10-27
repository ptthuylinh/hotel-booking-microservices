# KẾ HOẠCH & PHÂN CHIA NHIỆM VỤ TUẦN 4 (WORKLOG TUẦN 4 - NƯỚC RÚT & NGHIỆM THU)

## 📌 THÔNG TIN ĐỒ ÁN
- **Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS (Nhóm: Capstone)
- **Học phần:** Điện toán đám mây (Cloud) - Đợt 1 (Năm học 2026–2027)
- **Giảng viên hướng dẫn (GVHD):** Thầy Huỳnh Xuân Phụng
- **Mục tiêu Tuần 4:** Kiểm thử tổng thể (Comprehensive E2E, High-Load & Resilience Testing), Tối ưu hóa chi phí & Báo cáo sử dụng ngân sách AWS Learner Lab, Xây dựng kịch bản dọn dẹp tài nguyên an toàn (Teardown Script), Sản xuất Video Demo nghiệm thu ($\le 10$ phút), và Hoàn thiện Báo cáo Tổng kết Đồ án cùng Slide thuyết trình bảo vệ (Mỗi sinh viên thực hiện $\ge$ 8.0 giờ/tuần).
- **Môi trường thực hành:** AWS Academy Learner Lab, Region `us-east-1`, Account ID: `0556-5295-1832` (Tài khoản nhóm của Phan Thị Thùy Linh).
- **Quy định IAM bắt buộc:** Sử dụng `LabRole` / `LabInstanceProfile` (Không tạo IAM User / Custom Role).

---

## 📢 TIẾP THU NHẬN XÉT CỦA GVHD SAU BÁO CÁO TUẦN 3 & ĐỊNH HƯỚNG TUẦN 4

> **Trích nhận xét đánh giá của Thầy Huỳnh Xuân Phụng (Tuần 3):**  
> *"I. Phần đạt:  
> - 9 commit trên nhánh week-3 thầy đã kiểm tra đủ: 6 của Linh (400de7f — Bean Validation + RFC 7807 + Correlation ID; 54ec1f9 — ECR v1.1.0; 10ccbe3 — cập nhật kế hoạch theo góp ý GVHD; ffbe430, 6e61d7b, 6a70a05 — báo cáo + ảnh minh chứng) và 3 của Phúc (6607c95, b6f9851 — CloudWatch alarms; 794be84 — SSM deployment monitoring).  
> - 3 file tài liệu (tasks.md, báo cáo của Phúc, báo cáo của Linh) và 3 thư mục service trên nhánh week-3 đều mở được.  
> - Phân công rõ: Phúc (24110303) 9h — SSM SecureString, ECS Task Definitions v2, 4 CloudWatch Alarms, dashboard, auto scaling; Linh (24110271) 9h — Bean Validation/RFC 7807, image ECR v1.1.0, load test 200 requests, E2E 5/5 kịch bản.  
> - Mục "Khai báo sử dụng AI" trung thực (GPT-4o, Claude 3.5 Sonnet, Antigravity — rà soát cú pháp SSM, tham khảo cấu trúc filter, dàn ý báo cáo); tuần 2 đã được duyệt nên tiến độ liên tục.  
> - Lưu ý 1: phạm vi AI có mục "hoàn thiện dàn ý báo cáo" — thầy chấp nhận ở mức dàn ý, phần nội dung chi tiết các em tự viết.  
> - Lưu ý 2: báo cáo có file .docx đính kèm, file đính kèm thầy không mở khi chấm, việc duyệt dựa trên nội dung trong form và repo — nếu file có nội dung quan trọng hơn form, em đưa vào form.  
> III. Kết luận: Duyệt."*

### Hành động cụ thể của nhóm trong Tuần 4 nhằm đáp ứng triệt để góp ý của GVHD:
1. **Tuân thủ nguyên tắc sử dụng AI (Lưu ý 1):** Tiếp tục khai báo trung thực. Các công cụ AI (Antigravity IDE, Claude 3.5 Sonnet, GPT-4o) chỉ được dùng để hỗ trợ lập dàn ý báo cáo, format bảng biểu Markdown, và rà soát cú pháp câu lệnh PowerShell. Toàn bộ phần phân tích số liệu tải, đánh giá chi phí, triển khai trên AWS Learner Lab và nội dung chi tiết trong báo cáo tổng kết đều do 2 sinh viên trực tiếp thực hiện và tự viết.
2. **Hình thức nộp báo cáo (Lưu ý 2):** Tuyệt đối không phụ thuộc vào file đính kèm `.docx`. Toàn bộ nội dung Báo cáo Tổng kết Đồ án, Bảng phân công, Worklog, Nhật ký chi phí, Ma trận kiểm thử, Link Video Demo, và Ảnh chụp minh chứng đều được định dạng chuẩn GitHub Flavored Markdown để **dán trực tiếp vào khung nội dung Form Báo cáo Online trên LMS**, đồng thời đồng bộ đầy đủ trên kho mã nguồn GitHub nhánh `week-4` và `main`.
3. **Tiếp nối tiến độ liên tục:** Sau khi hoàn thành tích hợp, giám sát và auto-scaling ở Tuần 3, Tuần 4 là giai đoạn nước rút tập trung vào nghiệm thu chất lượng hệ thống, quay dựng video demo cô đọng $\le 10$ phút và giải phóng tài nguyên an toàn.

---

## 👥 BẢNG PHÂN CÔNG CÔNG VIỆC TUẦN 4 (WORKLOG TỔNG THỂ)

| STT | Thành viên | MSSV | Vai trò chính trong Tuần 4 | Số giờ dự kiến | Trạng thái |
|:---:|---|:---:|---|:---:|:---:|
| 1 | **Cao Hoàng Phúc** | `24110303` | **Cloud Infrastructure, Resilience, Cost Optimization & Teardown (DevOps Lead):** Kiểm thử chịu lỗi hạ tầng (Resilience & Chaos Testing trên ECS Fargate / ALB / RDS); Phân tích & Tối ưu hóa chi phí AWS Learner Lab; Xây dựng Sơ đồ Kiến trúc Tổng thể cuối kỳ; Xây dựng kịch bản & quy trình dọn dẹp tài nguyên an toàn (`scripts/teardown-environment.ps1`); Phối hợp quay video demo phần hạ tầng & giám sát. | 9.5 giờ | **Đang thực hiện** |
| 2 | **Phan Thị Thùy Linh** | `24110271` | **Backend Architecture, Comprehensive Testing, Video Demo & Final Documentation (Project Lead):** Kiểm thử tổng thể E2E đa kịch bản (8 test cases bao gồm Happy Path, Rollback bồi hoàn, DLQ poison message); Biên tập và sản xuất Video Demo nghiệm thu ($\le 10$ phút); Soạn thảo Báo cáo Tổng kết Đồ án hoàn chỉnh trên Form Online & Repo; Thiết kế Slide Thuyết trình và bộ câu hỏi/trả lời vấn đáp bảo vệ. | 9.5 giờ | **Đang thực hiện** |

---

## 🛠️ CHI TIẾT NHIỆM VỤ TỪNG THÀNH VIÊN TRONG TUẦN 4

### 🔹 Thành viên 1: Cao Hoàng Phúc (MSSV: 24110303)
- **Vai trò:** Phụ trách Kiểm thử Chịu lỗi Hạ tầng (Resilience Testing), Đánh giá & Tối ưu Chi phí Vận hành, Hoàn thiện Sơ đồ Kiến trúc và Dọn dẹp Tài nguyên.
- **Số giờ dự kiến:** 9.5 giờ.
- **Nhiệm vụ chi tiết:**

1. **Kiểm thử Chịu lỗi Hạ tầng & Phục hồi Tự động (Resilience & Chaos Testing - 2.5 giờ):**
   - **Kịch bản 1 (ECS Task Self-healing):** Giả lập sự cố bằng cách cưỡng bức dừng (`Stop-Task`) 1 container Fargate đang chạy của `booking-service`. Quan sát ECS Service Scheduler phát hiện container bị down và tự động khởi tạo task mới để duy trì `Desired Count = 1`.
   - **Kịch bản 2 (ALB Target Deregistration & Health Check):** Khi container lỗi hoặc khởi động chậm, kiểm chứng ALB Target Group chuyển trạng thái sang `Unhealthy`, ngừng điều phối lưu lượng vào task này, và tự động khôi phục chuyển traffic khi task mới `Healthy`.
   - **Kịch bản 3 (RDS / Database Network Blocker):** Tạm thời chặn Security Group hoặc dừng RDS để kiểm chứng ứng dụng bắt lỗi gracefully, trả về mã lỗi 503 RFC 7807, không bị crash toàn bộ service và ghi nhận alarm kích hoạt.

2. **Phân tích & Tối ưu hóa Chi phí Sử dụng AWS (Cost Analysis & Optimization Report - 2.0 giờ):**
   - Truy xuất dữ liệu từ AWS Cost Explorer / Billing Dashboard của tài khoản Learner Lab `0556-5295-1832`.
   - Lập bảng tổng kết chi phí thực tế đã sử dụng qua 4 tuần (So sánh với hạn mức $50.00 USD được cấp ban đầu).
   - Phân tích cơ cấu chi phí theo từng dịch vụ: ECS Fargate vCPU/Memory, ALB (Hourly + LCU), RDS PostgreSQL (`db.t3.micro`), DynamoDB, CloudWatch (Logs retention, metrics, alarms), Data Transfer.
   - Xây dựng báo cáo đề xuất tối ưu hóa chi phí cho môi trường Production thực tế:
     - Ứng dụng **AWS Fargate Spot** (tiết kiệm đến 70% chi phí tính toán cho các service phi trạng thái như `notification-service`).
     - Áp dụng **Compute Savings Plans / Reserved Instances** cho cụm container cố định.
     - Thiết lập Lifecycle Rules lưu trữ CloudWatch Logs sang S3 Glacier sau 7 ngày.
     - Tận dụng DynamoDB On-Demand Capacity thay vì Provisioned.

3. **Hoàn thiện Sơ đồ Kiến trúc Tổng thể Cuối Kỳ (Final Architecture Diagram - 1.5 giờ):**
   - Cập nhật sơ đồ kiến trúc chuẩn AWS Architecture Icons với đầy đủ các thành phần:
     - VPC 2 Availability Zones (`us-east-1a`, `us-east-1b`), Public Subnets (ALB, NAT/IGW) và Private Subnets (ECS Fargate, RDS PostgreSQL).
     - Luồng định tuyến Application Load Balancer (Path-based routing: `/api/rooms*`, `/api/bookings*`).
     - Tầng dữ liệu: Amazon RDS PostgreSQL (`hotel-db-instance`), Amazon DynamoDB (`booking-audit-log`).
     - Tầng trao đổi thông điệp bất đồng bộ: Amazon SNS (`booking-events-topic`), Amazon SQS (`booking-notification-queue`) kèm Dead Letter Queue (`booking-notification-dlq`).
     - Tầng bảo mật & giám sát: AWS Systems Manager Parameter Store (`SecureString`), Amazon CloudWatch (Logs Groups retention 3 ngày, Metrics, 4 Alarms, Dashboard tập trung).

4. **Xây dựng Kịch bản & Quy trình Dọn dẹp Triệt để Tài nguyên (Teardown Script - 1.5 giờ):**
   - Phát triển kịch bản PowerShell `scripts/teardown-environment.ps1` tự động giải phóng toàn bộ tài nguyên trên Learner Lab theo thứ tự an toàn:
     - Bước 1: Scale toàn bộ ECS Services về `desired-count 0`, xóa service và cluster.
     - Bước 2: Hủy đăng ký targets và xóa ALB Target Groups, ALB Listeners, ALB.
     - Bước 3: Dừng và xóa RDS Database instance (skip final snapshot theo đặc thù lab).
     - Bước 4: Xóa Amazon SQS Queues, DLQ và Amazon SNS Topics.
     - Bước 5: Xóa CloudWatch Alarms và Dashboard (giữ lại logs cần thiết làm minh chứng).
     - Bước 6: Xóa các tham số trong SSM Parameter Store (`/hotel/...`).
   - Kiểm tra xác nhận số dư Credits còn lại của Learner Lab sau khi dọn dẹp để đảm bảo tài khoản không bị phát sinh chi phí ngầm.

5. **Phối hợp Sản xuất Video Demo & Chuẩn bị Vấn đáp Kỹ thuật (2.0 giờ):**
   - Trực tiếp thực hiện các thao tác trên AWS Console và Windows Terminal cho các phân đoạn kỹ thuật trong Video Demo: Kiểm tra CloudWatch Dashboard, Logs Insights, ECS Auto Scaling khi tải cao, và cơ chế tự chữa lành của Fargate.
   - Cùng Linh chuẩn bị slide thuyết trình và luyện tập kịch bản trả lời các câu hỏi phản biện liên quan đến hạ tầng, bảo mật SSM, và chi phí đám mây.

---

### 🔹 Thành viên 2: Phan Thị Thùy Linh (MSSV: 24110271)
- **Vai trò:** Phụ trách Kiểm thử Nghiệp vụ Toàn diện E2E, Biên tập & Sản xuất Video Demo Nghiệm thu, Soạn thảo Báo cáo Tổng kết Đồ án và Slide Thuyết trình.
- **Số giờ dự kiến:** 9.5 giờ.
- **Nhiệm vụ chi tiết:**

1. **Kiểm thử Toàn diện End-to-End & Ma Trận Kiểm Thử Nghiệp Vụ (Comprehensive E2E Testing - 2.5 giờ):**
   - Xây dựng bảng Ma trận Kiểm thử (Test Matrix) gồm 8 kịch bản bao quát mọi trường hợp:
     - **TC01 (Tra cứu phòng):** `GET /api/rooms` và `GET /api/rooms?status=AVAILABLE` trả về danh sách kèm header `X-Correlation-Id`.
     - **TC02 (Happy Path Đặt phòng):** `POST /api/bookings` thành công (201 Created), trừ phòng bên `room-service`, ghi PostgreSQL, ghi DynamoDB audit log, phát SNS sang SQS, `notification-service` tiêu thụ message và giả lập gửi email thành công.
     - **TC03 (Validation Lỗi Đầu vào):** Gửi payload thiếu thông tin, sai định dạng email hoặc ngày quá khứ $\rightarrow$ Trả về mã 400 Bad Request kèm chi tiết lỗi RFC 7807 (Problem Details).
     - **TC04 (Phòng Đã Đặt):** Cố gắng đặt phòng có trạng thái khác `AVAILABLE` $\rightarrow$ Trả về mã 409 Conflict hoặc 400.
     - **TC05 (Compensating Rollback):** Giả lập lỗi ở bước ghi booking hoặc SNS $\rightarrow$ Giao dịch bồi hoàn tự động gọi `room-service` mở khóa lại phòng về trạng thái `AVAILABLE`.
     - **TC06 (Dead Letter Queue):** Gửi payload sai cấu trúc JSON vào SQS $\rightarrow$ Consumer thử lại 3 lần thất bại $\rightarrow$ Đẩy vào DLQ và kích hoạt Alarm.
     - **TC07 (High Load & ECS Auto Scaling):** Thực thi script bắn tải 500 requests liên tục $\rightarrow$ Tỷ lệ thành công 100%, ghi nhận CPU tăng và số Task tự động scale từ 1 lên 2 tasks.
     - **TC08 (Distributed Tracing):** Truy vết cùng một mã `X-Correlation-Id` qua toàn bộ chuỗi log từ `booking-service` đến `room-service` và `notification-service` trên CloudWatch Logs Insights.

2. **Biên tập & Sản xuất Video Demo Nghiệm Thu Đồ Án ($\le 10$ Phút - 3.0 giờ):**
   - Xây dựng kịch bản video (Storyline) chi tiết từng phút, đảm bảo tuân thủ nghiêm ngặt quy định nghiệm thu: **Thời lượng không vượt quá 10 phút**.
   - Phân chia bố cục video logic, mạch lạc:
     - **00:00 - 01:30 (1.5 phút):** Giới thiệu nhóm Capstone, đề tài, bài toán thực tế và Sơ đồ kiến trúc tổng thể trên AWS.
     - **01:30 - 04:30 (3.0 phút):** Demo luồng nghiệp vụ chuẩn (Happy Path) từ giao diện Postman qua ALB, kiểm tra dữ liệu trong PostgreSQL RDS, DynamoDB và log xử lý email trong SQS.
     - **04:30 - 06:30 (2.0 phút):** Demo tính năng chịu lỗi nâng cao: Giao dịch bồi hoàn (Compensating Rollback) chống treo phòng và SQS Poison Message rơi vào Dead Letter Queue.
     - **06:30 - 08:30 (2.0 phút):** Demo hệ thống Giám sát: Truy vết Correlation ID trên CloudWatch Logs Insights, Dashboard tập trung và chạy tải quan sát ECS Auto Scaling.
     - **08:30 - 09:30 (1.0 phút):** Demo cơ chế tự phục hồi Task Fargate (Self-healing) và thao tác dọn dẹp tài nguyên.
     - **09:30 - 10:00 (0.5 phút):** Báo cáo tổng kết chi phí Learner Lab, kết luận và lời cảm ơn.
   - Thu âm giọng đọc thuyết minh rõ ràng, chèn phụ đề tóm tắt các điểm nhấn công nghệ, xuất video ở độ phân giải Full HD 1080p.
   - Upload video lên YouTube dưới chế độ Unlisted (hoặc Google Drive mở quyền xem), kiểm tra link truy cập công khai.

3. **Soạn Thảo Báo Cáo Tổng Kết Đồ Án (Final Project Report - 2.0 giờ):**
   - Tổng hợp toàn bộ tài liệu từ Tuần 1 đến Tuần 4 thành một Báo cáo Tổng kết Đồ án hoàn chỉnh, chuẩn chỉnh văn phong học thuật và kỹ thuật.
   - Cấu trúc báo cáo bám sát yêu cầu đề cương:
     - Chương 1: Đặt vấn đề, mục tiêu và phạm vi đề tài.
     - Chương 2: Kiến trúc hệ thống microservices và thiết kế hạ tầng trên AWS ECS Fargate.
     - Chương 3: Hiện thực các dịch vụ cốt lõi, bảo mật SSM, và xử lý giao dịch phân tán.
     - Chương 4: Giám sát tập trung CloudWatch, Cảnh báo và Auto Scaling.
     - Chương 5: Đánh giá kiểm thử toàn diện, ma trận kết quả và phân tích chi phí vận hành.
     - Chương 6: Kết luận, hạn chế và hướng phát triển tương lai.
   - Định dạng toàn bộ báo cáo bằng Markdown để **dán trực tiếp vào Form Báo cáo Online trên LMS** (theo đúng lưu ý của Thầy Phụng: không để thông tin quan trọng trong file `.docx` đính kèm).

4. **Thiết Kế Slide Báo Cáo & Xây Dựng Ngân Hàng Câu Hỏi Vấn Đáp (2.0 giờ):**
   - Thiết kế bộ Slide thuyết trình nghiệm thu súc tích, trực quan (15–20 slides), tập trung vào kiến trúc hệ thống, các quyết định kỹ thuật quan trọng và bài học rút ra.
   - Soạn thảo bộ câu hỏi phản biện dự kiến và câu trả lời chi tiết cho buổi vấn đáp với GVHD (ví dụ: So sánh Fargate vs EC2 Launch Type; Tại sao dùng SQS/SNS thay vì Kafka trong phạm vi đồ án; Cơ chế xử lý idempotency khi mạng chập chờn; Cách thức kiểm soát chi phí Learner Lab).

---

## 📅 LỊCH TRÌNH THỰC HIỆN CHI TIẾT THEO NGÀY (TIMELINE & MILESTONES)

```mermaid
gantt
    title KẾ HOẠCH TRIỂN KHAI TUẦN 4 - NƯỚC RÚT & NGHIỆM THU
    dateFormat  YYYY-MM-DD
    section Phúc (DevOps & Cost)
    Resilience & Chaos Testing         :2026-10-28, 2d
    Cost Analysis & Optimization       :2026-10-29, 2d
    Final Architecture & Teardown Script:2026-10-30, 2d
    Phối hợp Demo & Vấn đáp           :2026-11-01, 2d
    section Linh (Testing & Delivery)
    Ma trận Kiểm thử E2E (8 TCs)       :2026-10-28, 2d
    Quay & Biên tập Video Demo (<=10m) :2026-10-30, 2d
    Báo cáo Tổng kết (Form & Repo)     :2026-10-31, 2d
    Slide Thuyết trình & Vấn đáp       :2026-11-01, 2d
```

| Ngày | Công việc chính của Cao Hoàng Phúc | Công việc chính của Phan Thị Thùy Linh | Sản phẩm bàn giao trong ngày |
|:---:|---|---|---|
| **28/10 (Thứ 4)** | Họp chốt kế hoạch tuần 4; Rà soát cluster ECS và cấu hình IAM LabRole; Dựng kịch bản Chaos Test. | Họp chốt kế hoạch tuần 4; Xây dựng Ma trận 8 test cases E2E; Chuẩn bị môi trường Postman / curl script. | File `docs/week-4/tasks.md` hoàn chỉnh; Bộ test cases sẵn sàng. |
| **29/10 (Thứ 5)** | Thực hiện Chaos Testing (kill task Fargate, ngắt RDS test 503); Thu thập metrics hồi phục trên CloudWatch. | Chạy toàn bộ 8 test cases E2E; Thu thập log phân tán qua Correlation ID trên CloudWatch Logs Insights. | Ảnh chụp minh chứng Self-healing, Rollback và DLQ retry. |
| **30/10 (Thứ 6)** | Trích xuất báo cáo Billing / Cost Explorer; Lập bảng phân tích chi phí và giải pháp tối ưu; Viết script teardown. | Viết kịch bản chi tiết cho Video Demo ($\le 10$ phút); Bắt đầu quay thô các phân đoạn Postman và Terminal. | File `scripts/teardown-environment.ps1`; Bản thảo kịch bản video demo. |
| **31/10 (Thứ 7)** | Hỗ trợ quay phân đoạn hạ tầng, CloudWatch Dashboard & Auto Scaling; Kiểm thử kịch bản teardown trên môi trường lab. | Biên tập, lồng tiếng và chèn phụ đề Video Demo; Render Full HD và upload YouTube Unlisted. | Video Demo hoàn chỉnh ($\le 10$ phút) kèm link công khai. |
| **01/11 (Chủ Nhật)**| Vẽ hoàn thiện Sơ đồ Kiến trúc Tổng thể cuối kỳ; Luyện tập các câu hỏi vấn đáp hạ tầng và bảo mật. | Soạn thảo Báo cáo Tổng kết Đồ án đầy đủ; Thiết kế bộ Slide thuyết trình bảo vệ đồ án. | Báo cáo Tổng kết Markdown; Slide thuyết trình; Bộ Q&A. |
| **02/11 (Thứ 2)** | Thực thi teardown dọn dẹp toàn bộ tài nguyên trên AWS Learner Lab; Chốt số dư Credits cuối cùng. | Đưa toàn bộ nội dung Báo cáo Tổng kết vào Form Online trên LMS; Push toàn bộ code và tài liệu lên nhánh `week-4` và `main`. | Form LMS đã nộp; Repo GitHub cập nhật 100%; Tài khoản AWS về $0/giờ. |

---

## 💰 KẾ HOẠCH THEO DÕI & TỔNG KẾT CHI PHÍ (AWS LEARNER LAB BUDGET - $50.00)

Theo dõi số dư ngân sách thực tế qua các mốc thời gian để đảm bảo hoàn thành đồ án an toàn trong hạn mức $50.00 USD:

| Giai đoạn | Ngày ghi nhận | Số dư Credits dự kiến | Chi phí tích lũy | Trạng thái tài nguyên ngoài giờ | Ghi chú vận hành |
|:---:|:---:|:---:|:---:|:---:|---|
| **Chốt Tuần 3** | 25/10/2026 | **$39.80** | **$10.20** | ECS tasks = 0, RDS `Stopped` | Đã nghiệm thu Tuần 3 (Đạt) |
| **Giữa Tuần 4** | 30/10/2026 | $37.50 | $12.50 | Chạy kiểm thử E2E, Chaos & quay demo | Bật lại hệ thống trong thời gian ngắn để quay video |
| **Chốt Nghiệm thu**| 02/11/2026 | **$\ge \$35.00$** | **$\le \$15.00$** | **ĐÃ DỌN DẸP 100% (TEARDOWN)** | Chạy `teardown-environment.ps1`, giải phóng toàn bộ tài nguyên |

---

## 🎬 KỊCH BẢN CHI TIẾT VIDEO DEMO NGHIỆM THU (THỜI LƯỢNG $\le$ 10 PHÚT)

| Phân đoạn | Thời lượng | Nội dung trình bày & Thao tác kỹ thuật | Người phụ trách thể hiện |
|:---:|:---:|---|:---:|
| **Phần 1: Giới thiệu** | 00:00 - 01:30 | - Giới thiệu nhóm Capstone, thành viên (Phúc & Linh) và đề tài.<br>- Trình chiếu Sơ đồ Kiến trúc Tổng thể: Mô hình Microservices trên ECS Fargate, ALB, RDS, DynamoDB, SNS/SQS, SSM và CloudWatch. | Linh |
| **Phần 2: Luồng Nghiệp Vụ Chuẩn (Happy Path)** | 01:30 - 04:30 | - Gửi request `GET /api/rooms` qua ALB để tra cứu phòng trống.<br>- Gửi request `POST /api/bookings` tạo đơn đặt phòng thành công.<br>- Minh chứng kiểm tra: Trạng thái phòng đổi sang `RESERVED`, bản ghi trong RDS `booking_db`, bản ghi trong DynamoDB `booking-audit-log`, và log xác nhận tiêu thụ tin nhắn trong SQS tại `notification-service`. | Linh |
| **Phần 3: Xử Lý Lỗi & Chịu Tải Nghiệp Vụ** | 04:30 - 06:30 | - Demo **Compensating Rollback**: Cố tình gây lỗi lưu trữ, chứng minh phòng tự động hoàn về `AVAILABLE` (chống deadlock phòng).<br>- Demo **Bean Validation & RFC 7807**: Nhập email sai định dạng, trả về chuẩn lỗi bảo mật.<br>- Demo **SQS DLQ**: Tin nhắn độc hại retry 3 lần rồi rơi vào DLQ, kích hoạt CloudWatch Alarm. | Linh |
| **Phần 4: Giám Sát, Tracing & Auto Scaling** | 06:30 - 08:30 | - Trình diễn **CloudWatch Logs Insights**: Truy vết toàn bộ luồng request qua duy nhất 1 mã `X-Correlation-Id`.<br>- Trình chiếu **CloudWatch Dashboard**: Các biểu đồ CPU, RAM, ALB Request Count, Healthy Host.<br>- Chạy script sinh tải (`scripts/load-test.ps1`), quan sát ECS Service Auto Scaling tự động tăng từ 1 task lên 2 tasks. | Phúc |
| **Phần 5: Chịu Lỗi Hạ Tầng & Dọn Dẹp Tài Nguyên** | 08:30 - 09:30 | - Demo **Self-healing ECS Fargate**: Cưỡng bức kill 1 task đang chạy, ECS tự động spawn task mới thay thế trong vài giây, ALB tự định tuyến lại.<br>- Trình chiếu kịch bản dọn dẹp tài nguyên tự động `scripts/teardown-environment.ps1`. | Phúc |
| **Phần 6: Tổng Kết** | 09:30 - 10:00 | - Tổng kết chi phí thực tế trên AWS Learner Lab (sử dụng ~\$12-14 / \$50).<br>- Tóm tắt kết quả đạt được, bài học kinh nghiệm và lời cảm ơn GVHD. | Phúc & Linh |

---

## 🤖 KHAI BÁO SỬ DỤNG AI (MINH BẠCH & ĐÚNG QUY ĐỊNH GVHD)

Tuân thủ nghiêm ngặt **Lưu ý 1** của Thầy Huỳnh Xuân Phụng:
- **Các công cụ AI đã tham khảo:** Antigravity IDE, Claude 3.5 Sonnet, ChatGPT-4o.
- **Phạm vi hỗ trợ cụ thể của AI:**
  1. Hỗ trợ xây dựng khung dàn ý cho kế hoạch Tuần 4 và bố cục Báo cáo Tổng kết Đồ án.
  2. Rà soát cú pháp câu lệnh PowerShell trong script dọn dẹp tài nguyên (`scripts/teardown-environment.ps1`).
  3. Chuẩn hóa định dạng Markdown và bảng biểu ma trận kiểm thử.
- **Cam kết của sinh viên:**
  - Toàn bộ các tài nguyên đám mây đều được triển khai, cấu hình và kiểm thử thực tế 100% trên môi trường AWS Academy Learner Lab.
  - Toàn bộ mã nguồn 3 microservices Java Spring Boot, các kịch bản kiểm thử tải, dữ liệu đo đạc và nội dung phân tích chi tiết trong báo cáo đều do nhóm tự tay thực hiện.
  - Cả hai thành viên nắm rõ từng thành phần kiến trúc và tự tin giải trình mọi quyết định kỹ thuật khi vấn đáp với GVHD.

---

## 📋 DANH MỤC MINH CHỨNG & SẢN PHẨM NGHIỆM THU TUẦN 4 (CHECKLIST)

### 1. Sản phẩm Nghiệm thu Trọng tâm:
- [ ] **Sản phẩm 1:** Video Demo nghiệm thu thời lượng $\le 10$ phút (Upload YouTube Unlisted / Google Drive, âm thanh thuyết minh rõ ràng).
- [ ] **Sản phẩm 2:** Báo cáo Tổng kết Đồ án định dạng Markdown, điền trực tiếp vào Form Báo cáo Online trên LMS và lưu trong repo `docs/week-4/final-report.md`.
- [ ] **Sản phẩm 3:** Slide Thuyết trình Báo cáo Đồ án (PDF / PPTX) tóm lược toàn bộ dự án.
- [ ] **Sản phẩm 4:** Kho mã nguồn GitHub hoàn chỉnh trên nhánh `week-4` và merge vào `main`.
- [ ] **Sản phẩm 5:** Kịch bản dọn dẹp tài nguyên `scripts/teardown-environment.ps1` và xác nhận số dư Learner Lab an toàn.

### 2. Minh chứng Kỹ thuật & Ảnh chụp Thực tế:
- [ ] **Ảnh 1:** Sơ đồ Kiến trúc Tổng thể hoàn chỉnh (Full Architecture Diagram) với VPC, ALB, ECS Fargate, RDS, DynamoDB, SNS/SQS, SSM, CloudWatch.
- [ ] **Ảnh 2:** Bảng Ma trận Kiểm thử E2E (8 test cases) kèm kết quả thực thi và HTTP status codes.
- [ ] **Ảnh 3:** Minh chứng Self-healing của ECS Fargate: Khi dừng task, task mới tự động khởi tạo để duy trì `desiredCount`.
- [ ] **Ảnh 4:** Minh chứng ALB Target Group tự động chuyển đổi giữa `Unhealthy` và `Healthy` trong kịch bản chịu lỗi.
- [ ] **Ảnh 5:** Minh chứng ECS Auto Scaling co giãn từ 1 lên 2 tasks dưới áp lực tải 500 requests liên tục.
- [ ] **Ảnh 6:** Minh chứng Distributed Tracing trên CloudWatch Logs Insights với 1 mã `X-Correlation-Id` xuất hiện xuyên suốt 3 services.
- [ ] **Ảnh 7:** Báo cáo AWS Cost Explorer / Billing Dashboard hiển thị tổng chi phí tích lũy $\le \$15.00$ / \$50.00.
- [ ] **Ảnh 8:** Minh chứng thực thi script dọn dẹp `teardown-environment.ps1`, toàn bộ task/service được xóa hoặc đưa về 0, không còn tài nguyên chạy ngầm.
