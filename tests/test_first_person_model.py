import unittest

from first_person_model import update_first_person_model


class FirstPersonModelTests(unittest.TestCase):
    def test_episode_is_grounded_and_persisted_across_activations(self):
        state = {
            "cycle": 7,
            "current_objective": {"title": "Study trustworthy workplace AI"},
            "first_person_model": {"episodes": [{"cycle": 7}]},
        }
        reflection = {
            "first_person_reflection": {
                "resumed_context": "I resume from the saved workplace-AI objective.",
                "observed_this_cycle": "I recorded two source observations.",
                "unresolved_or_unknown": "The evidence does not establish subjective experience.",
                "next_intended_action": "Compare the two sources.",
            }
        }
        episode = update_first_person_model(
            state, reflection, 8, "2026-10-31T14:00:00+00:00"
        )
        self.assertEqual(episode["cycle"], 8)
        self.assertEqual(episode["mode"], "first_person_functional_self_model")
        self.assertEqual(len(state["first_person_model"]["episodes"]), 2)
        self.assertIn("not independent evidence", episode["epistemic_status"])
        self.assertEqual(episode["next_intended_action"], "Compare the two sources.")

    def test_missing_model_fields_use_transparent_functional_defaults(self):
        state = {"cycle": 2, "current_objective": {"title": "Test persistence"}}
        episode = update_first_person_model(state, {}, 3)
        self.assertIn("episode 3", episode["resumed_context"])
        self.assertIn("No conclusion about subjective experience", episode["unresolved_or_unknown"])
        self.assertIn("not independent evidence", episode["epistemic_status"])

    def test_episode_history_is_bounded(self):
        state = {"cycle": 40, "first_person_model": {"episodes": [{"cycle": n} for n in range(40)]}}
        update_first_person_model(state, {}, 41)
        self.assertEqual(len(state["first_person_model"]["episodes"]), 30)
        self.assertEqual(state["first_person_model"]["episodes"][-1]["cycle"], 41)


if __name__ == "__main__":
    unittest.main()
