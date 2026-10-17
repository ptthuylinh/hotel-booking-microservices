package com.hotel.room;

import com.hotel.room.dto.RoomResponse;
import com.hotel.room.dto.UpdateRoomStatusRequest;
import com.hotel.room.service.RoomService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rooms")
public class RoomController {

    private final RoomService roomService;

    public RoomController(RoomService roomService) {
        this.roomService = roomService;
    }

    @GetMapping
    public ResponseEntity<List<RoomResponse>> list(@RequestParam(required = false) String status) {
        return ResponseEntity.ok(roomService.getAllRooms(status));
    }

    @GetMapping("/{id}")
    public ResponseEntity<RoomResponse> getById(@PathVariable Long id) {
        return ResponseEntity.ok(roomService.getRoomById(id));
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<RoomResponse> updateStatus(
            @PathVariable Long id,
            @RequestBody UpdateRoomStatusRequest request) {
        return ResponseEntity.ok(roomService.updateRoomStatus(id, request));
    }
}
