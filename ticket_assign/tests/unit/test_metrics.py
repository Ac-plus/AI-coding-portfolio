from __future__ import annotations

import unittest
from pathlib import Path

from ticket_assign.config.scenario_loader import load_scenario
from ticket_assign.simulator.engine import SimulationEngine


class MetricsTest(unittest.TestCase):
    def test_metrics_summary_is_generated_for_minimal_scenario(self) -> None:
        result = SimulationEngine.from_scenario(
            load_scenario(Path("scenarios/minimal.json"))
        ).run()
        metrics = result.metrics

        self.assertIn("response", metrics)
        self.assertIn("efficiency", metrics)
        self.assertIn("utilization", metrics)
        self.assertIn("fairness", metrics)
        self.assertIn("misassignment", metrics)

        self.assertEqual(metrics["response"]["p1_avg_wait_minutes"], 0.0)
        self.assertEqual(metrics["response"]["p1_p95_wait_minutes"], 0.0)
        self.assertEqual(metrics["response"]["p1_sla_rate"], 1.0)
        self.assertAlmostEqual(metrics["efficiency"]["avg_wait_minutes"], 3.0)
        self.assertAlmostEqual(metrics["efficiency"]["avg_completion_minutes"], 9.0)
        self.assertAlmostEqual(metrics["efficiency"]["avg_queue_length"], 0.6)
        self.assertAlmostEqual(metrics["utilization"]["avg_agent_utilization"], 0.6)
        self.assertAlmostEqual(metrics["utilization"]["agent_utilization_variance"], 0.16)
        self.assertEqual(metrics["utilization"]["peak_hour_throughput"], 3)
        self.assertEqual(metrics["fairness"]["max_tickets_per_agent"], 2)
        self.assertEqual(metrics["fairness"]["min_tickets_per_agent"], 1)
        self.assertAlmostEqual(metrics["fairness"]["ticket_count_variance"], 0.25)
        self.assertEqual(metrics["fairness"]["longest_normal_wait_minutes"], 9.0)
        self.assertEqual(metrics["fairness"]["starvation_ticket_count"], 0)
        self.assertEqual(metrics["misassignment"]["mismatch_assignment_count"], 0)
        self.assertEqual(metrics["misassignment"]["reroute_extra_cost_minutes"], 0)

    def test_metrics_capture_misassignment_and_reroute_cost(self) -> None:
        result = SimulationEngine.from_scenario(
            load_scenario(Path("scenarios/reroute_case.json"))
        ).run()
        metrics = result.metrics

        self.assertEqual(metrics["misassignment"]["mismatch_assignment_count"], 1)
        self.assertEqual(metrics["misassignment"]["reroute_extra_cost_minutes"], 5)
        self.assertEqual(metrics["efficiency"]["reroute_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()

