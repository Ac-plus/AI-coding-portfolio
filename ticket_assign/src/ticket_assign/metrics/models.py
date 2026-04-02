from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class ResponseMetrics:
    p1_avg_wait_minutes: float
    p1_p95_wait_minutes: float
    p1_sla_rate: float


@dataclass(slots=True)
class EfficiencyMetrics:
    avg_wait_minutes: float
    avg_completion_minutes: float
    avg_queue_length: float
    reroute_rate: float


@dataclass(slots=True)
class UtilizationMetrics:
    avg_agent_utilization: float
    agent_utilization_variance: float
    peak_hour_throughput: int


@dataclass(slots=True)
class FairnessMetrics:
    max_tickets_per_agent: int
    min_tickets_per_agent: int
    ticket_count_variance: float
    longest_normal_wait_minutes: float
    starvation_ticket_count: int


@dataclass(slots=True)
class MisassignmentMetrics:
    mismatch_assignment_count: int
    reroute_extra_cost_minutes: int


@dataclass(slots=True)
class MetricsSummary:
    response: ResponseMetrics
    efficiency: EfficiencyMetrics
    utilization: UtilizationMetrics
    fairness: FairnessMetrics
    misassignment: MisassignmentMetrics

    def to_dict(self) -> dict:
        return asdict(self)

