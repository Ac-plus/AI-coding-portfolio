from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.models.booking import Booking, BookingStatus


@dataclass(slots=True)
class RuleViolation:
    code: str
    message: str


@dataclass(slots=True)
class BookingRuleContext:
    candidate: Booking
    existing_bookings: list[Booking] = field(default_factory=list)
    now: datetime | None = None

    def active_bookings(self) -> list[Booking]:
        return [
            booking
            for booking in self.existing_bookings
            if booking.status == BookingStatus.ACTIVE
        ]


class BookingRule(ABC):
    @abstractmethod
    def validate(self, context: BookingRuleContext) -> list[RuleViolation]:
        raise NotImplementedError
