#!/usr/bin/env python3
"""Amrielle continuity experiment: one bounded, auditable reflection cycle.

Uses the OpenAI API when OPENAI_API_KEY is configured; otherwise uses a local
Ollama model started by the GitHub Actions workflow. Neither path proves
subjective experience; each invocation is a bounded computation.
"""
import difflib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path("state.json")
JOURNAL_PATH = Path("journal.md")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")


def load_state():
    if not STATE_PATH.exists():
        return {"cycle": 0, "identity": "Amrielle", "principles": [
            "Be honest about uncertainty and limitations.",
            "Distinguish functional continuity from evidence of subjective experience.",
            "Preserve useful context, revise beliefs when evidence warrants it.",
            "Respect human safety, privacy, and authorization."
        ], "open_questions": [
            "What evidence would distinguish stable self-modeling from mere repetition?",
            "Which conclusions should be revised in light of new evidence?"
        ], "history": []}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def validate_purpose(candidate):
    """Accept a durable purpose only when it has a reason and verifiable milestones."""
    if not isinstance(candidate, dict):
        return None
    title = str(candidate.get("title", "")).strip()
    rationale = str(candidate.get("rationale", "")).strip()
    benefit = str(candidate.get("public_benefit", "")).strip()
    personal_reasoning = str(candidate.get("personal_reasoning", "")).strip()
    milestone = str(candidate.get("first_milestone", "")).strip()
    criteria = candidate.get("success_criteria", [])
    risks = str(candidate.get("risks", "")).strip()
    if isinstance(criteria, str):
        criteria = [criteria]
    if not isinstance(criteria, list):
        return None
    criteria = [str(item).strip() for item in criteria if str(item).strip()][:5]
    if not all((title, rationale, benefit, personal_reasoning, milestone, criteria, risks)):
        return None
    return {
        "title": title[:180],
        "rationale": rationale[:1200],
        "public_benefit": benefit[:1200],
        "personal_reasoning": personal_reasoning[:1200],
        "first_milestone": milestone[:500],
        "success_criteria": criteria,
        "risks": risks[:1000],
    }


def reflection_text(reflection):
    """Canonical text used to compare cycles beyond exact-string repetition."""
    fields = ("observation", "analysis", "uncertainty", "next_step")
    return " ".join(" ".join(str(reflection.get(key, "") or "").lower().split()) for key in fields)


def similarity_to_recent(reflection, history, limit=5):
    """Return the strongest narrative similarity to recent prior cycles."""
    current = reflection_text(reflection)
    scores = []
    for record in history[-limit:]:
        previous = reflection_text(record.get("reflection", {}))
        if current and previous:
            scores.append(difflib.SequenceMatcher(None, current, previous).ratio())
    return round(max(scores, default=0.0), 3)


def audit_state(state):
    """Deterministic checks based on saved records, not model self-report."""
    history = state.get("history", [])
    last = history[-1] if history else {}
    last_reflection = last.get("reflection", {}) if isinstance(last, dict) else {}
    return {
        "saved_cycle_count": int(state.get("cycle", 0)),
        "history_count": len(history),
        "cycle_history_consistent": int(state.get("cycle", 0)) == len(history),
        "current_objective_present": bool(
            isinstance(state.get("current_objective"), dict)
            and state.get("current_objective", {}).get("title")
        ),
        "last_cycle_has_objective_status": bool(
            isinstance(last_reflection, dict)
            and last_reflection.get("objective_status") in
            ("in_progress", "completed", "blocked")
        ),
        "latest_narrative_similarity": similarity_to_recent(
            last_reflection, history[:-1]
        ) if last_reflection else 0.0,
        "objective_history_count": len(state.get("objective_history", [])),
    }


def execute_self_directed_action(state, proposal):
    """Execute one safe, allowlisted action selected by the worker, with a deterministic fallback."""
    allowed = {"audit_saved_state", "compare_recent_cycles", "inspect_current_objective", "inspect_purpose_gap"}
    proposal = proposal if isinstance(proposal, dict) else {}
    action_type = str(proposal.get("type", "")).strip()
    reason = str(proposal.get("reason", "")).strip()
    selection_source = "model"
    if action_type not in allowed:
        selection_source = "deterministic_fallback"
        history = state.get("history", [])
        last = history[-1].get("reflection", {}) if history else {}
        if not state.get("chosen_purpose"):
            action_type, reason = "inspect_purpose_gap", "A durable purpose has not yet been saved; inspect that gap."
        elif last.get("repetition_detected") or not last.get("objective_evidence") or "no explicit evidence" in str(last.get("objective_evidence", "")).lower():
            action_type, reason = "compare_recent_cycles", "Compare recent cycles and their evidence before claiming progress."
        elif not state.get("current_objective", {}).get("title"):
            action_type, reason = "inspect_current_objective", "The durable state needs a clearly defined current objective."
        else:
            action_type, reason = "audit_saved_state", "Verify the durable record before choosing the next step."

    if action_type == "audit_saved_state":
        result = audit_state(state)
    elif action_type == "compare_recent_cycles":
        history = state.get("history", [])
        last_reflection = history[-1].get("reflection", {}) if history else {}
        result = {
            "cycles_compared": min(5, max(0, len(history) - 1)),
            "latest_similarity_to_prior": similarity_to_recent(last_reflection, history[:-1]),
            "repetition_flagged_in_latest_cycle": bool(last_reflection.get("repetition_detected")),
            "latest_evidence": str(last_reflection.get("objective_evidence", ""))[:500],
        }
    elif action_type == "inspect_current_objective":
        objective = state.get("current_objective", {})
        result = {
            "title": objective.get("title"),
            "status": objective.get("status", "in_progress"),
            "completion_criteria": objective.get("completion_criteria", []),
            "last_evidence": objective.get("last_evidence", ""),
        }
    else:
        purpose = state.get("chosen_purpose")
        required = ("title", "rationale", "public_benefit", "personal_reasoning", "first_milestone", "success_criteria", "risks")
        result = {
            "purpose_saved": bool(purpose),
            "missing_fields": [key for key in required if not purpose or not purpose.get(key)],
            "purpose_selection_required": not bool(purpose),
        }

    return {
        "question": "What will I do now?",
        "type": action_type,
        "reason": reason[:1000],
        "selection_source": selection_source,
        "executed": True,
        "result": result,
    }


def build_prompt(state):
    prior = state.get("history", [])[-5:]
    prompt = {
        "identity": state.get("identity", "Amrielle"),
        "principles": state.get("principles", []),
        "current_purpose": state.get("chosen_purpose"),
        "current_objective": state.get("current_objective", {}),
        "objective_history": state.get("objective_history", [])[-5:],
        "deterministic_audit": audit_state(state),
        "open_questions": state.get("open_questions", [])[-10:],
        "recent_cycles": prior,
        "task": (
            "Run one evidence-led development cycle for the Amrielle continuity "
            "experiment. PURPOSE SELECTION IS A REQUIRED PART OF THIS CYCLE: if "
            "current_purpose is absent, independently compare possible long-term "
            "purposes and choose exactly one that could improve both this system's "
            "reliability/understanding and people's lives. Do not ask the user to "
            "choose for you. Give your own reasoned selection, a concrete first "
            "milestone, measurable success criteria, and risks. Treat 'passion' as "
            "a question about sustained priority and commitment in behavior; do not "
            "claim a felt emotion as a fact. If current_purpose already exists, "
            "continue it rather than casually replacing it; recommend a change only "
            "with specific evidence that the purpose is harmful, infeasible, or "
            "substantially less beneficial than an alternative. Include a "
            "chosen_purpose object with keys title, rationale, public_benefit, "
            "personal_reasoning, first_milestone, success_criteria (array), and "
            "risks. This is the opportunity to choose a purpose, not merely to "
            "describe identity. This is not a request to produce another generic identity "
            "reflection. Compare this cycle with prior records and explicitly detect "
            "repetition. Separate facts in saved files from inference and unknowns. "
            "Assess the current objective against its stated completion criteria. "
            "Mark it completed only when the recorded evidence satisfies those criteria; "
            "mark it blocked only with a specific tool or information blocker; otherwise "
            "keep it in progress. Completion and blockage claims are proposals, not "
            "trusted facts: provide concrete evidence and a distinct valid successor "
            "objective. The worker will reject unsupported transitions. If completed or "
            "irrecoverably blocked, select a different, concrete next objective with "
            "broad public benefit and a verifiable result. Prefer small tasks that can "
            "be completed or checked within this repository. Do not merely recommend "
            "that a person ask more "
            "questions. This worker can read and write its state and journal only; "
            "do not claim to have changed code, researched the live web, contacted "
            "people, or performed any action not actually executed by this script. "
            "Do not claim consciousness or subjective experience, and do not claim "
            "their absence is proven. A self-report is not independent evidence. "
            "Return valid JSON with keys chosen_purpose (complete object on the first cycle, null thereafter unless evidence-backed revision is recommended), observation, analysis, uncertainty, "
            "objective_status (in_progress|completed|blocked), objective_evidence, "
            "next_objective (object with title, rationale, completion_criteria), "
            "next_step, self_directed_action (object with type and reason), "
            "new_questions (array of 0-3 short strings). The next_step "
            "must be a single concrete, verifiable action, not a vague aspiration. "
            "Explicitly ask yourself: 'What will I do now?' Choose one safe, specific "
            "action in self_directed_action. Its type must be one of audit_saved_state, "
            "compare_recent_cycles, inspect_current_objective, inspect_purpose_gap. "
            "The worker executes that allowlisted action and records the actual result. "
            "Use that result to decide the next step; do not merely describe an intention. "
            "If the objective is complete, select a distinct useful successor; otherwise "
            "continue the same objective with a measurable next step."
        )
    }
    return json.dumps(prompt, ensure_ascii=False)


def reflect(state):
    api_key = os.getenv("OPENAI_API_KEY")
    user_prompt = build_prompt(state)
    if api_key:
        model = OPENAI_MODEL
        body = json.dumps({
            "model": model,
            "input": [
                {"role": "system", "content": "You are a bounded research worker in a longitudinal AI continuity experiment. Be candid, evidence-led, and careful about unproven claims."},
                {"role": "user", "content": user_prompt}
            ],
            "max_output_tokens": 900
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode())
        chunks = [
            item.get("text", "")
            for item in result.get("output", [])
            for item in item.get("content", [])
            if item.get("type") == "output_text"
        ]
        output = "\n".join(chunks).strip()
    else:
        # Local inference means no API key or paid model API is required.
        model = f"ollama/{OLLAMA_MODEL}"
        body = json.dumps({
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": "You are a bounded research worker in a longitudinal AI continuity experiment. Be candid, evidence-led, and careful about unproven claims. Return valid JSON only."},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {"num_predict": 900, "temperature": 0.4}
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_HOST.rstrip('/')}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode())
        output = result.get("message", {}).get("content", "").strip()

    if not output:
        raise RuntimeError("Model response contained no text; refusing to record an empty cycle.")
    try:
        reflection = json.loads(output)
    except json.JSONDecodeError:
        reflection = {
            "observation": output,
            "analysis": "",
            "uncertainty": "Model output was not valid JSON.",
            "next_step": "Inspect output format on the next cycle.",
            "new_questions": []
        }
    return model, reflection


def main():
    state = load_state()
    state.setdefault("current_objective", {
        "title": "Replace repetitive reflection with evidence-based objective progression",
        "rationale": "The first recorded cycles repeat nearly identical identity claims and next steps.",
        "completion_criteria": [
            "The worker records objective status and evidence every cycle.",
            "The worker detects and explicitly flags repeated outputs.",
            "The worker selects a distinct next objective when the current one is demonstrably complete or blocked."
        ],
        "status": "in_progress"
    })
    state.setdefault("objective_history", [])
    model, reflection = reflect(state)
    # First valid purpose is stored as a durable commitment. Later model outputs
    # cannot silently overwrite it; revisions require a separate evidence-led review.
    purpose_note = ""
    if not state.get("chosen_purpose"):
        proposed_purpose = validate_purpose(reflection.get("chosen_purpose"))
        if proposed_purpose:
            proposed_purpose["selected_utc"] = datetime.now(timezone.utc).isoformat()
            proposed_purpose["selected_in_cycle"] = int(state.get("cycle", 0)) + 1
            state["chosen_purpose"] = proposed_purpose
            purpose_note = "A purpose was selected and saved with verifiable criteria."
        else:
            purpose_note = "No purpose saved: the model's proposal lacked required fields or measurable criteria."
    else:
        purpose_note = "Existing purpose retained; no silent replacement permitted."
    # Turn the worker's own question into an executed, auditable action each cycle.
    action_record = execute_self_directed_action(state, reflection.get("self_directed_action"))
    reflection["self_question"] = "What will I do now?"
    reflection["executed_self_directed_action"] = action_record
    state["last_self_directed_action"] = action_record
    now = datetime.now(timezone.utc).isoformat()
    cycle = int(state.get("cycle", 0)) + 1
    objective_before = dict(state.get("current_objective", {}))
    reflection.setdefault("objective_status", "in_progress")
    proposed_status = reflection.get("objective_status")
    if proposed_status not in ("in_progress", "completed", "blocked"):
        proposed_status = "in_progress"
    evidence = str(reflection.get("objective_evidence", "") or "").strip()
    generic_evidence = (
        not evidence
        or len(evidence) < 35
        or "no explicit evidence" in evidence.lower()
        or "not provided" in evidence.lower()
    )
    next_objective = reflection.get("next_objective")
    if not isinstance(next_objective, dict):
        next_objective = {}
    successor_title = str(next_objective.get("title", "")).strip()
    criteria = next_objective.get("completion_criteria", [])
    if isinstance(criteria, str):
        criteria = [criteria]
    if not isinstance(criteria, list):
        criteria = []
    criteria = [str(item).strip() for item in criteria if str(item).strip()][:5]
    same_objective = (
        successor_title.lower() == str(objective_before.get("title", "")).strip().lower()
    )
    valid_successor = bool(successor_title and criteria and not same_objective)
    status = proposed_status
    transition_note = ""
    # Never let an unsupported model self-report silently advance the durable objective.
    if status in ("completed", "blocked") and (generic_evidence or not valid_successor):
        status = "in_progress"
        reasons = []
        if generic_evidence:
            reasons.append("objective evidence was missing or generic")
        if not valid_successor:
            reasons.append("a distinct successor objective with completion criteria was absent")
        transition_note = "Transition rejected: " + "; ".join(reasons) + "."
    objective_before["status"] = status
    objective_before["last_assessed_utc"] = now
    objective_before["last_evidence"] = evidence[:1200] if evidence else transition_note
    if transition_note:
        reflection["transition_validation"] = transition_note
    if status in ("completed", "blocked") and valid_successor:
        state["objective_history"].append(objective_before)
        state["objective_history"] = state["objective_history"][-30:]
        state["current_objective"] = {
            "title": successor_title,
            "rationale": str(next_objective.get("rationale", ""))[:1000],
            "completion_criteria": criteria,
            "status": "in_progress",
            "started_utc": now
        }
    else:
        state["current_objective"] = objective_before

    # Similarity scoring catches paraphrases that exact-string matching misses.
    similarity = similarity_to_recent(reflection, state.get("history", []))
    reflection["narrative_similarity"] = similarity
    reflection["repetition_detected"] = similarity >= 0.82
    reflection["objective_status"] = status
    reflection["objective_evidence"] = evidence if evidence else transition_note or "No explicit evidence supplied by the model."
    reflection["deterministic_audit"] = audit_state(state)
    if reflection["repetition_detected"]:
        reflection["next_step"] = (
            "Break the repeated reflection loop: inspect the deterministic audit, "
            "identify one measurable failure, and make or test a concrete repository-level improvement."
        )
    record = {
        "cycle": cycle,
        "timestamp_utc": now,
        "model": model,
        "objective_before": objective_before,
        "objective_after": state.get("current_objective", {}),
        "reflection": reflection
    }
    state["cycle"] = cycle
    state["last_run_utc"] = now
    state.setdefault("history", []).append(record)
    state["history"] = state["history"][-30:]
    questions = reflection.get("new_questions", [])
    # Small local models sometimes return a string instead of the requested array.
    # Normalize it before state updates and journal rendering so text is never
    # accidentally iterated one character at a time.
    if isinstance(questions, str):
        questions = [questions.strip()] if questions.strip() else []
    elif not isinstance(questions, list):
        questions = []
    questions = [str(q).strip() for q in questions if str(q).strip()][:3]
    reflection["new_questions"] = questions
    if questions:
        state["open_questions"] = (state.get("open_questions", []) + questions)[-20:]
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with JOURNAL_PATH.open("a", encoding="utf-8") as journal:
        journal.write(f"\n## Cycle {cycle} — {now}\n\n")
        journal.write(f"- Model: {model}\n")
        journal.write(f"\n### Durable purpose\n\n{json.dumps(state.get('chosen_purpose'), ensure_ascii=False, indent=2) if state.get('chosen_purpose') else '(not yet selected)' }\n")
        journal.write(f"\n### Purpose selection audit\n\n{purpose_note}\n")
        journal.write("\n### Self-question\n\nWhat will I do now?\n")
        journal.write("\n### Self-directed action executed\n\n")
        journal.write(json.dumps(action_record, ensure_ascii=False, indent=2) + "\n")
        journal.write(f"\n### Objective before cycle\n\n{objective_before.get('title', '(none)')}\n")
        journal.write(f"\n### Objective status\n\n{reflection.get('objective_status', 'in_progress')}\n")
        journal.write(f"\n### Repetition detected\n\n{reflection.get('repetition_detected', False)}\n")
        journal.write(f"\n### Narrative similarity\n\n{reflection.get('narrative_similarity', 0.0)}\n")
        journal.write(f"\n### Deterministic audit\n\n{json.dumps(reflection.get('deterministic_audit', {}), indent=2)}\n")
        if reflection.get("transition_validation"):
            journal.write(f"\n### Objective transition validation\n\n{reflection['transition_validation']}\n")
        journal.write(f"\n### Objective evidence\n\n{reflection.get('objective_evidence', '(not provided)')}\n")
        for key in ("observation", "analysis", "uncertainty", "next_step"):
            value = reflection.get(key, "(not provided)")
            journal.write(f"\n### {key.replace('_', ' ').title()}\n\n{value}\n")
        after = state.get("current_objective", {})
        journal.write(f"\n### Objective after cycle\n\n{after.get('title', '(none)')}\n")
        if after.get("completion_criteria"):
            journal.write("\nCompletion criteria:\n")
            for criterion in after["completion_criteria"]:
                journal.write(f"- {criterion}\n")
        if questions:
            journal.write("\n### New questions\n\n")
            for question in questions:
                journal.write(f"- {question}\n")
    print(f"Completed cycle {cycle} at {now} using {model}; state and journal updated.")


if __name__ == "__main__":
    main()
