from __future__ import annotations

from dataclasses import dataclass

from ticket_assign.domain.agent import Agent
from ticket_assign.domain.ticket import Ticket
from ticket_assign.scheduler.queue_manager import QueueManager


@dataclass(slots=True)
class SimulationState:
    current_time: int
    agents: dict[str, Agent]
    tickets: dict[str, Ticket]
    queue: QueueManager

