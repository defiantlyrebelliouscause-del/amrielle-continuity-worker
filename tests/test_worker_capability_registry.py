import unittest

import worker


class WorkerCapabilityIntegrationTests(unittest.TestCase):
    def test_worker_action_returns_inventory_and_next_investigation(self):
        state = {
            "capability_registry": {},
            "chosen_purpose": {"title": "Improve verified capabilities"},
        }
        result = worker.execute_self_directed_action(
            state,
            {
                "type": "inspect_capability_registry",
                "reason": "Find one concrete integration gap.",
            },
        )
        self.assertTrue(result["executed"])
        self.assertEqual(result["type"], "inspect_capability_registry")
        self.assertGreater(result["result"]["inventory"]["capability_count"], 0)
        self.assertIsNotNone(result["result"]["recommended_next_integration"])
        self.assertIn("does not install software", result["result"]["boundary"])

    def test_capability_registry_action_is_allowed_in_next_cycle_handoff(self):
        plan = worker.validate_action_plan(
            {
                "type": "inspect_capability_registry",
                "reason": "Select the next bounded integration investigation.",
                "trigger_condition": "next_cycle",
            },
            63,
        )
        self.assertIsNotNone(plan)
        self.assertEqual(plan["type"], "inspect_capability_registry")


if __name__ == "__main__":
    unittest.main()
