package com.hotel.booking.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hotel.booking.dto.BookingCreatedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.sns.SnsClient;
import org.slf4j.MDC;
import software.amazon.awssdk.services.sns.model.MessageAttributeValue;
import software.amazon.awssdk.services.sns.model.PublishRequest;
import software.amazon.awssdk.services.sns.model.PublishResponse;

import java.util.HashMap;
import java.util.Map;

@Service
public class EventPublisherService {

    private static final Logger log = LoggerFactory.getLogger(EventPublisherService.class);

    private final SnsClient snsClient;
    private final ObjectMapper objectMapper;

    @Value("${aws.sns.topic.booking:arn:aws:sns:us-east-1:055652951832:hotel-booking-events}")
    private String topicArn;

    public EventPublisherService(SnsClient snsClient, ObjectMapper objectMapper) {
        this.snsClient = snsClient;
        this.objectMapper = objectMapper;
    }

    public void publishBookingCreatedEvent(BookingCreatedEvent event) {
        log.info("Chuẩn bị phát hành sự kiện BookingCreatedEvent (EventId: {}) vào SNS Topic: {}",
                event.getEventId(), topicArn);

        try {
            String jsonPayload = objectMapper.writeValueAsString(event);
            log.info("Nội dung JSON Event phát hành:\n{}", jsonPayload);

            String corrId = MDC.get("correlationId");
            Map<String, MessageAttributeValue> messageAttributes = new HashMap<>();
            if (corrId != null && !corrId.isBlank()) {
                messageAttributes.put("correlationId", MessageAttributeValue.builder()
                        .dataType("String")
                        .stringValue(corrId)
                        .build());
            }

            PublishRequest.Builder publishRequestBuilder = PublishRequest.builder()
                    .topicArn(topicArn)
                    .message(jsonPayload)
                    .subject("BookingCreatedEvent");

            if (!messageAttributes.isEmpty()) {
                publishRequestBuilder.messageAttributes(messageAttributes);
            }

            PublishResponse response = snsClient.publish(publishRequestBuilder.build());
            log.info("Phát hành sự kiện lên Amazon SNS thành công! MessageId: {}", response.messageId());
        } catch (Exception e) {
            log.warn("Không thể phát hành sự kiện lên SNS (tiếp tục luồng chính): {}", e.getMessage());
        }
    }
}
