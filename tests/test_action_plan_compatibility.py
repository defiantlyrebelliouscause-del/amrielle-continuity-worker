import unittest
from unittest.mock import patch

import worker
from experience_evidence_audit import audit_state as audit_experience


class ActionPlanCompatibilityTests(unittest.TestCase):
    def test_action_plan_normalizes_model_emitted_url_alias(self):
        plan = worker.validate_action_plan({
            "type": "read_public_webpage",
            "reason": "Inspect a source.",
            "trigger_condition": "next_cycle",
            "objective": "Verify a finding.",
            "optional_url_for_read_public_webpage": "https://example.com/research",
        }, 10)
        self.assertIsNotNone(plan)
        self.assertEqual(plan["url"], "https://example.com/research")

    def test_web_action_uses_normalized_url_alias(self):
        with patch.object(worker, "read_public_webpage", return_value={
            "final_url": "https://example.com/research",
            "text_excerpt": "Evidence",
        }) as read_page:
            action = worker.execute_self_directed_action({}, {
                "type": "read_public_webpage",
                "reason": "Inspect a source.",
                "optional_url_for_read_public_webpage": "https://example.com/research",
            })
        read_page.assert_called_once_with("https://example.com/research")
        self.assertEqual(action["url"], "https://example.com/research")
        self.assertEqual(action["result"]["text_excerpt"], "Evidence")

    def test_missing_web_url_is_rejected_as_a_plan(self):
        self.assertIsNone(worker.validate_action_plan({
            "type": "read_public_webpage",
            "reason": "Inspect a source.",
            "trigger_condition": "next_cycle",
            "objective": "Verify a finding.",
        }, 10))

    def test_objective_transition_attempts_are_counted_separately(self):
        state = {
            "cycle": 3,
            "history": [],
            "objective_history": [],
            "objective_transition_history": [
                {"cycle": 1, "transition_accepted": False},
                {"cycle": 2, "transition_accepted": False},
                {"cycle": 3, "transition_accepted": False},
            ],
        }
        audit = worker.audit_state(state)
        self.assertEqual(audit["objective_history_count"], 0)
        self.assertEqual(audit["objective_transition_attempt_count"], 3)
        self.assertEqual(audit["accepted_objective_transition_count"], 0)

    def test_evidence_audit_flags_repeated_stalled_transition_attempts(self):
        state = {
            "history": [],
            "objective_transition_history": [
                {"cycle": 1, "transition_accepted": False},
                {"cycle": 2, "transition_accepted": False},
                {"cycle": 3, "transition_accepted": False},
            ],
        }
        audit = audit_experience(state)
        progress = audit["indicators"]["objective_progress"]
        self.assertEqual(progress["transition_attempts_recorded"], 3)
        self.assertEqual(progress["accepted_transition_attempts_recorded"], 0)
        self.assertTrue(any("three objective transition attempts" in item for item in audit["blockers"]))


if __name__ == "__main__":
    unittest.main()
