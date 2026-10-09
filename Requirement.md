# Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS (Nhóm: Capstone)

- **Trạng thái:** Đang đăng ký
- **Học kỳ:** Cloud - Đợt 1 - 2026-2027 · Môn học
- **Giảng viên hướng dẫn (GVHD):** Huỳnh Xuân Phụng

---

## 1. Mô tả đề tài
Thiết kế và triển khai hệ thống đặt phòng gồm nhiều microservice độc lập, giao tiếp đồng bộ (REST) và bất đồng bộ (SQS/SNS).

---

## 2. Sản phẩm dự kiến
- $\ge$ 3 microservice (`room`, `booking`, `notification`) chạy ECS Fargate.
- ALB path-based routing.
- RDS + DynamoDB.
- SNS/SQS.
- Log tập trung CloudWatch.
- Sơ đồ kiến trúc.

---

## 3. Yêu cầu sinh viên (Yêu cầu SV)

### Yêu cầu riêng
- **Dịch vụ:** ECS Fargate, ECR, ELB, RDS, DynamoDB, SNS, SQS, CloudWatch.
- Scale service về 0 khi không dùng.

### Kế hoạch 4 tuần (mỗi SV $\ge$ 8 giờ/tuần)
- **Tuần 1:** Tìm hiểu dịch vụ, thiết kế kiến trúc, vẽ sơ đồ, dựng nền tảng (VPC/IAM LabRole/S3...), gắn tag.
- **Tuần 2:** Triển khai các chức năng lõi trên AWS, kiểm thử từng thành phần.
- **Tuần 3:** Tích hợp, bảo mật, giám sát (CloudWatch), tự động hóa/IaC nếu có.
- **Tuần 4:** Kiểm thử tổng thể, tối ưu chi phí, dọn dẹp tài nguyên, viết báo cáo và demo.

### Yêu cầu chung
- **Quy mô nhóm & Thời gian:** Nhóm tối đa 2 SV; hoàn thành trong 4 tuần; nộp nhật ký công việc (worklog) hằng tuần ghi rõ phân công và số giờ của từng SV.
- **Sử dụng AI:** Được dùng LLM/AI (ChatGPT, Claude, Amazon Q Developer...) để tham khảo, sinh mã, gỡ lỗi; nhưng mọi tài nguyên phải được triển khai và chạy thật trên AWS Learner Lab. Ghi rõ phần nào có AI hỗ trợ; SV phải giải thích được mọi cấu hình/mã nguồn khi vấn đáp.
- **Giới hạn tài nguyên AWS:**
  - Chỉ dùng Region `us-east-1` / `us-west-2`.
  - Dùng `LabRole` / `LabInstanceProfile` (không tạo IAM user/role).
  - EC2: chỉ loại `nano` $\rightarrow$ `large`, $\le$ 9 instance và $\le$ 32 vCPU chạy đồng thời mỗi Region.
  - EBS $\le$ 100 GB (`gp2`/`gp3`).
  - Gắn tag `Project`/`Owner` cho tài nguyên.
  - Dừng/xóa tài nguyên sau mỗi buổi; báo cáo chi phí sử dụng cuối kỳ.
- **Minh chứng nghiệm thu:** Ảnh chụp console/CLI (có Account ID, Region, thời gian), mã nguồn/template trên Git, báo cáo + sơ đồ kiến trúc, video demo $\le$ 10 phút.
