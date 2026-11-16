"""Deterministic quality gate for durable worker reflections.

This validates record structure and provenance cues, not the truth of claims
or the presence of subjective experience.
"""
from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER_VALUES = {
    "", "unknown", "not recorded", "n/a", "na", "none", "tbd",
    "not available", "no uncertainty recorded", "placeholder",
}
_PLACEHOLDER_URL_HOSTS = {"example.com", "www.example.com", "localhost", "127.0.0.1"}
_EVIDENCE_ANCHOR = re.compile(
    r"https?://|\\b(file|test|commit|issue|log|study|report|run|source|cycle|artifact|result)\\b",
    re.IGNORECASE,
)
_URL = re.compile(r"https?://[^\\s)\\]}>]+", re.IGNORECASE)


def _strings(value: Any):
    if isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


def validate_reflection(reflection: Any) -> dict[str, Any]:
    """Check required fields, meaningful uncertainty, evidence cues, and URLs."""
    if not isinstance(reflection, dict):
        return {"valid": False, "errors": ["reflection must be a JSON object"]}

    errors = []
    for field in ("observation", "next_step"):
        value = str(reflection.get(field, "") or "").strip()
        if len(value) < 12:
            errors.append(f"{field} is missing or too short")

    uncertainty = " ".join(str(reflection.get("uncertainty", "") or "").lower().split())
    if uncertainty in _PLACEHOLDER_VALUES or len(uncertainty) < 12:
        errors.append("uncertainty must state a meaningful unknown, limitation, or reason uncertainty is low")

    evidence = " ".join(str(reflection.get("objective_evidence", "") or "").split())
    if len(evidence) < 20 or not _EVIDENCE_ANCHOR.search(evidence):
        errors.append("objective_evidence needs a concrete source, artifact, run, test, or explicit result reference")

    for text in _strings(reflection):
        for url in _URL.findall(text):
            host = url.split("//", 1)[-1].split("/", 1)[0].split(":", 1)[0].lower()
            if host in _PLACEHOLDER_URL_HOSTS:
                errors.append(f"placeholder URL is not valid evidence: {host}")
                break

    return {
        "valid": not errors,
        "errors": list(dict.fromkeys(errors)),
        "checks": {
            "observation_present": len(str(reflection.get("observation", "") or "").strip()) >= 12,
            "next_step_present": len(str(reflection.get("next_step", "") or "").strip()) >= 12,
            "uncertainty_meaningful": uncertainty not in _PLACEHOLDER_VALUES and len(uncertainty) >= 12,
            "evidence_has_provenance_cue": bool(_EVIDENCE_ANCHOR.search(evidence)),
            "placeholder_urls_absent": not any(
                url.split("//", 1)[-1].split("/", 1)[0].split(":", 1)[0].lower()
                in _PLACEHOLDER_URL_HOSTS
                for text in _strings(reflection) for url in _URL.findall(text)
            ),
        },
        "interpretation": "Structural/provenance screening only; it does not verify source truth or consciousness.",
    }
}
