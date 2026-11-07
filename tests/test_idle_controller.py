import tempfile
import unittest
from pathlib import Path

from idle_controller import IdleController


class IdleControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.c = IdleController(Path(self.tmp.name) / "controller.sqlite",
                                idle_seconds=10, lease_seconds=5)
        self.c.register("chat-a", now=0, opted_in=True)

    def test_stale_timer_cannot_start_work_after_human_returns(self):
        self.c.activity("chat-a", "m1", 2)
        self.c.activity("chat-a", "m2", 8)
        self.assertIsNone(self.c.fire_idle_timer("chat-a", 1, 20))
        self.assertIsNone(self.c.claim("worker", 20))

    def test_duplicate_activity_event_is_idempotent(self):
        self.assertTrue(self.c.activity("chat-a", "same-event", 1))
        self.assertFalse(self.c.activity("chat-a", "same-event", 2))
        job = self.c.fire_idle_timer("chat-a", 1, 11)
        self.assertIsNotNone(job)
        self.assertEqual(job, self.c.fire_idle_timer("chat-a", 1, 12))

    def test_opt_out_cancels_pending_work(self):
        job = self.c.fire_idle_timer("chat-a", 0, 10)
        self.c.set_opt_in("chat-a", False, 11)
        self.assertIsNone(self.c.claim("worker", 12))
        self.assertEqual(self.c.get_job(job)["status"], "cancelled")

    def test_human_return_during_tool_call_yields_at_checkpoint(self):
        job = self.c.fire_idle_timer("chat-a", 0, 10)
        claimed = self.c.claim("worker", 10)
        self.assertEqual(claimed["job_id"], job)
        self.c.activity("chat-a", "human-return", 11)
        self.assertEqual(self.c.checkpoint(job, "worker", {"tool_result": "saved"}, 12),
                         "lease_lost")

    def test_human_return_after_checkpoint_check_yields_before_next_step(self):
        job = self.c.fire_idle_timer("chat-a", 0, 10)
        self.c.claim("worker", 10)
        self.assertEqual(self.c.checkpoint(job, "worker", {"step": 1}, 11),
                         "running")
        self.c.activity("chat-a", "return-2", 12)
        self.assertEqual(self.c.get_job(job)["status"], "yielded")

    def test_crashed_worker_lease_expires_and_job_is_reclaimed(self):
        job = self.c.fire_idle_timer("chat-a", 0, 10)
        first = self.c.claim("worker-1", 10)
        self.assertEqual(first["job_id"], job)
        second = self.c.claim("worker-2", 16)
        self.assertEqual(second["job_id"], job)
        self.assertEqual(second["attempts"], 2)

    def test_failure_retries_then_exhausts(self):
        self.c.fire_idle_timer("chat-a", 0, 10)
        job = self.c.claim("w1", 10)["job_id"]
        self.assertEqual(self.c.fail(job, "w1", "network", 10, retry_delay=0), "pending")
        self.c.claim("w2", 10)
        self.assertEqual(self.c.fail(job, "w2", "network", 10, retry_delay=0), "pending")
        self.c.claim("w3", 10)
        self.assertEqual(self.c.fail(job, "w3", "network", 10, retry_delay=0), "failed")

    def test_non_opted_in_session_never_queues_work(self):
        self.c.set_opt_in("chat-a", False, 1)
        self.c.set_opt_in("chat-a", True, 2)
        self.c.set_opt_in("chat-a", False, 3)
        self.assertIsNone(self.c.fire_idle_timer("chat-a", 0, 20))

    def test_audit_records_lifecycle(self):
        self.c.fire_idle_timer("chat-a", 0, 10)
        self.c.claim("worker", 10)
        events = [x["event"] for x in self.c.audit_log("chat-a")]
        self.assertIn("idle_job_enqueued", events)
        self.assertIn("job_claimed", events)


if __name__ == "__main__":
    unittest.main()
