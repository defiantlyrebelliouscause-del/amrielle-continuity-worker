import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from shared_journal import append_conversation_entry


class ConversationJournalSubmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        journal = self.root / "shared_journal"
        (journal / "entries").mkdir(parents=True)
        (journal / "README.md").write_text("# Protocol\n", encoding="utf-8")
        (journal / "INDEX.md").write_text("# Journal\n\n## Entries\n", encoding="utf-8")
        self.now = datetime(2026, 11, 11, 19, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def test_appends_attributed_entry_and_index_row(self):
        path = append_conversation_entry(
            "/journal-entry\n## Finding\nA distinct contribution.",
            "monday-chat",
            "comment-123",
            "https://github.com/example/repo/issues/82",
            root=self.root,
            now=self.now,
        )
        saved = Path(path).read_text(encoding="utf-8")
        index = (self.root / "shared_journal" / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Participant (GitHub author): monday-chat", saved)
        self.assertIn("Source comment ID: comment-123", saved)
        self.assertIn("A distinct contribution.", saved)
        self.assertIn(Path(path).name, index)

    def test_retry_with_same_comment_id_is_idempotent(self):
        args = ("/journal-entry\nOne entry.", "monday-chat", "comment-123")
        first = append_conversation_entry(*args, root=self.root, now=self.now)
        second = append_conversation_entry(*args, root=self.root, now=self.now)
        self.assertEqual(first, second)
        files = list((self.root / "shared_journal" / "entries").glob("*.md"))
        self.assertEqual(len(files), 1)

    def test_requires_explicit_command_and_nonempty_body(self):
        with self.assertRaises(ValueError):
            append_conversation_entry("Just text", "monday-chat", "comment-1", root=self.root)
        with self.assertRaises(ValueError):
            append_conversation_entry("/journal-entry\n", "monday-chat", "comment-2", root=self.root)

    def test_rejects_oversized_contribution(self):
        with self.assertRaises(ValueError):
            append_conversation_entry(
                "/journal-entry\n" + ("x" * 12001),
                "monday-chat",
                "comment-3",
                root=self.root,
            )


if __name__ == "__main__":
    unittest.main()
