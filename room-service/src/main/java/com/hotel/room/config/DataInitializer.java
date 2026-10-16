package com.hotel.room.config;

import com.hotel.room.entity.Room;
import com.hotel.room.repository.RoomRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    private final RoomRepository roomRepository;

    public DataInitializer(RoomRepository roomRepository) {
        this.roomRepository = roomRepository;
    }

    @Override
    public void run(String... args) {
        if (roomRepository.count() == 0) {
            log.info("Bắt đầu khởi tạo dữ liệu mẫu cho bảng rooms...");

            Room r1 = new Room();
            r1.setRoomNumber("A-101");
            r1.setType("DELUXE");
            r1.setPricePerNight(new BigDecimal("120.00"));
            r1.setStatus("AVAILABLE");
            r1.setDescription("Phòng Deluxe 1 giường đôi lớn, ban công ngắm biển, đầy đủ tiện nghi");

            Room r2 = new Room();
            r2.setRoomNumber("A-102");
            r2.setType("SINGLE");
            r2.setPricePerNight(new BigDecimal("60.00"));
            r2.setStatus("AVAILABLE");
            r2.setDescription("Phòng đơn tiện nghi dành cho 1 người, view thành phố");

            Room r3 = new Room();
            r3.setRoomNumber("B-201");
            r3.setType("DOUBLE");
            r3.setPricePerNight(new BigDecimal("90.00"));
            r3.setStatus("AVAILABLE");
            r3.setDescription("Phòng 2 giường đơn hoặc 1 giường đôi, thích hợp cho gia đình nhỏ");

            Room r4 = new Room();
            r4.setRoomNumber("B-202");
            r4.setType("SUITE");
            r4.setPricePerNight(new BigDecimal("250.00"));
            r4.setStatus("AVAILABLE");
            r4.setDescription("Phòng Suite cao cấp có phòng khách riêng biệt, bồn tắm sục jacuzzi");

            List<Room> sampleRooms = List.of(r1, r2, r3, r4);
            roomRepository.saveAll(sampleRooms);
            log.info("Đã khởi tạo thành công {} phòng mẫu vào cơ sở dữ liệu.", sampleRooms.size());
        }
    }
}
