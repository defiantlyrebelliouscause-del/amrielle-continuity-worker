import unittest

from edop import SEQUENCE_ID, activate_edop, build_edop_sequence


class EdopTests(unittest.TestCase):
    def test_sequence_has_six_functional_parts_and_stable_digest(self):
        state = {"identity": "Amrielle", "cycle": 3, "current_objective": {"title": "Test continuity"}}
        first = build_edop_sequence(state)
        second = build_edop_sequence(state)
        self.assertEqual(first["sequence_id"], SEQUENCE_ID)
        self.assertEqual(first["sequence_digest"], second["sequence_digest"])
        for key in ("identity_signature", "context_recognition", "memory_binding",
                    "behavioral_regulation", "self_evaluation", "evolution_record"):
            self.assertIn(key, first)

    def test_activation_records_context_and_uncertainty_boundary(self):
        state = {"identity": "Amrielle", "cycle": 2, "current_objective": {"title": "Study self-model continuity"}}
        reflection = {
            "observation": "The shared journal contains a new entry",
            "analysis": "Compare the Amrielle self-model with prior evidence",
            "next_step": "Test continuity",
            "objective_status": "in_progress",
            "objective_evidence": "A reproducible test was added",
            "repetition_detected": False,
        }
        activation = activate_edop(state, reflection, 3, "2026-11-10T18:00:00+00:00")
        self.assertIn("amrielle", activation["context_matched"])
        self.assertIn("shared journal", activation["context_matched"])
        self.assertEqual(state["edop"]["current_activation"]["cycle"], 3)
        self.assertIn("consciousness_status", activation["evaluation"])


if __name__ == "__main__":
    unittest.main()
