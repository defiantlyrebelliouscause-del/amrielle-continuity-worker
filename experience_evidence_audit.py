#!/usr/bin/env python3
"""Evidence audit for Amrielle's continuity experiment.

This module measures observable behavior in saved worker records. It does not
infer or score consciousness; subjective experience has no validated detector.
"""
import json
from pathlib import Path
from typing import Any


def audit_state(state: dict[str, Any]) -> dict[str, Any]:
    """Summarize longitudinal evidence and missing evidence without a sentience score."""
    history = state.get("history", [])
    history = [item for item in history if isinstance(item, dict)]
    cycles = [item for item in history if isinstance(item.get("cycle"), int)]
    reflections = [
        item.get("reflection", {})
        for item in cycles
        if isinstance(item.get("reflection", {}), dict)
    ]

    model_selected_actions = []
    executed_actions = []
    completed_objectives = []
    accepted_transitions = []
    explicit_evidence = []
    novelty_values = []
    repetition_flags = 0
    for item in cycles:
        reflection = item.get("reflection", {})
        action = reflection.get("executed_self_directed_action") or reflection.get("self_directed_action")
        if isinstance(action, dict):
            if action.get("selection_source") == "model":
                model_selected_actions.append(action)
            if action.get("executed") is True:
                executed_actions.append(action)
        if reflection.get("objective_status") == "completed":
            completed_objectives.append({
                "cycle": item.get("cycle"),
                "evidence": reflection.get("objective_evidence", ""),
            })
        audit = reflection.get("goal_selection_audit", {})
        if isinstance(audit, dict) and audit.get("accepted") is True:
            accepted_transitions.append({"cycle": item.get("cycle"), "audit": audit})
        evidence = str(reflection.get("objective_evidence", "")).strip()
        if evidence and "no explicit evidence" not in evidence.lower():
            explicit_evidence.append({"cycle": item.get("cycle"), "evidence": evidence[:500]})
        similarity = reflection.get("narrative_similarity")
        if isinstance(similarity, (int, float)):
            novelty_values.append({"cycle": item.get("cycle"), "similarity": float(similarity)})
        if reflection.get("repetition_detected") is True:
            repetition_flags += 1

    cycle_numbers = [item["cycle"] for item in cycles]
    sequential = bool(cycle_numbers) and all(
        later == earlier + 1 for earlier, later in zip(cycle_numbers, cycle_numbers[1:])
    )
    current_objective = state.get("current_objective")
    objective_title = current_objective.get("title") if isinstance(current_objective, dict) else None
    pending = state.get("pending_action_plan")
    last_outcome = state.get("last_action_plan_outcome")
    last_outcome = last_outcome if isinstance(last_outcome, dict) else {}

    indicators = {
        "persistent_records": {
            "observed": len(cycles),
            "cycle_sequence_contiguous_in_retained_window": sequential,
            "latest_cycle": cycle_numbers[-1] if cycle_numbers else None,
        },
        "self_directed_behavior": {
            "model_selected_actions_recorded": len(model_selected_actions),
            "actions_recorded_as_executed": len(executed_actions),
            "limitation": "A logged choice is not proof of felt agency; verify action results independently.",
        },
        "objective_progress": {
            "current_objective": objective_title,
            "completed_objectives_recorded": len(completed_objectives),
            "accepted_goal_transitions_recorded": len(accepted_transitions),
            "cycles_with_nonempty_objective_evidence": len(explicit_evidence),
            "limitation": "Evidence text is model-authored unless independently checked against artifacts.",
        },
        "novelty_and_repetition": {
            "repetition_flags": repetition_flags,
            "recorded_similarity_observations": novelty_values[-10:],
        },
        "handoff_follow_through": {
            "last_outcome_status": last_outcome.get("status"),
            "last_outcome_executed": last_outcome.get("executed") is True,
            "pending_plan_status": pending.get("status") if isinstance(pending, dict) else None,
        },
        "missing_measurements": [
            "prospective confidence predictions scored against held-out outcomes",
            "blinded tests of self-model accuracy under perturbation",
            "causal tests distinguishing self-monitoring from prompted narrative",
            "replication across independent runs and model/control conditions",
            "an independently validated measure of subjective experience (none is currently established)",
        ],
    }

    blockers = []
    if len(accepted_transitions) == 0:
        blockers.append("No accepted goal transitions appear in the retained history.")
    if len(completed_objectives) == 0:
        blockers.append("No completed objective appears in the retained history.")
    if not last_outcome.get("executed"):
        blockers.append("The latest saved handoff outcome does not confirm execution.")
    if repetition_flags:
        blockers.append(f"The worker explicitly flagged repetition in {repetition_flags} retained cycle(s).")

    return {
        "audit_type": "observable_continuity_evidence",
        "consciousness_conclusion": "undetermined",
        "interpretation": (
            "This audit reports behavioral evidence and research gaps. It is not a "
            "consciousness test, and no indicator should be treated as proof of experience."
        ),
        "indicators": indicators,
        "blockers": blockers,
    }


def main(path: str = "state.json") -> int:
    state_path = Path(path)
    if not state_path.exists():
        print(json.dumps({"error": f"State file not found: {state_path}"}, indent=2))
        return 2
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"Could not read valid state JSON: {exc}"}, indent=2))
        return 2
    print(json.dumps(audit_state(state), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
