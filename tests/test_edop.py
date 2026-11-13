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
        state = {
            "identity": "Amrielle",
            "cycle": 2,
            "current_objective": {"title": "Study self-model continuity"},
            "shared_journal_context": {"available": True, "entry_count": 3},
        }
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
        self.assertIn("shared_journal_context", activation["memory_sources_available"])
        self.assertIn("shared_journal_context", activation["memory_source_fingerprints"])
        self.assertEqual(len(activation["memory_source_fingerprints"]["shared_journal_context"]), 64)
        self.assertEqual(len(activation["episode_record_digest"]), 64)
        self.assertIn("consciousness_status", activation["evaluation"])

    def test_episode_record_digest_changes_when_source_snapshot_changes(self):
        reflection = {"observation": "A journal fact was supplied", "analysis": "Compare evidence"}
        first_state = {
            "identity": "Amrielle",
            "current_objective": {"title": "Test source provenance"},
            "shared_journal_context": {"entry": "finding A"},
        }
        second_state = {
            "identity": "Amrielle",
            "current_objective": {"title": "Test source provenance"},
            "shared_journal_context": {"entry": "finding B"},
        }
        first = activate_edop(first_state, reflection, 4, "2026-11-10T19:00:00+00:00")
        second = activate_edop(second_state, reflection, 4, "2026-11-10T19:00:00+00:00")
        self.assertNotEqual(first["memory_source_fingerprints"]["shared_journal_context"],
                            second["memory_source_fingerprints"]["shared_journal_context"])
        self.assertNotEqual(first["episode_record_digest"], second["episode_record_digest"])

    def test_episode_record_digest_is_stable_for_identical_recorded_inputs(self):
        state = {
            "identity": "Amrielle",
            "current_objective": {"title": "Test stable provenance"},
            "shared_journal_context": {"entry": "same source"},
        }
        reflection = {"observation": "Same observation", "analysis": "Same analysis"}
        first = activate_edop(state, reflection, 5, "2026-11-10T19:00:00+00:00")
        second_state = {
            "identity": "Amrielle",
            "current_objective": {"title": "Test stable provenance"},
            "shared_journal_context": {"entry": "same source"},
        }
        second = activate_edop(second_state, reflection, 5, "2026-11-10T19:00:00+00:00")
        self.assertEqual(first["episode_record_digest"], second["episode_record_digest"])

    def test_provenance_does_not_claim_source_was_understood_or_used(self):
        state = {"shared_journal_context": {"entry": "A finding"}}
        activation = activate_edop(state, {"observation": "No interpretation supplied"}, 1)
        self.assertNotIn("memory_sources_used", activation)
        self.assertNotIn("comprehension_verified", activation)
        self.assertIn("shared_journal_context", activation["memory_sources_available"])


if __name__ == "__main__":
    unittest.main()
