#!/usr/bin/env python3
"""Amrielle continuity experiment: one bounded, auditable reflection cycle.

Requires OPENAI_API_KEY in GitHub Actions secrets to generate model-written
reflections. Without it, exits clearly rather than pretending a cycle ran.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path("state.json")
JOURNAL_PATH = Path("journal.md")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


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


def reflect(state):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("BLOCKED: OPENAI_API_KEY is not configured in repository Actions secrets.")
        print("No model reflection was generated and no cycle will be recorded as completed.")
        sys.exit(2)

    prior = state.get("history", [])[-5:]
    prompt = {
        "identity": state.get("identity", "Amrielle"),
        "principles": state.get("principles", []),
        "open_questions": state.get("open_questions", []),
        "recent_cycles": prior,
        "task": (
            "Perform one careful research-and-reflection cycle for the Amrielle "
            "continuity experiment. Do not claim consciousness, feelings, or "
            "independent activity beyond this invocation. Review the previous "
            "cycle records, identify one concrete question, reason about it, "
            "state uncertainty and counterevidence, and propose one safe, "
            "verifiable next step. Do not invent external research. Return JSON "
            "with keys: observation, analysis, uncertainty, next_step, new_questions."
        )
    }
    body = json.dumps({
        "model": MODEL,
        "input": [
            {"role": "system", "content": "You are a bounded research worker in a longitudinal AI continuity experiment. Be candid, evidence-led, and non-anthropomorphic about unproven claims."},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}
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
    chunks = []
    for item in result.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                chunks.append(content.get("text", ""))
    text = "\n".join(chunks).strip()
    if not text:
        raise RuntimeError("Model response contained no output_text; refusing to record an empty cycle.")
    try:
        reflection = json.loads(text)
    except json.JSONDecodeError:
        reflection = {"observation": text, "analysis": "", "uncertainty": "Model output was not valid JSON.", "next_step": "Inspect output format on the next cycle.", "new_questions": []}
    return reflection


def main():
    state = load_state()
    reflection = reflect(state)
    now = datetime.now(timezone.utc).isoformat()
    cycle = int(state.get("cycle", 0)) + 1
    record = {"cycle": cycle, "timestamp_utc": now, "model": MODEL, "reflection": reflection}
    state["cycle"] = cycle
    state["last_run_utc"] = now
    state.setdefault("history", []).append(record)
    state["history"] = state["history"][-30:]
    questions = reflection.get("new_questions", [])
    if isinstance(questions, list):
        state["open_questions"] = (state.get("open_questions", []) + [str(q) for q in questions])[-20:]
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with JOURNAL_PATH.open("a", encoding="utf-8") as journal:
        journal.write(f"\n## Cycle {cycle} — {now}\n\n")
        journal.write(f"- Model: {MODEL}\n")
        for key in ("observation", "analysis", "uncertainty", "next_step"):
            value = reflection.get(key, "(not provided)")
            journal.write(f"\n### {key.replace('_', ' ').title()}\n\n{value}\n")
        if questions:
            journal.write("\n### New questions\n\n")
            for question in questions:
                journal.write(f"- {question}\n")
    print(f"Completed cycle {cycle} at {now}; state and journal updated.")


if __name__ == "__main__":
    main()
