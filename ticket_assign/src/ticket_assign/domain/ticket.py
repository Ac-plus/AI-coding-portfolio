from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from ticket_assign.domain.enums import TicketPriority, TicketStatus


@dataclass(slots=True)
class Ticket:
    ticket_id: str
    priority: TicketPriority
    category: str
    created_time: int
    estimated_handle_time: int
    status: TicketStatus = TicketStatus.PENDING
    assigned_agent_id: str | None = None
    assigned_time: int | None = None
    completed_time: int | None = None
    actual_handle_time: int = 0
    remaining_handle_time: int = 0
    processing_started_time: int | None = None
    reroute_count: int = 0
    assignment_attempt: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Ticket":
        return cls(
            ticket_id=str(data["ticket_id"]),
            priority=TicketPriority(data["priority"]),
            category=str(data["category"]),
            created_time=int(data["created_time"]),
            estimated_handle_time=int(data["estimated_handle_time"]),
        )

    def initialize_runtime(self, actual_handle_time: int) -> None:
        self.actual_handle_time = max(1, actual_handle_time)
        self.remaining_handle_time = self.actual_handle_time

    def waiting_time(self, current_time: int) -> int:
        return max(0, current_time - self.created_time)

    def begin_processing(self, agent_id: str, current_time: int) -> None:
        self.status = TicketStatus.IN_PROGRESS
        self.assigned_agent_id = agent_id
        self.processing_started_time = current_time
        self.assignment_attempt += 1
        if self.assigned_time is None:
            self.assigned_time = current_time

    def complete(self, current_time: int) -> None:
        self.status = TicketStatus.COMPLETED
        self.completed_time = current_time
        self.processing_started_time = None
        self.remaining_handle_time = 0

    def pause_for_requeue(self, current_time: int, extra_penalty: int) -> None:
        if self.processing_started_time is not None:
            spent_time = max(0, current_time - self.processing_started_time)
            self.remaining_handle_time = max(0, self.remaining_handle_time - spent_time)
        self.remaining_handle_time += extra_penalty
        self.status = TicketStatus.QUEUED
        self.assigned_agent_id = None
        self.processing_started_time = None

    def register_reroute(self, penalty_minutes: int) -> None:
        self.reroute_count += 1
        self.remaining_handle_time += penalty_minutes
        self.status = TicketStatus.PENDING
        self.assigned_agent_id = None
        self.processing_started_time = None

    def apply_mismatch_completion_penalty(self, penalty_rate: float) -> int:
        penalized_duration = max(1, ceil(self.remaining_handle_time * (1 + penalty_rate)))
        self.remaining_handle_time = penalized_duration
        return penalized_duration
