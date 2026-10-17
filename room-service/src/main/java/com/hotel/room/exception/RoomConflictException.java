package com.hotel.room.exception;

public class RoomConflictException extends RuntimeException {
    public RoomConflictException(String message) {
        super(message);
    }
}
