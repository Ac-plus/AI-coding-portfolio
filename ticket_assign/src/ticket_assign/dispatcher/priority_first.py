from __future__ import annotations

from ticket_assign.dispatcher.base import Dispatcher
from ticket_assign.domain.agent import Agent
from ticket_assign.domain.ticket import Ticket


class PriorityFirstDispatcher(Dispatcher):
    name = "priority_first"

    _priority_rank = {"P1": 0, "P2": 1, "P3": 2}

    def order_tickets(
        self,
        queued_ticket_ids: list[str],
        tickets: dict[str, Ticket],
        current_time: int,
    ) -> list[str]:
        return sorted(
            queued_ticket_ids,
            key=lambda ticket_id: (
                self._priority_rank[tickets[ticket_id].priority.value],
                tickets[ticket_id].created_time,
                ticket_id,
            ),
        )

    def pick_agent(
        self,
        ticket: Ticket,
        candidate_agents: list[Agent],
        current_time: int,
    ) -> Agent | None:
        matching_agents, fallback_agents = self.select_agents(
            ticket=ticket,
            candidate_agents=candidate_agents,
            current_time=current_time,
        )
        if matching_agents:
            return matching_agents[0]
        if fallback_agents:
            return fallback_agents[0]
        return None

