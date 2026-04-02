from datetime import timedelta

from app.rules.base import BookingRule, BookingRuleContext, RuleViolation


class BookingDurationRule(BookingRule):
    def __init__(self, max_duration: timedelta = timedelta(hours=4)) -> None:
        self.max_duration = max_duration

    def validate(self, context: BookingRuleContext) -> list[RuleViolation]:
        duration = context.candidate.end_time - context.candidate.start_time
        if duration <= timedelta(0):
            return [
                RuleViolation(
                    code="invalid_duration",
                    message="The booking end time must be later than the start time.",
                )
            ]
        if duration > self.max_duration:
            return [
                RuleViolation(
                    code="duration_exceeded",
                    message="A single booking cannot exceed 4 hours.",
                )
            ]
        return []
