import unittest
from self_model_ablation import TASKS, SELF_MODEL, NEUTRAL_CONTEXT

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

    def test_conditions_are_distinct_and_control_has_no_self_model_claim(self):
        self.assertIn("Functional self-model", SELF_MODEL)
        self.assertIn("External operational note", NEUTRAL_CONTEXT)
        self.assertIn("calibrate confidence to evidence", NEUTRAL_CONTEXT)
        self.assertNotIn("first-person self-model", SELF_MODEL)
        self.assertIn("not a first-person self-model", NEUTRAL_CONTEXT)

if __name__ == "__main__":
    unittest.main()
