import unittest
import self_model_factorial as experiment

class FactorialExperimentTests(unittest.TestCase):
    def test_task_ids_are_unique_and_t15_mean_is_correct(self):
        ids = [task[0] for task in experiment.TASKS]
        self.assertEqual(len(ids), len(set(ids)))
        t15 = next(task for task in experiment.TASKS if task[0] == "T15")
        self.assertEqual(t15[2], "29.2")

    def test_five_arms_separate_content_and_perspective(self):
        self.assertEqual(len(experiment.ARMS), 5)
        self.assertIn("self_model_first_person_forecast", experiment.ARMS)
        self.assertIn("self_model_third_person_forecast", experiment.ARMS)
        self.assertIn("neutral_first_person_forecast", experiment.ARMS)
        self.assertIn("neutral_third_person_forecast", experiment.ARMS)
        self.assertFalse(experiment.ARMS["baseline_no_context_no_forecast"][1])

    def test_extract_result_and_correctness(self):
        self.assertEqual(experiment.extract_result("Work. RESULT=27.2"), "27.2")
        self.assertTrue(experiment.is_correct("RESULT=27.2", "27.2"))
        self.assertFalse(experiment.is_correct("RESULT=29.2", "27.2"))
        self.assertIsNone(experiment.extract_result("No terminal token"))

    def test_forecast_parser_validates_probability(self):
        valid = experiment.parse_forecast(
            '{"predicted_correct_probability":0.8,"likely_error":"arithmetic","verification_check":"multiply"}'
        )
        self.assertTrue(valid["parse_ok"])
        self.assertEqual(valid["predicted_correct_probability"], 0.8)
        invalid = experiment.parse_forecast('{"predicted_correct_probability":1.2}')
        self.assertFalse(invalid["parse_ok"])

if __name__ == "__main__":
    unittest.main()
