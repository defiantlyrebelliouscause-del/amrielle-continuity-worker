import unittest

import worker


class ContinuityAuditTests(unittest.TestCase):
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
