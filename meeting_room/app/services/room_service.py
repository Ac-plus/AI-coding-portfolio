from datetime import datetime

from app.concurrency.conflict_checker import time_ranges_overlap
from app.models.booking import BookingStatus
from app.models.room import Room
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository


class RoomService:
    def __init__(
        self,
        room_repository: RoomRepository,
        booking_repository: BookingRepository | None = None,
    ) -> None:
        self.room_repository = room_repository
        self.booking_repository = booking_repository

    def list_rooms(self) -> list[Room]:
        return self.room_repository.list_rooms()

    def get_occupancy_status(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict]:
        bookings = []
        if self.booking_repository is not None:
            bookings = self.booking_repository.list_bookings(include_inactive=False)

        occupancy_items = []
        for room in self.room_repository.list_rooms():
            conflicting_booking_ids = [
                booking.id
                for booking in bookings
                if booking.status == BookingStatus.ACTIVE
                and booking.room_id == room.id
                and time_ranges_overlap(start_time, end_time, booking.start_time, booking.end_time)
            ]
            occupancy_items.append(
                {
                    "room_id": room.id,
                    "room_name": room.name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "occupied": bool(conflicting_booking_ids),
                    "conflicting_booking_ids": conflicting_booking_ids,
                }
            )
        return occupancy_items
