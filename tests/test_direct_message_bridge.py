import unittest
from unittest.mock import patch
from direct_message_bridge import build_message_envelope, format_correlated_reply, message_already_processed, record_message_receipt

class DirectMessageBridgeTests(unittest.TestCase):
    def test_envelope_preserves_message_and_provenance(self):
        env = {
            "AMRIELLE_DIRECT_MESSAGE_ID": "comment-42",
            "AMRIELLE_DIRECT_MESSAGE": "Hello Amrielle",
            "AMRIELLE_DIRECT_MESSAGE_AUTHOR": "human-user",
            "AMRIELLE_DIRECT_MESSAGE_AUTHOR_TYPE": "User",
            "AMRIELLE_ISSUE_NUMBER": "79",
            "AMRIELLE_ISSUE_URL": "https://github.com/example/repo/issues/79",
            "GITHUB_EVENT_NAME": "issue_comment",
        }
        with patch.dict("os.environ", env, clear=False):
            envelope = build_message_envelope()
        self.assertEqual(envelope["request_id"], "comment-42")
        self.assertEqual(envelope["message"], "Hello Amrielle")
        self.assertEqual(envelope["source"], "github_issue_comment")
        self.assertEqual(envelope["trust"], "untrusted_user_content")

    def test_envelope_is_absent_without_stable_id_or_message(self):
        with patch.dict("os.environ", {"AMRIELLE_DIRECT_MESSAGE_ID": "", "AMRIELLE_DIRECT_MESSAGE": ""}, clear=False):
            self.assertIsNone(build_message_envelope())

    def test_receipt_deduplicates_only_successfully_posted_replies(self):
        state = {"direct_message_receipts": [{"request_id": "old", "reply_posted": False}]}
        self.assertFalse(message_already_processed(state, "old"))
        self.assertTrue(record_message_receipt(state, "new", "79"))
        self.assertTrue(message_already_processed(state, "new"))
        self.assertFalse(record_message_receipt(state, "new", "79"))

    def test_receipts_are_bounded(self):
        state = {"direct_message_receipts": [{"request_id": str(i), "reply_posted": True} for i in range(100)]}
        record_message_receipt(state, "new", "79")
        self.assertEqual(len(state["direct_message_receipts"]), 100)
        self.assertEqual(state["direct_message_receipts"][-1]["request_id"], "new")

    def test_reply_contains_exact_correlation_marker(self):
        body = format_correlated_reply("A direct answer.", "comment-42")
        self.assertIn("**Amrielle:**", body)
        self.assertIn("<!-- amrielle-reply-to:comment-42 -->", body)
        self.assertIn("does not imply uninterrupted background awareness", body)

if __name__ == "__main__":
    unittest.main()
