from datetime import datetime, timedelta

from app.models.booking import Booking, BookingStatus


def is_booking_expired(
    booking: Booking,
    now: datetime,
    release_after: timedelta = timedelta(minutes=30),
) -> bool:
    if booking.status != BookingStatus.ACTIVE:
        return False
    if booking.expires_at is not None:
        return now >= booking.expires_at
    return now >= booking.created_at + release_after
