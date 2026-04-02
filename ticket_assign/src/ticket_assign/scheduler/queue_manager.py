from __future__ import annotations

from collections import deque


class QueueManager:
    def __init__(self) -> None:
        self._queue: deque[str] = deque()

    def push(self, ticket_id: str) -> None:
        if ticket_id not in self._queue:
            self._queue.append(ticket_id)

    def peek_all(self) -> list[str]:
        return list(self._queue)

    def remove(self, ticket_id: str) -> None:
        if ticket_id in self._queue:
            self._queue.remove(ticket_id)

    def __len__(self) -> int:
        return len(self._queue)
