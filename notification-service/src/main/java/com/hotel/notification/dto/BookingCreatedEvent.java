package com.hotel.notification.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonIgnoreProperties(ignoreUnknown = true)
public class BookingCreatedEvent {

    private String eventId;
    private String eventType;
    private String eventSource;
    private String eventTimestamp;
    private String schemaVersion;
    private BookingEventData data;

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class BookingEventData {
        private String bookingId;
        private String customerId;
        private String customerName;
        private String customerEmail;
        private String customerPhone;
        private Long roomId;
        private String roomNumber;

        @JsonFormat(pattern = "yyyy-MM-dd")
        private LocalDate checkInDate;

        @JsonFormat(pattern = "yyyy-MM-dd")
        private LocalDate checkOutDate;

        private long numberOfNights;
        private BigDecimal totalPrice;
        private String currency;
        private String bookingStatus;

        public String getBookingId() { return bookingId; }
        public void setBookingId(String bookingId) { this.bookingId = bookingId; }
        public String getCustomerId() { return customerId; }
        public void setCustomerId(String customerId) { this.customerId = customerId; }
        public String getCustomerName() { return customerName; }
        public void setCustomerName(String customerName) { this.customerName = customerName; }
        public String getCustomerEmail() { return customerEmail; }
        public void setCustomerEmail(String customerEmail) { this.customerEmail = customerEmail; }
        public String getCustomerPhone() { return customerPhone; }
        public void setCustomerPhone(String customerPhone) { this.customerPhone = customerPhone; }
        public Long getRoomId() { return roomId; }
        public void setRoomId(Long roomId) { this.roomId = roomId; }
        public String getRoomNumber() { return roomNumber; }
        public void setRoomNumber(String roomNumber) { this.roomNumber = roomNumber; }
        public LocalDate getCheckInDate() { return checkInDate; }
        public void setCheckInDate(LocalDate checkInDate) { this.checkInDate = checkInDate; }
        public LocalDate getCheckOutDate() { return checkOutDate; }
        public void setCheckOutDate(LocalDate checkOutDate) { this.checkOutDate = checkOutDate; }
        public long getNumberOfNights() { return numberOfNights; }
        public void setNumberOfNights(long numberOfNights) { this.numberOfNights = numberOfNights; }
        public BigDecimal getTotalPrice() { return totalPrice; }
        public void setTotalPrice(BigDecimal totalPrice) { this.totalPrice = totalPrice; }
        public String getCurrency() { return currency; }
        public void setCurrency(String currency) { this.currency = currency; }
        public String getBookingStatus() { return bookingStatus; }
        public void setBookingStatus(String bookingStatus) { this.bookingStatus = bookingStatus; }
    }

    public String getEventId() { return eventId; }
    public void setEventId(String eventId) { this.eventId = eventId; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public String getEventSource() { return eventSource; }
    public void setEventSource(String eventSource) { this.eventSource = eventSource; }
    public String getEventTimestamp() { return eventTimestamp; }
    public void setEventTimestamp(String eventTimestamp) { this.eventTimestamp = eventTimestamp; }
    public String getSchemaVersion() { return schemaVersion; }
    public void setSchemaVersion(String schemaVersion) { this.schemaVersion = schemaVersion; }
    public BookingEventData getData() { return data; }
    public void setData(BookingEventData data) { this.data = data; }
}
