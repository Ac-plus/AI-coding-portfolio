from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Assignment:
    ticket_id: str
    agent_id: str
    assigned_time: int
    matched_skill: bool
    queue_size_after: int
