from __future__ import annotations

from ticket_assign.config.scenario_loader import AgentEventConfig
from ticket_assign.domain.enums import EventType
from ticket_assign.domain.event import Event
from ticket_assign.domain.ticket import Ticket


def generate_arrival_events(tickets: list[Ticket]) -> list[Event]:
    events: list[Event] = []
    for sequence, ticket in enumerate(sorted(tickets, key=lambda item: item.created_time)):
        events.append(
            Event(
                time=ticket.created_time,
                sequence=sequence,
                event_type=EventType.TICKET_ARRIVAL,
                ticket_id=ticket.ticket_id,
            )
        )
    return events


def generate_agent_events(agent_events: list[AgentEventConfig], start_sequence: int) -> list[Event]:
    events: list[Event] = []
    sequence = start_sequence
    for agent_event in sorted(agent_events, key=lambda item: (item.time, item.agent_id, item.status)):
        event_type = EventType.AGENT_OFFLINE
        if agent_event.status == "online":
            event_type = EventType.AGENT_ONLINE
        events.append(
            Event(
                time=agent_event.time,
                sequence=sequence,
                event_type=event_type,
                agent_id=agent_event.agent_id,
            )
        )
        sequence += 1
    return events
