package com.hotel.notification.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.hotel.notification.dto.BookingCreatedEvent;
import com.hotel.notification.dto.NotificationRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.DeleteMessageRequest;
import software.amazon.awssdk.services.sqs.model.Message;
import software.amazon.awssdk.services.sqs.model.ReceiveMessageRequest;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class NotificationConsumerService {

    private static final Logger log = LoggerFactory.getLogger(NotificationConsumerService.class);

    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;

    @Value("${aws.sqs.queue.url:https://sqs.us-east-1.amazonaws.com/055652951832/booking-notification-queue}")
    private String queueUrl;

    @Value("${notification.polling.enabled:true}")
    private boolean pollingEnabled;

    // Idempotency: Bộ nhớ lưu các eventId đã xử lý để tránh gửi trùng lặp email
    private final Set<String> processedEventIds = ConcurrentHashMap.newKeySet();

    // Lịch sử các thông báo đã gửi để phục vụ API GET /api/notifications
    private final List<NotificationRecord> notificationHistory = new CopyOnWriteArrayList<>();

    public NotificationConsumerService(SqsClient sqsClient, ObjectMapper objectMapper) {
        this.sqsClient = sqsClient;
        this.objectMapper = objectMapper;
    }

    public List<NotificationRecord> getNotificationHistory() {
        return new ArrayList<>(notificationHistory);
    }

    @Scheduled(fixedDelay = 5000)
    public void pollMessagesFromQueue() {
        if (!pollingEnabled) {
            return;
        }

        try {
            ReceiveMessageRequest receiveRequest = ReceiveMessageRequest.builder()
                    .queueUrl(queueUrl)
                    .maxNumberOfMessages(10)
                    .waitTimeSeconds(2) // Long polling ngắn
                    .build();

            List<Message> messages = sqsClient.receiveMessage(receiveRequest).messages();

            if (!messages.isEmpty()) {
                log.info("Nhận được {} tin nhắn từ hàng đợi SQS: {}", messages.size(), queueUrl);
                for (Message message : messages) {
                    processSingleMessage(message);
                }
            }
        } catch (Exception e) {
            // Log ở mức debug/warn khi chạy offline hoặc chưa cấu hình SQS
            log.trace("SQS polling check (bỏ qua nếu chưa kết nối AWS thật): {}", e.getMessage());
        }
    }

    private void processSingleMessage(Message message) {
        String body = message.body();
        try {
            BookingCreatedEvent event = parseEventFromBody(body);
            if (event == null || event.getEventId() == null) {
                throw new IllegalArgumentException("Message must contain a booking eventId");
            }

            // Cơ chế Idempotency: Kiểm tra eventId đã xử lý chưa
            String eventId = event.getEventId();
            if (processedEventIds.contains(eventId)) {
                log.warn("⚠️ [IDEMPOTENCY] Phát hiện sự kiện trùng lặp (eventId: {})! Bỏ qua gửi email lần 2.", eventId);
                deleteMessageFromQueue(message);
                return;
            }

            // Đánh dấu eventId đã được xử lý
            processedEventIds.add(eventId);

            // Mô phỏng gửi email và ghi log chi tiết cho CloudWatch
            simulateSendEmail(event);

            // Xóa message khỏi SQS Queue (ACK - Acknowledgment)
            deleteMessageFromQueue(message);

        } catch (Exception e) {
            log.error("Lỗi khi xử lý message SQS (MessageId: {}): {}", message.messageId(), e.getMessage());
            // Không xóa message để SQS chuyển sang DLQ sau khi vượt quá maxReceiveCount = 3
        }
    }

    private BookingCreatedEvent parseEventFromBody(String body) {
        try {
            JsonNode rootNode = objectMapper.readTree(body);

            // Trường hợp SNS Fanout sang SQS không bật Raw Message Delivery (được bọc trong SNS Envelope)
            if (rootNode.has("Type") && "Notification".equals(rootNode.get("Type").asText()) && rootNode.has("Message")) {
                String innerMessage = rootNode.get("Message").asText();
                return objectMapper.readValue(innerMessage, BookingCreatedEvent.class);
            }

            // Trường hợp Raw Message Delivery bật (trực tiếp payload BookingCreatedEvent)
            return objectMapper.readValue(body, BookingCreatedEvent.class);
        } catch (Exception e) {
            log.error("Không thể giải mã JSON message payload: {}", e.getMessage());
            throw new IllegalArgumentException("Cannot parse booking event payload", e);
        }
    }

    private void simulateSendEmail(BookingCreatedEvent event) {
        BookingCreatedEvent.BookingEventData data = event.getData();
        if (data == null) {
            data = new BookingCreatedEvent.BookingEventData();
        }

        String recipient = data.getCustomerEmail() != null ? data.getCustomerEmail() : "guest@example.com";
        String customerName = data.getCustomerName() != null ? data.getCustomerName() : "Quý khách";
        String bookingId = data.getBookingId() != null ? data.getBookingId() : "N/A";
        String roomNumber = data.getRoomNumber() != null ? data.getRoomNumber() : "N/A";

        log.info("""
                ================================================================================
                📧 [MÔ PHỎNG EMAIL] GỬI THÀNH CÔNG EMAIL XÁC NHẬN ĐẶT PHÒNG
                --------------------------------------------------------------------------------
                Kính gửi:         {} <{}>
                Số điện thoại:    {}
                Mã đơn đặt phòng: {}
                Số phòng:         {}
                Thời gian:        {} -> {} ({} đêm)
                Tổng tiền:        {} {}
                Trạng thái:       {}
                Mã sự kiện:       {}
                Thời điểm gửi:    {}
                ================================================================================""",
                customerName, recipient,
                data.getCustomerPhone(),
                bookingId,
                roomNumber,
                data.getCheckInDate(), data.getCheckOutDate(), data.getNumberOfNights(),
                data.getTotalPrice(), data.getCurrency() != null ? data.getCurrency() : "USD",
                data.getBookingStatus(),
                event.getEventId(),
                LocalDateTime.now()
        );

        // Lưu bản ghi vào danh sách lịch sử
        NotificationRecord record = NotificationRecord.builder()
                .notificationId("notif-" + UUID.randomUUID())
                .eventId(event.getEventId())
                .bookingId(bookingId)
                .customerName(customerName)
                .customerEmail(recipient)
                .roomNumber(roomNumber)
                .totalPrice(data.getTotalPrice())
                .channel("EMAIL")
                .status("SENT")
                .sentAt(LocalDateTime.now())
                .build();

        notificationHistory.add(0, record);
    }

    private void deleteMessageFromQueue(Message message) {
        try {
            DeleteMessageRequest deleteRequest = DeleteMessageRequest.builder()
                    .queueUrl(queueUrl)
                    .receiptHandle(message.receiptHandle())
                    .build();
            sqsClient.deleteMessage(deleteRequest);
            log.info("Đã xóa tin nhắn thành công khỏi SQS (ACK ReceiptHandle: {}...)",
                    message.receiptHandle().substring(0, Math.min(15, message.receiptHandle().length())));
        } catch (Exception e) {
            log.warn("Không thể xóa message khỏi SQS: {}", e.getMessage());
        }
    }
}
