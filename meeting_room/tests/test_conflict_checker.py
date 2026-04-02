from datetime import timedelta

from app.concurrency.conflict_checker import has_time_conflict, time_ranges_overlap
from app.models.booking import Booking, BookingStatus


def test_time_ranges_overlap_when_ranges_intersect(base_now):
    assert time_ranges_overlap(
        base_now,
        base_now + timedelta(hours=1),
        base_now + timedelta(minutes=30),
        base_now + timedelta(hours=2),
    )


def test_time_ranges_do_not_overlap_on_touching_boundaries(base_now):
    assert not time_ranges_overlap(
        base_now,
        base_now + timedelta(hours=1),
        base_now + timedelta(hours=1),
        base_now + timedelta(hours=2),
    )


def test_has_time_conflict_only_checks_same_room(active_booking, base_now):
    candidate = Booking(
        id="booking-2",
        room_id="room-b",
        user_id="user-2",
        start_time=base_now + timedelta(hours=2, minutes=30),
        end_time=base_now + timedelta(hours=3, minutes=30),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
    )

    assert not has_time_conflict(candidate, [active_booking])


def test_has_time_conflict_detects_overlap(active_booking, base_now):
    candidate = Booking(
        id="booking-3",
        room_id="room-a",
        user_id="user-2",
        start_time=base_now + timedelta(hours=2, minutes=30),
        end_time=base_now + timedelta(hours=4),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
    )

    assert has_time_conflict(candidate, [active_booking])
