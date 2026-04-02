from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from ticket_assign.config.scenario_loader import Scenario
from ticket_assign.metrics.calculators import percentile_95, safe_mean, safe_variance
from ticket_assign.metrics.models import (
    EfficiencyMetrics,
    FairnessMetrics,
    MetricsSummary,
    MisassignmentMetrics,
    ResponseMetrics,
    UtilizationMetrics,
)

if TYPE_CHECKING:
    from ticket_assign.simulator.engine import SimulationResult


class MetricsCollector:
    SLA_MINUTES = {"P1": 5, "P2": 30, "P3": 120}

    def collect(self, scenario: Scenario, result: SimulationResult) -> MetricsSummary:
        tickets = result.tickets
        logs = result.logs
        final_time = max(1, result.final_time)

        wait_times = self._wait_times_by_ticket(tickets)
        completion_times = self._completion_times_by_ticket(tickets)
        p1_waits = [wait for ticket_id, wait in wait_times.items() if self._ticket_priority(tickets, ticket_id) == "P1"]

        response = ResponseMetrics(
            p1_avg_wait_minutes=safe_mean(p1_waits),
            p1_p95_wait_minutes=percentile_95(p1_waits),
            p1_sla_rate=self._sla_rate(tickets, wait_times, "P1"),
        )

        rerouted_tickets = sum(1 for ticket in tickets if ticket["reroute_count"] > 0)
        efficiency = EfficiencyMetrics(
            avg_wait_minutes=safe_mean(list(wait_times.values())),
            avg_completion_minutes=safe_mean(list(completion_times.values())),
            avg_queue_length=self._average_queue_length(logs, final_time),
            reroute_rate=(rerouted_tickets / len(tickets)) if tickets else 0.0,
        )

        agent_ticket_counts = [agent["handled_ticket_count"] for agent in result.agents]
        agent_utilizations = self._agent_utilizations(result.agents, logs, final_time)
        utilization = UtilizationMetrics(
            avg_agent_utilization=safe_mean(list(agent_utilizations.values())),
            agent_utilization_variance=safe_variance(list(agent_utilizations.values())),
            peak_hour_throughput=self._peak_hour_throughput(logs),
        )

        normal_waits = [
            wait
            for ticket_id, wait in wait_times.items()
            if self._ticket_priority(tickets, ticket_id) in {"P2", "P3"}
        ]
        fairness = FairnessMetrics(
            max_tickets_per_agent=max(agent_ticket_counts) if agent_ticket_counts else 0,
            min_tickets_per_agent=min(agent_ticket_counts) if agent_ticket_counts else 0,
            ticket_count_variance=safe_variance(agent_ticket_counts),
            longest_normal_wait_minutes=max(normal_waits) if normal_waits else 0.0,
            starvation_ticket_count=self._starvation_count(tickets, wait_times),
        )

        mismatch_count = sum(
            1
            for entry in logs
            if entry["action"] == "ticket_assigned" and not entry["details"].get("matched_skill", True)
        )
        reroute_extra_cost = sum(ticket["reroute_count"] for ticket in tickets) * scenario.settings.reroute_penalty_minutes
        misassignment = MisassignmentMetrics(
            mismatch_assignment_count=mismatch_count,
            reroute_extra_cost_minutes=reroute_extra_cost,
        )

        return MetricsSummary(
            response=response,
            efficiency=efficiency,
            utilization=utilization,
            fairness=fairness,
            misassignment=misassignment,
        )

    def _wait_times_by_ticket(self, tickets: list[dict]) -> dict[str, float]:
        wait_times: dict[str, float] = {}
        for ticket in tickets:
            assigned_time = ticket["assigned_time"]
            if assigned_time is None:
                continue
            wait_times[ticket["ticket_id"]] = float(assigned_time - ticket["created_time"])
        return wait_times

    def _completion_times_by_ticket(self, tickets: list[dict]) -> dict[str, float]:
        completion_times: dict[str, float] = {}
        for ticket in tickets:
            completed_time = ticket["completed_time"]
            if completed_time is None:
                continue
            completion_times[ticket["ticket_id"]] = float(completed_time - ticket["created_time"])
        return completion_times

    def _ticket_priority(self, tickets: list[dict], ticket_id: str) -> str:
        for ticket in tickets:
            if ticket["ticket_id"] == ticket_id:
                return ticket["priority"]
        raise KeyError(ticket_id)

    def _sla_rate(self, tickets: list[dict], wait_times: dict[str, float], priority: str) -> float:
        target_ticket_ids = [ticket["ticket_id"] for ticket in tickets if ticket["priority"] == priority]
        if not target_ticket_ids:
            return 0.0
        success_count = sum(
            1 for ticket_id in target_ticket_ids if wait_times.get(ticket_id, float("inf")) <= self.SLA_MINUTES[priority]
        )
        return success_count / len(target_ticket_ids)

    def _average_queue_length(self, logs: list[dict], final_time: int) -> float:
        queue_length = 0
        queue_time = 0
        last_time = 0
        for entry in logs:
            current_time = entry["time"]
            queue_time += queue_length * (current_time - last_time)
            if "queue_size" in entry["details"]:
                queue_length = int(entry["details"]["queue_size"])
            last_time = current_time
        queue_time += queue_length * (final_time - last_time)
        return queue_time / final_time if final_time > 0 else 0.0

    def _agent_utilizations(self, agents: list[dict], logs: list[dict], final_time: int) -> dict[str, float]:
        active_counts = {agent["agent_id"]: 0 for agent in agents}
        slot_time = {agent["agent_id"]: 0.0 for agent in agents}
        capacities = {agent["agent_id"]: max(1, agent["max_concurrent"]) for agent in agents}
        last_time = 0

        for entry in logs:
            current_time = entry["time"]
            delta = current_time - last_time
            if delta > 0:
                for agent_id, active_count in active_counts.items():
                    slot_time[agent_id] += delta * (active_count / capacities[agent_id])
            action = entry["action"]
            agent_id = entry["details"].get("agent_id")
            if action == "ticket_assigned" and agent_id in active_counts:
                active_counts[agent_id] += 1
            elif action in {"ticket_completed", "ticket_requeued_from_offline"} and agent_id in active_counts:
                active_counts[agent_id] = max(0, active_counts[agent_id] - 1)
            last_time = current_time

        if final_time > last_time:
            delta = final_time - last_time
            for agent_id, active_count in active_counts.items():
                slot_time[agent_id] += delta * (active_count / capacities[agent_id])

        return {
            agent["agent_id"]: (slot_time[agent["agent_id"]] / final_time if final_time > 0 else 0.0)
            for agent in agents
        }

    def _peak_hour_throughput(self, logs: list[dict]) -> int:
        buckets: dict[int, int] = defaultdict(int)
        for entry in logs:
            if entry["action"] != "ticket_completed":
                continue
            bucket = entry["time"] // 60
            buckets[bucket] += 1
        return max(buckets.values(), default=0)

    def _starvation_count(self, tickets: list[dict], wait_times: dict[str, float]) -> int:
        starvation_count = 0
        for ticket in tickets:
            wait_time = wait_times.get(ticket["ticket_id"])
            if wait_time is None:
                continue
            if wait_time > self.SLA_MINUTES[ticket["priority"]] * 2:
                starvation_count += 1
        return starvation_count
