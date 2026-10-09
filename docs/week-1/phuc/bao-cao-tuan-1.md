# Báo cáo công việc tuần 1 — Cao Hoàng Phúc

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS  
**Sinh viên:** Cao Hoàng Phúc — MSSV `24110303`  
**Học phần:** Điện toán đám mây, đợt 1 năm học 2026–2027  
**Môi trường:** AWS Academy Learner Lab, Region `us-east-1`  
**Nguồn phân công:** [`docs/week-1/tasks.md`](https://github.com/pttlinh32/hotel-booking-microservices/blob/main/docs/week-1/tasks.md) và [`docs/week-1/notes.md`](https://github.com/pttlinh32/hotel-booking-microservices/blob/main/docs/week-1/notes.md) trong repository nhóm.

> **Phạm vi minh chứng:** Báo cáo dựa trên các ảnh AWS Console chụp tối 09/10/2026 và tài liệu nhóm. Ảnh được cắt đúng vùng thông tin cần dùng, không chỉnh sửa giá trị cấu hình. Với ECS SG và RDS SG, em xác nhận đã bấm **Create** sau khi chụp ảnh. Ảnh đính kèm ghi lại cấu hình trước khi lưu; báo cáo phân biệt rõ xác nhận này với bằng chứng trực tiếp từ trang chi tiết tài nguyên.

## 1. Mục tiêu và phân công

Theo `tasks.md`, em phụ trách thiết kế kiến trúc tổng thể và phần mạng: VPC, subnet, Internet Gateway, route table, security group; đồng thời nghiên cứu ECS Fargate, ALB path-based routing, CloudWatch và gắn tag tài nguyên. Kế hoạch tuần 1 ghi **9,0 giờ** cho thành viên 1. Đây là số giờ **theo kế hoạch**, chưa có bảng chấm giờ thực tế đầy đủ để xác nhận tổng giờ đã làm.

Mục tiêu của buổi cấu hình được ghi lại trong báo cáo là tạo nền mạng cho ba service `room`, `booking`, `notification`: ALB nhận yêu cầu từ Internet, các service và cơ sở dữ liệu chỉ nhận kết nối cần thiết qua VPC.

## 2. Nhật ký thực hiện và cách em ra quyết định

| Mốc theo ảnh chụp | Việc thực hiện | Lý do và kết quả quan sát |
|---|---|---|
| 23:37–23:38 | Chọn 2 Availability Zone, 2 public subnet, 2 private subnet; xem trước mạng trước khi tạo. | ALB cần subnet ở hai AZ; em giữ mỗi AZ một public và một private subnet. Các CIDR `/20` do console đề xuất nằm trong VPC `10.0.0.0/16` và không chồng lấn. |
| 23:38 | Để NAT Gateway và VPC endpoint ở `None`, bật DNS, nhập tag `Project`/`Owner`. | Tuần 1 mới dựng nền mạng; không tạo NAT tính phí khi chưa chạy ECS. Em ghi lại rằng ECS trong private subnet sẽ cần đường ra phù hợp ở giai đoạn triển khai. |
| 23:40–23:45 | Kiểm tra VPC đã tạo, Resource map, tag và route table public. | Em đối chiếu tài nguyên thật với bản preview, xác nhận 4 subnet và Internet Gateway. Route public có `0.0.0.0/0 → Internet Gateway`, hai public subnet dùng chung route table này. |
| 23:45 | Tạo và kiểm tra security group cho ALB. | Chỉ mở HTTP port `80` từ `0.0.0.0/0` cho đường vào demo. ECS và RDS sẽ không dùng rule public này. |
| 23:49–23:51 | Nhập rule ECS SG và cấu hình RDS SG, sau đó bấm **Create** (theo xác nhận của em). | ECS nhận port `8081`/`8082` từ ALB SG; RDS chưa mở inbound vì nhóm chưa chọn PostgreSQL hay MySQL. Cần ảnh trang chi tiết để xác nhận ID và trạng thái sau tạo. |

**Dấu thời gian, Account ID và Region của ảnh gốc:** thanh trên của AWS Console cho thấy Account ID `055652951832`, `United States (N. Virginia)` tức `us-east-1`, và thời gian chụp. Ảnh cắt dưới đây giữ phần nhận diện này và che địa chỉ email tài khoản; các ảnh cấu hình tiếp theo được đối chiếu từ cùng loạt ảnh gốc.

![Bối cảnh AWS Console: thời gian, Region, Account ID](images/09-console-context.png)

## 3. Thiết kế mạng đã chọn

```text
Region us-east-1 — VPC 10.0.0.0/16
├── AZ us-east-1a
│   ├── Public subnet:  10.0.0.0/20   → route public → Internet Gateway
│   └── Private subnet: 10.0.128.0/20 → route private (chưa có NAT)
└── AZ us-east-1b
    ├── Public subnet:  10.0.16.0/20  → route public → Internet Gateway
    └── Private subnet: 10.0.144.0/20 → route private (chưa có NAT)
```

Em dùng CIDR `/16` cho VPC để có dải địa chỉ chung, rồi chia thành bốn subnet `/20`. Public subnet là vị trí dự kiến của ALB; private subnet là vị trí dự kiến của ECS Fargate và RDS. Việc public hay private phụ thuộc vào route table: public có route tới Internet Gateway, private không có route trực tiếp đó.

![Cấu hình 2 AZ, 4 subnet và các CIDR trước khi tạo](images/01-subnet-plan.png)

Sau khi tạo, VPC `hotel-booking-vpc` có ID `vpc-025a0fd949a26f610`, CIDR `10.0.0.0/16`, trạng thái `Available`; DNS resolution và DNS hostnames được bật. Resource map cho thấy 4 subnet, 4 route table (gồm **1 main route table mặc định**) và 1 Internet Gateway.

![Chi tiết VPC đã tạo](images/02-vpc-details.png)

![Resource map: subnet, route table và Internet Gateway](images/03-resource-map.png)

Em kiểm tra tag của VPC: `Project=hotel-booking-microservices` và `Owner=phuc-linh`. Ảnh dưới đây xác nhận tag trên **VPC**; cần kiểm tra riêng tag của từng subnet, route table, Internet Gateway và security group khi hoàn thiện minh chứng.

![Tag của VPC](images/04-vpc-tags.png)

## 4. Kiểm tra định tuyến và security group

Route table public `hotel-booking-rtb-public` có hai route đang hoạt động: `10.0.0.0/16 → local` cho giao tiếp nội bộ VPC và `0.0.0.0/0 → igw-0507312179d4dbcca` cho lưu lượng ra Internet. Màn hình cũng cho thấy route table này liên kết với **2 subnet**. Em đã xem danh sách hai private route table; ảnh hiện có chưa chụp trực tiếp tab **Routes** của chúng, nên chưa ghi là đã xác minh từng route private bằng ảnh.

![Route table public và hai route đang hoạt động](images/05-public-route.png)

Security group `hotel-booking-alb-sg` (`sg-08119fcb3bd5f4f1d`) đã xuất hiện trong danh sách security group. Tab inbound của nó có **1 rule HTTP/TCP port 80, source `0.0.0.0/0`**. Em chọn phạm vi này vì ALB là điểm nhận yêu cầu từ người dùng. Port 443 sẽ chỉ được bổ sung khi có listener HTTPS và chứng chỉ phù hợp.

![Inbound rule của ALB security group đã tạo](images/06-alb-ingress.png)

Em tạo `hotel-booking-ecs-sg`; ảnh trước khi bấm Create cho thấy hai rule: TCP `8081` và `8082`, cùng source là ALB security group. Dự kiến `booking-service` gọi `room-service` nội bộ, nên SG cần thêm rule TCP `8081` tự tham chiếu. Em đã xác nhận thao tác tạo SG; **ảnh dưới đây vẫn ở màn hình Create, chưa chứng minh rule tự tham chiếu đã được lưu**. Cần ảnh tab Inbound rules sau tạo để đối chiếu.

![Các rule dự kiến cho ECS SG ở màn hình tạo](images/07-ecs-sg-draft.png)

Em đã bấm Create cho `hotel-booking-rds-sg` theo xác nhận sau buổi thao tác; ảnh hiện có ghi lại cấu hình trước khi lưu và chưa có inbound rule. Em chưa chọn port database vì tài liệu nhóm chưa xác định PostgreSQL (`5432`) hay MySQL (`3306`). Khi chốt loại RDS, source của rule sẽ là ECS SG, không phải `0.0.0.0/0`.

![Khung RDS SG chưa có inbound rule](images/08-rds-sg-draft.png)

## 5. Đối chiếu với nhiệm vụ tuần 1

| Nhiệm vụ trong `tasks.md` | Trạng thái theo minh chứng hiện có |
|---|---|
| VPC `10.0.0.0/16` ở `us-east-1` | **Đã xác nhận** bằng ảnh VPC đã tạo. |
| 2 public + 2 private subnet trên 2 AZ | **Đã xác nhận** trên Resource map. |
| Internet Gateway và public route table | **Đã xác nhận** bằng Resource map và tab Routes. |
| Private route tables | **Có trong Resource map**; cần thêm ảnh tab Routes của từng bảng. |
| ALB security group | **Đã xác nhận**: HTTP 80 từ Internet. |
| ECS security group | **Sinh viên xác nhận đã tạo**; ảnh hiện có chứng minh cấu hình trước khi lưu. Cần ảnh trang chi tiết và rule tự tham chiếu để đối chiếu. |
| RDS security group | **Sinh viên xác nhận đã tạo**; chưa mở inbound khi loại database chưa chốt. Cần ảnh trang chi tiết để đối chiếu. |
| Tag `Project`/`Owner` cho toàn bộ tài nguyên mạng | **Đã xác nhận trên VPC**; còn phải đối chiếu từng tài nguyên khác. |
| Sơ đồ kiến trúc tổng thể | **Bản mô tả mạng trong báo cáo này**; chưa có sơ đồ hoàn chỉnh thể hiện ECS, RDS, DynamoDB, SNS/SQS, CloudWatch. |
| Nghiên cứu ECS, ALB, CloudWatch | Chưa có ghi chép hoặc minh chứng riêng trong ảnh; cần bổ sung vào nhật ký tuần. |

## 6. Việc cần tiếp tục

1. Chụp màn hình **Routes** của hai private route table, danh sách/tag các subnet và Internet Gateway.
2. Chụp trang chi tiết của ECS SG và RDS SG để bổ sung ID, tag và inbound rules sau tạo. Kiểm tra ECS self-reference rule TCP `8081` nếu nhóm dùng chung SG cho `room` và `booking`.
3. Chốt loại RDS và cách ECS ở private subnet truy cập ECR, CloudWatch, SNS/SQS, DynamoDB: NAT Gateway hoặc VPC endpoint phù hợp. Hiện chưa có NAT, nên **chưa thể kết luận ECS private task sẽ khởi chạy được**.
4. Vẽ sơ đồ kiến trúc tổng thể, sau đó mới triển khai ALB/ECS khi image và mã nguồn đã sẵn sàng. ALB, ECS, RDS và luồng đặt phòng **chưa được chứng minh là đã chạy** trong bộ ảnh này.
5. Bổ sung giờ thực tế vào worklog. Mốc 23:37–23:51 chỉ là khoảng thời gian của các ảnh được cung cấp, **không đại diện cho tổng 9 giờ làm việc** của tuần 1.

## 7. Ghi nhận sử dụng AI

Em sử dụng AI để giải thích khái niệm VPC/CIDR/subnet/NAT, rà soát các lựa chọn cấu hình và hỗ trợ biên tập báo cáo này. Việc thao tác AWS Console do em thực hiện. Các kết luận về trạng thái tài nguyên chỉ dựa trên ảnh chụp, không được AI xác nhận trực tiếp qua tài khoản AWS.
