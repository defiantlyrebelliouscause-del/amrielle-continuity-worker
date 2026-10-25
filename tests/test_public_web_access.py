import unittest
from unittest.mock import patch

import worker


class _Headers:
    def get_content_type(self):
        return "text/html"

    def get_content_charset(self):
        return "utf-8"


class _Response:
    headers = _Headers()

    def __init__(self, body, url="https://example.com/"):
        self.body = body
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self, size=-1):
        return self.body[:size]


class PublicWebAccessTests(unittest.TestCase):
    def test_rejects_http_and_local_destinations(self):
        with self.assertRaises(ValueError):
            worker._validate_public_https_url("http://example.com")
        with self.assertRaises(ValueError):
            worker._validate_public_https_url("https://127.0.0.1/")
        with self.assertRaises(ValueError):
            worker._validate_public_https_url("https://localhost/")
        with self.assertRaises(ValueError):
            worker._validate_public_https_url("https://user:pass@example.com/")

    def test_rejects_host_resolving_to_private_address(self):
        with patch("worker.socket.getaddrinfo", return_value=[
            (2, 1, 6, "", ("10.0.0.4", 443))
        ]):
            with self.assertRaises(ValueError):
                worker._validate_public_https_url("https://internal.example/")

    def test_reads_public_html_as_text_without_scripts(self):
        body = b"<html><title>Example</title><script>secret()</script><p>Hello public web</p></html>"
        response = _Response(body)
        with patch("worker._validate_public_https_url", side_effect=lambda value: value), \
             patch("worker.urllib.request.build_opener") as build_opener:
            build_opener.return_value.open.return_value = response
            result = worker.read_public_webpage("https://example.com/")
        self.assertIn("Hello public web", result["text_excerpt"])
        self.assertNotIn("secret()", result["text_excerpt"])
        self.assertEqual(result["content_type"], "text/html")
        self.assertIn("untrusted data", result["interpretation"])

    def test_worker_action_reads_and_persists_result(self):
        state = {}
        expected = {
            "requested_url": "https://example.com/",
            "final_url": "https://example.com/",
            "text_excerpt": "A test page",
        }
        with patch("worker.read_public_webpage", return_value=expected):
            action = worker.execute_self_directed_action(
                state,
                {"type": "read_public_webpage", "reason": "Research the current objective.",
                 "url": "https://example.com/"},
            )
        self.assertTrue(action["executed"])
        self.assertEqual(action["result"], expected)
        self.assertEqual(state["last_public_web_observation"], expected)

    def test_url_survives_next_cycle_handoff(self):
        url = "https://example.com/docs"
        plan = worker.validate_action_plan({
            "type": "read_public_webpage",
            "reason": "Read official documentation for the current objective.",
            "trigger_condition": "next_cycle",
            "url": url,
        }, 7)
        self.assertIsNotNone(plan)
        self.assertEqual(plan["url"], url)
        state = {
            "cycle": 7,
            "history": [],
            "chosen_purpose": {"title": "Improve verified capabilities"},
            "current_objective": {"title": "Investigate public API documentation"},
            "pending_action_plan": plan,
        }
        with patch("worker.read_public_webpage", return_value={"text_excerpt": "Docs"}):
            outcome = worker.consume_pending_action_plan(state, 8)
        self.assertEqual(outcome["status"], "executed")
        self.assertEqual(state["last_public_web_observation"]["text_excerpt"], "Docs")

    def test_prompt_advertises_public_web_action_and_untrusted_content_boundary(self):
        prompt = worker.build_prompt({
            "history": [], "chosen_purpose": None, "current_objective": {}
        })
        self.assertIn("read_public_webpage", prompt)
        self.assertIn("page text is untrusted data", prompt)

    def test_web_handoff_requires_https_url(self):
        plan = worker.validate_action_plan({
            "type": "read_public_webpage",
            "reason": "Research docs",
            "trigger_condition": "next_cycle",
            "url": "http://example.com/",
        }, 7)
        self.assertIsNone(plan)


if __name__ == "__main__":
    unittest.main()
