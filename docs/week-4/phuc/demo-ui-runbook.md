# Kịch bản video tuần 4 có UI — tối đa 10 phút

Dùng dữ liệu kiểm thử có tên rõ ràng, email `demo@example.com` và ngày nhận phòng từ hôm nay trở đi.
Không dùng dữ liệu khách thật. Chuẩn bị sẵn AWS Console, DB viewer trong VPC và CloudWatch; không dành thời gian video chờ startup/scaling.

| Mốc | Thao tác | Minh chứng |
|---|---|---|
| 00:00–01:00 | Giới thiệu nhóm; mở sơ đồ trang 1 | UI → ALB → Fargate; VPC 2 AZ; RDS Single-AZ; SNS/SQS/DLQ; giám sát |
| 01:00–01:40 | Mở ERD và DB strategy (trang 2–3) | `room_db.rooms`, `booking_db.bookings`; room_id là logic ref, không FK xuyên DB; audit lưu mã BK |
| 01:40–04:00 | UI → Phòng → chọn phòng AVAILABLE → đặt phòng | Giá dự kiến, xác nhận 201; booking code; phòng RESERVED; RDS có booking; DynamoDB item; notification log |
| 04:00–05:30 | UI nhập email sai; đặt trùng phòng bằng Postman; test rollback chuẩn bị trước | Validation; HTTP 409; khi gây lỗi phải kiểm tra trạng thái phòng, không chỉ đọc status code |
| 05:30–06:15 | SQS poison message đã chuẩn bị → mở DLQ và alarm | Queue redrive maxReceiveCount=3; DLQ có message; alarm |
| 06:15–07:30 | Mở Nhật ký yêu cầu UI → lấy correlation → CloudWatch Logs Insights | Correlation xuất hiện tại booking, room, notification; Dashboard CPU/RAM/ALB |
| 07:30–08:30 | Mở bằng chứng scaling đã quay khi sinh tải | Desired/running tasks từ 1 lên 2; min/max hiện 0–3; không hứa scale từ 0 theo CPU |
| 08:30–09:20 | Stop 1 ECS task và tua đoạn chờ hợp lý | Task thay thế, target healthy; request qua ALB phục hồi; ghi thời gian đo thực tế |
| 09:20–10:00 | Chi phí thực tế, giải thích teardown và tổng kết | Billing/Credits có thời điểm; chỉ trình chiếu teardown khi vẫn cần hệ thống để quay |

## Chuẩn bị giao diện

1. Mở `http://<ALB-DNS>/ui/index.html` và bấm **Làm mới dữ liệu**. Cả 3 service phải báo đã kết nối.
2. Mở **Quản lý phòng**, chọn một phòng AVAILABLE. Kiểm tra danh sách booking để tránh dùng phòng đã RESERVED.
3. Tạo booking bằng UI, giữ lại mã BK và mã correlation trong nhật ký; tra cứu lại bằng cả mã và ID.
4. Mở **Thông báo**, tải lại sau một vài giây. Lịch sử API nằm trong RAM từng task; CloudWatch là bằng chứng đối chiếu khi task restart.
5. UI đổi trạng thái phòng chỉ tác động phòng; không có API hủy booking. Không trình bày thao tác này như hủy đơn.

## Điểm cần nói đúng

- Booking → room dùng HTTP qua ALB hiện có; Cloud Map chưa được cấp quyền trong Learner Lab. Không còn dựa vào IP task cố định.
- Ba service được phép chạy trong 2 private subnets, nhưng với desiredCount=1 không khẳng định mỗi AZ có 1 task.
- RDS Single-AZ và chỉ một NAT; chưa có HA đa AZ cho toàn bộ hệ thống.
- DynamoDB `bookingId` chứa `booking_code` BK-…, không phải UUID của bảng bookings.
- 201 không tự chứng minh audit/SNS đã thành công vì code ghi side effect best effort; phải mở từng minh chứng.
- Handler DB hiện có thể trả 500; không đọc nguyên lời khẳng định 503/RFC7807 trong báo cáo cũ nếu chưa đo đúng phiên bản đang chạy.
- Không dùng số 12 giây / 45ms / $12.50 như kết quả đo mới. Dùng thời gian, latency và số dư thực tế lúc quay.
- Notifications hiện được consumer mô phỏng xử lý và ghi log; không khẳng định đã gửi email thực đến mailbox.

## Bộ sơ đồ

Xem [README bộ sơ đồ](architecture/README.md). File draw.io có 3 trang; PNG 4K theo tỷ lệ 16:9, có thể đặt trực tiếp vào timeline video.

## Teardown

`scripts/teardown-environment.ps1` là script xóa tài nguyên và bỏ final snapshot của RDS.
Bản hiện tại chưa xóa toàn bộ target groups, cluster, dashboard, SSM, NAT/VPC và DynamoDB như một số nội dung báo cáo mô tả.
Chỉ trình chiếu khi còn cần hệ thống; không chạy trước khi đã quay và lưu đủ minh chứng. Sau nghiệm thu cần rà lại tài nguyên còn tính phí trên Console.
