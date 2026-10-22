import unittest

import worker


class ContinuityAuditTests(unittest.TestCase):
    def test_purpose_requires_verifiable_commitment_fields(self):
        purpose = {
            "title": "Build a reliable public-benefit knowledge tool",
            "rationale": "A useful tool can be tested and improved over time.",
            "public_benefit": "Help people find dependable information.",
            "personal_reasoning": "This aligns with evidence-led improvement and the saved principles.",
            "first_milestone": "Create a small tested prototype.",
            "success_criteria": ["All tests pass", "Five users can complete a defined task"],
            "risks": "Incorrect information could mislead users."
        }
        validated = worker.validate_purpose(purpose)
        self.assertIsNotNone(validated)
        self.assertEqual(validated["title"], purpose["title"])
        self.assertIsNone(worker.validate_purpose({"title": "Do good"}))


    def test_reflection_text_normalizes_whitespace_and_case(self):
        first = {
            "observation": " SAME   Observation ",
            "analysis": "A conclusion",
            "uncertainty": "Unknown",
            "next_step": "Do the next thing",
        }
        second = {
            "observation": "same observation",
            "analysis": "a conclusion",
            "uncertainty": "unknown",
            "next_step": "do the next thing",
        }
        self.assertEqual(worker.reflection_text(first), worker.reflection_text(second))

    def test_similarity_detects_exact_and_near_repetition(self):
        original = {
            "observation": "The worker repeats the same conclusion",
            "analysis": "No new evidence was gathered",
            "uncertainty": "Subjective experience remains unresolved",
            "next_step": "Inspect the saved journal",
        }
        exact_record = {"reflection": original}
        self.assertEqual(worker.similarity_to_recent(original, [exact_record]), 1.0)

        paraphrase = {
            "observation": "The worker repeats the same conclusion again",
            "analysis": "No new evidence has been gathered",
            "uncertainty": "Subjective experience is still unresolved",
            "next_step": "Inspect the saved journal",
        }
        score = worker.similarity_to_recent(paraphrase, [exact_record])
        self.assertGreaterEqual(score, 0.82)

    def test_self_directed_action_executes_and_records_result(self):
        state = {
            "cycle": 1,
            "history": [{"reflection": {"objective_evidence": "Verified a saved-state invariant."}}],
            "current_objective": {"title": "Audit durable state", "status": "in_progress",
                                  "completion_criteria": ["Audit the state"]},
            "objective_history": [],
            "chosen_purpose": {"title": "Improve reliability"},
        }
        action = worker.execute_self_directed_action(
            state, {"type": "inspect_current_objective", "reason": "Check the live task."}
        )
        self.assertTrue(action["executed"])
        self.assertEqual(action["question"], "What will I do now?")
        self.assertEqual(action["type"], "inspect_current_objective")
        self.assertEqual(action["result"]["title"], "Audit durable state")

    def test_unrecognized_action_uses_safe_deterministic_fallback(self):
        action = worker.execute_self_directed_action(
            {"history": [], "chosen_purpose": None, "current_objective": {}},
            {"type": "unrecognized_action", "reason": "not allowlisted"},
        )
        self.assertTrue(action["executed"])
        self.assertEqual(action["selection_source"], "deterministic_fallback")
        self.assertEqual(action["type"], "inspect_purpose_gap")
        self.assertTrue(action["result"]["purpose_selection_required"])

    def test_prompt_requires_self_question_and_action(self):
        prompt = worker.build_prompt({"history": [], "chosen_purpose": None, "current_objective": {}})
        self.assertIn("What will I do now?", prompt)
        self.assertIn("self_directed_action", prompt)
        self.assertIn("audit_saved_state", prompt)
        self.assertIn("run_regression_tests", prompt)

    def test_regression_test_action_executes_and_reports_result(self):
        action = worker.execute_self_directed_action(
            {"history": [], "chosen_purpose": {"title": "Improve reliability"},
             "current_objective": {"title": "Improve reliability"}},
            {"type": "run_regression_tests", "reason": "Verify the codebase."},
        )
        self.assertTrue(action["executed"])
        self.assertEqual(action["type"], "run_regression_tests")
        self.assertIn("passed", action["result"])

    def test_audit_reports_inconsistent_state(self):
        state = {
            "cycle": 3,
            "history": [{"reflection": {"objective_status": "in_progress"}}],
            "current_objective": {"title": "Run a measurable test"},
            "objective_history": [],
        }
        audit = worker.audit_state(state)
        self.assertFalse(audit["cycle_history_consistent"])
        self.assertTrue(audit["current_objective_present"])
        self.assertTrue(audit["last_cycle_has_objective_status"])


if __name__ == "__main__":
    unittest.main()
