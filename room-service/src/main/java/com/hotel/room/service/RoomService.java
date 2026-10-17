package com.hotel.room.service;

import com.hotel.room.dto.RoomResponse;
import com.hotel.room.dto.UpdateRoomStatusRequest;
import com.hotel.room.entity.Room;
import com.hotel.room.exception.RoomConflictException;
import com.hotel.room.exception.RoomNotFoundException;
import com.hotel.room.repository.RoomRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class RoomService {

    private static final Logger log = LoggerFactory.getLogger(RoomService.class);

    private final RoomRepository roomRepository;

    public RoomService(RoomRepository roomRepository) {
        this.roomRepository = roomRepository;
    }

    @Transactional(readOnly = true)
    public List<RoomResponse> getAllRooms(String status) {
        List<Room> rooms;
        if (status != null && !status.isBlank()) {
            rooms = roomRepository.findByStatusIgnoreCase(status.trim());
        } else {
            rooms = roomRepository.findAll();
        }
        return rooms.stream().map(RoomResponse::fromEntity).toList();
    }

    @Transactional(readOnly = true)
    public RoomResponse getRoomById(Long id) {
        Room room = roomRepository.findById(id)
                .orElseThrow(() -> new RoomNotFoundException(id));
        return RoomResponse.fromEntity(room);
    }

    @Transactional
    public RoomResponse updateRoomStatus(Long id, UpdateRoomStatusRequest request) {
        Room room = roomRepository.findById(id)
                .orElseThrow(() -> new RoomNotFoundException(id));

        String targetStatus = request.resolveStatus();
        if (targetStatus == null || targetStatus.isBlank()) {
            throw new IllegalArgumentException("Trạng thái (status/targetStatus) không được để trống");
        }

        log.info("Yêu cầu đổi trạng thái phòng ID {} từ {} sang {} (BookingId: {})",
                id, room.getStatus(), targetStatus, request.getBookingId());

        // Nếu muốn khóa phòng (RESERVED) mà phòng không còn AVAILABLE -> Báo lỗi 409 CONFLICT
        if ("RESERVED".equalsIgnoreCase(targetStatus) && !"AVAILABLE".equalsIgnoreCase(room.getStatus())) {
            log.warn("Phòng ID {} không khả dụng để đặt (Hiện tại: {})", id, room.getStatus());
            throw new RoomConflictException("Phòng " + room.getRoomNumber() + " hiện tại không khả dụng (" + room.getStatus() + ")");
        }

        room.setStatus(targetStatus);
        Room updated = roomRepository.save(room);
        log.info("Cập nhật thành công trạng thái phòng ID {} sang {}", id, updated.getStatus());

        return RoomResponse.fromEntity(updated);
    }
}
