from __future__ import annotations

from ticket_assign.dispatcher.base import Dispatcher
from ticket_assign.domain.agent import Agent
from ticket_assign.domain.ticket import Ticket


class LeastLoadedDispatcher(Dispatcher):
    name = "least_loaded"

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
            return min(
                matching_agents,
                key=lambda agent: (agent.load_ratio, agent.handled_ticket_count, agent.agent_id),
            )
        if fallback_agents:
            return min(
                fallback_agents,
                key=lambda agent: (agent.load_ratio, agent.handled_ticket_count, agent.agent_id),
            )
        return None

