from app.models.booking import Booking, BookingStatus


def time_ranges_overlap(start_one, end_one, start_two, end_two) -> bool:
    return max(start_one, start_two) < min(end_one, end_two)


def has_time_conflict(candidate: Booking, existing_bookings: list[Booking]) -> bool:
    for booking in existing_bookings:
        if booking.status != BookingStatus.ACTIVE:
            continue
        if booking.room_id != candidate.room_id:
            continue
        if booking.id == candidate.id:
            continue
        if time_ranges_overlap(
            candidate.start_time,
            candidate.end_time,
            booking.start_time,
            booking.end_time,
        ):
            return True
    return False
