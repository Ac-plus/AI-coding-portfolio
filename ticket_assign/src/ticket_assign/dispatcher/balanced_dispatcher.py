from __future__ import annotations

from ticket_assign.dispatcher.base import Dispatcher
from ticket_assign.domain.agent import Agent
from ticket_assign.domain.ticket import Ticket


class BalancedDispatcher(Dispatcher):
    name = "balanced"

    _priority_weight = {"P1": 300, "P2": 150, "P3": 50}

    def order_tickets(
        self,
        queued_ticket_ids: list[str],
        tickets: dict[str, Ticket],
        current_time: int,
    ) -> list[str]:
        return sorted(
            queued_ticket_ids,
            key=lambda ticket_id: (
                -self._ticket_score(tickets[ticket_id], current_time),
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
            return max(matching_agents, key=self._agent_score)
        if fallback_agents:
            return max(fallback_agents, key=self._agent_score)
        return None

    def _ticket_score(self, ticket: Ticket, current_time: int) -> int:
        return self._priority_weight[ticket.priority.value] + ticket.waiting_time(current_time) * 5

    def _agent_score(self, agent: Agent) -> float:
        return (1 - agent.load_ratio) * 100 - agent.handled_ticket_count

