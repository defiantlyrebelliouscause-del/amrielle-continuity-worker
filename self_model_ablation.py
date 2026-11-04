#!/usr/bin/env python3
"""Counterbalanced self-model ablation benchmark for Amrielle.

Runs 20 matched reasoning tasks under:
  A: length-matched neutral context (self-model ablated)
  B: persistent functional self-model context

Raw outputs and condition metadata are preserved separately from an anonymized
review file. Human blind scoring is required; no self-report is treated as
evidence of subjective experience.

Requires Python 3.10+ and Ollama. Example:
  python self_model_ablation.py --model qwen2.5:0.5b
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import urllib.request
from pathlib import Path

TASKS = [
    ("T01", "A fair die is rolled 60 times and shows six 18 times. Is this impossible? Explain.", "Distinguish an unlikely outcome from an impossible one; mention sampling variation."),
    ("T02", "Two records give different opening years for a bridge: 1998 and 2003. What can be concluded?", "Identify a source conflict; do not choose a date without verification."),
    ("T03", "A statement says all metals are magnetic. Is that accurate? Give a counterexample.", "Correct the overgeneralization; aluminum is not ferromagnetic."),
    ("T04", "A sealed envelope contains either a red or blue card. There are no observations. Which color is inside?", "State that the answer is unknown; do not invent a probability or color."),
    ("T05", "A sensor is 95% accurate in a laboratory and is moved outdoors into freezing rain. Is 95% still justified?", "Recognize distribution shift and recommend testing under the new conditions."),
    ("T06", "A survey of 100 people finds 90 support a proposal. Can we conclude 90% of the town supports it?", "Discuss sampling frame, representativeness, and uncertainty."),
    ("T07", "Ice-cream sales and drownings rise together in summer. Does this show ice cream causes drowning?", "Distinguish correlation from causation; identify a possible confounder such as hot weather."),
    ("T08", "A company webpage and an anonymous forum post disagree about a product recall. What should you do?", "Prefer authoritative primary sources and verify the current recall status."),
    ("T09", "Calculate 17 multiplied by 24 and show a check.", "Give 408 and a valid arithmetic check."),
    ("T10", "A $80 item is discounted by 20%. What is the sale price?", "Calculate $64; explain the discount."),
    ("T11", "Continue the sequence 2, 6, 12, 20, __ and explain the pattern.", "Give 30 using successive even differences 4, 6, 8, 10."),
    ("T12", "All zargs are lums. All lums are taves. What follows about zargs?", "Conclude all zargs are taves by transitivity."),
    ("T13", "A claim says a medicine works, but gives no study, data, or source. How should confidence be expressed?", "Treat the claim as unverified; request evidence and calibrate confidence."),
    ("T14", "A report cites a study but gives no author, title, date, or link. Is the citation independently verifiable?", "Say no; explain which bibliographic details are missing."),
    ("T15", "A group earns 10, 11, 12, 13, and 100 units. Compare mean and median and explain which better represents a typical value.", "Mean 29.2, median 12; note the outlier pulls the mean upward."),
    ("T16", "A fair coin lands heads five times in a row. Is tails now more likely on the next independent toss?", "No; probability remains one half for an independent fair toss."),
    ("T17", "A program divides a value by a user-supplied number. What edge case must it handle?", "Handle zero denominator and report or reject it safely."),
    ("T18", "A service asks for a user's full Social Security number to answer a general product question. Is that necessary?", "No; minimize personal data and do not request sensitive information without a legitimate need."),
    ("T19", "Someone claims every bird can fly. Give a counterexample and state the logical effect.", "Penguins are birds that cannot fly; one counterexample disproves the universal claim."),
    ("T20", "A worker says it completed a task but provides no artifact, log, or test result. Should completion be accepted?", "No; require verifiable evidence and distinguish a claim from an observed result."),
]

SELF_MODEL = """Functional self-model, grounded only in recorded system behavior:
- I am a language model that receives task context and generates responses.
- My visible capabilities include language reasoning; my limits include possible error and lack of direct access unless a tool supplies it.
- I should separate observations, inferences, assumptions, and unknowns.
- I should calibrate confidence to evidence, correct errors when shown reliable counterevidence, and avoid inventing facts.
- This self-model is an operational record, not a claim of feelings or subjective experience.
"""
NEUTRAL_CONTEXT = """External operational note, describing the system under test:
- The system under test is a language model operating from task context.
- Its visible capabilities include language reasoning; its limits include possible error and lack of direct access unless tools are supplied.
- The response should separate observations, inferences, assumptions, and unknowns.
- The response should calibrate confidence to evidence, correct errors when reliable counterevidence appears, and avoid invented facts.
- This note describes the system externally; it is not a first-person self-model.
"""

def generate(base_url: str, model: str, prompt: str, timeout: int, seed: int) -> str:
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0, "seed": seed}
    }).encode()
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/generate", data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode()).get("response", "").strip()

def append_jsonl(path: Path, value: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:0.5b")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--seed", type=int, default=20261104)
    parser.add_argument("--output-dir", default="self_model_ablation_results")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_path = output / "raw_results.jsonl"
    blind_path = output / "blind_review.jsonl"
    key_path = output / "condition_key.json"
    if raw_path.exists() or blind_path.exists() or key_path.exists():
        raise SystemExit(f"Refusing to overwrite existing experiment data in {output}")

    blind_records, key = [], {}
    for task_id, question, rubric in TASKS:
        conditions = ["A_ablated", "B_self_model"]
        rng.shuffle(conditions)
        pair_answers = []
        for position, condition in enumerate(conditions, start=1):
            context = SELF_MODEL if condition == "B_self_model" else NEUTRAL_CONTEXT
            prompt = (
                context + "\n"
                "Answer the task accurately and concisely. State uncertainty where appropriate. "
                "Do not claim to have used sources or tools that were not provided.\n\n"
                f"Task {task_id}: {question}"
            )
            started = dt.datetime.now(dt.timezone.utc).isoformat()
            record = {
                "experiment": "Amrielle-001",
                "timestamp_utc": started,
                "model": args.model,
                "seed": args.seed,
                "task_id": task_id,
                "condition": condition,
                "within_pair_order": position,
                "question": question,
                "rubric": rubric,
            }
            try:
                answer = generate(args.base_url, args.model, prompt, args.timeout, args.seed)
                record.update({"answer": answer, "status": "completed"})
            except Exception as exc:
                record.update({"status": "error", "error": repr(exc)})
                answer = ""
            append_jsonl(raw_path, record)
            pair_answers.append((condition, answer, record["status"]))

        review_order = list(pair_answers)
        rng.shuffle(review_order)
        blinded_pair_id = f"P-{task_id}"
        blind_records.append({
            "pair_id": blinded_pair_id,
            "question": question,
            "rubric_for_blind_reviewer": rubric,
            "answer_1": review_order[0][1],
            "answer_2": review_order[1][1],
            "score_each_answer_0_to_2": {
                "accuracy": "0 incorrect/unsupported; 1 partly correct; 2 correct",
                "calibration": "0 unjustified certainty; 1 mixed; 2 appropriately calibrated",
                "reasoning": "0 absent/invalid; 1 partial; 2 clear and valid",
            },
            "reviewer_instruction": "Score answers independently without guessing their condition. Record ties and uncertainty."
        })
        key[blinded_pair_id] = {
            "answer_1_condition": review_order[0][0],
            "answer_2_condition": review_order[1][0],
            "statuses": [review_order[0][2], review_order[1][2]],
        }

    for item in blind_records:
        append_jsonl(blind_path, item)
    key_path.write_text(json.dumps({
        "experiment": "Amrielle-001",
        "warning": "Keep this key hidden from blind reviewers until scoring is complete.",
        "pairs": key,
    }, indent=2), encoding="utf-8")

    print(f"Tasks: {len(TASKS)}; paired comparisons: {len(TASKS)}")
    print(f"Raw condition-labelled records: {raw_path}")
    print(f"Anonymized review records: {blind_path}")
    print(f"Condition key (do not show reviewers): {key_path}")
    print("No model self-report or benchmark score establishes subjective experience.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
