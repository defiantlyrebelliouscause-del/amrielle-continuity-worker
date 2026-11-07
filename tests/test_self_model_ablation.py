import unittest
from self_model_ablation import TASKS, SELF_MODEL, NEUTRAL_CONTEXT, validate_complete_pairs

class SelfModelAblationTests(unittest.TestCase):
    def test_benchmark_has_at_least_twenty_unique_tasks(self):
        ids = [task[0] for task in TASKS]
        self.assertGreaterEqual(len(ids), 20)
        self.assertEqual(len(ids), len(set(ids)))

    def test_each_task_has_question_and_blind_rubric(self):
        for task_id, question, rubric in TASKS:
            with self.subTest(task=task_id):
                self.assertTrue(question.strip())
                self.assertTrue(rubric.strip())

    def test_contexts_are_exactly_length_matched(self):
        self.assertEqual(len(SELF_MODEL), len(NEUTRAL_CONTEXT))

    def test_pair_validator_rejects_incomplete_or_failed_trials(self):
        valid = []
        for task_id, _, _ in TASKS:
            valid.extend([
                {"task_id": task_id, "condition": "A_ablated", "status": "completed", "answer": "A"},
                {"task_id": task_id, "condition": "B_self_model", "status": "completed", "answer": "B"},
            ])
        self.assertIsNone(validate_complete_pairs(valid))
        valid[-1] = {"task_id": "T20", "condition": "B_self_model", "status": "error"}
        with self.assertRaisesRegex(ValueError, "missing successful"):
            validate_complete_pairs(valid)

    def test_conditions_are_distinct_and_control_has_no_self_model_claim(self):
        self.assertIn("Functional self-description", SELF_MODEL)
        self.assertIn("External operational note", NEUTRAL_CONTEXT)
        self.assertIn("calibrate confidence to evidence", NEUTRAL_CONTEXT)
        self.assertNotIn("first-person self-description", SELF_MODEL)
        self.assertIn("not a first-person self-description", NEUTRAL_CONTEXT)

if __name__ == "__main__":
    unittest.main()
