from datetime import timedelta

import pytest

from app.models.booking import BookingStatus
from app.services import BookingConflictError, BookingValidationError


def test_booking_service_creates_booking(booking_service, base_now):
    booking = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now,
    )

    assert booking.room_id == "room-a"
    assert booking.status == BookingStatus.ACTIVE


def test_booking_service_rejects_conflict(booking_service, base_now):
    booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now,
    )

    with pytest.raises(BookingConflictError):
        booking_service.create_booking(
            room_id="room-a",
            user_id="user-2",
            start_time=base_now + timedelta(hours=1, minutes=30),
            end_time=base_now + timedelta(hours=2, minutes=30),
            now=base_now,
        )


def test_booking_service_cancels_booking(booking_service, base_now):
    booking = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now,
    )

    cancelled = booking_service.cancel_booking(booking.id, user_id="user-1")

    assert cancelled.status == BookingStatus.CANCELLED


def test_booking_service_rejects_wrong_owner_cancel(booking_service, base_now):
    booking = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now,
    )

    with pytest.raises(BookingValidationError):
        booking_service.cancel_booking(booking.id, user_id="user-2")
