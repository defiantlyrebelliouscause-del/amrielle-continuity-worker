import hashlib
import hmac
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from idle_controller import IdleController
from idle_event_server import make_handler, run_scheduler, signed_payload


class EventServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.controller = IdleController(Path(self.tmp.name) / "events.sqlite",
                                         idle_seconds=10, lease_seconds=5)
        self.secret = "test-secret-that-is-at-least-32-characters"
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), make_handler(self.controller, self.secret,
                                           clock=lambda: 100.0))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.shutdown)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.thread.join)
        self.base = "http://127.0.0.1:%d" % self.server.server_address[1]

    def post(self, path, data, secret=None):
        body = json.dumps(data).encode()
        signature = signed_payload(secret or self.secret, body)
        request = Request(self.base + path, data=body, method="POST",
                          headers={"Content-Type": "application/json",
                                   "X-Amrielle-Signature": signature})
        try:
            with urlopen(request) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_signed_opt_in_registration_and_activity(self):
        status, result = self.post("/v1/sessions",
                                   {"session_id": "opaque-1", "opted_in": True})
        self.assertEqual(status, 201)
        self.assertTrue(result["registered"])
        status, result = self.post("/v1/activity",
                                   {"session_id": "opaque-1", "event_id": "evt-1"})
        self.assertEqual(status, 202)
        self.assertTrue(result["accepted"])

    def test_invalid_signature_is_rejected(self):
        status, result = self.post("/v1/sessions",
                                   {"session_id": "opaque-2", "opted_in": True},
                                   secret="wrong-secret")
        self.assertEqual(status, 401)
        self.assertEqual(result["error"], "invalid_signature")

    def test_activity_requires_registered_session(self):
        status, result = self.post("/v1/activity",
                                   {"session_id": "unknown", "event_id": "evt"})
        self.assertEqual(status, 404)

    def test_opt_in_must_be_explicit_boolean(self):
        status, result = self.post("/v1/sessions",
                                   {"session_id": "opaque-3", "opted_in": "yes"})
        self.assertEqual(status, 400)

    def test_scheduler_enqueues_after_persisted_idle_deadline(self):
        self.controller.register("opaque-4", now=0, opted_in=True)
        stop = threading.Event()
        # Deterministic scheduler behavior is exercised through due_sessions and timer.
        due = self.controller.due_sessions(10)
        self.assertEqual(due, [("opaque-4", 0)])
        job = self.controller.fire_idle_timer("opaque-4", 0, 10)
        self.assertIsNotNone(job)

    def test_consent_can_be_revoked_through_signed_endpoint(self):
        self.post("/v1/sessions", {"session_id": "opaque-5", "opted_in": True})
        status, result = self.post("/v1/consent",
                                   {"session_id": "opaque-5", "enabled": False})
        self.assertEqual(status, 200)
        self.assertFalse(result["opted_in"])

    def test_worker_can_claim_and_checkpoint_through_signed_api(self):
        self.controller.register("opaque-6", now=0, opted_in=True)
        job_id = self.controller.fire_idle_timer("opaque-6", 0, 10)
        status, result = self.post("/v1/jobs/claim", {"worker_id": "worker-api"})
        self.assertEqual(status, 200)
        self.assertEqual(result["job"]["job_id"], job_id)
        status, result = self.post(
            "/v1/jobs/" + job_id + "/checkpoint",
            {"worker_id": "worker-api", "payload": {"stage": "research"}, "final": True})
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "completed")


if __name__ == "__main__":
    unittest.main()
