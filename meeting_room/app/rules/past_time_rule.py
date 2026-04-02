from app.rules.base import BookingRule, BookingRuleContext, RuleViolation


class PastTimeRule(BookingRule):
    def validate(self, context: BookingRuleContext) -> list[RuleViolation]:
        now = context.now or context.candidate.created_at
        if context.candidate.start_time < now:
            return [
                RuleViolation(
                    code="cannot_book_past_time",
                    message="Past time slots cannot be booked.",
                )
            ]
        return []
