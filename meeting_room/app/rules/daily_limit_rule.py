from app.rules.base import BookingRule, BookingRuleContext, RuleViolation


class DailyLimitRule(BookingRule):
    def __init__(self, max_daily_bookings: int = 3) -> None:
        self.max_daily_bookings = max_daily_bookings

    def validate(self, context: BookingRuleContext) -> list[RuleViolation]:
        candidate = context.candidate
        booking_day = candidate.start_time.date()
        matching_bookings = [
            booking
            for booking in context.active_bookings()
            if booking.user_id == candidate.user_id
            and booking.start_time.date() == booking_day
            and booking.id != candidate.id
        ]
        if len(matching_bookings) >= self.max_daily_bookings:
            return [
                RuleViolation(
                    code="daily_booking_limit_exceeded",
                    message="A user can only create 3 bookings per day.",
                )
            ]
        return []
