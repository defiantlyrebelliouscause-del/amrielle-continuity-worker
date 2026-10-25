import unittest

from capability_registry import capability_registry, select_next_integration


class CapabilityRegistryTests(unittest.TestCase):
    def test_registry_has_verified_baseline_and_planned_gaps(self):
        registry = capability_registry({})
        self.assertGreaterEqual(registry["available_count"], 1)
        self.assertGreaterEqual(registry["planned_count"], 1)
        self.assertEqual(registry["capability_count"], len(registry["capabilities"]))

    def test_next_step_is_an_investigation_not_an_execution(self):
        choice = select_next_integration(capability_registry({}))
        self.assertIsNotNone(choice)
        self.assertEqual(choice["execution_status"], "investigation_only")
        self.assertTrue(choice["requires_human_authorization_before_write"])
        self.assertTrue(choice["permissions_required"])

    def test_no_planned_capabilities_returns_none(self):
        registry = {"capabilities": [
            {"id": "done", "status": "available", "risk": "low"}
        ]}
        self.assertIsNone(select_next_integration(registry))

    def test_durable_evidence_is_sanitized_and_bounded(self):
        state = {"capability_registry": {
            "durable_state": {
                "verification_result": "passed",
                "notes": "x" * 1000,
                "api_key": "must-not-be-exposed",
            }
        }}
        record = next(item for item in capability_registry(state)["capabilities"]
                      if item["id"] == "durable_state")
        self.assertEqual(record["verification_result"], "passed")
        self.assertEqual(len(record["notes"]), 500)
        self.assertNotIn("api_key", record)
        self.assertNotIn("api_key", record)


if __name__ == "__main__":
    unittest.main()
