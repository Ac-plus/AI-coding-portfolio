import logging
from datetime import datetime

from app.concurrency.lock_manager import LockManager
from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository
from app.rules.expiration_rule import is_booking_expired
from app.services.metrics_service import MetricsService
from app.utils.time_utils import utc_now


class ExpirationService:
    def __init__(
        self,
        booking_repository: BookingRepository,
        lock_manager: LockManager,
        metrics_service: MetricsService | None = None,
    ) -> None:
        self.booking_repository = booking_repository
        self.lock_manager = lock_manager
        self.metrics_service = metrics_service
        self.logger = logging.getLogger("meeting_room.expiration")

    def release_expired_bookings(self, now: datetime | None = None) -> list[Booking]:
        effective_now = now or utc_now()

        with self.lock_manager.acquire_resources(["file:bookings"], timeout=2):
            bookings = self.booking_repository.list_bookings(include_inactive=True)
            released: list[Booking] = []

            for booking in bookings:
                if is_booking_expired(booking, effective_now):
                    booking.status = BookingStatus.EXPIRED
                    released.append(booking)
                    self.logger.info(
                        "auto_release booking_id=%s room_id=%s user_id=%s reason=expired_over_30_minutes",
                        booking.id,
                        booking.room_id,
                        booking.user_id,
                    )

            if released:
                self.booking_repository.save_bookings(bookings)
                if self.metrics_service is not None:
                    self.metrics_service.increment("auto_release.triggered", len(released))

            return released
