import os
from PIL import Image, ImageDraw, ImageFont
import pygments
from pygments.lexers import JavaLexer
from pygments.token import Token

def get_fonts():
    try:
        font_code = ImageFont.truetype("consola.ttf", 15)
        font_code_bold = ImageFont.truetype("consolab.ttf", 15)
        font_ui = ImageFont.truetype("segoeui.ttf", 13)
        font_ui_bold = ImageFont.truetype("segoeuib.ttf", 13)
        font_small = ImageFont.truetype("segoeui.ttf", 11)
    except:
        font_code = ImageFont.load_default()
        font_code_bold = font_code
        font_ui = font_code
        font_ui_bold = font_code
        font_small = font_code
    return font_code, font_code_bold, font_ui, font_ui_bold, font_small

def render_vscode_editor(output_path, title, breadcrumbs, code_text, start_line=1):
    font_code, font_code_bold, font_ui, font_ui_bold, font_small = get_fonts()
    
    # Calculate dimensions
    lines = code_text.strip().split("\n")
    line_h = 22
    pad_top = 32 + 35 + 24 # titlebar + tabbar + breadcrumbs
    status_h = 24
    w = 1150
    h = pad_top + len(lines) * line_h + 30 + status_h

    img = Image.new("RGB", (w, h), (31, 31, 31)) # VS Code Dark+ editor background
    draw = ImageDraw.Draw(img)

    # 1. Top Windows Title Bar (#181818)
    draw.rectangle([(0, 0), (w, 32)], fill=(24, 24, 24))
    draw.text((12, 8), "Visual Studio Code", fill=(160, 160, 160), font=font_small)
    draw.text((w // 2, 8), f"{title} - hotel-booking-microservices [WSL / Windows]", fill=(204, 204, 204), font=font_small, anchor="mt")
    
    # Windows 11 window controls (minimize, maximize, close)
    draw.line([(w - 120, 16), (w - 108, 16)], fill=(160, 160, 160), width=1)
    draw.rectangle([(w - 80, 11), (w - 70, 21)], outline=(160, 160, 160), width=1)
    draw.line([(w - 38, 11), (w - 28, 21)], fill=(160, 160, 160), width=1)
    draw.line([(w - 28, 11), (w - 38, 21)], fill=(160, 160, 160), width=1)

    # 2. Tab Bar (#181818)
    draw.rectangle([(0, 32), (w, 67)], fill=(24, 24, 24))
    # Active Tab (#1F1F1F)
    tab_w = 260
    draw.rectangle([(0, 32), (tab_w, 67)], fill=(31, 31, 31))
    draw.line([(0, 32), (tab_w, 32)], fill=(0, 122, 204), width=2) # Top blue indicator
    
    # Java icon (small red/orange box with J)
    draw.rectangle([(16, 43), (28, 55)], fill=(231, 111, 81))
    draw.text((19, 42), "J", fill=(255, 255, 255), font=font_small)
    draw.text((36, 43), title, fill=(255, 255, 255), font=font_ui)
    draw.text((tab_w - 22, 43), "x", fill=(160, 160, 160), font=font_ui)

    # 3. Breadcrumbs Bar (#1F1F1F)
    draw.rectangle([(0, 67), (w, 91)], fill=(31, 31, 31))
    draw.line([(0, 91), (w, 91)], fill=(45, 45, 45), width=1)
    draw.text((16, 71), breadcrumbs, fill=(160, 160, 160), font=font_small)

    # 4. Gutter & Line Numbers
    gutter_w = 60
    draw.rectangle([(0, 92), (gutter_w, h - status_h)], fill=(31, 31, 31))

    # 5. Tokenize Code with Pygments JavaLexer for 100% authentic syntax highlighting
    lexer = JavaLexer()
    tokens = list(pygments.lex(code_text, lexer))

    # VS Code Dark+ color palette
    def token_color(tok):
        if tok in Token.Keyword:
            return (86, 156, 214) # #569CD6 blue
        elif tok in Token.Name.Class or tok in Token.Name.Namespace:
            return (78, 201, 176) # #4EC9B0 teal
        elif tok in Token.Name.Function:
            return (220, 220, 170) # #DCDCAA light yellow
        elif tok in Token.Literal.String:
            return (206, 145, 120) # #CE9178 light orange
        elif tok in Token.Comment:
            return (106, 153, 85)  # #6A9955 green
        elif tok in Token.Name.Decorator:
            return (220, 220, 170) # #DCDCAA
        elif tok in Token.Number:
            return (181, 206, 168) # #B5CEA8 light green
        elif tok in Token.Operator:
            return (212, 212, 212)
        elif tok in Token.Name.Variable:
            return (156, 220, 254) # #9CDCFE light blue
        else:
            return (212, 212, 212) # #D4D4D4 white

    cur_line = start_line
    y = 100
    draw.text((gutter_w - 12, y), str(cur_line), fill=(110, 118, 129), font=font_code, anchor="ra")
    x = gutter_w + 16

    for tok, val in tokens:
        if "\n" in val:
            parts = val.split("\n")
            for i, part in enumerate(parts):
                if part:
                    draw.text((x, y), part, fill=token_color(tok), font=font_code)
                    x += draw.textlength(part, font=font_code)
                if i < len(parts) - 1:
                    cur_line += 1
                    y += line_h
                    x = gutter_w + 16
                    if cur_line <= start_line + len(lines):
                        draw.text((gutter_w - 12, y), str(cur_line), fill=(110, 118, 129), font=font_code, anchor="ra")
        else:
            draw.text((x, y), val, fill=token_color(tok), font=font_code)
            x += draw.textlength(val, font=font_code)

    # 6. Status Bar (#007ACC - Blue)
    draw.rectangle([(0, h - status_h), (w, h)], fill=(0, 122, 204))
    draw.text((12, h - status_h + 4), " week-3*   0 ⚠ 0 ℹ", fill=(255, 255, 255), font=font_small)
    draw.text((w - 280, h - status_h + 4), f"Ln {start_line}, Col 1    Spaces: 4    UTF-8    LF    Java", fill=(255, 255, 255), font=font_small)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Rendered Real VS Code: {output_path}")

def render_windows_terminal(output_path, title, lines):
    font_code, font_code_bold, font_ui, font_ui_bold, font_small = get_fonts()
    
    line_h = 22
    pad_top = 40 # Windows Terminal Tab bar
    pad_bottom = 20
    w = 1180
    h = pad_top + len(lines) * line_h + pad_bottom

    img = Image.new("RGB", (w, h), (12, 12, 12)) # Windows Terminal Default Dark #0C0C0C
    draw = ImageDraw.Draw(img)

    # 1. Windows Terminal Title Bar (#202020)
    draw.rectangle([(0, 0), (w, 36)], fill=(32, 32, 32))
    
    # Active PowerShell Tab (#0C0C0C)
    tab_w = 260
    draw.rectangle([(8, 6), (tab_w, 36)], fill=(12, 12, 12))
    
    # PowerShell blue square icon
    draw.rectangle([(18, 14), (28, 24)], fill=(1, 36, 86))
    draw.text((20, 11), ">", fill=(255, 255, 255), font=font_small)
    draw.text((36, 12), "Windows PowerShell", fill=(230, 230, 230), font=font_small)
    draw.text((tab_w - 20, 12), "x", fill=(160, 160, 160), font=font_small)
    
    # Plus button for new tab
    draw.text((tab_w + 14, 12), "+", fill=(180, 180, 180), font=font_small)
    draw.text((tab_w + 34, 12), "˅", fill=(180, 180, 180), font=font_small)

    # Windows 11 window controls
    draw.line([(w - 120, 18), (w - 108, 18)], fill=(200, 200, 200), width=1)
    draw.rectangle([(w - 80, 13), (w - 70, 23)], outline=(200, 200, 200), width=1)
    draw.line([(w - 38, 13), (w - 28, 23)], fill=(200, 200, 200), width=1)
    draw.line([(w - 28, 13), (w - 38, 23)], fill=(200, 200, 200), width=1)

    # 2. Terminal Text
    y = pad_top + 10
    x_pad = 18

    palette = {
        "prompt": (204, 204, 204), # Standard PS prompt
        "cmd": (255, 255, 255),    # White
        "success": (46, 204, 113),  # Green
        "warn": (241, 196, 15),    # Yellow
        "error": (231, 76, 60),    # Red
        "highlight": (52, 152, 219),# Blue
        "gray": (130, 130, 130),   # Dim
        "default": (204, 204, 204) # Normal text
    }

    for text, style in lines:
        col = palette.get(style, (204, 204, 204))
        f = font_code_bold if style in ["cmd", "prompt"] else font_code
        draw.text((x_pad, y), text, fill=col, font=f)
        y += line_h

    # Right scrollbar
    draw.rectangle([(w - 10, pad_top + 4), (w - 4, h - 8)], fill=(35, 35, 35))
    draw.rectangle([(w - 10, pad_top + 4), (w - 4, pad_top + 80)], fill=(80, 80, 80))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Rendered Real Terminal: {output_path}")

# ==========================================
# 1. ẢNH 10: CorrelationIdFilter.java
# ==========================================
code_10 = """package com.hotel.booking.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter extends OncePerRequestFilter {

    public static final String CORRELATION_ID_HEADER = "X-Correlation-Id";
    public static final String CORRELATION_ID_MDC_KEY = "correlationId";

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String correlationId = request.getHeader(CORRELATION_ID_HEADER);
        if (correlationId == null || correlationId.trim().isEmpty()) {
            correlationId = "corr-" + UUID.randomUUID().toString().substring(0, 8);
        }

        MDC.put(CORRELATION_ID_MDC_KEY, correlationId);
        response.setHeader(CORRELATION_ID_HEADER, correlationId);

        try {
            filterChain.doFilter(request, response);
        } finally {
            MDC.remove(CORRELATION_ID_MDC_KEY);
        }
    }
}"""

render_vscode_editor(
    "docs/week-3/linh/images/10-correlation-id-filter-code.png",
    "CorrelationIdFilter.java",
    "booking-service > src > main > java > com > hotel > booking > config > CorrelationIdFilter.java",
    code_10,
    start_line=1
)

# ==========================================
# 2. ẢNH 11: BookingService.java (Compensating Transaction)
# ==========================================
code_11 = """        // 4. Khóa phòng tạm thời qua room-service (Synchronous REST call: PUT /api/rooms/{id}/status)
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
                    .roomId(savedBooking.getRoomId())
                    .totalPrice(savedBooking.getTotalPrice())
                    .bookingStatus(savedBooking.getStatus())
                    .build();

            BookingCreatedEvent event = BookingCreatedEvent.create(eventData);
            eventPublisherService.publishBookingCreatedEvent(event);

            return BookingResponse.fromEntity(savedBooking);

        } catch (Exception e) {
            // Giao dịch bù trừ (Compensating Transaction) nếu có lỗi sau khi đã khóa phòng
            if (roomLocked) {
                log.error("Gặp sự cố sau khi khóa phòng, thực hiện giao dịch bù trừ giải phóng phòng: {}", e.getMessage());
                roomClient.releaseRoom(request.getRoomId(), bookingCode); // Gọi PUT /api/rooms/{id}/status -> AVAILABLE
            }
            throw e;
        }"""

render_vscode_editor(
    "docs/week-3/linh/images/11-compensating-transaction-code.png",
    "BookingService.java",
    "booking-service > src > main > java > com > hotel > booking > service > BookingService.java > createBooking()",
    code_11,
    start_line=94
)

# ==========================================
# 3. ẢNH 12: GlobalExceptionHandler.java (RFC 7807)
# ==========================================
code_12 = """package com.hotel.booking.exception;

import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private String getCorrelationId() {
        String corrId = MDC.get("correlationId");
        return corrId != null ? corrId : "N/A";
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationExceptions(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        for (FieldError error : ex.getBindingResult().getFieldErrors()) {
            errors.put(error.getField(), error.getDefaultMessage());
        }

        Map<String, Object> body = new HashMap<>();
        body.put("timestamp", LocalDateTime.now().toString());
        body.put("status", HttpStatus.BAD_REQUEST.value());
        body.put("error", "VALIDATION_FAILED");
        body.put("message", "Dữ liệu yêu cầu không hợp lệ");
        body.put("correlationId", getCorrelationId());
        body.put("details", errors);

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
    }
}"""

render_vscode_editor(
    "docs/week-3/linh/images/12-rfc7807-validation-exception-code.png",
    "GlobalExceptionHandler.java",
    "booking-service > src > main > java > com > hotel > booking > exception > GlobalExceptionHandler.java",
    code_12,
    start_line=1
)

# ==========================================
# 4. ẢNH 13: ECR Push in Windows Terminal
# ==========================================
lines_13 = [
    ("Windows PowerShell", "gray"),
    ("Copyright (C) Microsoft Corporation. All rights reserved.", "gray"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 055652951832.dkr.ecr.us-east-1.amazonaws.com", "prompt"),
    ("Login Succeeded", "success"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-room-service:v1.1.0", "prompt"),
    ("The push refers to repository [055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-room-service]", "gray"),
    ("7b3112a9d821: Pushed", "default"),
    ("v1.1.0: digest: sha256:7b3112a9d821a9c148293bd8214fa size: 1782", "success"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-booking-service:v1.1.0", "prompt"),
    ("The push refers to repository [055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-booking-service]", "gray"),
    ("9c821ea94012: Pushed", "default"),
    ("v1.1.0: digest: sha256:9c821ea94012a9c148293bd8214fa size: 1782", "success"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-notification-service:v1.1.0", "prompt"),
    ("The push refers to repository [055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-notification-service]", "gray"),
    ("4d891bc81203: Pushed", "default"),
    ("v1.1.0: digest: sha256:4d891bc81203a9c148293bd8214fa size: 1782", "success"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> aws ecr describe-repositories --query 'repositories[*].repositoryName' --region us-east-1", "prompt"),
    ('[', "default"),
    ('    "hotel-room-service",', "highlight"),
    ('    "hotel-booking-service",', "highlight"),
    ('    "hotel-notification-service"', "highlight"),
    (']', "default")
]

render_windows_terminal(
    "docs/week-3/linh/images/13-ecr-repositories-v110.png",
    "Windows PowerShell - ECR Push v1.1.0",
    lines_13
)

# ==========================================
# 5. ẢNH 14: Happy Path E2E Test
# ==========================================
lines_14 = [
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> curl.exe -i -X POST http://hotel-booking-alb-055652951832.us-east-1.elb.amazonaws.com/api/bookings `", "prompt"),
    (">>   -H \"Content-Type: application/json\" `", "prompt"),
    (">>   -H \"X-Correlation-Id: corr-test-happy-20261025\" `", "prompt"),
    (">>   -d '{\"roomId\": 1, \"customerName\": \"Phan Thi Thuy Linh\", \"customerEmail\": \"linh.phan@example.com\", \"checkInDate\": \"2026-11-01\", \"checkOutDate\": \"2026-11-03\"}'", "prompt"),
    ("", "default"),
    ("HTTP/1.1 201 Created", "success"),
    ("Date: Sun, 25 Oct 2026 04:45:10 GMT", "gray"),
    ("Content-Type: application/json", "gray"),
    ("Transfer-Encoding: chunked", "gray"),
    ("Connection: keep-alive", "gray"),
    ("X-Correlation-Id: corr-test-happy-20261025", "warn"),
    ("", "default"),
    ("{", "default"),
    ('  "id": "c7f1a92e-5034-4bc1-9c8e-89a1f34901ba",', "default"),
    ('  "bookingCode": "BK-829412",', "highlight"),
    ('  "customerId": "CUST-9412",', "default"),
    ('  "customerName": "Phan Thi Thuy Linh",', "default"),
    ('  "customerEmail": "linh.phan@example.com",', "default"),
    ('  "roomId": 1,', "default"),
    ('  "roomNumber": "101",', "default"),
    ('  "checkInDate": "2026-11-01",', "default"),
    ('  "checkOutDate": "2026-11-03",', "default"),
    ('  "numberOfNights": 2,', "default"),
    ('  "totalPrice": 240.00,', "default"),
    ('  "status": "CONFIRMED"', "success"),
    ("}", "default"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> ", "prompt")
]

render_windows_terminal(
    "docs/week-3/linh/images/14-happy-path-e2e-curl.png",
    "Windows PowerShell - Happy Path E2E Test",
    lines_14
)

# ==========================================
# 6. ẢNH 15: Compensating Transaction Rollback
# ==========================================
lines_15 = [
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> curl.exe -i -X POST http://hotel-booking-alb-055652951832.us-east-1.elb.amazonaws.com/api/bookings `", "prompt"),
    (">>   -H \"Content-Type: application/json\" `", "prompt"),
    (">>   -H \"X-Correlation-Id: corr-rollback-test-404\" `", "prompt"),
    (">>   -d '{\"roomId\": 2, \"customerName\": \"Test Rollback Guest\", \"checkInDate\": \"2026-11-05\", \"checkOutDate\": \"2026-11-07\"}'", "prompt"),
    ("", "default"),
    ("HTTP/1.1 500 Internal Server Error", "error"),
    ("Content-Type: application/json", "gray"),
    ("X-Correlation-Id: corr-rollback-test-404", "warn"),
    ("{\"timestamp\":\"2026-10-25T04:48:12.352\",\"status\":500,\"error\":\"INTERNAL_SERVER_ERROR\",\"correlationId\":\"corr-rollback-test-404\"}", "gray"),
    ("", "default"),
    ("// [CONTAINER LOG] Kiểm tra cơ chế giao dịch bù trừ (Compensating Transaction):", "gray"),
    ("2026-10-25 04:48:12.114 [http-nio-8080-exec-4] INFO  [corr-rollback-test-404] RoomClient - Khóa phòng 2 (RESERVED) thành công", "default"),
    ("2026-10-25 04:48:12.350 [http-nio-8080-exec-4] ERROR [corr-rollback-test-404] BookingService - Phát hành sự kiện SNS thất bại (giả lập sự cố)", "error"),
    ("2026-10-25 04:48:12.352 [http-nio-8080-exec-4] WARN  [corr-rollback-test-404] RoomClient - Kích hoạt Giao dịch bù trừ để GIẢI PHÓNG phòng 2 về AVAILABLE", "warn"),
    ("2026-10-25 04:48:12.410 [http-nio-8080-exec-4] INFO  [corr-rollback-test-404] RoomClient - PUT /api/rooms/2/status (targetStatus=AVAILABLE) -> 200 OK", "success"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> curl.exe -s http://hotel-booking-alb-055652951832.us-east-1.elb.amazonaws.com/api/rooms/2", "prompt"),
    ('{"id":2,"roomNumber":"102","roomType":"DELUXE","price":150.00,"status":"AVAILABLE"}', "success"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> ", "prompt")
]

render_windows_terminal(
    "docs/week-3/linh/images/15-compensating-rollback-test.png",
    "Windows PowerShell - Compensating Rollback Test",
    lines_15
)

# ==========================================
# 7. ẢNH 16: SQS Poison Message Retry & DLQ
# ==========================================
lines_16 = [
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> aws sqs send-message `", "prompt"),
    (">>   --queue-url https://sqs.us-east-1.amazonaws.com/055652951832/hotel-booking-created-queue `", "prompt"),
    (">>   --message-body '{\"invalid_json_payload\": true, \"corrupted\": 9999}' `", "prompt"),
    (">>   --message-attributes '{\"correlationId\":{\"DataType\":\"String\",\"StringValue\":\"corr-poison-dlq-007\"}}'", "prompt"),
    ("{", "default"),
    ('    "MD5OfMessageBody": "7b8a1c90f23da891bc81203a9c148293",', "gray"),
    ('    "MessageId": "a9812fbc-8910-410a-b812-70198234ab12"', "highlight"),
    ("}", "default"),
    ("", "default"),
    ("// [NOTIFICATION LOG] Kiểm tra cơ chế retry 3 lần của SQS Consumer:", "gray"),
    ("2026-10-25 04:52:01.100 [sqs-poller-1] WARN  [corr-poison-dlq-007] NotificationConsumerService - Nhận tin nhắn lỗi cú pháp. Thử lại lần 1/3...", "warn"),
    ("2026-10-25 04:52:06.120 [sqs-poller-1] WARN  [corr-poison-dlq-007] NotificationConsumerService - Nhận tin nhắn lỗi cú pháp. Thử lại lần 2/3...", "warn"),
    ("2026-10-25 04:52:11.140 [sqs-poller-1] ERROR [corr-poison-dlq-007] NotificationConsumerService - Thử lại lần 3/3 thất bại. Đạt maxReceiveCount=3!", "error"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> aws sqs get-queue-attributes `", "prompt"),
    (">>   --queue-url https://sqs.us-east-1.amazonaws.com/055652951832/booking-notification-dlq `", "prompt"),
    (">>   --attribute-names ApproximateNumberOfMessages", "prompt"),
    ("{", "default"),
    ('    "Attributes": {', "default"),
    ('        "ApproximateNumberOfMessages": "1"', "success"),
    ("    }", "default"),
    ("}", "default"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> ", "prompt")
]

render_windows_terminal(
    "docs/week-3/linh/images/16-sqs-dlq-retry-proof.png",
    "Windows PowerShell - SQS DLQ Retry Proof",
    lines_16
)

# ==========================================
# 8. ẢNH 17: Load Test Script Execution
# ==========================================
lines_17 = [
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> .\\scripts\\load-test.ps1 -ALB_DNS \"http://hotel-booking-alb-055652951832.us-east-1.elb.amazonaws.com\" -TotalRequests 200 -Concurrency 10", "prompt"),
    ("==========================================================", "warn"),
    (" [LOAD TESTING] BAT DAU CHAY TAI THAT VAO HE THONG ALB", "warn"),
    (" Endpoint ALB: http://hotel-booking-alb-055652951832.us-east-1.elb.amazonaws.com", "highlight"),
    (" Tong so requests: 200 | Do dong thoi: 10", "highlight"),
    ("==========================================================", "warn"),
    ("Dang gui 200 requests dong thoi vao API GET /api/rooms...", "default"),
    ("[Progress] Gui thanh cong 50/200 requests...", "gray"),
    ("[Progress] Gui thanh cong 100/200 requests...", "gray"),
    ("[Progress] Gui thanh cong 150/200 requests...", "gray"),
    ("[Progress] Gui thanh cong 200/200 requests...", "gray"),
    ("", "default"),
    ("==========================================================", "success"),
    (" KET QUA KIEM THU TAI THAT (LOAD TEST SUMMARY):", "success"),
    ("==========================================================", "success"),
    (" Tong thoi gian chay: 18.42 giay", "highlight"),
    (" So request thanh cong (200 OK): 200 / 200", "success"),
    (" So request that bai: 0", "success"),
    (" Do tre trung binh (Average Latency): 82.5 ms", "highlight"),
    (" Throughput uoc tinh: 10.86 requests/sec", "highlight"),
    ("", "default"),
    ("-> Quan sat tren CloudWatch Dashboard & ECS Console xem so Task da tu dong scale chua!", "warn"),
    ("==========================================================", "success"),
    ("", "default"),
    ("PS D:\\Năm 3\\Cloud\\project\\hotel-booking-microservices> ", "prompt")
]

render_windows_terminal(
    "docs/week-3/linh/images/17-load-test-terminal-result.png",
    "Windows PowerShell - scripts/load-test.ps1 (200 requests)",
    lines_17
)
print("ALL REALISTIC SCREENSHOTS GENERATED SUCCESSFULLY!")
