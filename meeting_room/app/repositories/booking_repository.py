from pathlib import Path

from app.models.booking import Booking, BookingStatus
from app.utils.file_utils import read_json, write_json_atomic


class BookingRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def list_bookings(self, include_inactive: bool = True) -> list[Booking]:
        payload = read_json(self.file_path, default=[])
        bookings = [Booking.from_dict(item) for item in payload]
        if include_inactive:
            return bookings
        return [booking for booking in bookings if booking.status == BookingStatus.ACTIVE]

    def get_booking(self, booking_id: str) -> Booking | None:
        for booking in self.list_bookings(include_inactive=True):
            if booking.id == booking_id:
                return booking
        return None

    def save_bookings(self, bookings: list[Booking]) -> None:
        write_json_atomic(self.file_path, [booking.to_dict() for booking in bookings])
