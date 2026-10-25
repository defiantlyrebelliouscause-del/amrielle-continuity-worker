import unittest

from goal_selection import score_candidate


class ObjectiveGateSmokeTest(unittest.TestCase):
    def test_gate_module_is_importable_and_rejects_missing_evidence(self):
        result = score_candidate({
            "title": "Measure a new objective",
            "evidence": "",
            "completion_criteria": ["At least 3 cases pass"],
            "public_benefit": "Reduce repeated work and improve auditability for maintainers.",
            "risk_level": "read_only",
        }, "A different objective")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["scores"]["evidence"], 0)


if __name__ == "__main__":
    unittest.main()
