from app.config import AUTO_RELEASE_INTERVAL_SECONDS, BOOKINGS_FILE, ROOMS_FILE
from app.concurrency.lock_manager import LockManager
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.services import AutoReleaseWorker, BookingService, ExpirationService, RoomService


_lock_manager = LockManager()
_room_repository = RoomRepository(ROOMS_FILE)
_booking_repository = BookingRepository(BOOKINGS_FILE)
_room_service = RoomService(_room_repository)
_booking_service = BookingService(_booking_repository, _room_repository, _lock_manager)
_expiration_service = ExpirationService(_booking_repository, _lock_manager)
_auto_release_worker = AutoReleaseWorker(_expiration_service, AUTO_RELEASE_INTERVAL_SECONDS)


def get_room_service() -> RoomService:
    return _room_service


def get_booking_service() -> BookingService:
    return _booking_service


def get_expiration_service() -> ExpirationService:
    return _expiration_service


def get_auto_release_worker() -> AutoReleaseWorker:
    return _auto_release_worker
