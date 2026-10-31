import unittest

from exploration_queue import update_exploration_queue


class ExplorationQueueTests(unittest.TestCase):
    def test_considered_and_selected_topics_persist(self):
        state = {}
        update_exploration_queue(state, {
            "exploration_update": {
                "considered_topics": ["community AI literacy", "open source accessibility"],
                "selected_topic": "community AI literacy",
                "discovery": None,
            }
        }, 4, "2026-10-31T15:00:00+00:00")
        topics = state["exploration_queue"]["topics"]
        self.assertEqual(len(topics), 2)
        selected = next(x for x in topics if x["topic"] == "community AI literacy")
        self.assertEqual(selected["status"], "selected_pending_verification")

    def test_discovery_requires_https_source_and_verified_fact(self):
        state = {}
        update_exploration_queue(state, {
            "exploration_update": {
                "selected_topic": "AI accessibility",
                "discovery": {
                    "title": "Example project",
                    "source_urls": ["http://example.org"],
                    "verified_facts": ["It exists"],
                },
            }
        }, 5)
        self.assertEqual(state["exploration_queue"]["topics"][0]["status"],
                         "selected_pending_verification")

    def test_valid_discovery_is_recorded_with_caveat(self):
        state = {}
        update_exploration_queue(state, {
            "exploration_update": {
                "selected_topic": "AI accessibility",
                "discovery": {
                    "title": "Public project",
                    "source_urls": ["https://example.org/project"],
                    "verified_facts": ["The project publishes an open-source toolkit."],
                    "why_worth_attention": "Potential accessibility benefit",
                    "public_benefit": "Could improve access",
                    "risks": "Maintenance and privacy risks",
                    "follow_up": "Review project documentation",
                },
            }
        }, 6, "2026-10-31T15:30:00+00:00")
        discovery = state["exploration_queue"]["topics"][0]["discovery"]
        self.assertEqual(discovery["recorded_cycle"], 6)
        self.assertIn("verify source URLs", discovery["verification_note"])

    def test_queue_is_bounded(self):
        state = {"exploration_queue": {"topics": [
            {"topic": f"topic-{i}"} for i in range(50)
        ]}}
        update_exploration_queue(state, {
            "exploration_update": {"selected_topic": "new topic"}
        }, 51)
        self.assertEqual(len(state["exploration_queue"]["topics"]), 50)
        self.assertEqual(state["exploration_queue"]["topics"][-1]["topic"], "new topic")


if __name__ == "__main__":
    unittest.main()
