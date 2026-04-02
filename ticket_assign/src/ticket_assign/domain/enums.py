from __future__ import annotations

from enum import Enum


class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class TicketPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TicketStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class EventType(str, Enum):
    TICKET_ARRIVAL = "ticket_arrival"
    TICKET_COMPLETION = "ticket_completion"
    TICKET_REROUTE = "ticket_reroute"
    AGENT_OFFLINE = "agent_offline"
    AGENT_ONLINE = "agent_online"
