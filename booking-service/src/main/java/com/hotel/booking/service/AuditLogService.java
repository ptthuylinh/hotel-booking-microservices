package com.hotel.booking.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class AuditLogService {

    private static final Logger log = LoggerFactory.getLogger(AuditLogService.class);

    private final DynamoDbClient dynamoDbClient;

    @Value("${aws.dynamodb.table.audit:hotel-booking-audit-logs}")
    private String auditTableName;

    public AuditLogService(DynamoDbClient dynamoDbClient) {
        this.dynamoDbClient = dynamoDbClient;
    }

    public void recordAuditLog(String bookingId, String action, String previousStatus, String newStatus, Map<String, String> details) {
        String timestamp = Instant.now().toString();
        String auditId = "aud-" + UUID.randomUUID();

        log.info("Ghi nhận Audit Trail vào DynamoDB table '{}' cho bookingId: {}", auditTableName, bookingId);

        try {
            Map<String, AttributeValue> item = new HashMap<>();
            item.put("bookingId", AttributeValue.builder().s(bookingId).build());
            item.put("timestamp", AttributeValue.builder().s(timestamp).build());
            item.put("auditId", AttributeValue.builder().s(auditId).build());
            item.put("action", AttributeValue.builder().s(action).build());
            item.put("previousStatus", AttributeValue.builder().s(previousStatus).build());
            item.put("newStatus", AttributeValue.builder().s(newStatus).build());
            item.put("actor", AttributeValue.builder().s("booking-service").build());

            if (details != null && !details.isEmpty()) {
                Map<String, AttributeValue> detailsMap = new HashMap<>();
                details.forEach((k, v) -> detailsMap.put(k, AttributeValue.builder().s(v != null ? v : "").build()));
                item.put("details", AttributeValue.builder().m(detailsMap).build());
            }

            PutItemRequest putItemRequest = PutItemRequest.builder()
                    .tableName(auditTableName)
                    .item(item)
                    .build();

            dynamoDbClient.putItem(putItemRequest);
            log.info("Ghi DynamoDB Audit Log thành công (auditId: {})", auditId);
        } catch (Exception e) {
            log.warn("Không thể ghi Audit Log vào DynamoDB (tiếp tục luồng chính): {}", e.getMessage());
        }
    }
}
