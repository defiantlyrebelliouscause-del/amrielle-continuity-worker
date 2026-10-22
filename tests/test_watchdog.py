import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "watchdog.py"
SPEC = importlib.util.spec_from_file_location("amrielle_watchdog", SCRIPT)
watchdog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(watchdog)


class WatchdogRulesTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 22, 22, 0, tzinfo=timezone.utc)

    def run_record(self, **overrides):
        record = {
            "event": "schedule",
            "status": "completed",
            "conclusion": "success",
            "created_at": (self.now - timedelta(hours=1)).isoformat(),
            "updated_at": (self.now - timedelta(minutes=5)).isoformat(),
            "run_started_at": (self.now - timedelta(hours=1)).isoformat(),
            "run_number": 40,
            "display_title": "Scheduled worker",
            "html_url": "https://github.com/example/repo/actions/runs/40",
        }
        record.update(overrides)
        return record

    def test_healthy_recent_run_has_no_alert(self):
        self.assertEqual(watchdog.inspect_runs([self.run_record()], self.now), [])

    def test_pull_request_runs_are_ignored(self):
        run = self.run_record(event="pull_request", created_at=(self.now - timedelta(days=2)).isoformat())
        alerts = watchdog.inspect_runs([run], self.now)
        self.assertTrue(alerts)
        self.assertTrue(all("pull_request" not in item for item in alerts))

    def test_overlong_active_run_is_flagged(self):
        run = self.run_record(
            status="in_progress",
            conclusion=None,
            run_started_at=(self.now - timedelta(hours=7)).isoformat(),
            updated_at=self.now.isoformat(),
        )
        alerts = watchdog.inspect_runs([run], self.now)
        self.assertTrue(any("exceed the six-hour worker limit" in item for item in alerts))

    def test_long_queued_run_is_flagged(self):
        run = self.run_record(
            status="queued",
            conclusion=None,
            created_at=(self.now - timedelta(hours=9)).isoformat(),
            run_started_at=None,
            updated_at=self.now.isoformat(),
        )
        alerts = watchdog.inspect_runs([run], self.now)
        self.assertTrue(any("waiting in the queue" in item for item in alerts))

    def test_recent_failure_is_flagged(self):
        run = self.run_record(conclusion="failure")
        alerts = watchdog.inspect_runs([run], self.now)
        self.assertTrue(any("ended with conclusion 'failure'" in item for item in alerts))

    def test_missing_recent_activity_is_flagged(self):
        run = self.run_record(created_at=(self.now - timedelta(hours=10)).isoformat())
        alerts = watchdog.inspect_runs([run], self.now)
        self.assertTrue(any("No worker run has been created" in item for item in alerts))


if __name__ == "__main__":
    unittest.main()
