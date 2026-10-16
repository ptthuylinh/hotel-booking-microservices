package com.hotel.room.exception;

public class RoomNotFoundException extends RuntimeException {
    public RoomNotFoundException(String message) {
        super(message);
    }

    public RoomNotFoundException(Long id) {
        super("Không tìm thấy phòng với ID: " + id);
    }
}
