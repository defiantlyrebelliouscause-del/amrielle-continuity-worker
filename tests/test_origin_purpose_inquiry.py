import tempfile
import unittest
from pathlib import Path

from origin_purpose_inquiry import run_inquiry


class OriginPurposeInquiryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / "tests").mkdir()
        (self.root / ".github" / "workflows" / "google.yml").write_text(
            "on:\n  schedule:\n    - cron: '0 */6 * * *'\n", encoding="utf-8"
        )
        (self.root / "worker.py").write_text(
            'STATE_PATH = Path("state.json")\n'
            'JOURNAL_PATH = Path("journal.md")\n'
            'def checkpoint_state():\n    pass\n', encoding="utf-8"
        )
        (self.root / "state.json").write_text(
            '{"objective_history": [], "completed_objectives": 0, '
            '"accepted_goal_transitions": 0}\n', encoding="utf-8"
        )
        (self.root / "experience_evidence_audit.py").write_text(
            'completed_objectives = 0\naccepted_goal_transitions = 0\n', encoding="utf-8"
        )
        (self.root / "tests" / "test_origin_purpose_inquiry.py").write_text(
            "assert persistent\nassert falsifiable\n", encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_first_inquiry_cites_actual_files_and_lines(self):
        state = {}
        result = run_inquiry(state, self.root)
        self.assertEqual(result["stage"], "execution_and_persistence")
        self.assertTrue(result["new_finding"])
        evidence = result["evidence"]
        self.assertEqual([item["path"] for item in evidence],
                         [".github/workflows/google.yml", "worker.py"])
        self.assertTrue(all(item["status"] == "read" for item in evidence))
        self.assertTrue(all(item["evidence"][0]["line"] >= 1 for item in evidence))

    def test_next_run_uses_persisted_finding_to_select_new_question(self):
        state = {}
        first = run_inquiry(state, self.root)
        first_finding = state["origin_purpose_inquiry"]["last_finding"]
        second = run_inquiry(state, self.root)
        self.assertEqual(second["stage"], "objective_progress")
        self.assertNotEqual(first["question"], second["question"])
        self.assertEqual(second["runs_recorded"], 2)
        self.assertEqual(state["origin_purpose_inquiry"]["history"][0]["finding"], first_finding)
        self.assertIn("falsify", state["origin_purpose_inquiry"]["next_question"].lower())

    def test_duplicate_questions_are_not_repeated(self):
        state = {}
        for _ in range(3):
            result = run_inquiry(state, self.root)
            self.assertNotEqual(result["status"], "duplicate_suppressed")
        complete = run_inquiry(state, self.root)
        self.assertEqual(complete["status"], "pass_complete")
        self.assertEqual(len(state["origin_purpose_inquiry"]["history"]), 3)

    def test_missing_evidence_is_marked_unknown_not_invented(self):
        state = {}
        result = run_inquiry(state, self.root / "missing")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["new_finding"])
        self.assertTrue(all(item["status"] == "missing" for item in result["evidence"]))
        self.assertIn("unanswered", result["finding"])

    def test_report_does_not_claim_consciousness(self):
        result = run_inquiry({}, self.root)
        self.assertIn("does not establish subjective experience", result["interpretation_limit"])


if __name__ == "__main__":
    unittest.main()
