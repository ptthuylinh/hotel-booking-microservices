package com.hotel.booking.client;

import com.hotel.booking.dto.RoomClientResponse;
import com.hotel.booking.exception.RoomNotAvailableException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.util.Map;

@Component
public class RoomClient {

    private static final Logger log = LoggerFactory.getLogger(RoomClient.class);

    private final RestClient restClient;

    public RoomClient(
            @Value("${room.service.url:http://room-service.hotel.local:8080}") String roomServiceUrl) {
        log.info("Khởi tạo RoomClient kết nối tới room-service tại URL: {}", roomServiceUrl);

        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout((int) Duration.ofMillis(3000).toMillis());
        requestFactory.setReadTimeout((int) Duration.ofMillis(5000).toMillis());

        this.restClient = RestClient.builder()
                .baseUrl(roomServiceUrl)
                .requestFactory(requestFactory)
                .build();
    }

    public RoomClientResponse getRoom(Long roomId) {
        log.info("Gọi nội bộ GET /api/rooms/{}", roomId);
        try {
            return restClient.get()
                    .uri("/api/rooms/{id}", roomId)
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .onStatus(HttpStatusCode::is4xxClientError, (req, resp) -> {
                        throw new RoomNotAvailableException("Không tìm thấy thông tin phòng ID: " + roomId);
                    })
                    .body(RoomClientResponse.class);
        } catch (RoomNotAvailableException e) {
            throw e;
        } catch (Exception e) {
            log.error("Lỗi khi gọi sang room-service: {}", e.getMessage());
            throw new RuntimeException("Không thể kết nối tới room-service: " + e.getMessage(), e);
        }
    }

    public RoomClientResponse reserveRoom(Long roomId, String bookingCode) {
        log.info("Gọi nội bộ PUT /api/rooms/{}/status để KHÓA phòng RESERVED (Booking: {})", roomId, bookingCode);
        try {
            return restClient.put()
                    .uri("/api/rooms/{id}/status", roomId)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of(
                            "targetStatus", "RESERVED",
                            "bookingReference", bookingCode,
                            "reason", "Lock room for pending customer booking"
                    ))
                    .retrieve()
                    .onStatus(status -> status.value() == 409, (req, resp) -> {
                        throw new RoomNotAvailableException("Phòng ID " + roomId + " đã có người đặt hoặc không khả dụng (409 Conflict)");
                    })
                    .body(RoomClientResponse.class);
        } catch (RoomNotAvailableException e) {
            throw e;
        } catch (Exception e) {
            log.error("Lỗi khi khóa phòng qua room-service: {}", e.getMessage());
            throw new RuntimeException("Lỗi giao tiếp với room-service: " + e.getMessage(), e);
        }
    }

    public void releaseRoom(Long roomId, String bookingCode) {
        log.warn("Kích hoạt Giao dịch bù trừ (Compensating Transaction) để GIẢI PHÓNG phòng {} về AVAILABLE", roomId);
        try {
            restClient.put()
                    .uri("/api/rooms/{id}/status", roomId)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of(
                            "targetStatus", "AVAILABLE",
                            "bookingReference", bookingCode,
                            "reason", "Compensating transaction - rollback room status"
                    ))
                    .retrieve()
                    .toBodilessEntity();
            log.info("Giải phóng phòng {} thành công.", roomId);
        } catch (Exception e) {
            log.error("Không thể giải phóng phòng {} trong giao dịch bù trừ: {}", roomId, e.getMessage());
        }
    }
}
