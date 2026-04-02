from datetime import timedelta

from app.models.booking import Booking, BookingStatus
from app.rules import (
    AdvanceBookingRule,
    BookingDurationRule,
    BookingRuleContext,
    DailyLimitRule,
    PastTimeRule,
    is_booking_expired,
)


def test_booking_duration_rule_rejects_more_than_four_hours(base_now):
    booking = Booking(
        id="booking-2",
        room_id="room-a",
        user_id="user-2",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=6),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
    )

    violations = BookingDurationRule().validate(BookingRuleContext(candidate=booking, now=base_now))

    assert violations
    assert violations[0].code == "duration_exceeded"


def test_daily_limit_rule_rejects_fourth_booking(base_now):
    existing = []
    for index in range(3):
        existing.append(
            Booking(
                id=f"existing-{index}",
                room_id="room-a",
                user_id="user-1",
                start_time=base_now + timedelta(hours=2 + index),
                end_time=base_now + timedelta(hours=3 + index),
                status=BookingStatus.ACTIVE,
                created_at=base_now,
            )
        )

    candidate = Booking(
        id="booking-4",
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=8),
        end_time=base_now + timedelta(hours=9),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
    )

    violations = DailyLimitRule().validate(
        BookingRuleContext(candidate=candidate, existing_bookings=existing, now=base_now)
    )

    assert violations
    assert violations[0].code == "daily_booking_limit_exceeded"


def test_past_time_rule_rejects_past_start(base_now):
    candidate = Booking(
        id="booking-past",
        room_id="room-a",
        user_id="user-1",
        start_time=base_now - timedelta(minutes=1),
        end_time=base_now + timedelta(minutes=10),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
    )

    violations = PastTimeRule().validate(BookingRuleContext(candidate=candidate, now=base_now))

    assert violations
    assert violations[0].code == "cannot_book_past_time"


def test_advance_booking_rule_requires_fifteen_minutes(base_now):
    candidate = Booking(
        id="booking-advance",
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(minutes=10),
        end_time=base_now + timedelta(hours=1),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
    )

    violations = AdvanceBookingRule().validate(BookingRuleContext(candidate=candidate, now=base_now))

    assert violations
    assert violations[0].code == "advance_booking_required"


def test_expiration_rule_marks_old_booking_as_expired(base_now):
    candidate = Booking(
        id="booking-expired",
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        status=BookingStatus.ACTIVE,
        created_at=base_now - timedelta(minutes=31),
    )

    assert is_booking_expired(candidate, now=base_now)
