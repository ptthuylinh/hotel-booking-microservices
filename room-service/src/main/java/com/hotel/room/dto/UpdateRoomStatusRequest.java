package com.hotel.room.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateRoomStatusRequest {

    @JsonAlias({"targetStatus"})
    private String status;

    @JsonAlias({"bookingReference"})
    private String bookingId;

    private String reason;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getBookingId() {
        return bookingId;
    }

    public void setBookingId(String bookingId) {
        this.bookingId = bookingId;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public String resolveStatus() {
        return status != null ? status.trim().toUpperCase() : null;
    }
}
