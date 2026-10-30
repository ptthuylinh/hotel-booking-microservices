# Bộ sơ đồ kiến trúc, ERD và database strategy — Tuần 4

Bản tuần 4 thay thế việc sử dụng mô hình khái niệm tuần 1 để mô tả hệ thống đã triển khai.
Giữ nguyên [file gốc tuần 1](../../../week-1/hotel-microservices-erd-and-db-strategy.drawio) làm lịch sử thiết kế.

## Dùng cho video

| Trang | Nội dung | File trình chiếu |
|---|---|---|
| 1 | VPC 2 AZ, ALB/UI, ECS, RDS, SNS/SQS/DLQ, DynamoDB, SSM, CloudWatch | [PNG 4K](01-aws-architecture-week4.png) · [SVG](01-aws-architecture-week4.svg) |
| 2 | ERD triển khai, khóa/kiểu dữ liệu, quan hệ logic giữa service | [PNG 4K](02-erd-week4.png) · [SVG](02-erd-week4.svg) |
| 3 | Quyền sở hữu dữ liệu, transaction local, bồi hoàn và event | [PNG 4K](03-db-strategy-week4.png) · [SVG](03-db-strategy-week4.svg) |

**Chỉnh sửa:** mở [file draw.io 3 trang](hotel-week4-architecture-erd-db-strategy.drawio) bằng diagrams.net.
Ảnh PNG 3840×2160, tỷ lệ 16:9; có thể thu về 1920×1080 khi dựng video.

**Nguồn icon:** [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/), gói ngày 31/07/2026.
Chỉ trích xuất các SVG cần dùng vào `assets/`; bản PNG/SVG đã nhúng icon, không cần kết nối Internet.

## Điểm đã sửa so với thiết kế tuần 1

- PostgreSQL hiện có **2 bảng JPA**: `room_db.rooms` và `booking_db.bookings`.
- Không đưa `khach_hang`, `loai_phong`, thanh toán hay bảng thông báo vào ERD vật lý vì chưa có entity/API tương ứng.
- `rooms.type` lưu trực tiếp loại phòng; thông tin khách được chụp lại trong booking.
- `bookings.room_id` là tham chiếu logic tới `rooms.id`, không phải SQL FK xuyên database; mỗi service truy cập DB riêng.
- `bookings.id` là chuỗi UUID 36 ký tự; `booking_code` là mã BK-… có unique constraint.
- DynamoDB `hotel-booking-audit-logs` dùng **PK `bookingId` + SK `timestamp`**, cả hai kiểu String; billing `PAY_PER_REQUEST` đã đối chiếu AWS.
- `AuditLogService` ghi `bookingId` bằng **booking code**, không phải UUID.
- Notification history và dedup event IDs nằm trong RAM từng task; không phải database bền vững.
- RDS hiện **Single-AZ tại us-east-1b**, private, không vẽ thêm standby/replica chưa triển khai.
- ECS được phép đặt task trong 2 private subnets; mỗi service có 1 task không đồng nghĩa luôn có task ở cả 2 AZ.
- Có một NAT Gateway tại public subnet us-east-1a; không mô tả NAT có dự phòng đa AZ.
- Có 4 alarm do nhóm tạo, ngoài ra có các alarm do target tracking tự tạo. Autoscaling room/booking hiện min=0, max=3 để phục vụ tiết kiệm Lab; CPU scaling không tự khởi động lại từ 0 nếu không có CPU metric.

## Nguồn đối chiếu

- `room-service/.../entity/Room.java` và `booking-service/.../entity/Booking.java`: tên bảng, cột, độ dài, nullability, unique, precision/scale.
- `BookingService.java`: thứ tự REST giữ phòng, JPA save, audit, SNS, bồi hoàn.
- `AuditLogService.java`: các thuộc tính audit và việc bắt lỗi rồi tiếp tục.
- `NotificationConsumerService.java`, `NotificationRecord.java`: consumer, RAM history, dedup theo eventId.
- AWS CloudShell ngày 30/10/2026: ECS services/network, VPC/subnet/route/NAT, RDS, Security Groups, SSM parameter names, SNS subscription, SQS redrive, DynamoDB key schema, CloudWatch retention/dashboard/alarms, scaling bounds. Không xuất giá trị secrets vào tài liệu.

## Dữ liệu và transaction

| Thành phần | Dữ liệu sở hữu | Cách truy cập |
|---|---|---|
| room-service | PostgreSQL `room_db.rooms` | JPA, tài khoản DB riêng |
| booking-service | PostgreSQL `booking_db.bookings` | JPA, tài khoản DB riêng |
| booking-service / audit | DynamoDB audit trail | AWS SDK / IAM task role |
| notification-service | SQS message; history/dedup trong RAM | SQS polling, xóa message sau xử lý |

`@Transactional` chỉ bao phủ database của từng service. Không có transaction ACID bao phủ room DB, booking DB, DynamoDB và SNS.
Khi exception xảy ra trong khối try sau khi khóa phòng, code cố gọi `releaseRoom` để bồi hoàn. Đây là best effort: release có thể lỗi, và lỗi DB tại thời điểm transaction commit sau khi method trả về có thể nằm ngoài khối catch.
Audit và publish SNS tự bắt exception rồi tiếp tục, nên 201 không tự chứng minh cả hai side effects đã thành công; phải kiểm tra audit item và notification log.
Chưa có transactional outbox, dedup bền vững hay cơ chế reconciliation. Không mô tả các tính năng này như đã hoàn thành.

## Thuyết minh gợi ý (60–90 giây)

“Giao diện web và API đi qua ALB. Ba service chạy trên Fargate trong private subnets của hai AZ; room-service đồng thời phục vụ UI. Room và Booking sở hữu hai logical database riêng trên cùng RDS để tiết kiệm Lab; quan hệ room_id là tham chiếu qua REST, không join xuyên database. Booking giữ phòng, lưu đơn rồi ghi audit và phát sự kiện SNS. SQS tách việc xử lý thông báo khỏi request; message lỗi được chuyển DLQ theo maxReceiveCount=3. Cấu hình DB lấy từ SSM SecureString, quyền AWS qua LabRole. CloudWatch lưu log ba ngày và dùng correlation ID để truy vết. RDS và NAT hiện chỉ có một instance/gateway, nên sơ đồ không khẳng định toàn hệ thống đã có HA đa AZ.”

## Tái tạo

```bash
python3 scripts/render-week4-diagrams.py --discovery alb
```

Dùng `--discovery static` khi mô tả môi trường cũ dùng bản ghi A tĩnh trong private zone `hotel.local`.
Chỉ chọn bản Cloud Map khi bước cấu hình discovery đã thành công và được xác minh.

## REST sau triển khai tuần 4

Learner Lab từ chối `servicediscovery:CreatePrivateDnsNamespace`; không mô tả Cloud Map như đã triển khai.
`ROOM_SERVICE_URL` được cấu hình bằng DNS ổn định của ALB hiện có; booking gọi REST qua ALB tới room target group.
Luồng qua NAT/ALB có thêm độ trễ/chi phí nhưng không còn phụ thuộc IP của một task. Private zone `hotel.local` cũ được giữ nguyên và không dùng làm endpoint booking.
