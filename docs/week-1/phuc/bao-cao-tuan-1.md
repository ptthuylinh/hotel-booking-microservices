# Báo cáo tuần 1 — Cao Hoàng Phúc

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS  
**Sinh viên:** Cao Hoàng Phúc — MSSV `24110303`  
**Môi trường:** AWS Academy Learner Lab, `us-east-1`  
**Ngày thực hiện:** 09/10/2026

Em đã dựng phần mạng ban đầu cho hệ thống trên AWS Learner Lab. Ảnh chụp Console ghi lại thời gian, Region và Account ID của buổi thực hiện.

![Thời gian, Region và Account ID](images/09-console-context.png)

## Công việc đã làm

1. **Tạo VPC** `hotel-booking-vpc` với CIDR `10.0.0.0/16`. Em chia VPC thành **2 public subnet và 2 private subnet** trên `us-east-1a` và `us-east-1b`, bật DNS và gắn tag `Project=hotel-booking-microservices`, `Owner=phuc-linh`.

   ![VPC và bốn subnet trên hai AZ](images/03-resource-map.png)

   ![Tag của VPC](images/04-vpc-tags.png)

2. **Cấu hình Internet Gateway và route table.** Hai public subnet dùng route `0.0.0.0/0` tới Internet Gateway; các private subnet dùng route table riêng. Em chưa tạo NAT Gateway trong tuần dựng nền mạng.

   ![Route table của public subnet](images/05-public-route.png)

3. **Tạo ba security group** cho ALB, ECS và RDS. ALB SG mở HTTP port `80` cho người dùng. ECS SG nhận port `8081` và `8082` từ ALB SG. RDS SG chưa mở inbound; em sẽ thêm port database từ ECS SG khi triển khai RDS.

   ![Inbound rule của ALB SG](images/06-alb-ingress.png)

   ![Cấu hình ECS SG](images/07-ecs-sg-draft.png)

   ![Cấu hình RDS SG](images/08-rds-sg-draft.png)

**Kết quả:** VPC, subnet, Internet Gateway, route table và security group đã sẵn sàng làm nền cho ALB, ECS Fargate và RDS ở các tuần tiếp theo.

**Sử dụng AI:** Em dùng AI để tìm hiểu VPC, CIDR, subnet, NAT và hỗ trợ biên tập báo cáo; em tự thực hiện cấu hình trên AWS.
