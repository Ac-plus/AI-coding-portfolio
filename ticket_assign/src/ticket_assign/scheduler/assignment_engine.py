from __future__ import annotations

from dataclasses import dataclass

from ticket_assign.config.settings import SimulationSettings
from ticket_assign.dispatcher.base import Dispatcher
from ticket_assign.domain.assignment import Assignment
from ticket_assign.domain.agent import Agent
from ticket_assign.domain.enums import EventType, TicketStatus
from ticket_assign.domain.event import Event
from ticket_assign.domain.ticket import Ticket
from ticket_assign.scheduler.queue_manager import QueueManager
from ticket_assign.scheduler.reroute_manager import RerouteManager


@dataclass(slots=True)
class AssignmentOutcome:
    assignments: list[Assignment]
    completion_events: list[Event]
    reroute_events: list[Event]


class AssignmentEngine:
    def __init__(self, dispatcher: Dispatcher, settings: SimulationSettings) -> None:
        self.dispatcher = dispatcher
        self.settings = settings
        self.reroute_manager = RerouteManager(settings.reroute_penalty_minutes)

    def assign_waiting_tickets(
        self,
        current_time: int,
        agents: dict[str, Agent],
        tickets: dict[str, Ticket],
        queue: QueueManager,
        next_sequence: int,
    ) -> AssignmentOutcome:
        assignments: list[Assignment] = []
        completion_events: list[Event] = []
        reroute_events: list[Event] = []
        sequence = next_sequence

        ordered_ticket_ids = self.dispatcher.order_tickets(
            queue.peek_all(),
            tickets=tickets,
            current_time=current_time,
        )
        for ticket_id in ordered_ticket_ids:
            ticket = tickets[ticket_id]
            if ticket.status != TicketStatus.QUEUED:
                continue
            candidate_agents = [
                agent for agent in agents.values() if agent.can_take_any(current_time=current_time)
            ]
            selected_agent = self.dispatcher.pick_agent(ticket, candidate_agents, current_time)
            if selected_agent is None:
                continue

            queue.remove(ticket.ticket_id)
            is_skill_match = selected_agent.has_skill(ticket.category)

            if (not is_skill_match) and ticket.reroute_count < self.settings.max_reroutes:
                assignments.append(
                    Assignment(
                        ticket_id=ticket.ticket_id,
                        agent_id=selected_agent.agent_id,
                        assigned_time=current_time,
                        matched_skill=False,
                        queue_size_after=len(queue),
                    )
                )
                self.reroute_manager.reroute(ticket)
                reroute_events.append(
                    Event(
                        time=current_time + 1,
                        sequence=sequence,
                        event_type=EventType.TICKET_REROUTE,
                        ticket_id=ticket.ticket_id,
                    )
                )
                sequence += 1
                continue

            selected_agent.assign(ticket.ticket_id)
            ticket.begin_processing(agent_id=selected_agent.agent_id, current_time=current_time)

            duration = ticket.remaining_handle_time
            if not is_skill_match:
                duration = ticket.apply_mismatch_completion_penalty(
                    self.settings.mismatch_handle_penalty_rate
                )

            assignments.append(
                Assignment(
                    ticket_id=ticket.ticket_id,
                    agent_id=selected_agent.agent_id,
                    assigned_time=current_time,
                    matched_skill=is_skill_match,
                    queue_size_after=len(queue),
                )
            )
            completion_events.append(
                Event(
                    time=current_time + duration,
                    sequence=sequence,
                    event_type=EventType.TICKET_COMPLETION,
                    ticket_id=ticket.ticket_id,
                    agent_id=selected_agent.agent_id,
                    assignment_attempt=ticket.assignment_attempt,
                )
            )
            sequence += 1

        return AssignmentOutcome(
            assignments=assignments,
            completion_events=completion_events,
            reroute_events=reroute_events,
        )
