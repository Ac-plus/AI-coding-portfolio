from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ticket_assign.config.settings import SimulationSettings
from ticket_assign.domain.agent import Agent
from ticket_assign.domain.ticket import Ticket


@dataclass(slots=True)
class AgentEventConfig:
    time: int
    agent_id: str
    status: str


@dataclass(slots=True)
class Scenario:
    name: str
    settings: SimulationSettings
    agents: list[Agent]
    tickets: list[Ticket]
    agent_events: list[AgentEventConfig]


def load_scenario(path: str | Path) -> Scenario:
    scenario_path = Path(path)
    data = json.loads(scenario_path.read_text(encoding="utf-8"))
    settings_data = data.get("settings", {})
    settings = SimulationSettings(
        seed=settings_data.get("seed", 0),
        actual_handle_time_variation_pct=settings_data.get(
            "actual_handle_time_variation_pct", 0.3
        ),
        reroute_penalty_minutes=settings_data.get("reroute_penalty_minutes", 5),
        context_switch_penalty_minutes=settings_data.get("context_switch_penalty_minutes", 10),
        mismatch_handle_penalty_rate=settings_data.get("mismatch_handle_penalty_rate", 0.5),
        allow_mismatch_after_minutes=settings_data.get("allow_mismatch_after_minutes"),
        max_reroutes=settings_data.get("max_reroutes", 1),
        require_matching_after_reroute=settings_data.get(
            "require_matching_after_reroute", True
        ),
    )
    agents = [Agent.from_dict(item) for item in data.get("agents", [])]
    tickets = [Ticket.from_dict(item) for item in data.get("tickets", [])]
    agent_events = [
        AgentEventConfig(
            time=int(item["time"]),
            agent_id=str(item["agent_id"]),
            status=str(item["status"]),
        )
        for item in data.get("agent_events", [])
    ]
    return Scenario(
        name=data.get("name", scenario_path.stem),
        settings=settings,
        agents=agents,
        tickets=tickets,
        agent_events=agent_events,
    )
