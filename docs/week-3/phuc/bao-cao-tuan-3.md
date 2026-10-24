# Báo cáo tiến độ tuần 3 – Cao Hoàng Phúc (24110303)

Ngày thực hiện: 24/10/2026. AWS account: 055652951832; Region: us-east-1.

## Phạm vi đã hoàn thành: mục 3 – CloudWatch Metrics & Alarms

Cấu hình bằng giao diện AWS Console; không dùng AWS CLI/CloudShell. Đã tạo SNS Standard topic `hotel-system-alerts` với ARN `arn:aws:sns:us-east-1:055652951832:hotel-system-alerts`. Topic chưa có subscription; chưa xác nhận việc gửi email tới người nhận.

| Alarm | Metric và phạm vi | Điều kiện | SNS action |
|---|---|---|---|
| ECS-High-CPU-Utilization | AWS/ECS, CPUUtilization; hotel-cluster / booking-service; Average | ≥80%, 2/2 kỳ × 60 giây | hotel-system-alerts |
| ECS-High-Memory-Utilization | AWS/ECS, MemoryUtilization; hotel-cluster / booking-service; Average | ≥85%, 2/2 kỳ × 60 giây | hotel-system-alerts |
| ALB-High-Target-5XX-Errors | AWS/ApplicationELB, HTTPCode_Target_5XX_Count; app/hotel-booking-alb/4bb29c65802c7069; Sum | ≥5 lỗi, 1/1 kỳ × 60 giây | hotel-system-alerts |
| SQS-DLQ-Has-Poison-Messages | AWS/SQS, ApproximateNumberOfMessagesVisible; booking-notification-dlq; Maximum | ≥1 tin nhắn, 1/1 kỳ × 60 giây | hotel-system-alerts |

Cả bốn alarm bật actions; missing data được giữ là missing. CPU và Memory hiện giám sát booking-service, chưa bao phủ room-service/notification-service. Metric lỗi target 5XX được cấu hình theo đúng tên metric; không có sẵn trong danh sách metric gần đây nên chọn dimension của ALB đang tồn tại rồi sửa tên metric trong form Console.

## Kết quả quan sát trên AWS

Console xác nhận tạo thành công cả bốn alarm. DLQ đã tự chuyển sang **ALARM** khi giám sát dữ liệu có sẵn của queue. Không bơm thêm poison message và không xóa tin nhắn. Đây là quan sát trạng thái alarm, chưa phải kết quả kiểm thử retry/redrive end-to-end. Ba alarm CPU/Memory/ALB đang **Insufficient data** tại thời điểm chụp; chưa chạy tải hoặc chứng minh các alarm này chuyển trạng thái.

![Bốn alarm và trạng thái DLQ ALARM](images/106-four-alarms-dlq-alarm.jpg)

![Chi tiết DLQ ALARM](images/107-dlq-alarm-detail.jpg)

## Kiểm tra ban đầu và các việc còn lại

- Ba log group thực tế là `/ecs/hotel/room-service`, `/ecs/hotel/booking-service`, `/ecs/hotel/notification-service`; cả ba đã có retention 3 ngày trước phiên này. Chưa đổi tên log group hoặc cấu hình ECS.
- Parameter Store hiển thị trang bắt đầu sử dụng; chưa tạo sáu SecureString và chưa chuyển ECS environment sang secrets.
- Chưa cấu hình dashboard, Logs Insights query, Auto Scaling hoặc triển khai v1.1.0 trong phiên này.
- Chưa chạy script bật/tắt, load test, hoặc kiểm tra trạng thái dừng của RDS/ECS. Không ghi nhận hoàn thành các mục đó.
- Learner Lab đầu phiên hiển thị Used $8.80/$50, tương đương còn $41.20; đây là số hiển thị đầu phiên, không phải số chốt sau phiên.

## Ảnh từng bước

Ảnh minh chứng bên dưới được chụp sau khi cursor Codex tự ẩn, giữ nguyên nội dung Console. Các ảnh gốc đầu phiên còn cursor được lưu cục bộ riêng, không dùng làm ảnh báo cáo. Chưa chỉnh sửa hoặc tái tạo nội dung ảnh.

- [050-cpu-metric-picker.jpg](images/050-cpu-metric-picker.jpg)
- [051-ecs-metric-group-no-cursor.jpg](images/051-ecs-metric-group-no-cursor.jpg)
- [052-ecs-service-metrics-no-cursor.jpg](images/052-ecs-service-metrics-no-cursor.jpg)
- [053-booking-cpu-selected-no-cursor.jpg](images/053-booking-cpu-selected-no-cursor.jpg)
- [054-cpu-picker.jpg](images/054-cpu-picker.jpg)
- [055-ecs-namespace.jpg](images/055-ecs-namespace.jpg)
- [056-ecs-service-list.jpg](images/056-ecs-service-list.jpg)
- [057-booking-cpu-checked.jpg](images/057-booking-cpu-checked.jpg)
- [058-booking-cpu-conditions.jpg](images/058-booking-cpu-conditions.jpg)
- [059-cpu-period-menu.jpg](images/059-cpu-period-menu.jpg)
- [060-cpu-period-one-minute.jpg](images/060-cpu-period-one-minute.jpg)
- [061-cpu-greater-equal.jpg](images/061-cpu-greater-equal.jpg)
- [062-cpu-threshold-80.jpg](images/062-cpu-threshold-80.jpg)
- [063-cpu-additional.jpg](images/063-cpu-additional.jpg)
- [064-cpu-evaluation-two.jpg](images/064-cpu-evaluation-two.jpg)
- [065-cpu-datapoints-two.jpg](images/065-cpu-datapoints-two.jpg)
- [066-cpu-actions.jpg](images/066-cpu-actions.jpg)
- [067-cpu-topic-arn-option.jpg](images/067-cpu-topic-arn-option.jpg)
- [068-cpu-alert-topic.jpg](images/068-cpu-alert-topic.jpg)
- [069-cpu-name-form.jpg](images/069-cpu-name-form.jpg)
- [070-cpu-alarm-name.jpg](images/070-cpu-alarm-name.jpg)
- [071-cpu-alarm-review.jpg](images/071-cpu-alarm-review.jpg)
- [072-cpu-alarm-created.jpg](images/072-cpu-alarm-created.jpg)
- [073-cpu-alarm-detail.jpg](images/073-cpu-alarm-detail.jpg)
- [074-cpu-alarm-actions-menu.jpg](images/074-cpu-alarm-actions-menu.jpg)
- [075-copy-alarm-for-memory.jpg](images/075-copy-alarm-for-memory.jpg)
- [076-memory-metric-name.jpg](images/076-memory-metric-name.jpg)
- [077-memory-threshold-85.jpg](images/077-memory-threshold-85.jpg)
- [078-memory-actions.jpg](images/078-memory-actions.jpg)
- [079-memory-name-form.jpg](images/079-memory-name-form.jpg)
- [080-memory-alarm-name.jpg](images/080-memory-alarm-name.jpg)
- [081-memory-review.jpg](images/081-memory-review.jpg)
- [082-memory-alarm-created.jpg](images/082-memory-alarm-created.jpg)
- [083-new-alb-alarm.jpg](images/083-new-alb-alarm.jpg)
- [084-alb-metric-picker.jpg](images/084-alb-metric-picker.jpg)
- [085-applicationelb-namespace.jpg](images/085-applicationelb-namespace.jpg)
- [086-alb-metrics-list.jpg](images/086-alb-metrics-list.jpg)
- [087-home-for-alb-check.jpg](images/087-home-for-alb-check.jpg)
- [088-ec2-for-alb-check.jpg](images/088-ec2-for-alb-check.jpg)
- [089-current-load-balancers.jpg](images/089-current-load-balancers.jpg)
- [090-current-alb-metric-selected.jpg](images/090-current-alb-metric-selected.jpg)
- [091-alb-metric-conditions.jpg](images/091-alb-metric-conditions.jpg)
- [092-target-5xx-metric.jpg](images/092-target-5xx-metric.jpg)
- [093-alb-statistic-menu.jpg](images/093-alb-statistic-menu.jpg)
- [094-alb-sum.jpg](images/094-alb-sum.jpg)
- [095-alb-period-menu.jpg](images/095-alb-period-menu.jpg)
- [096-alb-one-minute.jpg](images/096-alb-one-minute.jpg)
- [097-alb-greater-equal.jpg](images/097-alb-greater-equal.jpg)
- [098-alb-five-errors.jpg](images/098-alb-five-errors.jpg)
- [099-alb-actions.jpg](images/099-alb-actions.jpg)
- [100-alb-sns-option.jpg](images/100-alb-sns-option.jpg)
- [101-alb-alert-arn.jpg](images/101-alb-alert-arn.jpg)
- [102-alb-name-form.jpg](images/102-alb-name-form.jpg)
- [103-alb-alarm-name.jpg](images/103-alb-alarm-name.jpg)
- [104-alb-alarm-review.jpg](images/104-alb-alarm-review.jpg)
- [105-four-alarms-created.jpg](images/105-four-alarms-created.jpg)
- [106-four-alarms-dlq-alarm.jpg](images/106-four-alarms-dlq-alarm.jpg)
- [107-dlq-alarm-detail.jpg](images/107-dlq-alarm-detail.jpg)
