import logging
from datetime import datetime, timedelta
from uuid import uuid4

from app.concurrency.conflict_checker import has_time_conflict
from app.concurrency.lock_manager import LockManager
from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.rules import (
    AdvanceBookingRule,
    BookingDurationRule,
    BookingRule,
    BookingRuleContext,
    DailyLimitRule,
    PastTimeRule,
)
from app.services.exceptions import (
    BookingConflictError,
    BookingNotFoundError,
    UserNotFoundError,
    BookingValidationError,
    RoomNotFoundError,
)
from app.services.metrics_service import MetricsService
from app.utils.time_utils import utc_now


class BookingService:
    def __init__(
        self,
        booking_repository: BookingRepository,
        room_repository: RoomRepository,
        lock_manager: LockManager,
        user_repository: UserRepository | None = None,
        rules: list[BookingRule] | None = None,
        lock_timeout: float = 2,
        metrics_service: MetricsService | None = None,
    ) -> None:
        self.booking_repository = booking_repository
        self.room_repository = room_repository
        self.lock_manager = lock_manager
        self.user_repository = user_repository
        self.rules = rules or [
            BookingDurationRule(),
            PastTimeRule(),
            AdvanceBookingRule(),
            DailyLimitRule(),
        ]
        self.lock_timeout = lock_timeout
        self.metrics_service = metrics_service
        self.logger = logging.getLogger("meeting_room.booking")

    def list_bookings(
        self,
        *,
        user_id: str | None = None,
        room_id: str | None = None,
        booking_date: str | None = None,
        include_inactive: bool = True,
    ) -> list[Booking]:
        bookings = self.booking_repository.list_bookings(include_inactive=include_inactive)
        if user_id is not None:
            bookings = [booking for booking in bookings if booking.user_id == user_id]
        if room_id is not None:
            bookings = [booking for booking in bookings if booking.room_id == room_id]
        if booking_date is not None:
            bookings = [
                booking
                for booking in bookings
                if booking.start_time.date().isoformat() == booking_date
            ]
        return bookings

    def create_booking(
        self,
        *,
        room_id: str,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        now: datetime | None = None,
    ) -> Booking:
        effective_now = now or utc_now()

        with self.lock_manager.acquire_booking_flow(room_id, timeout=self.lock_timeout):
            room = self.room_repository.get_room(room_id)
            if room is None:
                self.logger.warning("booking_failed room_id=%s user_id=%s reason=room_not_found", room_id, user_id)
                raise RoomNotFoundError(f"Room `{room_id}` does not exist.")
            if self.user_repository is not None and self.user_repository.get_user(user_id) is None:
                self.logger.warning("booking_failed room_id=%s user_id=%s reason=user_not_found", room_id, user_id)
                raise UserNotFoundError(f"User `{user_id}` does not exist.")

            bookings = self.booking_repository.list_bookings(include_inactive=True)
            candidate = Booking(
                id=str(uuid4()),
                room_id=room.id,
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                status=BookingStatus.ACTIVE,
                created_at=effective_now,
                expires_at=effective_now + timedelta(minutes=30),
            )

            violations = self._validate_rules(candidate, bookings, effective_now)
            if violations:
                self.logger.info(
                    "booking_rejected booking_id=%s room_id=%s user_id=%s reason=rule_validation errors=%s",
                    candidate.id,
                    candidate.room_id,
                    candidate.user_id,
                    violations,
                )
                if self.metrics_service is not None:
                    self.metrics_service.increment("booking.failed")
                raise BookingValidationError(violations)

            if has_time_conflict(candidate, bookings):
                self.logger.info(
                    "booking_conflict booking_id=%s room_id=%s user_id=%s reason=time_slot_occupied",
                    candidate.id,
                    candidate.room_id,
                    candidate.user_id,
                )
                if self.metrics_service is not None:
                    self.metrics_service.increment("booking.conflict")
                raise BookingConflictError("The selected time slot is already booked.")

            bookings.append(candidate)
            self.booking_repository.save_bookings(bookings)
            self.logger.info(
                "booking_created booking_id=%s room_id=%s user_id=%s start_time=%s end_time=%s",
                candidate.id,
                candidate.room_id,
                candidate.user_id,
                candidate.start_time.isoformat(),
                candidate.end_time.isoformat(),
            )
            if self.metrics_service is not None:
                self.metrics_service.increment("booking.success")
            return candidate

    def cancel_booking(
        self,
        booking_id: str,
        *,
        user_id: str | None = None,
    ) -> Booking:
        with self.lock_manager.acquire_resources(["file:bookings"], timeout=self.lock_timeout):
            bookings = self.booking_repository.list_bookings(include_inactive=True)
            target = next((booking for booking in bookings if booking.id == booking_id), None)
            if target is None:
                self.logger.warning("cancel_failed booking_id=%s user_id=%s reason=not_found", booking_id, user_id)
                raise BookingNotFoundError(f"Booking `{booking_id}` does not exist.")

            if user_id is not None and target.user_id != user_id:
                self.logger.info(
                    "cancel_rejected booking_id=%s user_id=%s reason=owner_mismatch target_user_id=%s",
                    booking_id,
                    user_id,
                    target.user_id,
                )
                raise BookingValidationError(
                    [{"code": "booking_owner_mismatch", "message": "The booking does not belong to this user."}]
                )

            if target.status != BookingStatus.ACTIVE:
                self.logger.info(
                    "cancel_rejected booking_id=%s user_id=%s reason=booking_not_active status=%s",
                    booking_id,
                    user_id,
                    target.status.value,
                )
                raise BookingValidationError(
                    [{"code": "booking_not_active", "message": "Only active bookings can be cancelled."}]
                )

            target.status = BookingStatus.CANCELLED
            self.booking_repository.save_bookings(bookings)
            self.logger.info("booking_cancelled booking_id=%s room_id=%s user_id=%s", target.id, target.room_id, target.user_id)
            if self.metrics_service is not None:
                self.metrics_service.increment("booking.cancelled")
            return target

    def _validate_rules(
        self,
        candidate: Booking,
        existing_bookings: list[Booking],
        now: datetime,
    ) -> list[dict[str, str]]:
        context = BookingRuleContext(candidate=candidate, existing_bookings=existing_bookings, now=now)
        violations: list[dict[str, str]] = []

        for rule in self.rules:
            for violation in rule.validate(context):
                violations.append({"code": violation.code, "message": violation.message})

        return violations
