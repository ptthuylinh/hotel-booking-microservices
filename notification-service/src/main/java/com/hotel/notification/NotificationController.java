package com.hotel.notification;

import com.hotel.notification.dto.NotificationRecord;
import com.hotel.notification.service.NotificationConsumerService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/notifications")
public class NotificationController {

    private final NotificationConsumerService notificationConsumerService;

    public NotificationController(NotificationConsumerService notificationConsumerService) {
        this.notificationConsumerService = notificationConsumerService;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getNotifications() {
        List<NotificationRecord> history = notificationConsumerService.getNotificationHistory();
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "notification-service",
                "totalSent", history.size(),
                "notifications", history
        ));
    }
}
