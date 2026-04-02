from __future__ import annotations

import heapq

from ticket_assign.domain.event import Event


class EventQueue:
    def __init__(self) -> None:
        self._events: list[Event] = []

    def push(self, event: Event) -> None:
        heapq.heappush(self._events, event)

    def pop(self) -> Event:
        return heapq.heappop(self._events)

    def __bool__(self) -> bool:
        return bool(self._events)

