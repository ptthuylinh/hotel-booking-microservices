package com.hotel.booking.service;

import com.hotel.booking.client.RoomClient;
import com.hotel.booking.dto.BookingCreatedEvent;
import com.hotel.booking.dto.BookingResponse;
import com.hotel.booking.dto.CreateBookingRequest;
import com.hotel.booking.dto.RoomClientResponse;
import com.hotel.booking.entity.Booking;
import com.hotel.booking.exception.BookingNotFoundException;
import com.hotel.booking.repository.BookingRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class BookingService {

    private static final Logger log = LoggerFactory.getLogger(BookingService.class);

    private final BookingRepository bookingRepository;
    private final RoomClient roomClient;
    private final AuditLogService auditLogService;
    private final EventPublisherService eventPublisherService;

    public BookingService(
            BookingRepository bookingRepository,
            RoomClient roomClient,
            AuditLogService auditLogService,
            EventPublisherService eventPublisherService) {
        this.bookingRepository = bookingRepository;
        this.roomClient = roomClient;
        this.auditLogService = auditLogService;
        this.eventPublisherService = eventPublisherService;
    }

    @Transactional(readOnly = true)
    public List<BookingResponse> getAllBookings() {
        return bookingRepository.findAll().stream().map(BookingResponse::fromEntity).toList();
    }

    @Transactional(readOnly = true)
    public BookingResponse getBookingById(String id) {
        Booking booking = bookingRepository.findById(id)
                .orElseThrow(() -> new BookingNotFoundException("Không tìm thấy đơn đặt phòng với ID: " + id));
        return BookingResponse.fromEntity(booking);
    }

    @Transactional(readOnly = true)
    public BookingResponse getBookingByCode(String code) {
        Booking booking = bookingRepository.findByBookingCode(code)
                .orElseThrow(() -> new BookingNotFoundException("Không tìm thấy đơn đặt phòng với mã: " + code));
        return BookingResponse.fromEntity(booking);
    }

    @Transactional
    public BookingResponse createBooking(CreateBookingRequest request) {
        log.info("Tiếp nhận yêu cầu tạo đơn đặt phòng mới cho khách: {} (Phòng: {})",
                request.getCustomerName(), request.getRoomId());

        // 1. Kiểm tra tính hợp lệ của ngày đặt
        LocalDate checkIn = request.getCheckInDate() != null ? request.getCheckInDate() : LocalDate.now();
        LocalDate checkOut = request.getCheckOutDate() != null ? request.getCheckOutDate() : checkIn.plusDays(1);

        if (!checkOut.isAfter(checkIn)) {
            throw new IllegalArgumentException("Ngày trả phòng (checkOutDate) phải sau ngày nhận phòng (checkInDate)");
        }

        long numberOfNights = ChronoUnit.DAYS.between(checkIn, checkOut);
        if (numberOfNights <= 0) {
            numberOfNights = 1;
        }

        String bookingId = UUID.randomUUID().toString();
        String bookingCode = "BK-" + System.currentTimeMillis() % 1000000;

        // 2. Tra cứu thông tin phòng từ room-service (REST nội bộ)
        RoomClientResponse room = roomClient.getRoom(request.getRoomId());

        // 3. Tính toán tổng tiền nếu chưa có
        BigDecimal totalPrice = request.getTotalPrice();
        if (totalPrice == null || totalPrice.compareTo(BigDecimal.ZERO) <= 0) {
            BigDecimal pricePerNight = room.resolvePrice() != null ? room.resolvePrice() : new BigDecimal("100.00");
            totalPrice = pricePerNight.multiply(BigDecimal.valueOf(numberOfNights));
        }

        // 4. Khóa phòng tạm thời qua room-service (Synchronous REST call: PUT /api/rooms/{id}/status)
        boolean roomLocked = false;
        try {
            roomClient.reserveRoom(request.getRoomId(), bookingCode);
            roomLocked = true;

            // 5. Lưu bản ghi Booking vào PostgreSQL booking_db với trạng thái CONFIRMED
            Booking booking = new Booking();
            booking.setId(bookingId);
            booking.setBookingCode(bookingCode);
            booking.setCustomerId(request.getCustomerId() != null ? request.getCustomerId() : "CUST-" + (System.currentTimeMillis() % 10000));
            booking.setCustomerName(request.getCustomerName() != null ? request.getCustomerName() : "Khách hàng");
            booking.setCustomerEmail(request.getCustomerEmail() != null ? request.getCustomerEmail() : "guest@example.com");
            booking.setCustomerPhone(request.getCustomerPhone());
            booking.setRoomId(request.getRoomId());
            booking.setCheckInDate(checkIn);
            booking.setCheckOutDate(checkOut);
            booking.setTotalPrice(totalPrice);
            booking.setStatus("CONFIRMED");

            Booking savedBooking = bookingRepository.save(booking);
            log.info("Lưu đơn đặt phòng thành công vào booking_db: ID={}, Code={}", savedBooking.getId(), savedBooking.getBookingCode());

            // 6. Ghi nhật ký kiểm toán (Audit Trail) vào DynamoDB
            auditLogService.recordAuditLog(
                    savedBooking.getBookingCode(),
                    "BOOKING_CREATED",
                    "PENDING",
                    "CONFIRMED",
                    Map.of(
                            "roomId", String.valueOf(savedBooking.getRoomId()),
                            "totalPrice", savedBooking.getTotalPrice().toString(),
                            "customerEmail", savedBooking.getCustomerEmail()
                    )
            );

            // 7. Phát hành sự kiện BookingCreatedEvent lên Amazon SNS Topic
            BookingCreatedEvent.BookingEventData eventData = BookingCreatedEvent.BookingEventData.builder()
                    .bookingId(savedBooking.getBookingCode())
                    .customerId(savedBooking.getCustomerId())
                    .customerName(savedBooking.getCustomerName())
                    .customerEmail(savedBooking.getCustomerEmail())
                    .customerPhone(savedBooking.getCustomerPhone())
                    .roomId(savedBooking.getRoomId())
                    .roomNumber(room.resolveRoomNumber())
                    .checkInDate(savedBooking.getCheckInDate())
                    .checkOutDate(savedBooking.getCheckOutDate())
                    .numberOfNights(numberOfNights)
                    .totalPrice(savedBooking.getTotalPrice())
                    .currency("USD")
                    .bookingStatus(savedBooking.getStatus())
                    .build();

            BookingCreatedEvent event = BookingCreatedEvent.create(eventData);
            eventPublisherService.publishBookingCreatedEvent(event);

            return BookingResponse.fromEntity(savedBooking);

        } catch (Exception e) {
            // Giao dịch bù trừ (Compensating Transaction) nếu có lỗi sau khi đã khóa phòng
            if (roomLocked) {
                log.error("Gặp sự cố sau khi khóa phòng, thực hiện giao dịch bù trừ giải phóng phòng: {}", e.getMessage());
                roomClient.releaseRoom(request.getRoomId(), bookingCode);
            }
            throw e;
        }
    }
}
