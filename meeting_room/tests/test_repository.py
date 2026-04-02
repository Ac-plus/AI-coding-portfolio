from datetime import timedelta

from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository


def test_room_repository_round_trip(tmp_path):
    repo = RoomRepository(tmp_path / "rooms.json")
    rooms = [Room(id="room-a", name="A01", capacity=12, location="3F East")]

    repo.save_rooms(rooms)

    restored = repo.list_rooms()
    assert restored == rooms


def test_booking_repository_filters_inactive_records(tmp_path, base_now):
    repo = BookingRepository(tmp_path / "bookings.json")
    active = Booking(
        id="booking-active",
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
    )
    cancelled = Booking(
        id="booking-cancelled",
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=3),
        end_time=base_now + timedelta(hours=4),
        status=BookingStatus.CANCELLED,
        created_at=base_now,
    )

    repo.save_bookings([active, cancelled])

    restored = repo.list_bookings(include_inactive=False)
    assert restored == [active]
