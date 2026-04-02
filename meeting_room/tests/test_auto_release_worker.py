import asyncio
from datetime import timedelta

from app.services.auto_release_worker import AutoReleaseWorker


def test_auto_release_worker_run_once_releases_expired_bookings(tmp_path, base_now):
    booking_service, expiration_service = _build_services(tmp_path)
    booking = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now - timedelta(minutes=31),
    )
    worker = AutoReleaseWorker(expiration_service, interval_seconds=1)

    asyncio.run(worker.run_once())

    refreshed = booking_service.list_bookings()
    assert refreshed[0].id == booking.id
    assert refreshed[0].status.value == "expired"


def _build_services(tmp_path):
    from app.concurrency.lock_manager import LockManager
    from app.models.room import Room
    from app.repositories.booking_repository import BookingRepository
    from app.repositories.room_repository import RoomRepository
    from app.services import BookingService, ExpirationService

    room_repository = RoomRepository(tmp_path / "rooms.json")
    booking_repository = BookingRepository(tmp_path / "bookings.json")
    lock_manager = LockManager()
    room_repository.save_rooms([Room(id="room-a", name="A01", capacity=12, location="3F")])

    booking_service = BookingService(booking_repository, room_repository, lock_manager)
    expiration_service = ExpirationService(booking_repository, lock_manager)
    return booking_service, expiration_service
