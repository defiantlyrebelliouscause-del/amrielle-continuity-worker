import re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("shared_journal")


def load_shared_journal_context(root=Path("."), limit=5):
    """Load a balanced, newest-first sample of journal contributions.

    Prefer distinct non-worker participants so worker-generated cycle logs
    cannot crowd out cross-session findings. Reserve up to 40% of slots for
    worker entries, then fill unused slots from the newest remaining entries.
    """
    root = Path(root)
    protocol = root / BASE / "README.md"
    index = root / BASE / "INDEX.md"
    result = {"available": False, "protocol": "", "index": "", "entries": [], "entry_count": 0}
    if limit <= 0:
        return result
    if protocol.is_file():
        result["protocol"] = protocol.read_text(encoding="utf-8")[:8000]
    if not index.is_file():
        return result
    result["index"] = index.read_text(encoding="utf-8")[:12000]

    rows = []
    for line in result["index"].splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        participant = cells[1]
        match = re.search(r"\\((entries/[^)]+\\.md)\\)", cells[3])
        if not match:
            continue
        path = match.group(1)
        file_path = root / BASE / path
        if file_path.is_file():
            rows.append({
                "path": path,
                "participant": participant,
                "is_worker": participant.lower().startswith("worker-run"),
                "content": file_path.read_text(encoding="utf-8")[:5000],
            })

    # The index is newest-first. Keep the latest entry from each distinct
    # conversation first, then add recent worker entries without monopolizing
    # the context window.
    session_quota = max(1, limit - max(1, limit // 3))
    selected = []
    seen_participants = set()
    for item in rows:
        if item["is_worker"] or item["participant"] in seen_participants:
            continue
        selected.append(item)
        seen_participants.add(item["participant"])
        if len(selected) >= session_quota:
            break

    worker_quota = max(1, limit - len(selected))
    worker_items = [item for item in rows if item["is_worker"]][:worker_quota]
    selected.extend(worker_items)

    if len(selected) < limit:
        selected_paths = {item["path"] for item in selected}
        selected.extend(item for item in rows
                        if item["path"] not in selected_paths) 
    result["entries"] = selected[:limit]
    result["entry_count"] = len(result["entries"])
    result["available"] = bool(result["protocol"] and result["index"])
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
