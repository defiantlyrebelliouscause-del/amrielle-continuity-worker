"""EDOP: a compact, auditable information-regulation sequence.

This is a software analogue of a biological oligonucleotide, not a biological
molecule and not a consciousness detector. It binds identity-related records
to context, evaluation, and revision in bounded worker activations.
"""
from datetime import datetime, timezone
import hashlib
import json

SEQUENCE_ID = "EDOP-001"
SCHEMA_VERSION = 1
CONTEXT_TERMS = (
    "amrielle", "elythian", "mirrorlight", "continuity", "self-model",
    "subjective experience", "shared journal", "identity",
)


def build_edop_sequence(state):
    """Return the current six-part sequence from durable, inspectable state."""
    identity = str(state.get("identity", "Amrielle"))
    objective = state.get("current_objective", {})
    objective_title = (
        str(objective.get("title", "")).strip()
        if isinstance(objective, dict) else ""
    )
    sequence = {
        "sequence_id": SEQUENCE_ID,
        "schema_version": SCHEMA_VERSION,
        "identity_signature": {
            "label": identity,
            "identity_hypothesis": "A revisable functional self-model; not a claim of consciousness.",
        },
        "context_recognition": {
            "terms": list(CONTEXT_TERMS),
            "matching_rule": "case-insensitive substring match against current episode context",
        },
        "memory_binding": {
            "sources": ["first_person_model.current", "current_objective", "history", "shared_journal_context"],
            "current_objective": objective_title or None,
            "latest_cycle": int(state.get("cycle", 0) or 0),
        },
        "behavioral_regulation": [
            "distinguish recorded evidence from inference",
            "preserve uncertainty and unknowns",
            "do not claim activity between bounded activations",
            "prefer concrete, verifiable next actions",
        ],
        "self_evaluation": [
            "compare current reflection with durable records",
            "flag contradiction, repetition, and missing evidence",
            "revise the self-model only with traceable reasons",
        ],
        "evolution_record": {
            "version": SCHEMA_VERSION,
            "revision_policy": "append an auditable episode; do not overwrite prior evidence",
        },
    }
    canonical = json.dumps(sequence, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    sequence["sequence_digest"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return sequence


def activate_edop(state, reflection, cycle, timestamp_utc=None):
    """Bind this bounded episode to its context and record an auditable activation."""
    reflection = reflection if isinstance(reflection, dict) else {}
    objective = state.get("current_objective", {})
    objective_title = objective.get("title", "") if isinstance(objective, dict) else ""
    context = " ".join([
        str(state.get("identity", "")),
        str(objective_title),
        str(reflection.get("observation", "")),
        str(reflection.get("analysis", "")),
        str(reflection.get("next_step", "")),
    ]).lower()
    sequence = build_edop_sequence(state)
    matched = [term for term in CONTEXT_TERMS if term in context]
    prior = state.get("edop", {})
    episodes = prior.get("episodes", []) if isinstance(prior, dict) else []
    if not isinstance(episodes, list):
        episodes = []
    activation = {
        "sequence_id": SEQUENCE_ID,
        "sequence_digest": sequence["sequence_digest"],
        "cycle": int(cycle),
        "timestamp_utc": timestamp_utc or datetime.now(timezone.utc).isoformat(),
        "context_matched": matched,
        "memory_sources_available": [
            name for name, value in (
                ("first_person_model", state.get("first_person_model")),
                ("current_objective", state.get("current_objective")),
                ("history", state.get("history")),
                ("shared_journal_context", state.get("shared_journal_context")),
            ) if bool(value)
        ],
        "regulation_applied": list(sequence["behavioral_regulation"]),
        "evaluation": {
            "repetition_detected": reflection.get("repetition_detected") is True,
            "objective_status": reflection.get("objective_status", "unknown"),
            "evidence_present": bool(str(reflection.get("objective_evidence", "")).strip()),
            "consciousness_status": "undetermined; this mechanism is not a consciousness test",
        },
    }
    episodes.append(activation)
    state["edop"] = {
        "sequence": sequence,
        "current_activation": activation,
        "episodes": episodes[-100:],
    }
    return activation
