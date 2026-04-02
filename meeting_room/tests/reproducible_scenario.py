import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from app.concurrency.lock_manager import LockManager
from app.models.room import Room
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.services import BookingConflictError, BookingService, MetricsService, RoomService


def run_scenario() -> dict:
    tmpdir = Path(tempfile.mkdtemp())
    room_repository = RoomRepository(tmpdir / "rooms.json")
    booking_repository = BookingRepository(tmpdir / "bookings.json")
    user_repository = UserRepository(tmpdir / "users.json")
    metrics_service = MetricsService()

    room_repository.save_rooms(
        [
            Room(id="room-a", name="A01", capacity=12, location="3F"),
            Room(id="room-b", name="B01", capacity=8, location="5F"),
        ]
    )
    user_repository.save_users(
        [
            User(id="user-1", name="Alice", team="Platform"),
            User(id="user-2", name="Bob", team="Operations"),
        ]
    )

    booking_service = BookingService(
        booking_repository,
        room_repository,
        LockManager(),
        user_repository=user_repository,
        metrics_service=metrics_service,
    )
    room_service = RoomService(room_repository, booking_repository)

    now = datetime(2026, 4, 2, 9, 0, 0)
    first = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=now + timedelta(hours=2),
        end_time=now + timedelta(hours=3),
        now=now,
    )

    try:
        booking_service.create_booking(
            room_id="room-a",
            user_id="user-2",
            start_time=now + timedelta(hours=2, minutes=30),
            end_time=now + timedelta(hours=3, minutes=30),
            now=now,
        )
        conflict_result = "unexpected_success"
    except BookingConflictError:
        conflict_result = "conflict_rejected"

    occupancy = room_service.get_occupancy_status(
        start_time=now + timedelta(hours=2, minutes=15),
        end_time=now + timedelta(hours=2, minutes=45),
    )
    snapshot = metrics_service.snapshot()

    return {
        "created_booking_room": first.room_id,
        "created_booking_user": first.user_id,
        "conflict_result": conflict_result,
        "occupancy_room_a": next(item for item in occupancy if item["room_id"] == "room-a")["occupied"],
        "metrics": snapshot,
    }


if __name__ == "__main__":
    print(json.dumps(run_scenario(), ensure_ascii=False, sort_keys=True, indent=2))
