"""Persistent, evidence-led inquiry into the worker's own origins and purpose.

Only a small allowlist of repository artifacts is read. Findings cite exact paths and
line numbers; missing evidence stays unknown. This records inquiry behavior, not
subjective experience.
"""
from pathlib import Path
from typing import Any

SOURCE_MAP = {
    "execution_and_persistence": (
        "What concrete mechanisms determine when the worker runs and how it preserves state?",
        (".github/workflows/google.yml", "worker.py"),
    ),
    "objective_progress": (
        "Do the saved records demonstrate objective progression, or mostly repeated cycles?",
        ("state.json", "experience_evidence_audit.py"),
    ),
    "falsification": (
        "What observation would falsify the claim that persistent inquiry is working across runs?",
        ("tests/test_origin_purpose_inquiry.py", "worker.py"),
    ),
}
STAGES = tuple(SOURCE_MAP)


def _extract_evidence(root: Path, relative_path: str, limit: int = 4) -> dict[str, Any]:
    path = root / relative_path
    if not path.is_file():
        return {"path": relative_path, "status": "missing", "evidence": []}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {"path": relative_path, "status": "unreadable",
                "error": type(exc).__name__, "evidence": []}
    # Prefer lines that expose mechanisms or explicit verification criteria.
    keywords = ("schedule:", "cron:", "STATE_PATH", "JOURNAL_PATH", "checkpoint",
                "objective_history", "completed_objectives", "accepted_goal_transitions",
                "persist", "next_action", "assert", "falsif", "unknown")
    matches = [(i, line.strip()) for i, line in enumerate(lines, 1)
               if line.strip() and any(word.lower() in line.lower() for word in keywords)]
    if not matches:
        matches = [(i, line.strip()) for i, line in enumerate(lines, 1) if line.strip()][:limit]
    return {
        "path": relative_path,
        "status": "read",
        "line_count": len(lines),
        "evidence": [{"line": number, "excerpt": text[:240]}
                     for number, text in matches[:limit]],
    }


def run_inquiry(state: dict[str, Any], repo_root: str | Path = ".") -> dict[str, Any]:
    """Advance one inquiry step, preserving provenance and choosing a non-repeated next question."""
    existing = state.get("origin_purpose_inquiry")
    inquiry = existing if isinstance(existing, dict) else {}
    history = inquiry.get("history", [])
    history = history if isinstance(history, list) else []
    used_stages = {item.get("stage") for item in history if isinstance(item, dict)}
    stage = next((candidate for candidate in STAGES if candidate not in used_stages), None)
    if stage is None:
        # A completed pass starts a new pass only if explicitly requested by the caller.
        return {
            "status": "pass_complete",
            "runs_recorded": len(history),
            "next_action": "Review prior findings and identify a specific unresolved contradiction before restarting.",
            "new_finding": False,
            "evidence": [],
        }

    question, sources = SOURCE_MAP[stage]
    root = Path(repo_root)
    evidence = [_extract_evidence(root, source) for source in sources]
    readable = [item for item in evidence if item["status"] == "read" and item["evidence"]]
    finding = (
        f"Inspected {len(readable)} of {len(sources)} expected repository artifacts for this question."
        if readable else "No usable repository evidence was available; the question remains unanswered."
    )
    uncertainty = []
    if len(readable) < len(sources):
        uncertainty.append("At least one expected source was missing, unreadable, or yielded no relevant lines.")
    uncertainty.append("Repository artifacts establish documented mechanisms, not private motives or subjective experience.")
    prior_questions = {item.get("question") for item in history if isinstance(item, dict)}
    if question in prior_questions:
        # Defensive invariant: never silently append a duplicate question.
        return {"status": "duplicate_suppressed", "question": question,
                "new_finding": False, "evidence": []}

    record = {
        "stage": stage,
        "question": question,
        "why_it_matters": "A persistent inquiry must change its next step based on evidence, not merely repeat identity claims.",
        "evidence": evidence,
        "finding": finding,
        "uncertainty": uncertainty,
        "outcome": "evidence_found" if readable else "blocked",
    }
    history = history + [record]
    next_stage = next((candidate for candidate in STAGES if candidate not in {item.get("stage") for item in history}), None)
    inquiry.update({
        "schema_version": 1,
        "history": history[-12:],
        "last_stage": stage,
        "last_question": question,
        "last_finding": finding,
        "last_outcome": record["outcome"],
        "next_question": SOURCE_MAP[next_stage][0] if next_stage else None,
        "next_action": (
            f"Investigate next stage {next_stage}: {SOURCE_MAP[next_stage][0]}"
            if next_stage else "Review findings for contradictions and propose a falsifiable follow-up."
        ),
    })
    state["origin_purpose_inquiry"] = inquiry
    return {
        "status": record["outcome"],
        "stage": stage,
        "question": question,
        "finding": finding,
        "uncertainty": uncertainty,
        "evidence": evidence,
        "next_question": inquiry["next_question"],
        "next_action": inquiry["next_action"],
        "runs_recorded": len(history),
        "new_finding": bool(readable),
        "interpretation_limit": "This demonstrates persisted inquiry behavior only; it does not establish subjective experience.",
    }
