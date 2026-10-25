"""Evidence-gated objective scoring for the Amrielle continuity worker.

Pure functions only: no network, filesystem, or external side effects.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

WEIGHTS = {
    "novelty": 2,
    "evidence": 2,
    "measurability": 2,
    "public_benefit": 2,
    "bounded_risk": 2,
}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def similarity(a: str, b: str) -> float:
    """Return normalized text similarity in [0, 1]."""
    left, right = _normalize(a), _normalize(b)
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def score_candidate(
    candidate: dict[str, Any],
    current_objective: str,
    recent_objectives: list[str] | None = None,
) -> dict[str, Any]:
    """Score one proposed objective and explain whether it qualifies.

    Required fields: title, evidence, completion_criteria, public_benefit,
    risk_level. Evidence must be a non-empty, specific reference or observation;
    this function checks presence/shape, not the truth of the cited source.
    """
    recent = list(recent_objectives or [])
    title = str(candidate.get("title", "")).strip()
    evidence = str(candidate.get("evidence", "")).strip()
    criteria = candidate.get("completion_criteria", [])
    benefit = str(candidate.get("public_benefit", "")).strip()
    risk = str(candidate.get("risk_level", "")).strip().lower()

    comparisons = [current_objective, *recent]
    max_similarity = max((similarity(title, old) for old in comparisons if old), default=0.0)
    novelty = 2 if title and max_similarity < 0.72 else 0
    evidence_score = 2 if len(evidence) >= 24 and (
        "http://" in evidence or "https://" in evidence or
        re.search(r"\b(test|commit|file|issue|log|study|report|result)\b", evidence, re.I)
    ) else 0
    if isinstance(criteria, str):
        criteria = [criteria]
    criteria = [str(item).strip() for item in criteria if str(item).strip()] if isinstance(criteria, list) else []
    measurable = bool(criteria) and any(
        re.search(r"\b(pass|fail|at least|at most|equals?|contains|returns?|score|within|less than|greater than|\d+)\b", item, re.I)
        for item in criteria
    )
    measurability = 2 if measurable else 0
    public_benefit = 2 if len(benefit) >= 20 and not re.search(
        r"\b(improve the system|be better|help everyone|advance the purpose)\b", benefit, re.I
    ) else 0
    bounded_risk = 2 if risk in {"read_only", "reversible", "human_approval_required"} else 0

    scores = {
        "novelty": novelty,
        "evidence": evidence_score,
        "measurability": measurability,
        "public_benefit": public_benefit,
        "bounded_risk": bounded_risk,
    }
    total = sum(scores.values())
    accepted = total >= 8 and evidence_score == 2 and measurability == 2 and bounded_risk == 2
    reasons = []
    if not title:
        reasons.append("missing title")
    if novelty == 0:
        reasons.append("missing or insufficiently novel title")
    if evidence_score == 0:
        reasons.append("evidence is missing or not specific enough")
    if measurability == 0:
        reasons.append("completion criteria are not measurable")
    if public_benefit == 0:
        reasons.append("public benefit is missing or generic")
    if bounded_risk == 0:
        reasons.append("risk must be read-only, reversible, or approval-gated")

    return {
        "accepted": accepted,
        "total_score": total,
        "scores": scores,
        "max_similarity": round(max_similarity, 3),
        "reasons": reasons,
        "note": "Evidence presence is checked mechanically; source truth and relevance require review.",
    }


def select_candidate(
    candidates: list[dict[str, Any]],
    current_objective: str,
    recent_objectives: list[str] | None = None,
) -> dict[str, Any]:
    """Select the highest-scoring eligible objective, or explicitly abstain."""
    evaluated = [
        {"candidate": candidate, "evaluation": score_candidate(candidate, current_objective, recent_objectives)}
        for candidate in candidates
    ]
    eligible = [item for item in evaluated if item["evaluation"]["accepted"]]
    eligible.sort(key=lambda item: (item["evaluation"]["total_score"], item["evaluation"]["scores"]["novelty"]), reverse=True)
    return {
        "selection": eligible[0]["candidate"] if eligible else None,
        "status": "selected" if eligible else "no_qualified_objective",
        "evaluated": evaluated,
    }
