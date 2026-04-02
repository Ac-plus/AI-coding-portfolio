from __future__ import annotations

from dataclasses import dataclass
from random import Random

from ticket_assign.config.scenario_loader import Scenario
from ticket_assign.dispatcher import build_dispatcher
from ticket_assign.domain.enums import EventType, TicketStatus
from ticket_assign.metrics.collector import MetricsCollector
from ticket_assign.reporting.logger import EventLogger
from ticket_assign.scheduler.assignment_engine import AssignmentEngine
from ticket_assign.scheduler.queue_manager import QueueManager
from ticket_assign.simulator.event_queue import EventQueue
from ticket_assign.simulator.generators import generate_agent_events, generate_arrival_events
from ticket_assign.simulator.state import SimulationState


@dataclass(slots=True)
class SimulationResult:
    scenario_name: str
    dispatcher: str
    final_time: int
    queue_size: int
    agents: list[dict]
    tickets: list[dict]
    logs: list[dict]
    metrics: dict

    def to_dict(self) -> dict:
        return {
            "scenario_name": self.scenario_name,
            "dispatcher": self.dispatcher,
            "final_time": self.final_time,
            "queue_size": self.queue_size,
            "agents": self.agents,
            "tickets": self.tickets,
            "logs": self.logs,
            "metrics": self.metrics,
        }


class SimulationEngine:
    def __init__(self, scenario: Scenario, dispatcher_name: str = "fifo") -> None:
        self.scenario = scenario
        self.dispatcher = build_dispatcher(dispatcher_name, scenario.settings)
        self.assignment_engine = AssignmentEngine(self.dispatcher, scenario.settings)
        self.metrics_collector = MetricsCollector()
        self.logger = EventLogger()
        self.event_queue = EventQueue()
        self.random = Random(scenario.settings.seed)
        self.state = SimulationState(
            current_time=0,
            agents={agent.agent_id: agent for agent in scenario.agents},
            tickets={ticket.ticket_id: ticket for ticket in scenario.tickets},
            queue=QueueManager(),
        )
        self._initialize_tickets()

    @classmethod
    def from_scenario(cls, scenario: Scenario, dispatcher_name: str = "fifo") -> "SimulationEngine":
        engine = cls(scenario, dispatcher_name=dispatcher_name)
        for event in generate_arrival_events(scenario.tickets):
            engine.event_queue.push(event)
        for event in generate_agent_events(
            scenario.agent_events,
            start_sequence=len(scenario.tickets),
        ):
            engine.event_queue.push(event)
        return engine

    def run(self) -> SimulationResult:
        next_sequence = len(self.state.tickets) + len(self.scenario.agent_events)
        while self.event_queue:
            event = self.event_queue.pop()
            self.state.current_time = event.time

            if event.event_type == EventType.TICKET_ARRIVAL:
                self._handle_ticket_arrival(event.ticket_id)
            elif event.event_type == EventType.TICKET_COMPLETION:
                self._handle_ticket_completion(event.ticket_id, event.agent_id, event.assignment_attempt)
            elif event.event_type == EventType.TICKET_REROUTE:
                self._handle_ticket_reroute(event.ticket_id)
            elif event.event_type == EventType.AGENT_OFFLINE:
                self._handle_agent_offline(event.agent_id)
            elif event.event_type == EventType.AGENT_ONLINE:
                self._handle_agent_online(event.agent_id)

            outcome = self.assignment_engine.assign_waiting_tickets(
                current_time=self.state.current_time,
                agents=self.state.agents,
                tickets=self.state.tickets,
                queue=self.state.queue,
                next_sequence=next_sequence,
            )
            next_sequence += len(outcome.completion_events)
            for assignment in outcome.assignments:
                self.logger.log(
                    time=self.state.current_time,
                    action="ticket_assigned",
                    ticket_id=assignment.ticket_id,
                    agent_id=assignment.agent_id,
                    matched_skill=assignment.matched_skill,
                    queue_size=assignment.queue_size_after,
                )
            for completion_event in outcome.completion_events:
                self.event_queue.push(completion_event)
            for reroute_event in outcome.reroute_events:
                self.event_queue.push(reroute_event)

        agents = []
        for agent in self.state.agents.values():
            agents.append(
                {
                    "agent_id": agent.agent_id,
                    "status": agent.status.value,
                    "max_concurrent": agent.max_concurrent,
                    "handled_ticket_count": agent.handled_ticket_count,
                }
            )

        tickets = []
        for ticket in self.state.tickets.values():
            tickets.append(
                {
                    "ticket_id": ticket.ticket_id,
                    "priority": ticket.priority.value,
                    "category": ticket.category,
                    "created_time": ticket.created_time,
                    "status": ticket.status.value,
                    "assigned_agent_id": ticket.assigned_agent_id,
                    "assigned_time": ticket.assigned_time,
                    "completed_time": ticket.completed_time,
                    "actual_handle_time": ticket.actual_handle_time,
                    "reroute_count": ticket.reroute_count,
                    "remaining_handle_time": ticket.remaining_handle_time,
                }
            )

        result = SimulationResult(
            scenario_name=self.scenario.name,
            dispatcher=self.dispatcher.name,
            final_time=self.state.current_time,
            queue_size=len(self.state.queue),
            agents=sorted(agents, key=lambda item: item["agent_id"]),
            tickets=sorted(tickets, key=lambda item: item["ticket_id"]),
            logs=[entry.to_dict() for entry in self.logger.entries],
            metrics={},
        )
        result.metrics = self.metrics_collector.collect(self.scenario, result).to_dict()

        return result

    def _handle_ticket_arrival(self, ticket_id: str) -> None:
        ticket = self.state.tickets[ticket_id]
        ticket.status = TicketStatus.QUEUED
        self.state.queue.push(ticket_id)
        self.logger.log(
            time=self.state.current_time,
            action="ticket_arrived",
            ticket_id=ticket_id,
            queue_size=len(self.state.queue),
        )

    def _handle_ticket_completion(
        self,
        ticket_id: str | None,
        agent_id: str | None,
        assignment_attempt: int | None,
    ) -> None:
        if ticket_id is None or agent_id is None or assignment_attempt is None:
            return
        ticket = self.state.tickets[ticket_id]
        if (
            ticket.assigned_agent_id != agent_id
            or ticket.assignment_attempt != assignment_attempt
            or ticket.status != TicketStatus.IN_PROGRESS
        ):
            return
        agent = self.state.agents[agent_id]
        ticket.complete(self.state.current_time)
        agent.release(ticket_id)
        agent.handled_ticket_count += 1
        self.logger.log(
            time=self.state.current_time,
            action="ticket_completed",
            ticket_id=ticket_id,
            agent_id=agent.agent_id,
        )

    def _handle_ticket_reroute(self, ticket_id: str | None) -> None:
        if ticket_id is None:
            return
        ticket = self.state.tickets[ticket_id]
        ticket.status = TicketStatus.QUEUED
        self.state.queue.push(ticket_id)
        self.logger.log(
            time=self.state.current_time,
            action="ticket_rerouted",
            ticket_id=ticket_id,
            reroute_count=ticket.reroute_count,
            queue_size=len(self.state.queue),
        )

    def _handle_agent_offline(self, agent_id: str | None) -> None:
        if agent_id is None:
            return
        agent = self.state.agents[agent_id]
        active_ticket_ids = list(agent.active_ticket_ids)
        agent.go_offline()
        self.logger.log(
            time=self.state.current_time,
            action="agent_offline",
            ticket_id="",
            agent_id=agent_id,
        )
        for ticket_id in active_ticket_ids:
            ticket = self.state.tickets[ticket_id]
            agent.release(ticket_id)
            ticket.pause_for_requeue(
                current_time=self.state.current_time,
                extra_penalty=self.scenario.settings.context_switch_penalty_minutes,
            )
            self.state.queue.push(ticket_id)
            self.logger.log(
                time=self.state.current_time,
                action="ticket_requeued_from_offline",
                ticket_id=ticket_id,
                agent_id=agent_id,
                queue_size=len(self.state.queue),
            )

    def _handle_agent_online(self, agent_id: str | None) -> None:
        if agent_id is None:
            return
        agent = self.state.agents[agent_id]
        agent.go_online()
        self.logger.log(
            time=self.state.current_time,
            action="agent_online",
            ticket_id="",
            agent_id=agent_id,
        )

    def _initialize_tickets(self) -> None:
        variation_pct = self.scenario.settings.actual_handle_time_variation_pct
        for ticket in self.state.tickets.values():
            factor = 1.0
            if variation_pct > 0:
                factor += self.random.uniform(-variation_pct, variation_pct)
            actual_handle_time = max(1, round(ticket.estimated_handle_time * factor))
            ticket.initialize_runtime(actual_handle_time=actual_handle_time)
