import unittest

import worker


class EvidenceFallbackTests(unittest.TestCase):
    def test_stalled_objective_falls_back_to_diagnosis_not_regression_tests(self):
        state = {
            "cycle": 83,
            "chosen_purpose": {"title": "Improve reliability"},
            "current_objective": {"title": "Replace repetitive reflection"},
            "history": [{
                "cycle": 83,
                "reflection": {
                    "objective_status": "in_progress",
                    "objective_evidence": "Transition rejected: evidence was generic.",
                    "transition_validation": "Transition rejected: successor failed the goal-selection gate.",
                    "repetition_detected": True,
                },
            }],
            "last_action_plan_outcome": {"status": "executed", "executed": True, "type": "run_regression_tests"},
        }
        action = worker.execute_self_directed_action(
            state, {"type": "not_an_allowed_action", "reason": "force fallback"}
        )
        self.assertEqual(action["type"], "audit_experience_evidence")
        self.assertEqual(action["selection_source"], "deterministic_fallback")
        self.assertIn("No accepted goal transitions", " ".join(action["result"]["blockers"]))

    def test_experience_evidence_audit_is_an_allowlisted_action(self):
        action = worker.execute_self_directed_action(
            {"cycle": 1, "history": [], "current_objective": {"title": "Test evidence"}},
            {"type": "audit_experience_evidence", "reason": "Inspect observable evidence."},
        )
        self.assertTrue(action["executed"])
        self.assertEqual(action["type"], "audit_experience_evidence")
        self.assertEqual(action["result"]["consciousness_conclusion"], "undetermined")

    def test_prompt_exposes_evidence_audit_action(self):
        prompt = worker.build_prompt({"history": [], "chosen_purpose": None, "current_objective": {}})
        self.assertIn("audit_experience_evidence", prompt)


if __name__ == "__main__":
    unittest.main()
