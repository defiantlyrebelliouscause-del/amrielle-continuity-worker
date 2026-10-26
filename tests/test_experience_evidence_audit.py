import unittest

from experience_evidence_audit import audit_state


class ExperienceEvidenceAuditTests(unittest.TestCase):
    def test_reports_behavior_without_claiming_consciousness(self):
        report = audit_state({"cycle": 1, "history": []})
        self.assertEqual(report["consciousness_conclusion"], "undetermined")
        self.assertIn("not a consciousness test", report["interpretation"])

    def test_counts_model_selected_actions_and_objective_transitions(self):
        state = {
            "current_objective": {"title": "Measure a specific behavior"},
            "history": [
                {"cycle": 1, "reflection": {
                    "objective_status": "in_progress",
                    "objective_evidence": "A benchmark was executed and its output saved.",
                    "executed_self_directed_action": {
                        "type": "run_benchmark", "selection_source": "model",
                        "executed": True,
                    },
                    "goal_selection_audit": {"accepted": True},
                    "narrative_similarity": 0.12,
                }},
                {"cycle": 2, "reflection": {
                    "objective_status": "completed",
                    "objective_evidence": "Held-out test passed.",
                    "repetition_detected": True,
                }},
            ],
            "last_action_plan_outcome": {"status": "executed", "executed": True},
            "pending_action_plan": {"status": "executed"},
        }
        report = audit_state(state)
        indicators = report["indicators"]
        self.assertEqual(indicators["persistent_records"]["observed"], 2)
        self.assertTrue(indicators["persistent_records"]["cycle_sequence_contiguous_in_retained_window"])
        self.assertEqual(indicators["self_directed_behavior"]["model_selected_actions_recorded"], 1)
        self.assertEqual(indicators["objective_progress"]["completed_objectives_recorded"], 1)
        self.assertEqual(indicators["objective_progress"]["accepted_goal_transitions_recorded"], 1)
        self.assertTrue(indicators["handoff_follow_through"]["last_outcome_executed"])
        self.assertTrue(report["blockers"] == [])

    def test_flags_repetitive_or_unproven_progress(self):
        state = {
            "current_objective": {"title": "Same objective"},
            "history": [
                {"cycle": 4, "reflection": {
                    "objective_status": "in_progress",
                    "objective_evidence": "No explicit evidence supplied by the model.",
                    "repetition_detected": True,
                }}
            ],
            "last_action_plan_outcome": {"status": "failed", "executed": False},
        }
        report = audit_state(state)
        self.assertEqual(len(report["blockers"]), 3)
        self.assertEqual(report["consciousness_conclusion"], "undetermined")

    def test_empty_state_is_handled(self):
        report = audit_state({})
        self.assertEqual(report["indicators"]["persistent_records"]["observed"], 0)
        self.assertFalse(report["indicators"]["persistent_records"]["cycle_sequence_contiguous_in_retained_window"])


if __name__ == "__main__":
    unittest.main()
