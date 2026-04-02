from app.config import AUTO_RELEASE_INTERVAL_SECONDS, BOOKINGS_FILE, ROOMS_FILE, USERS_FILE
from app.concurrency.lock_manager import LockManager
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.services import (
    AutoReleaseWorker,
    BookingService,
    ExpirationService,
    MetricsService,
    RoomService,
    UserService,
)


_lock_manager = LockManager()
_room_repository = RoomRepository(ROOMS_FILE)
_booking_repository = BookingRepository(BOOKINGS_FILE)
_user_repository = UserRepository(USERS_FILE)
_metrics_service = MetricsService()
_room_service = RoomService(_room_repository, _booking_repository)
_booking_service = BookingService(
    _booking_repository,
    _room_repository,
    _lock_manager,
    user_repository=_user_repository,
    metrics_service=_metrics_service,
)
_expiration_service = ExpirationService(_booking_repository, _lock_manager, metrics_service=_metrics_service)
_user_service = UserService(_user_repository)
_auto_release_worker = AutoReleaseWorker(_expiration_service, AUTO_RELEASE_INTERVAL_SECONDS)


def get_room_service() -> RoomService:
    return _room_service


def get_booking_service() -> BookingService:
    return _booking_service


def get_expiration_service() -> ExpirationService:
    return _expiration_service


def get_user_service() -> UserService:
    return _user_service


def get_metrics_service() -> MetricsService:
    return _metrics_service


def get_auto_release_worker() -> AutoReleaseWorker:
    return _auto_release_worker
