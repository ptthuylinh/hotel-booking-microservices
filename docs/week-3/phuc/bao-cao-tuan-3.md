# Báo cáo tuần 3 — Cao Hoàng Phúc

**Đề tài:** Hệ thống đặt phòng khách sạn với kiến trúc microservices trên ECS\
**Sinh viên:** Cao Hoàng Phúc — MSSV `24110303`\
**Phân công:** SSM Parameter Store, CloudWatch, ECS Auto Scaling và quản lý chi phí\
**Trạng thái:** Đã hoàn thành cấu hình mục 3 — CloudWatch Metrics & Alarms; các mục còn lại đang thực hiện\
**Môi trường:** AWS Academy Learner Lab, tài khoản nhóm `055652951832`, Region `us-east-1`\
**Repository:** https://github.com/pttlinh32/hotel-booking-microservices\
**Ngày thực hiện:** 24/10/2026

## Công việc đã làm

### Thiết lập kênh nhận sự kiện cảnh báo bằng Amazon SNS

Em tạo SNS topic **`hotel-system-alerts`**, loại **Standard**, để tập trung sự kiện cảnh báo của hệ thống. Khi một CloudWatch alarm chuyển sang trạng thái `ALARM`, CloudWatch được cấu hình phát thông báo tới topic này.

Topic có ARN `arn:aws:sns:us-east-1:055652951832:hotel-system-alerts`. Em gắn cùng ARN này vào hành động **In alarm** của cả bốn alarm, giúp quản lý nơi nhận cảnh báo tập trung thay vì cấu hình riêng cho từng tài nguyên.

![Cấu hình CPU alarm gửi sự kiện tới SNS hotel-system-alerts](images/068-cpu-alert-topic.jpg)

Topic hiện chưa có subscription. Vì vậy, phần đã hoàn thành là tạo kênh SNS và cấu hình hành động từ CloudWatch; chưa xác nhận việc gửi email hoặc chuyển thông báo tới người nhận cuối.

### Cấu hình cảnh báo CPU và bộ nhớ của ECS

Em cấu hình hai alarm theo dõi tài nguyên của **`booking-service`** trong cluster **`hotel-cluster`**. Cả hai sử dụng namespace `AWS/ECS`, với hai dimension `ClusterName=hotel-cluster` và `ServiceName=booking-service`. Việc chỉ định đủ dimension giúp alarm theo dõi đúng service thay vì gộp nhầm dữ liệu của các service khác.

| Alarm | Metric | Thống kê | Chu kỳ | Điều kiện kích hoạt |
|---|---|---|---|---|
| `ECS-High-CPU-Utilization` | `CPUUtilization` | Average | 60 giây | CPU ≥80% trong 2/2 kỳ đánh giá liên tiếp |
| `ECS-High-Memory-Utilization` | `MemoryUtilization` | Average | 60 giây | Memory ≥85% trong 2/2 kỳ đánh giá liên tiếp |

Với cấu hình trên, alarm CPU chỉ kích hoạt khi giá trị trung bình vượt hoặc bằng 80% trong hai phút liên tiếp. Điều này hạn chế cảnh báo do một lần tăng tải ngắn. Alarm bộ nhớ được cấu hình tương tự với ngưỡng 85%.

![Thông số CPU alarm: đúng service, ngưỡng 80%, chu kỳ một phút và hai kỳ đánh giá](images/073-cpu-alarm-detail.jpg)

Em tạo alarm bộ nhớ từ cấu hình CPU, đổi metric thành `MemoryUtilization`, đổi ngưỡng thành `85` và đặt tên alarm riêng. Cách này giữ thống nhất chu kỳ đánh giá và SNS action giữa hai alarm.

![Cấu hình Memory alarm trước khi lưu](images/081-memory-review.jpg)

Hai alarm hiện giám sát `booking-service`; chưa mở rộng sang `room-service` và `notification-service`. Đây là cảnh báo vận hành, chưa phải chính sách ECS Auto Scaling.

### Cấu hình cảnh báo lỗi 5XX từ target của ALB

Em kiểm tra danh sách load balancer để xác định đúng ALB đang tồn tại, do CloudWatch còn lưu metric của một ALB cũ cùng tên. ALB được chọn là **`hotel-booking-alb`**, trạng thái **Active**, có dimension:

`LoadBalancer=app/hotel-booking-alb/4bb29c65802c7069`

![ALB hotel-booking-alb hiện hành trên EC2 Console](images/089-current-load-balancers.jpg)

Em tạo alarm **`ALB-High-Target-5XX-Errors`** với namespace `AWS/ApplicationELB`, metric **`HTTPCode_Target_5XX_Count`**, thống kê **Sum**, chu kỳ **60 giây** và điều kiện **≥5 lỗi trong một kỳ đánh giá**. Metric này đếm lỗi HTTP 5XX do ứng dụng phía target trả về; không phải metric lỗi do chính ALB tạo ra.

Trong danh sách metric gần đây chưa có metric lỗi target cần dùng. Em chọn dimension của ALB hiện hành rồi sửa tên metric trong biểu mẫu Console thành `HTTPCode_Target_5XX_Count`. Cấu hình đã được AWS lưu; cần phát sinh dữ liệu thực tế để xác nhận alarm chuyển trạng thái theo đúng ngưỡng.

![Cấu hình ALB target 5XX: Sum, một phút, ngưỡng năm lỗi và SNS action](images/104-alb-alarm-review.jpg)

### Cấu hình cảnh báo tin nhắn lỗi trong DLQ

Em tạo alarm **`SQS-DLQ-Has-Poison-Messages`** theo dõi queue **`booking-notification-dlq`**. Alarm sử dụng metric `ApproximateNumberOfMessagesVisible` trong namespace `AWS/SQS`, dimension `QueueName=booking-notification-dlq`, thống kê **Maximum**, chu kỳ **60 giây**, điều kiện **≥1 tin nhắn trong một kỳ đánh giá**.

Mục đích là phát hiện khi DLQ còn tin nhắn chờ xử lý để nhóm kiểm tra nguyên nhân và có phương án xử lý lại. Giá trị Maximum giúp ghi nhận tình huống có ít nhất một tin nhắn nhìn thấy được trong kỳ đo.

Sau khi tạo, alarm đã chuyển sang trạng thái **ALARM** dựa trên dữ liệu có sẵn của queue. Trong phiên này em không gửi thêm poison message và không xóa tin nhắn trong DLQ. Kết quả này chứng minh alarm đã đánh giá dữ liệu và kích hoạt; chưa thay thế cho kiểm thử luồng retry/redrive end-to-end.

![Alarm DLQ đã chuyển sang trạng thái ALARM](images/107-dlq-alarm-detail.jpg)

### Kiểm tra kết quả cấu hình

AWS Console xác nhận đã tạo thành công cả bốn alarm. Các alarm đều bật actions, gửi sự kiện khi vào trạng thái `ALARM` tới `hotel-system-alerts`, và giữ cách xử lý dữ liệu thiếu là **Treat missing data as missing**.

| Nội dung kiểm tra | Kết quả quan sát |
|---|---|
| SNS topic cảnh báo | Đã tạo `hotel-system-alerts`, loại Standard; chưa có subscription |
| Danh sách CloudWatch Alarms | Có đủ bốn alarm đã cấu hình |
| Alarm DLQ | Đã chuyển sang `ALARM` từ dữ liệu có sẵn |
| Alarm CPU và Memory | `Insufficient data` tại thời điểm chụp |
| Alarm ALB target 5XX | `Insufficient data` tại thời điểm chụp |
| Kiểm thử bằng tải thật hoặc tạo lỗi 5XX | Chưa thực hiện trong phiên này |
| Gửi cảnh báo tới email | Chưa kiểm thử vì SNS chưa có subscription |

Trạng thái `Insufficient data` cho biết alarm chưa có đủ điểm dữ liệu để kết luận bình thường hay vượt ngưỡng; không được xem là kết quả kiểm thử thành công dưới tải.

![Tổng hợp bốn alarm, trong đó DLQ đang ALARM](images/106-four-alarms-dlq-alarm.jpg)

### Kiểm tra log và kết thúc buổi thực hành

Em kiểm tra ba log group đang được hệ thống dùng: `/ecs/hotel/room-service`, `/ecs/hotel/booking-service` và `/ecs/hotel/notification-service`. Cả ba đã có retention **3 ngày** từ trước phiên này. Tên thực tế khác với tên dự kiến trong kế hoạch tuần 3; em ghi nhận theo tài nguyên hiện có, chưa đổi tên log group hoặc sửa cấu hình ECS.

Đầu phiên, Learner Lab hiển thị **đã dùng $8.80/$50**, tương đương **còn $41.20**. Đây là số đầu phiên, không phải chi phí chốt sau khi thực hành.

Sau khi hoàn tất cấu hình và lưu báo cáo lên nhánh `week-3`, em chọn **End Lab**. Giao diện Learner Lab xác nhận **AWS Status: Terminated**, thời gian **00:00**. Trong phiên này chưa kiểm tra riêng trạng thái RDS `Stopped` và ECS task bằng 0, nên việc End Lab không được dùng làm bằng chứng đã hoàn thành hai yêu cầu dọn tài nguyên đó.

![Learner Lab xác nhận kết thúc phiên](images/108-end-lab-terminated.jpg)

## Nghiên cứu dịch vụ

1. **CloudWatch Metrics và Alarms:** Dùng namespace, metric và dimension để xác định đúng tài nguyên cần giám sát; kết hợp ngưỡng, chu kỳ và số kỳ đánh giá để quyết định lúc cảnh báo.
2. **Amazon SNS:** Tập trung sự kiện cảnh báo vào một topic. Subscription là bước tiếp theo để chuyển thông báo tới người nhận hoặc hệ thống xử lý.
3. **ALB target 5XX:** Phân biệt lỗi do target ứng dụng trả về với lỗi do ALB tạo ra, lựa chọn thống kê Sum để đếm số lỗi trong một phút.
4. **SQS DLQ:** Dùng số tin nhắn nhìn thấy trong DLQ làm tín hiệu phát hiện sự kiện xử lý thất bại cần được kiểm tra.

## Công việc chưa hoàn thành so với tasks.md tuần 3

- Tạo sáu tham số SSM SecureString và chuyển thông tin kết nối DB trong ECS sang `secrets`; rà soát lại security group và public IP.
- Thực hiện truy vấn Logs Insights theo correlation ID, xây dựng `HotelBooking-System-Dashboard`.
- Cấu hình ECS Auto Scaling cho room/booking, triển khai image `v1.1.0` và phối hợp chạy tải thật để ghi nhận task tự co giãn.
- Bổ sung SNS subscription, xác nhận thông báo tới người nhận và kiểm thử kích hoạt CPU/Memory/ALB alarm.
- Thực thi và xác minh script bật/tắt; ghi nhật ký chi phí cuối phiên cùng bằng chứng RDS Stopped và ECS task bằng 0.

**Sử dụng AI:** Em dùng AI hỗ trợ thao tác AWS Console, đối chiếu metric và cấu hình alarm, chụp ảnh minh chứng và biên tập báo cáo. Nội dung trên chỉ ghi nhận cấu hình và kết quả đã quan sát trong phiên ngày 24/10/2026.
