from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LogEntry:
    time: int
    action: str
    ticket_id: str
    details: dict

    def to_dict(self) -> dict:
        return {
            "time": self.time,
            "action": self.action,
            "ticket_id": self.ticket_id,
            "details": self.details,
        }


class EventLogger:
    def __init__(self) -> None:
        self.entries: list[LogEntry] = []

    def log(self, time: int, action: str, ticket_id: str, **details: object) -> None:
        self.entries.append(
            LogEntry(time=time, action=action, ticket_id=ticket_id, details=dict(details))
        )

