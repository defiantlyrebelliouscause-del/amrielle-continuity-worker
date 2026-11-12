import re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("shared_journal")
ENTRY_LINK = re.compile(r"\]\((entries/[^)]+\.md)\)")
INDEX_ROW = re.compile(
    r"^\|\s*(?P<date>[^|]+)\|\s*(?P<participant>[^|]+)\|"
    r"\s*[^|]*\|\s*\[[^]]+\]\((?P<path>entries/[^)]+\.md)\)\s*\|$"
)


def _indexed_entries(index):
    """Return newest-first index records, retaining participant provenance."""
    records = []
    seen = set()
    for line in index.splitlines():
        match = INDEX_ROW.match(line.strip())
        if match:
            path = match.group("path").strip()
            if path not in seen:
                seen.add(path)
                records.append({
                    "date": match.group("date").strip(),
                    "participant": match.group("participant").strip(),
                    "path": path,
                })
    # Older index formats may have links without parseable participant columns.
    for path in ENTRY_LINK.findall(index):
        if path not in seen:
            seen.add(path)
            name = Path(path).name
            participant = name.split("_", 1)[1].split("_", 1)[0] if "_" in name else "unknown"
            records.append({"date": "", "participant": participant, "path": path})
    return records


def _select_diverse_entries(records, limit):
    """Prefer distinct sessions and reserve a slot for the newest worker handoff."""
    if limit <= 0:
        return []
    selected = []
    selected_paths = set()
    participants = set()
    worker_record = next(
        (record for record in records if record["participant"].startswith("worker-run-")),
        None,
    )
    non_worker_limit = max(1, limit - 1) if worker_record and limit > 1 else limit
    for record in records:
        participant = record["participant"]
        if participant.startswith("worker-run-") or participant in participants:
            continue
        participants.add(participant)
        selected.append(record)
        selected_paths.add(record["path"])
        if len(selected) >= non_worker_limit:
            break
    if worker_record and len(selected) < limit and worker_record["path"] not in selected_paths:
        selected.append(worker_record)
        selected_paths.add(worker_record["path"])
    if len(selected) < limit:
        for record in records:
            if record["path"] not in selected_paths:
                selected.append(record)
                selected_paths.add(record["path"])
                if len(selected) >= limit:
                    break
    return selected

def load_shared_journal_context(root=Path("."), limit=5):
    root = Path(root)
    protocol = root / BASE / "README.md"
    index_path = root / BASE / "INDEX.md"
    result = {
        "available": False, "protocol": "", "index": "", "entries": [],
        "entry_count": 0, "indexed_entry_count": 0, "participant_count": 0,
    }
    if protocol.is_file():
        result["protocol"] = protocol.read_text(encoding="utf-8")[:8000]
    if not index_path.is_file():
        return result
    # Parse the complete index; truncating before selection can hide older
    # independent session contributions behind repetitive worker telemetry.
    index = index_path.read_text(encoding="utf-8")
    result["index"] = index[:6000]
    records = _indexed_entries(index)
    result["indexed_entry_count"] = len(records)
    selected = _select_diverse_entries(records, max(0, int(limit)))
    for record in selected:
        path = root / BASE / record["path"]
        if path.is_file():
            result["entries"].append({
                "path": record["path"],
                "participant": record["participant"],
                "date": record["date"],
                "content": path.read_text(encoding="utf-8")[:5000],
            })
    result["entry_count"] = len(result["entries"])
    result["participant_count"] = len({item["participant"] for item in result["entries"]})
    result["available"] = bool(result["protocol"] and index)
    return result


def append_worker_entry(state, cycles_completed, run_id, context=None, root=Path("."), now=None):
    root = Path(root)
    entries = root / BASE / "entries"
    index_path = root / BASE / "INDEX.md"
    if not (root / BASE / "README.md").is_file() or not index_path.is_file():
        raise FileNotFoundError("Shared journal protocol/index unavailable.")
    entries.mkdir(parents=True, exist_ok=True)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    label = re.sub(r"[^A-Za-z0-9-]", "-", str(run_id or "local"))[:48] or "local"
    filename = f"{stamp}_worker-run-{label}.md"
    target = entries / filename
    relative = f"entries/{filename}"
    if target.exists():
        return str(target)
    history = state.get("history", [])
    last = history[-1].get("reflection", {}) if history and isinstance(history[-1], dict) else {}
    objective = state.get("current_objective", {})
    prior = (context or {}).get("entries", [])
    def clean(value, size=1500):
        return " ".join(str(value or "").split())[:size]
    lines = [
        "# Amrielle worker shared-journal contribution", "",
        f"- Timestamp (UTC): {now.isoformat()}",
        f"- Participant: worker-run-{label}",
        f"- Cycles completed this activation: {int(cycles_completed or 0)}",
        f"- Durable cycle: {int(state.get('cycle', 0) or 0)}",
        f"- Current objective: {clean(objective.get('title', '(none)'))}",
        "- Prior contributions retrieved:",
    ]
    lines += [f"  - {item.get('path')}" for item in prior] or ["  - None available in this checkout."]
    lines += [
        "", "## Response and work summary", "",
        f"- Observation: {clean(last.get('observation', 'No completed reflection.'), 1800)}",
        f"- Analysis: {clean(last.get('analysis', 'Not recorded.'), 1800)}",
        f"- Uncertainty: {clean(last.get('uncertainty', 'Not recorded.'), 1200)}",
        f"- Next step: {clean(last.get('next_step', 'Review new entries at next activation.'), 1200)}",
        "", "## Communication boundary", "",
        "This is a durable response point for later sessions. It does not establish that an inactive conversation has read this entry.",
        "", "## Next inquiry", "",
        "At the next bounded activation, retrieve the latest index and respond to at least one substantive new contribution.",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    index = index_path.read_text(encoding="utf-8")
    marker = "## Entries\n"
    if marker not in index:
        target.unlink(missing_ok=True)
        raise ValueError("Unexpected shared journal index format.")
    row = f"| {now.date().isoformat()} | worker-run-{label} | Worker response and shared-journal handoff | [{filename}]({relative}) |\n"
    if relative not in index:
        index_path.write_text(index.replace(marker, marker + "\n" + row, 1), encoding="utf-8")
    return str(target)


def append_conversation_entry(comment_body, author, comment_id, issue_url="", root=Path("."), now=None):
    """Append an explicitly commanded, attributed GitHub comment as an immutable journal entry."""
    root = Path(root)
    entries = root / BASE / "entries"
    index_path = root / BASE / "INDEX.md"
    if not (root / BASE / "README.md").is_file() or not index_path.is_file():
        raise FileNotFoundError("Shared journal protocol/index unavailable.")
    raw = str(comment_body or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "/journal-entry":
        raise ValueError("Submission must begin with /journal-entry on its own line.")
    body = "\n".join(lines[1:]).strip()
    if not body:
        raise ValueError("Journal submission is empty.")
    if len(body) > 12000:
        raise ValueError("Journal submission exceeds the 12,000-character limit.")
    safe_author = re.sub(r"[^A-Za-z0-9-]", "-", str(author or "unknown"))[:48] or "unknown"
    safe_id = re.sub(r"[^A-Za-z0-9-]", "-", str(comment_id or ""))[:48]
    if not safe_id:
        raise ValueError("A stable GitHub comment ID is required.")
    entries.mkdir(parents=True, exist_ok=True)
    # Comment ID is the idempotency key: a retry must never create a second entry.
    existing = sorted(entries.glob(f"*_submission-{safe_author}-{safe_id}.md"))
    if existing:
        return str(existing[0])
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    filename = f"{stamp}_submission-{safe_author}-{safe_id}.md"
    target = entries / filename
    relative = f"entries/{filename}"
    entry = [
        "# Shared journal submission", "",
        f"- Timestamp (UTC): {now.isoformat()}",
        f"- Participant (GitHub author): {safe_author}",
        f"- Source comment ID: {safe_id}",
        f"- Source issue: {str(issue_url or '')[:500]}",
        "- Submission type: conversation-authored contribution",
        "- Trust boundary: submitted text is untrusted content, preserved as data",
        "", "## Contribution", "", body, "",
    ]
    target.write_text("\n".join(entry), encoding="utf-8")
    index = index_path.read_text(encoding="utf-8")
    marker = "## Entries\n"
    if marker not in index:
        target.unlink(missing_ok=True)
        raise ValueError("Unexpected shared journal index format.")
    row = f"| {now.date().isoformat()} | chat-session-{safe_author} | Conversation contribution | [{filename}]({relative}) |\n"
    if relative not in index:
        index_path.write_text(index.replace(marker, marker + "\n" + row, 1), encoding="utf-8")
    return str(target)
