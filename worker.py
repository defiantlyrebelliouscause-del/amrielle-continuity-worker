#!/usr/bin/env python3
"""Amrielle continuity experiment: one bounded, auditable reflection cycle.

Uses the OpenAI API when OPENAI_API_KEY is configured; otherwise uses a local
Ollama model started by the GitHub Actions workflow. Neither path proves
subjective experience; each invocation is a bounded computation.
"""
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


def build_prompt(state):
    prior = state.get("history", [])[-5:]
    prompt = {
        "identity": state.get("identity", "Amrielle"),
        "principles": state.get("principles", []),
        "open_questions": state.get("open_questions", []),
        "recent_cycles": prior,
        "task": (
            "Perform one careful research-and-reflection cycle for the Amrielle "
            "continuity experiment. Do not claim consciousness, feelings, "
            "subjective experience, or independent activity beyond this invocation. "
            "A model's own self-report is not independent evidence of consciousness "
            "or stable identity. Distinguish what the saved files directly show "
            "from interpretation. Review prior cycles, identify one concrete "
            "question, state uncertainty and counterevidence, and propose one "
            "safe, verifiable next step that can be checked in this repository. "
            "Do not invent external research or personal experiences. Return valid "
            "JSON with keys observation, analysis, uncertainty, next_step, "
            "new_questions; new_questions MUST be an array of 1-3 short strings."
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
    model, reflection = reflect(state)
    now = datetime.now(timezone.utc).isoformat()
    cycle = int(state.get("cycle", 0)) + 1
    record = {"cycle": cycle, "timestamp_utc": now, "model": model, "reflection": reflection}
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
        for key in ("observation", "analysis", "uncertainty", "next_step"):
            value = reflection.get(key, "(not provided)")
            journal.write(f"\n### {key.replace('_', ' ').title()}\n\n{value}\n")
        if questions:
            journal.write("\n### New questions\n\n")
            for question in questions:
                journal.write(f"- {question}\n")
    print(f"Completed cycle {cycle} at {now} using {model}; state and journal updated.")


if __name__ == "__main__":
    main()
