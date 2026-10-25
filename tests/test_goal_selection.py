import unittest

from goal_selection import score_candidate, select_candidate, similarity


CURRENT = "Replace repetitive reflection with evidence-based objective progression"
GOOD = {
    "title": "Measure objective selection quality across twelve fixed test cases",
    "evidence": "Repository file research/goal-selection-benchmark.md describes the 12-case test plan.",
    "completion_criteria": ["At least 10 of 12 fixed cases produce the expected selection status"],
    "public_benefit": "Reduce wasted worker cycles so maintainers can trust useful, auditable progress.",
    "risk_level": "read_only",
}


class GoalSelectionTests(unittest.TestCase):
    def test_good_candidate_qualifies(self):
        result = score_candidate(GOOD, CURRENT)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["total_score"], 10)

    def test_exact_repeat_is_rejected(self):
        candidate = dict(GOOD, title=CURRENT)
        result = score_candidate(candidate, CURRENT)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["scores"]["novelty"], 0)

    def test_paraphrase_is_rejected(self):
        self.assertGreater(similarity("Improve system reliability", "Improve the system reliability"), 0.7)

    def test_missing_evidence_is_rejected(self):
        result = score_candidate(dict(GOOD, evidence=""), CURRENT)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["scores"]["evidence"], 0)

    def test_vague_criteria_are_rejected(self):
        result = score_candidate(dict(GOOD, completion_criteria=["Make progress"]), CURRENT)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["scores"]["measurability"], 0)

    def test_unsafe_risk_is_rejected(self):
        result = score_candidate(dict(GOOD, risk_level="unrestricted_external_action"), CURRENT)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["scores"]["bounded_risk"], 0)

    def test_generic_benefit_is_rejected(self):
        result = score_candidate(dict(GOOD, public_benefit="Improve the system"), CURRENT)
        self.assertFalse(result["accepted"])

    def test_no_qualified_candidate_abstains(self):
        result = select_candidate([{"title": CURRENT}], CURRENT)
        self.assertIsNone(result["selection"])
        self.assertEqual(result["status"], "no_qualified_objective")

    def test_selects_eligible_candidate(self):
        result = select_candidate([{"title": CURRENT}, GOOD], CURRENT)
        self.assertEqual(result["selection"], GOOD)
        self.assertEqual(result["status"], "selected")

    def test_empty_title_fails(self):
        self.assertFalse(score_candidate(dict(GOOD, title=""), CURRENT)["accepted"])

    def test_recent_duplicate_is_rejected(self):
        result = score_candidate(GOOD, "unrelated objective", [GOOD["title"]])
        self.assertFalse(result["accepted"])

    def test_evidence_truth_is_not_claimed(self):
        result = score_candidate(GOOD, CURRENT)
        self.assertIn("require review", result["note"])


if __name__ == "__main__":
    unittest.main()
