# Kiểm chứng UI và triển khai — 30/10/2026

## Phạm vi

UI tiếng Việt trong static resources của room-service, bao phủ các endpoint nghiệp vụ hiện có của 3 microservices.
Không bổ sung API thanh toán, hủy booking, đăng nhập hoặc thao tác hạ tầng từ UI.

## Kiểm thử local đã thực hiện

| Nhóm | Kết quả | Phạm vi / giới hạn |
|---|---|---|
| UI automation qua DOM | 16 kịch bản PASS (17 test entries gồm parent suite) | Overview; lọc phòng; room detail/PUT; chọn phòng; dự toán; ngày sai; độ dài cột; 409/retry; tạo booking; lookup code/ID; 404; notifications; 503 từng phần; malformed JSON structure; escape HTML; fallback route; correlation trên HTTP ALB |
| HTTP tích hợp | 23 checks PASS | Static assets/entrypoints; API room/booking/notification; tạo 201, validation 400, duplicate 409, lookup 404, room state; 3 Spring Boot containers + PostgreSQL 16 thật |
| Maven context | 3/3 service PASS | Dùng PostgreSQL test local; notification polling tắt; không dùng credentials AWS thật |
| Routing/deploy helper | 3 tests PASS | Fallback ALB khi Cloud Map bị từ chối; giữ secrets/task role/sidecar khi đổi endpoint; AWS waiter stdout rỗng |
| Docker | 3 image build PASS | Linux amd64; label `org.opencontainers.image.revision` khớp source commit |
| Browser | Kiểm tra desktop và viewport 390px | Đã tạo booking qua form với backend local, nhận CONFIRMED và tổng tiền theo server |
| ERD | Khớp entity và DDL local | Đã truy vấn information_schema cho 2 bảng; AWS describe-table cho khóa DynamoDB |

Local HTTP integration không kiểm chứng publish SNS/DynamoDB/SQS thực: AWS credential provider bị vô hiệu hóa trong môi trường test.
Kiểm chứng AWS sau deploy phải ghi riêng, không gộp vào kết quả local.

## Triển khai

- CloudShell đúng AWS account `055652951832`, region `us-east-1`.
- RDS được khởi động lại tại chỗ, không recreate database hoặc thay Security Groups.
- Image archive đã kiểm thử local được upload CloudShell, đối chiếu SHA256 rồi docker load/push ECR.
- Mỗi image có label Git revision; script từ chối nếu source revision không khớp.
- Giữ các thông số ECS task/secret/network từ task definition cũ, chỉ đổi image; room có thêm static UI.
- Thêm ALB UI routes, giữ các API rules.
- Learner Lab từ chối `servicediscovery:CreatePrivateDnsNamespace`; dùng ALB hiện có làm endpoint ổn định của REST booking→room.
- Rollout đã hoàn tất: room-service revision **3**, booking-service revision **4**, notification-service revision **3**; mỗi service 1 task, trạng thái `COMPLETED`.
- Image tag: `ui-442329f323b8`; source revision `442329f323b84551eb00e30a1878dbd1e2361570`.

## Kết quả kiểm chứng AWS thực tế

**UI:** http://hotel-booking-alb-1393379083.us-east-1.elb.amazonaws.com/ui/index.html

| Kiểm tra | Kết quả quan sát |
|---|---|
| UI tải dữ liệu | Cả 3 service kết nối; 4 phòng; 7 booking sau lượt thử, giữ nguyên 6 đơn cũ |
| Room filter/detail/status | Lọc B-202 + RESERVED; GET detail 200; PUT trạng thái 200 |
| Validation UI | Ngày trả trước ngày nhận bị chặn, không gửi POST |
| Tạo booking qua browser | **201 Created**, `BK-98346`, UUID `0b357113-4e85-417e-b125-83b31297a94d` |
| Dữ liệu booking | Khách `UI Smoke Test 30-10`, email `ui-smoke@example.com`, phòng B-202, 15–17/01/2027, 2 đêm, **500 USD**, CONFIRMED |
| Tra cứu | GET theo mã BK và UUID đều 200, trả cùng đơn |
| Room sau booking | Phòng ID 4 trở về RESERVED, trùng trạng thái trước lượt thử |
| Audit | DynamoDB có `BOOKING_CREATED`, `newStatus=CONFIRMED`, bookingId=BK-98346, timestamp `2026-10-30T08:31:39.352391875Z` |
| SNS/SQS/consumer | Notification API có cùng mã BK; `SENT`, event `evt-63dea13e-321c-4992-839d-99f1fd1f5928`; đây là mô phỏng email qua log |
| Tracing | Correlation `web-bbcf87edc5a57e3b96f67f49d8da3727` xuất hiện trong cả 3 log groups |
| Cloud smoke script | **15/15 PASS**, gồm static assets, room filter/detail, booking list/code/UUID, notifications, 404, validation 400, duplicate 409 |
| Responsive | Đã kiểm tra bản cloud ở viewport 390px, không tràn toàn trang; thanh điều hướng và bảng có vùng cuộn |

Browser ghi nhận POST tạo booking đầu tiên khoảng **7.7 giây**, là một mẫu smoke test có chi phí khởi tạo SDK; không dùng làm kết quả benchmark/latency SLA.
Timestamp LocalDateTime từ API là giờ máy chủ ECS (UTC); ngày/giờ của browser hiển thị theo máy người dùng.

Chạy lại kiểm tra cloud với dữ liệu thử đã có:

```bash
python3 scripts/cloud-smoke-test.py \
  --base-url http://hotel-booking-alb-1393379083.us-east-1.elb.amazonaws.com \
  --booking-code BK-98346 --negative-writes
```

Không chạy lại các POST lỗi bằng dữ liệu thật. Script kiểm tra phòng vẫn RESERVED trước các negative cases; khi thay dữ liệu demo phải kiểm tra lại điều kiện này.

Các thử nghiệm chaos/load/teardown của kế hoạch tuần 4 không được chạy lại trong đợt bổ sung UI này. Kịch bản video tách rõ minh chứng hiện có và phần cần quay lại.

## Minh bạch AI cho phần cập nhật này

Codex hỗ trợ triển khai UI, kiểm thử tự động, script triển khai và dựng lại sơ đồ từ source code/cấu hình AWS đã đọc.
Ảnh PNG của bộ sơ đồ là bản vẽ kiến trúc, không phải ảnh chụp Console. Ảnh UI và kết quả AWS chỉ ghi là thực nghiệm khi đã quan sát trực tiếp.
