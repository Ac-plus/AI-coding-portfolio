from datetime import timedelta

from app.rules.base import BookingRule, BookingRuleContext, RuleViolation


class AdvanceBookingRule(BookingRule):
    def __init__(self, min_advance: timedelta = timedelta(minutes=15)) -> None:
        self.min_advance = min_advance

    def validate(self, context: BookingRuleContext) -> list[RuleViolation]:
        now = context.now or context.candidate.created_at
        if context.candidate.start_time - now < self.min_advance:
            return [
                RuleViolation(
                    code="advance_booking_required",
                    message="Bookings must be made at least 15 minutes in advance.",
                )
            ]
        return []
