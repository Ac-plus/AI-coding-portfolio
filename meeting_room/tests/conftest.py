from datetime import datetime, timedelta

import pytest

from app.concurrency.lock_manager import LockManager
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.services import BookingService, MetricsService, RoomService, UserService


@pytest.fixture
def sample_room() -> Room:
    return Room(id="room-a", name="A01 大会议室", capacity=12, location="3F East")


@pytest.fixture
def base_now() -> datetime:
    return datetime(2026, 4, 2, 9, 0, 0)


@pytest.fixture
def active_booking(base_now: datetime) -> Booking:
    return Booking(
        id="booking-1",
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=2),
        end_time=base_now + timedelta(hours=3),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
        expires_at=base_now + timedelta(minutes=30),
    )


@pytest.fixture
def room_service(tmp_path) -> RoomService:
    room_repository = RoomRepository(tmp_path / "rooms.json")
    room_repository.save_rooms([Room(id="room-a", name="A01", capacity=12, location="3F")])
    booking_repository = BookingRepository(tmp_path / "bookings.json")
    return RoomService(room_repository, booking_repository)


@pytest.fixture
def user_service(tmp_path) -> UserService:
    user_repository = UserRepository(tmp_path / "users.json")
    user_repository.save_users([User(id="user-1", name="Alice", team="Platform")])
    return UserService(user_repository)


@pytest.fixture
def booking_service(tmp_path) -> BookingService:
    room_repository = RoomRepository(tmp_path / "rooms.json")
    booking_repository = BookingRepository(tmp_path / "bookings.json")
    user_repository = UserRepository(tmp_path / "users.json")
    room_repository.save_rooms([Room(id="room-a", name="A01", capacity=12, location="3F")])
    user_repository.save_users(
        [
            User(id="user-1", name="Alice", team="Platform"),
            User(id="user-2", name="Bob", team="Operations"),
            User(id="user-3", name="Carol", team="Product"),
        ]
    )
    return BookingService(
        booking_repository,
        room_repository,
        LockManager(),
        user_repository=user_repository,
        metrics_service=MetricsService(),
    )
