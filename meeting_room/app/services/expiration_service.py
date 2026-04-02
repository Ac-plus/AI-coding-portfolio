from datetime import datetime

from app.concurrency.lock_manager import LockManager
from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository
from app.rules.expiration_rule import is_booking_expired
from app.utils.time_utils import utc_now


class ExpirationService:
    def __init__(
        self,
        booking_repository: BookingRepository,
        lock_manager: LockManager,
    ) -> None:
        self.booking_repository = booking_repository
        self.lock_manager = lock_manager

    def release_expired_bookings(self, now: datetime | None = None) -> list[Booking]:
        effective_now = now or utc_now()

        with self.lock_manager.acquire_resources(["file:bookings"], timeout=2):
            bookings = self.booking_repository.list_bookings(include_inactive=True)
            released: list[Booking] = []

            for booking in bookings:
                if is_booking_expired(booking, effective_now):
                    booking.status = BookingStatus.EXPIRED
                    released.append(booking)

            if released:
                self.booking_repository.save_bookings(bookings)

            return released
