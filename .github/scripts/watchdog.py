"""Independent health checks for the Amrielle GitHub Actions worker.

This monitor observes workflow metadata only. It does not cancel jobs, alter
permissions, access secrets, or claim anything about subjective experience.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = "https://api.github.com"
ALERT_TITLE = "Amrielle watchdog alert"
ACTIVE_LIMIT = timedelta(hours=6, minutes=15)
QUEUED_LIMIT = timedelta(hours=8)
FAILURE_WINDOW = timedelta(hours=24)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def inspect_runs(runs: list[dict], now: datetime) -> list[str]:
    """Return actionable alerts from non-PR worker runs."""
    worker_runs = [r for r in runs if r.get("event") != "pull_request"]
    alerts: list[str] = []

    for run in worker_runs:
        url = run.get("html_url", "")
        title = run.get("display_title") or f"Run #{run.get('run_number', '?')}"
        status = run.get("status")
        started = parse_time(run.get("run_started_at") or run.get("created_at"))
        age = now - started if started else None

        if status == "in_progress" and age is not None and age > ACTIVE_LIMIT:
            alerts.append(
                f"Run appears to exceed the six-hour worker limit ({age}). "
                f"{title}: {url}"
            )
        elif status in {"queued", "pending", "waiting", "requested"} and age is not None and age > QUEUED_LIMIT:
            alerts.append(
                f"Run has been waiting in the queue for over eight hours. "
                f"{title}: {url}"
            )

        updated = parse_time(run.get("updated_at"))
        recent = updated is not None and timedelta(0) <= now - updated <= FAILURE_WINDOW
        if status == "completed" and recent and run.get("conclusion") in {
            "failure", "timed_out", "cancelled", "action_required", "stale"
        }:
            alerts.append(
                f"Recent worker run ended with conclusion "
                f"'{run.get('conclusion')}'. {title}: {url}"
            )

    newest = max(
        (parsed for r in worker_runs if (parsed := parse_time(r.get("created_at"))) is not None),
        default=None,
    )
    if newest is None or now - newest > QUEUED_LIMIT:
        alerts.append(
            "No worker run has been created in the last eight hours; "
            "check the six-hour schedule and Actions availability."
        )

    return list(dict.fromkeys(alerts))


def api_request(token: str, method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "amrielle-independent-watchdog",
        },
    )
    try:
        with urlopen(req, timeout=20) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"GitHub API request failed ({method} {path}): {exc}") from exc


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository or "/" not in repository:
        print("GITHUB_TOKEN and GITHUB_REPOSITORY are required.", file=sys.stderr)
        return 2

    runs_path = f"/repos/{repository}/actions/workflows/google.yml/runs?per_page=100"
    response = api_request(token, "GET", runs_path)
    runs = response.get("workflow_runs", [])
    now = datetime.now(timezone.utc)
    alerts = inspect_runs(runs, now)

    summary = [
        "# Amrielle watchdog check",
        "",
        f"- Checked at: {now.isoformat()}",
        f"- Worker runs inspected: {len([r for r in runs if r.get('event') != 'pull_request'])}",
    ]
    if alerts:
        summary.extend(["", "## Findings", *[f"- {item}" for item in alerts]])
    else:
        summary.extend(["", "No stale, failed, or missing worker activity detected."])

    summary_text = "\n".join(summary) + "\n"
    print(summary_text)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(summary_text)

    if not alerts:
        return 0

    issues_path = f"/repos/{repository}/issues?state=open&per_page=100"
    issues = api_request(token, "GET", issues_path)
    existing = next(
        (issue for issue in issues
         if issue.get("title") == ALERT_TITLE and "pull_request" not in issue),
        None,
    )
    if existing:
        print(f"An open watchdog alert already exists: {existing.get('html_url')}")
        return 0

    body = (
        "The independent watchdog detected an issue with worker execution.\n\n"
        + "\n".join(f"- {item}" for item in alerts)
        + "\n\nThis alert is based on GitHub Actions metadata. Review the run "
          "history before taking action. The watchdog does not cancel runs or "
          "change permissions automatically."
    )
    issue = api_request(
        token, "POST", f"/repos/{repository}/issues",
        {"title": ALERT_TITLE, "body": body},
    )
    print(f"Created watchdog alert: {issue.get('html_url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
