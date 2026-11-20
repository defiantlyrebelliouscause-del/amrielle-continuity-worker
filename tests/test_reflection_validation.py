import unittest

from reflection_validation import validate_reflection


class ReflectionValidationTests(unittest.TestCase):
    def good_reflection(self):
        return {
            "observation": "The prior run's test output shows the validation branch executed.",
            "analysis": "The result is consistent with the recorded code path.",
            "uncertainty": "The test does not establish whether the external source is correct.",
            "objective_status": "in_progress",
            "objective_evidence": "Test artifact: tests/test_worker.py, run 43907228478; result recorded.",
            "next_step": "Inspect the failing assertion and add a regression case.",
            "next_action_plan": {"url": "https://github.com/example/repo"},
        }

    def test_accepts_sourced_reflection_with_explicit_uncertainty(self):
        result = validate_reflection(self.good_reflection())
        self.assertTrue(result["valid"], result["errors"])

    def test_rejects_missing_uncertainty(self):
        reflection = self.good_reflection()
        reflection["uncertainty"] = "Not recorded"
        result = validate_reflection(reflection)
        self.assertFalse(result["valid"])
        self.assertTrue(any("uncertainty" in error for error in result["errors"]))

    def test_rejects_generic_evidence_without_provenance_cue(self):
        reflection = self.good_reflection()
        reflection["objective_evidence"] = "Things seem to be improving and progress is happening."
        result = validate_reflection(reflection)
        self.assertFalse(result["valid"])
        self.assertTrue(any("objective_evidence" in error for error in result["errors"]))

    def test_rejects_placeholder_url(self):
        reflection = self.good_reflection()
        reflection["next_action_plan"]["url"] = "https://example.com/run_ablation"
        result = validate_reflection(reflection)
        self.assertFalse(result["valid"])
        self.assertTrue(any("placeholder URL" in error for error in result["errors"]))

    def test_rejects_non_object_reflection(self):
        self.assertFalse(validate_reflection(["not", "an", "object"])["valid"])


if __name__ == "__main__":
    unittest.main()
