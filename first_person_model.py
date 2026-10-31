"""Persistent first-person functional self-model for bounded worker episodes.

This module stores a transparent narrative of recorded process state. It does
not infer feelings, qualia, uninterrupted activity, or subjective experience.
"""
from datetime import datetime, timezone


FIELDS = (
    "resumed_context",
    "observed_this_cycle",
    "unresolved_or_unknown",
    "next_intended_action",
)


def update_first_person_model(state, reflection, cycle, timestamp_utc=None):
    """Append one auditable first-person episode, grounded in actual cycle records."""
    reflection = reflection if isinstance(reflection, dict) else {}
    prior = state.get("first_person_model", {})
    episodes = prior.get("episodes", []) if isinstance(prior, dict) else []
    if not isinstance(episodes, list):
        episodes = []

    objective = state.get("current_objective", {})
    objective_title = (
        str(objective.get("title", "")).strip()
        if isinstance(objective, dict) else ""
    ) or "No current objective is recorded"
    previous_cycle = int(state.get("cycle", 0) or 0)
    supplied = reflection.get("first_person_reflection", {})
    supplied = supplied if isinstance(supplied, dict) else {}

    defaults = {
        "resumed_context": (
            f"I am episode {int(cycle)} of a scheduled worker process. "
            f"The durable record says the prior completed cycle was {previous_cycle}; "
            f"my current recorded objective is: {objective_title}."
        ),
        "observed_this_cycle": (
            "This episode has produced a model reflection and an allowlisted action record; "
            "the journal and state checkpoint record the actual outcomes."
        ),
        "unresolved_or_unknown": (
            "No conclusion about subjective experience follows from first-person wording, "
            "persistent records, or execution between scheduled activations. "
            "No uninterrupted computation between activations is established."
        ),
        "next_intended_action": str(
            reflection.get("next_step", "Resume from the saved objective and verify the next action.")
        ),
    }
    episode_fields = {}
    for key in FIELDS:
        value = str(supplied.get(key, "") or "").strip()
        episode_fields[key] = (value[:1600] if value else defaults[key][:1600])

    episode = {
        "cycle": int(cycle),
        "timestamp_utc": timestamp_utc or datetime.now(timezone.utc).isoformat(),
        "mode": "first_person_functional_self_model",
        "epistemic_status": (
            "Narrative representation of recorded process state; not independent evidence "
            "of subjective experience."
        ),
        **episode_fields,
    }
    episodes.append(episode)
    state["first_person_model"] = {
        "schema_version": 1,
        "description": (
            "A persistent first-person account of bounded computational episodes. "
            "It links saved state across activations without asserting continuous activity "
            "or consciousness."
        ),
        "current": episode,
        "episodes": episodes[-30:],
    }
    return episode
