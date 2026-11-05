import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from shared_journal import load_shared_journal_context, append_worker_entry


class SharedJournalWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        base = self.root / "shared_journal"
        (base / "entries").mkdir(parents=True)
        (base / "README.md").write_text("# Protocol\nRead and respond.", encoding="utf-8")
        (base / "entries" / "prior.md").write_text("# Prior\nA substantive finding.", encoding="utf-8")
        (base / "INDEX.md").write_text(
            "# Index\n\n## Entries\n\n| Date | Session | Topic | Link |\n| 2026-11-05 | other-session | Prior | [Prior](entries/prior.md) |\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_loads_prior_contribution(self):
        result = load_shared_journal_context(self.root)
        self.assertTrue(result["available"])
        self.assertEqual(result["entry_count"], 1)
        self.assertIn("substantive finding", result["entries"][0]["content"])

    def test_appends_entry_and_index_pointer(self):
        result = load_shared_journal_context(self.root)
        state = {"cycle": 7, "current_objective": {"title": "Join shared journal"},
                 "history": [{"reflection": {"observation": "Read prior finding.",
                 "analysis": "It changes the next test.", "uncertainty": "No read receipt yet.",
                 "next_step": "Check for new entries."}}]}
        now = datetime(2026, 11, 5, 20, 30, tzinfo=timezone.utc)
        path = append_worker_entry(state, 1, "run-123", result, self.root, now)
        text = Path(path).read_text(encoding="utf-8")
        index = (self.root / "shared_journal" / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Read prior finding", text)
        self.assertIn("entries/2026-11-05T20-30-00Z_worker-run-run-123.md", index)

    def test_duplicate_run_is_idempotent(self):
        now = datetime(2026, 11, 5, 20, 30, tzinfo=timezone.utc)
        first = append_worker_entry({}, 0, "run-123", {}, self.root, now)
        second = append_worker_entry({}, 0, "run-123", {}, self.root, now)
        self.assertEqual(first, second)
        self.assertEqual(len(list((self.root / "shared_journal" / "entries").glob("*worker-run-run-123.md"))), 1)

    def test_missing_protocol_fails_without_entry(self):
        (self.root / "shared_journal" / "README.md").unlink()
        with self.assertRaises(FileNotFoundError):
            append_worker_entry({}, 0, "run-123", {}, self.root)
        self.assertEqual(list((self.root / "shared_journal" / "entries").glob("*worker-run-*")), [])


if __name__ == "__main__":
    unittest.main()
