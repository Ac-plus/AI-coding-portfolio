from __future__ import annotations

from ticket_assign.dispatcher.base import Dispatcher
from ticket_assign.domain.agent import Agent
from ticket_assign.domain.ticket import Ticket


class FIFODispatcher(Dispatcher):
    name = "fifo"

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
        for agent in matching_agents:
            if agent.can_take_ticket(current_time=current_time, category=ticket.category):
                return agent
        for agent in fallback_agents:
            if agent.can_take_any(current_time=current_time):
                return agent
        return None
