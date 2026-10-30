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
- Kết quả smoke test AWS và task revisions sẽ được ghi sau khi rollout hoàn tất.

## Minh bạch AI cho phần cập nhật này

Codex hỗ trợ triển khai UI, kiểm thử tự động, script triển khai và dựng lại sơ đồ từ source code/cấu hình AWS đã đọc.
Ảnh PNG của bộ sơ đồ là bản vẽ kiến trúc, không phải ảnh chụp Console. Ảnh UI và kết quả AWS chỉ ghi là thực nghiệm khi đã quan sát trực tiếp.
