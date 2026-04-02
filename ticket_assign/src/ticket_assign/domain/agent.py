from __future__ import annotations

from dataclasses import dataclass, field

from ticket_assign.domain.enums import AgentStatus


@dataclass(slots=True)
class Agent:
    agent_id: str
    skill_set: set[str]
    shift_start: int
    shift_end: int
    max_concurrent: int = 1
    status: AgentStatus = AgentStatus.ONLINE
    active_ticket_ids: list[str] = field(default_factory=list)
    offline_override: bool = False
    handled_ticket_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        status = AgentStatus(data.get("status", AgentStatus.ONLINE.value))
        return cls(
            agent_id=str(data["agent_id"]),
            skill_set=set(data.get("skill_set", [])),
            shift_start=int(data.get("shift_start", 0)),
            shift_end=int(data.get("shift_end", 24 * 60)),
            max_concurrent=int(data.get("max_concurrent", 1)),
            status=status,
            offline_override=(status == AgentStatus.OFFLINE),
        )

    def has_skill(self, category: str) -> bool:
        return category in self.skill_set

    def can_take_any(self, current_time: int) -> bool:
        in_shift = self.shift_start <= current_time <= self.shift_end
        has_capacity = len(self.active_ticket_ids) < self.max_concurrent
        return (not self.offline_override) and in_shift and has_capacity

    def can_take_ticket(self, current_time: int, category: str) -> bool:
        return self.can_take_any(current_time) and self.has_skill(category)

    @property
    def load_ratio(self) -> float:
        return len(self.active_ticket_ids) / self.max_concurrent

    def assign(self, ticket_id: str) -> None:
        self.active_ticket_ids.append(ticket_id)
        self._refresh_status()

    def release(self, ticket_id: str) -> None:
        if ticket_id in self.active_ticket_ids:
            self.active_ticket_ids.remove(ticket_id)
        self._refresh_status()

    def go_offline(self) -> None:
        self.offline_override = True
        self.status = AgentStatus.OFFLINE

    def go_online(self) -> None:
        self.offline_override = False
        self._refresh_status()

    def _refresh_status(self) -> None:
        if self.offline_override:
            self.status = AgentStatus.OFFLINE
        elif len(self.active_ticket_ids) >= self.max_concurrent:
            self.status = AgentStatus.BUSY
        else:
            self.status = AgentStatus.ONLINE
