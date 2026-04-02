from __future__ import annotations

from dataclasses import dataclass, field

from ticket_assign.domain.enums import EventType


@dataclass(order=True, slots=True)
class Event:
    time: int
    sequence: int
    event_type: EventType = field(compare=False)
    ticket_id: str | None = field(default=None, compare=False)
    agent_id: str | None = field(default=None, compare=False)
    assignment_attempt: int | None = field(default=None, compare=False)
