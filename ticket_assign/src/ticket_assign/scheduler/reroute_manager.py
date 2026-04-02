from __future__ import annotations

from ticket_assign.domain.ticket import Ticket


class RerouteManager:
    def __init__(self, reroute_penalty_minutes: int) -> None:
        self.reroute_penalty_minutes = reroute_penalty_minutes

    def reroute(self, ticket: Ticket) -> None:
        ticket.register_reroute(self.reroute_penalty_minutes)
