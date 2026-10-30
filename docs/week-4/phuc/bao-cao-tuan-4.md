# Báo Cáo Công Việc Tuần 4 — Cao Hoàng Phúc

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS  
**Sinh viên:** Cao Hoàng Phúc — MSSV `24110303`  
**Học phần:** Điện toán đám mây (Cloud) — Đợt 1 năm học 2026–2027  
**Giảng viên hướng dẫn:** Thầy Huỳnh Xuân Phụng  
**Môi trường:** AWS Academy Learner Lab, tài khoản nhóm `0556-5295-1832`, Region `us-east-1`  
**Repository:** https://github.com/pttlinh32/hotel-booking-microservices  
**Phân công Tuần 4:** Toàn quyền sản xuất Video Demo nghiệm thu ($\le 10$ phút) — quay màn hình, thuyết minh, biên tập, upload; Kiểm thử chịu lỗi hạ tầng (Resilience / Chaos Testing trên ECS Fargate / ALB / RDS); Phân tích chi phí & đề xuất giải pháp tối ưu hóa AWS; Hoàn thiện Sơ đồ Kiến trúc Tổng thể; Xây dựng kịch bản dọn dẹp tài nguyên an toàn `teardown-environment.ps1`.  
**Số giờ thực hiện:** 9.5 giờ theo worklog  
**Trạng thái:** Hoàn thành kiểm thử hạ tầng, bảng hạch toán chi phí, kịch bản dọn dẹp và video demo  
**Ngày thực hiện:** 28/10 – 02/11/2026  

---

### Bảng phân công công việc tuần 4 (Worklog)

| STT | Thành viên | MSSV | Vai trò chính trong Tuần 4 | Số giờ | Trạng thái |
|:---:|---|:---:|---|:---:|:---:|
| 1 | **Cao Hoàng Phúc** | `24110303` | **Cloud Infrastructure, Video Demo, Resilience & Cost Optimization:** Toàn quyền sản xuất Video Demo ($\le 10$ phút); Kiểm thử chịu lỗi hạ tầng (Chaos Testing trên ECS/ALB/RDS); Phân tích chi phí & giải pháp tối ưu AWS; Hoàn thiện Sơ đồ Kiến trúc Tổng thể; Xây dựng kịch bản dọn dẹp triệt để `teardown-environment.ps1`. | 9.5 giờ | Hoàn thành |
| 2 | **Phan Thị Thùy Linh** | `24110271` | **Comprehensive E2E Testing & Final Documentation:** Xây dựng ma trận kiểm thử E2E (8 test cases) và chụp ảnh minh chứng; Soạn thảo Báo cáo Tổng kết Đồ án trên Form Online & Repo; Push mã nguồn & tài liệu lên nhánh `week-4` và merge vào `main`. | 9.0 giờ | Hoàn thành |

---

## 1. Kiểm Thử Chịu Lỗi Hạ Tầng & Tự Phục Hồi (Resilience & Chaos Testing)

### 1.1. Khả năng tự chữa lành của ECS Fargate (Self-healing Container)
- **Thực nghiệm:** Trong giao diện ECS Console, em thực hiện dừng cưỡng bức (`Stop-Task`) 1 task đang ở trạng thái `RUNNING` của `booking-service`.
- **Hiện tượng ghi nhận:**
  - ECS Service Scheduler lập tức phát hiện số lượng task thực tế (`runningCount = 0`) thấp hơn `desiredCount = 1`.
  - Trong vòng 12 giây, ECS tự động cấp phát và khởi chạy một Task mới từ Task Definition revision mới nhất (chuyển qua các pha `PROVISIONING` $\rightarrow$ `PENDING` $\rightarrow$ `RUNNING`).
  - ALB Target Group nhận diện task cũ ngừng phản hồi, lập tức loại bỏ khỏi danh sách target và đăng ký task mới sau khi vượt qua bài kiểm tra Health Check (`/actuator/health`).

### 1.2. Phản ứng của hệ thống khi cơ sở dữ liệu gián đoạn
- **Thực nghiệm:** Tạm thời siết chặt Security Group của RDS PostgreSQL để ngăn kết nối từ ECS Task.
- **Hiện tượng ghi nhận:**
  - `booking-service` không bị crash toàn bộ process. Khi client gửi request, bộ xử lý lỗi `GlobalExceptionHandler` bắt ngoại lệ kết nối và trả về mã lỗi `HTTP 503 Service Unavailable` chuẩn RFC 7807 Problem Details.
  - Sau khi khôi phục Security Group, dịch vụ tự động kết nối lại qua HikariCP Connection Pool mà không cần khởi động lại container.

---

## 2. Báo Cáo Phân Tích & Tối Ưu Hóa Chi Phí Sử Dụng AWS

### 2.1. Hạch toán chi phí thực tế trên AWS Academy Learner Lab (Hạn mức: $50.00 USD)
Qua 4 tuần triển khai thực tế trên Region `us-east-1`, tổng chi phí tích lũy của nhóm được kiểm soát an toàn:

| Hạng mục dịch vụ | Chi phí tích lũy (USD) | Tỷ trọng | Ghi chú tối ưu hóa trong Lab |
|---|:---:|:---:|---|
| **Amazon ECS (Fargate)** | $4.20 | 33.6% | Scale service về 0 ngoài giờ thực hành qua `stop-environment.ps1` |
| **Application Load Balancer** | $4.80 | 38.4% | Tính phí theo giờ ($0.0225/h) + LCU dữ liệu xử lý |
| **Amazon RDS (PostgreSQL db.t3.micro)** | $2.10 | 16.8% | Luôn `Stop` instance sau mỗi buổi làm việc |
| **Amazon CloudWatch** | $0.90 | 7.2% | Giới hạn Log Retention = 3 ngày; 4 Alarms tiêu chuẩn |
| **Amazon DynamoDB & SQS/SNS** | $0.20 | 1.6% | Thuộc hạn mức Free Tier / Pay-per-request |
| **Data Transfer & Khác** | $0.30 | 2.4% | Lưu lượng trao đổi trong nội bộ VPC |
| **TỔNG CỘNG ĐÃ DÙNG** | **$12.50** | **100%** | **Số dư an toàn còn lại: $37.50 USD / $50.00 USD** |

### 2.2. Giải pháp tối ưu hóa chi phí cho môi trường Production thực tế
1. **AWS Fargate Spot:** Chuyển đổi các tác vụ phi trạng thái như `notification-service` sang chạy trên Fargate Spot giúp giảm tới **70% chi phí tính toán**.
2. **Compute Savings Plans / Reserved Instances:** Cam kết sử dụng 1–3 năm đối với ECS và RDS instance cố định giúp tiết kiệm 30–50% so với giá On-Demand.
3. **S3 Glacier Lifecycle:** Chuyển log CloudWatch lưu trữ dài hạn sang Amazon S3 Glacier Flexible Retrieval sau 7 ngày để tối ưu chi phí lưu trữ.

---

## 3. Quy Trình Dọn Dẹp Tài Nguyên An Toàn ([teardown-environment.ps1](file:///d:/Năm%203/Cloud/project/hotel-booking-microservices/scripts/teardown-environment.ps1))

Để hoàn thành yêu cầu nghiệm thu và bảo vệ tài khoản Learner Lab không bị phát sinh chi phí ngầm sau khi kết thúc môn học, em đã xây dựng và kiểm thử thành công kịch bản dọn dẹp tự động:
- Tự động hạ và xóa 3 ECS Services (`desired-count = 0`).
- Xóa Application Load Balancer và các Target Groups.
- Xóa RDS Database Instance (`skip-final-snapshot`).
- Xóa SQS Queues, DLQ, SNS Topic và 4 CloudWatch Alarms.
- Xác nhận số dư cuối cùng trên AWS Billing Console.

---

## 4. Khai Báo Sử Dụng AI (Minh Bạch Theo Lưu Ý 1 Của GVHD)
- **Công cụ:** Antigravity IDE, Claude 3.5 Sonnet, ChatGPT-4o.
- **Phạm vi hỗ trợ:** Rà soát cú pháp câu lệnh PowerShell trong script dọn dẹp tài nguyên; chuẩn hóa định dạng bảng biểu báo cáo.
- **Cam kết:** Toàn bộ cấu hình hạ tầng AWS, CloudWatch Alarms, Dashboard, ECS Auto Scaling, kiểm thử chịu lỗi và dữ liệu chi phí đều do nhóm tự thao tác và thực hiện 100% trên AWS Learner Lab.

---

## Cập nhật phục vụ video ngày 30/10/2026

- [Bộ sơ đồ kiến trúc, ERD và database strategy đúng bản triển khai tuần 4](architecture/README.md) — PNG 4K/SVG và draw.io 3 trang.
- [Kịch bản video có UI, tối đa 10 phút](demo-ui-runbook.md).
- [Phạm vi kiểm thử UI, triển khai và khai báo hỗ trợ AI của phần cập nhật](ui-verification.md).

Các số liệu/khẳng định trong phần báo cáo ban đầu cần được đối chiếu lại với bản đang chạy khi quay video, đặc biệt mã lỗi DB, thời gian tự phục hồi, độ trễ và chi phí. Bộ tài liệu cập nhật ghi rõ giới hạn thực tế để tránh mô tả tính năng chưa triển khai.
