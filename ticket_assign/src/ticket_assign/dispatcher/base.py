from __future__ import annotations

from abc import ABC, abstractmethod

from ticket_assign.config.settings import SimulationSettings
from ticket_assign.domain.agent import Agent
from ticket_assign.domain.ticket import Ticket


class Dispatcher(ABC):
    name = "base"

    def __init__(self, settings: SimulationSettings) -> None:
        self.settings = settings

    def order_tickets(
        self,
        queued_ticket_ids: list[str],
        tickets: dict[str, Ticket],
        current_time: int,
    ) -> list[str]:
        return queued_ticket_ids

    @abstractmethod
    def pick_agent(
        self,
        ticket: Ticket,
        candidate_agents: list[Agent],
        current_time: int,
    ) -> Agent | None:
        raise NotImplementedError

    def select_agents(
        self,
        ticket: Ticket,
        candidate_agents: list[Agent],
        current_time: int,
    ) -> tuple[list[Agent], list[Agent]]:
        matching = [agent for agent in candidate_agents if agent.has_skill(ticket.category)]
        fallback = self._fallback_agents(ticket, candidate_agents, current_time)
        return matching, fallback

    def _fallback_agents(
        self,
        ticket: Ticket,
        candidate_agents: list[Agent],
        current_time: int,
    ) -> list[Agent]:
        wait_threshold = self.settings.allow_mismatch_after_minutes
        if wait_threshold is None:
            return []
        if ticket.reroute_count >= self.settings.max_reroutes and self.settings.require_matching_after_reroute:
            return []
        if ticket.waiting_time(current_time) < wait_threshold:
            return []
        return [agent for agent in candidate_agents if not agent.has_skill(ticket.category)]
