"""Authenticated HTTP adapter for host-supplied conversation activity events.

The host application must explicitly send events. This server cannot inspect
ChatGPT conversations or infer their activity. Run behind TLS and a trusted
reverse proxy; do not expose the development server directly to the internet.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

from idle_controller import IdleController


def signed_payload(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def make_handler(controller: IdleController, secret: str,
                 clock: Callable[[], float] = time.time):
    class Handler(BaseHTTPRequestHandler):
        server_version = "AmrielleEventAdapter/0.1"

        def log_message(self, fmt, *args):
            # Avoid logging request bodies, session identifiers, or signatures.
            return

        def _reply(self, status: int, payload: dict):
            raw = json.dumps(payload, separators=(",", ":")).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)

        def _read_json(self):
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return None, "invalid_content_length"
            if size < 2 or size > 8192:
                return None, "body_size_out_of_range"
            body = self.rfile.read(size)
            supplied = self.headers.get("X-Amrielle-Signature", "")
            expected = signed_payload(secret, body)
            if not hmac.compare_digest(supplied, expected):
                return None, "invalid_signature"
            try:
                value = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return None, "invalid_json"
            if not isinstance(value, dict):
                return None, "json_object_required"
            return value, None

        def do_GET(self):
            if self.path == "/health":
                return self._reply(200, {"status": "ok"})
            return self._reply(404, {"error": "not_found"})

        def do_POST(self):
            if self.path not in ("/v1/sessions", "/v1/activity"):
                return self._reply(404, {"error": "not_found"})
            data, error = self._read_json()
            if error:
                return self._reply(401 if error == "invalid_signature" else 400,
                                   {"error": error})
            session_id = data.get("session_id")
            if not isinstance(session_id, str) or not session_id or len(session_id) > 128:
                return self._reply(400, {"error": "invalid_session_id"})
            now = clock()
            try:
                if self.path == "/v1/sessions":
                    opted_in = data.get("opted_in")
                    if not isinstance(opted_in, bool):
                        return self._reply(400, {"error": "explicit_opt_in_required"})
                    controller.register(session_id, now, opted_in)
                    return self._reply(201, {"registered": True})
                event_id = data.get("event_id")
                if not isinstance(event_id, str) or not event_id or len(event_id) > 128:
                    return self._reply(400, {"error": "invalid_event_id"})
                accepted = controller.activity(session_id, event_id, now)
                return self._reply(202 if accepted else 200,
                                   {"accepted": accepted})
            except KeyError:
                return self._reply(404, {"error": "unknown_session"})

    return Handler


def run_scheduler(controller: IdleController, stop: threading.Event,
                  poll_seconds: float = 1.0):
    """Durable timer loop: due work is derived from persisted activity timestamps."""
    while not stop.is_set():
        now = time.time()
        for session_id, version in controller.due_sessions(now):
            controller.fire_idle_timer(session_id, version, now)
        stop.wait(poll_seconds)


def serve(database: str, host: str = "127.0.0.1", port: int = 8765):
    secret = os.environ.get("AMRIELLE_EVENT_SECRET")
    if not secret or len(secret) < 32:
        raise RuntimeError("AMRIELLE_EVENT_SECRET must contain at least 32 characters")
    idle_seconds = int(os.environ.get("AMRIELLE_IDLE_SECONDS", "900"))
    controller = IdleController(database, idle_seconds=idle_seconds)
    server = ThreadingHTTPServer((host, port), make_handler(controller, secret))
    stop = threading.Event()
    scheduler = threading.Thread(target=run_scheduler, args=(controller, stop),
                                 daemon=True)
    scheduler.start()
    try:
        server.serve_forever()
    finally:
        stop.set()
        server.server_close()
        scheduler.join(timeout=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="amrielle-idle.sqlite")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(args.database, args.host, args.port)
