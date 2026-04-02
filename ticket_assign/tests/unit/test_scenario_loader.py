from __future__ import annotations

import unittest
from pathlib import Path

from ticket_assign.config.scenario_loader import load_scenario


class ScenarioLoaderTest(unittest.TestCase):
    def test_load_minimal_scenario(self) -> None:
        scenario = load_scenario(Path("scenarios/minimal.json"))
        self.assertEqual(scenario.name, "minimal_fifo_demo")
        self.assertEqual(len(scenario.agents), 2)
        self.assertEqual(len(scenario.tickets), 3)
        self.assertEqual(scenario.tickets[0].ticket_id, "ticket-1")


if __name__ == "__main__":
    unittest.main()

