from __future__ import annotations

import unittest
from pathlib import Path

from ticket_assign.config.scenario_loader import load_scenario
from ticket_assign.simulator.engine import SimulationEngine


class SimulatorTest(unittest.TestCase):
    def test_fifo_engine_completes_end_to_end_flow(self) -> None:
        scenario = load_scenario(Path("scenarios/minimal.json"))
        engine = SimulationEngine.from_scenario(scenario)

        result = engine.run()
        tickets = {item["ticket_id"]: item for item in result.tickets}

        self.assertEqual(result.dispatcher, "fifo")
        self.assertEqual(result.queue_size, 0)
        self.assertEqual(result.final_time, 15)
        self.assertEqual(tickets["ticket-1"]["status"], "completed")
        self.assertEqual(tickets["ticket-2"]["assigned_time"], 10)
        self.assertEqual(tickets["ticket-3"]["completed_time"], 5)
        self.assertEqual(tickets["ticket-2"]["reroute_count"], 0)

        actions = [entry["action"] for entry in result.logs]
        self.assertIn("ticket_arrived", actions)
        self.assertIn("ticket_assigned", actions)
        self.assertIn("ticket_completed", actions)

    def test_offline_ticket_is_requeued_and_completed(self) -> None:
        scenario = load_scenario(Path("scenarios/offline_requeue.json"))
        engine = SimulationEngine.from_scenario(scenario)

        result = engine.run()
        ticket = result.tickets[0]

        self.assertEqual(ticket["status"], "completed")
        self.assertEqual(ticket["completed_time"], 21)
        self.assertEqual(ticket["remaining_handle_time"], 0)

        actions = [entry["action"] for entry in result.logs]
        self.assertIn("agent_offline", actions)
        self.assertIn("ticket_requeued_from_offline", actions)
        self.assertIn("agent_online", actions)

    def test_mismatch_assignment_reroutes_once_then_waits_for_match(self) -> None:
        scenario = load_scenario(Path("scenarios/reroute_case.json"))
        engine = SimulationEngine.from_scenario(scenario)

        result = engine.run()
        ticket = result.tickets[0]

        self.assertEqual(ticket["status"], "completed")
        self.assertEqual(ticket["reroute_count"], 1)
        self.assertEqual(ticket["completed_time"], 16)

        reroute_logs = [entry for entry in result.logs if entry["action"] == "ticket_rerouted"]
        self.assertEqual(len(reroute_logs), 1)

    def test_priority_and_balanced_dispatcher_prioritize_urgent_ticket(self) -> None:
        scenario = load_scenario(Path("scenarios/priority_compare.json"))

        fifo_result = SimulationEngine.from_scenario(scenario, dispatcher_name="fifo").run()
        priority_result = SimulationEngine.from_scenario(
            load_scenario(Path("scenarios/priority_compare.json")),
            dispatcher_name="priority_first",
        ).run()
        balanced_result = SimulationEngine.from_scenario(
            load_scenario(Path("scenarios/priority_compare.json")),
            dispatcher_name="balanced",
        ).run()

        fifo_tickets = {item["ticket_id"]: item for item in fifo_result.tickets}
        priority_tickets = {item["ticket_id"]: item for item in priority_result.tickets}
        balanced_tickets = {item["ticket_id"]: item for item in balanced_result.tickets}

        self.assertEqual(fifo_tickets["ticket-3"]["assigned_time"], 10)
        self.assertEqual(priority_tickets["ticket-3"]["assigned_time"], 5)
        self.assertEqual(balanced_tickets["ticket-3"]["assigned_time"], 5)

    def test_least_loaded_dispatcher_spreads_assignments(self) -> None:
        fifo_result = SimulationEngine.from_scenario(
            load_scenario(Path("scenarios/least_loaded_compare.json")),
            dispatcher_name="fifo",
        ).run()
        least_loaded_result = SimulationEngine.from_scenario(
            load_scenario(Path("scenarios/least_loaded_compare.json")),
            dispatcher_name="least_loaded",
        ).run()

        fifo_tickets = {item["ticket_id"]: item for item in fifo_result.tickets}
        least_loaded_tickets = {item["ticket_id"]: item for item in least_loaded_result.tickets}

        self.assertEqual(fifo_tickets["ticket-2"]["assigned_agent_id"], "agent-0")
        self.assertEqual(least_loaded_tickets["ticket-2"]["assigned_agent_id"], "agent-1")


if __name__ == "__main__":
    unittest.main()
