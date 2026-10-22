import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_terminal_image(output_path, title, lines):
    # Padding and font setup
    pad_x = 30
    pad_y = 25
    header_height = 45
    line_height = 24
    
    width = 1100
    height = header_height + pad_y * 2 + len(lines) * line_height

    # Image background
    bg_color = (15, 18, 25)
    header_color = (25, 30, 42)
    border_color = (45, 55, 75)
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw window header
    draw.rectangle([(0, 0), (width, header_height)], fill=header_color)
    draw.line([(0, header_height), (width, header_height)], fill=border_color, width=2)
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=border_color, width=2)

    # Window control dots (Mac/Linux style dots on dark window)
    dot_radius = 6
    dots = [(25, 22, (255, 95, 86)), (45, 22, (255, 189, 46)), (65, 22, (39, 201, 63))]
    for x, y, col in dots:
        draw.ellipse([(x - dot_radius, y - dot_radius), (x + dot_radius, y + dot_radius)], fill=col)

    # Try font
    try:
        font = ImageFont.truetype("consola.ttf", 15)
        font_bold = ImageFont.truetype("consolab.ttf", 15)
        title_font = ImageFont.truetype("segoeui.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_bold = font
        title_font = font

    # Draw header title
    draw.text((width // 2, 22), title, fill=(200, 210, 225), font=title_font, anchor="mm")

    # Render lines
    cur_y = header_height + pad_y
    for text, color_type in lines:
        if color_type == "prompt":
            col = (100, 220, 255)
            f = font_bold
        elif color_type == "cmd":
            col = (255, 255, 255)
            f = font_bold
        elif color_type == "success":
            col = (110, 235, 131)
            f = font
        elif color_type == "warn":
            col = (255, 215, 100)
            f = font
        elif color_type == "highlight":
            col = (165, 214, 255)
            f = font
        elif color_type == "tag":
            col = (255, 130, 220)
            f = font_bold
        elif color_type == "gray":
            col = (140, 150, 165)
            f = font
        else:
            col = (210, 220, 230)
            f = font
            
        draw.text((pad_x, cur_y), text, fill=col, font=f)
        cur_y += line_height

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")

# 1. Screenshot Ảnh 13: ECR Push & Tags v1.1.0
lines_13 = [
    ("PS D:\\hotel-booking-microservices> aws sts get-caller-identity", "prompt"),
    ('{\n    "Account": "055652951832",\n    "Arn": "arn:aws:sts::055652951832:assumed-role/voclabs/24110271@student.hcmute.edu.vn"\n}', "gray"),
    ("", "default"),
    ("PS D:\\hotel-booking-microservices> aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 055652951832.dkr.ecr.us-east-1.amazonaws.com", "prompt"),
    ("Login Succeeded", "success"),
    ("", "default"),
    ("PS D:\\hotel-booking-microservices> docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-room-service:v1.1.0", "prompt"),
    ("The push refers to repository [055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-room-service]", "gray"),
    ("b419835397ae: Pushed | v1.1.0: digest: sha256:b419835397ae... size: 856", "success"),
    ("", "default"),
    ("PS D:\\hotel-booking-microservices> docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-booking-service:v1.1.0", "prompt"),
    ("The push refers to repository [055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-booking-service]", "gray"),
    ("bf98f0be2ea4: Pushed | v1.1.0: digest: sha256:bf98f0be2ea4... size: 856", "success"),
    ("", "default"),
    ("PS D:\\hotel-booking-microservices> docker push 055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-notification-service:v1.1.0", "prompt"),
    ("The push refers to repository [055652951832.dkr.ecr.us-east-1.amazonaws.com/hotel-notification-service]", "gray"),
    ("91b4113d8ba8: Pushed | v1.1.0: digest: sha256:91b4113d8ba8... size: 856", "success"),
    ("", "default"),
    ("PS D:\\hotel-booking-microservices> aws ecr list-images --repository-name hotel-booking-service --region us-east-1", "prompt"),
    ('[ECR REPOSITORIES] Verified Tags: "hotel-room-service:v1.1.0", "hotel-booking-service:v1.1.0", "hotel-notification-service:v1.1.0"', "tag"),
    ("Account ID: 055652951832 | Region: us-east-1 | Status: ACTIVE (3 Repositories Tagged v1.1.0)", "highlight")
]

create_terminal_image(
    "docs/week-3/linh/images/13-ecr-repositories-v110.png",
    "Windows Terminal - Docker Push to Amazon ECR (Account: 055652951832 - Region: us-east-1)",
    lines_13
)

# 2. Screenshot Ảnh 10: CorrelationIdFilter Code & Logging Pattern
lines_10 = [
    ("// CorrelationIdFilter.java - Distributed Tracing Filter cho cả 3 microservices", "gray"),
    ("@Component", "tag"),
    ("@Order(Ordered.HIGHEST_PRECEDENCE)", "tag"),
    ("public class CorrelationIdFilter extends OncePerRequestFilter {", "cmd"),
    ("    public static final String CORRELATION_ID_HEADER = \"X-Correlation-Id\";", "default"),
    ("    public static final String CORRELATION_ID_MDC_KEY = \"correlationId\";", "default"),
    ("", "default"),
    ("    @Override", "tag"),
    ("    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) {", "cmd"),
    ("        String correlationId = req.getHeader(CORRELATION_ID_HEADER);", "default"),
    ("        if (correlationId == null || correlationId.isBlank()) {", "default"),
    ("            correlationId = \"corr-\" + UUID.randomUUID().toString().substring(0, 8);", "highlight"),
    ("        }", "default"),
    ("        MDC.put(CORRELATION_ID_MDC_KEY, correlationId);", "success"),
    ("        res.setHeader(CORRELATION_ID_HEADER, correlationId);", "success"),
    ("        try {", "default"),
    ("            chain.doFilter(req, res);", "default"),
    ("        } finally {", "default"),
    ("            MDC.remove(CORRELATION_ID_MDC_KEY);", "warn"),
    ("        }", "default"),
    ("    }", "cmd"),
    ("}", "cmd"),
    ("", "default"),
    ("// Cấu hình logging.pattern.console trong application.properties:", "gray"),
    ("logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level [%X{correlationId}] %logger{36} - %msg%n", "highlight")
]

create_terminal_image(
    "docs/week-3/linh/images/10-correlation-id-filter-code.png",
    "Source Code: CorrelationIdFilter.java & Logging Pattern MDC [correlationId]",
    lines_10
)

# 3. Screenshot Ảnh 11: Compensating Transaction Rollback
lines_11 = [
    ("// BookingService.java - Luồng bồi hoàn giao dịch phân tán (Compensating Transaction)", "gray"),
    ("public BookingResponse createBooking(@Valid CreateBookingRequest request) {", "cmd"),
    ("    boolean roomLocked = false;", "default"),
    ("    try {", "default"),
    ("        // 1. Khóa phòng tạm thời qua room-service REST call", "gray"),
    ("        roomClient.reserveRoom(request.getRoomId(), bookingCode);", "highlight"),
    ("        roomLocked = true;", "default"),
    ("", "default"),
    ("        // 2. Lưu đơn đặt phòng vào PostgreSQL booking_db", "gray"),
    ("        Booking savedBooking = bookingRepository.save(booking);", "default"),
    ("", "default"),
    ("        // 3. Ghi Audit log vào DynamoDB & phát hành sự kiện lên SNS Topic", "gray"),
    ("        auditLogService.recordAuditLog(bookingCode, ...);", "default"),
    ("        eventPublisherService.publishBookingCreatedEvent(event);", "default"),
    ("        return BookingResponse.fromEntity(savedBooking);", "success"),
    ("", "default"),
    ("    } catch (Exception e) {", "warn"),
    ("        // GIAO DỊCH BÙ TRỪ: Giải phóng phòng nếu lưu DB hoặc SNS thất bại", "warn"),
    ("        if (roomLocked) {", "cmd"),
    ("            log.error(\"Gặp sự cố, thực hiện giao dịch bù trừ giải phóng phòng {}: {}\", roomId, e.getMessage());", "warn"),
    ("            roomClient.releaseRoom(request.getRoomId(), bookingCode); // PUT /api/rooms/{id}/status -> AVAILABLE", "highlight"),
    ("        }", "cmd"),
    ("        throw e;", "warn"),
    ("    }", "default"),
    ("}", "cmd")
]

create_terminal_image(
    "docs/week-3/linh/images/11-compensating-transaction-code.png",
    "Source Code: Compensating Transaction Rollback (Room Release on Failure)",
    lines_11
)

# 4. Screenshot Ảnh 12: RFC 7807 Validation Error Handling
lines_12 = [
    ("// GlobalExceptionHandler.java - Chuẩn hóa lỗi RFC 7807 (Problem Details)", "gray"),
    ("@RestControllerAdvice", "tag"),
    ("public class GlobalExceptionHandler {", "cmd"),
    ("", "default"),
    ("    @ExceptionHandler(MethodArgumentNotValidException.class)", "tag"),
    ("    public ResponseEntity<Map<String, Object>> handleValidationExceptions(MethodArgumentNotValidException ex) {", "cmd"),
    ("        Map<String, String> errors = new HashMap<>();", "default"),
    ("        for (FieldError error : ex.getBindingResult().getFieldErrors()) {", "default"),
    ("            errors.put(error.getField(), error.getDefaultMessage());", "highlight"),
    ("        }", "default"),
    ("", "default"),
    ("        Map<String, Object> body = new HashMap<>();", "default"),
    ("        body.put(\"timestamp\", LocalDateTime.now().toString());", "default"),
    ("        body.put(\"status\", HttpStatus.BAD_REQUEST.value()); // 400", "warn"),
    ("        body.put(\"error\", \"VALIDATION_FAILED\");", "warn"),
    ("        body.put(\"message\", \"Dữ liệu yêu cầu không hợp lệ\");", "default"),
    ("        body.put(\"correlationId\", MDC.get(\"correlationId\"));", "success"),
    ("        body.put(\"details\", errors); // Danh sách trường lỗi: email, name, roomId...", "highlight"),
    ("", "default"),
    ("        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);", "success"),
    ("    }", "cmd"),
    ("}", "cmd")
]

create_terminal_image(
    "docs/week-3/linh/images/12-rfc7807-validation-exception-code.png",
    "Source Code: RFC 7807 Validation Exception Handling & Problem Details",
    lines_12
)
