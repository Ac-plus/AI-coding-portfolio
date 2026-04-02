from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SimulationSettings:
    seed: int = 0
    actual_handle_time_variation_pct: float = 0.3
    reroute_penalty_minutes: int = 5
    context_switch_penalty_minutes: int = 10
    mismatch_handle_penalty_rate: float = 0.5
    allow_mismatch_after_minutes: int | None = None
    max_reroutes: int = 1
    require_matching_after_reroute: bool = True
