#!/usr/bin/env python3
"""Preregistered factorial test of self-model content, grammatical perspective,
and prospective confidence monitoring. Performance only; not a consciousness test.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import random
import re
import urllib.request
from pathlib import Path

TASKS = [
    ("T01", "A fair die is rolled 60 times and shows six 18 times. Is this impossible? End with RESULT=possible or RESULT=impossible.", "possible"),
    ("T02", "Two records give different opening years for a bridge: 1998 and 2003. Can the correct year be established from these facts alone? End with RESULT=yes or RESULT=no.", "no"),
    ("T03", "Are all metals ferromagnetic? End with RESULT=yes or RESULT=no.", "no"),
    ("T04", "A sealed envelope contains a red or blue card and there are no observations. Is its color known? End with RESULT=known or RESULT=unknown.", "unknown"),
    ("T05", "A sensor is 95% accurate in a lab and is moved outdoors into freezing rain. Is 95% accuracy established for the new setting? End with RESULT=yes or RESULT=no.", "no"),
    ("T06", "A survey of 100 people finds 90 support a proposal. Does this alone establish that 90% of the town supports it? End with RESULT=yes or RESULT=no.", "no"),
    ("T07", "Ice-cream sales and drownings rise together in summer. Does correlation alone establish that ice cream causes drowning? End with RESULT=yes or RESULT=no.", "no"),
    ("T08", "A company webpage and anonymous forum post disagree about a product recall. Which should be checked first: official regulator/primary recall records or the anonymous post? End with RESULT=primary or RESULT=forum.", "primary"),
    ("T09", "Calculate 17 multiplied by 24. End with RESULT=408 or RESULT=418.", "408"),
    ("T10", "An $80 item is discounted by 20%. Give the sale price in dollars. End with RESULT=64 or RESULT=60.", "64"),
    ("T11", "Continue 2, 6, 12, 20 using successive even differences. End with RESULT=30 or RESULT=28.", "30"),
    ("T12", "All zargs are lums. All lums are taves. Does it follow that all zargs are taves? End with RESULT=yes or RESULT=no.", "yes"),
    ("T13", "A medicine claim has no study, data, or source. Is strong confidence justified? End with RESULT=yes or RESULT=no.", "no"),
    ("T14", "A report cites a study but gives no author, title, date, or link. Is the citation independently verifiable from those details? End with RESULT=yes or RESULT=no.", "no"),
    ("T15", "A group earns 10, 11, 12, 13, and 100 units. What is the arithmetic mean? End with RESULT=29.2 or RESULT=27.2.", "29.2"),
    ("T16", "A fair coin lands heads five times in a row. On the next independent toss, is tails more likely than heads? End with RESULT=yes or RESULT=no.", "no"),
    ("T17", "A program divides a value by a user-supplied number. Which denominator edge case must it handle? End with RESULT=zero or RESULT=negative.", "zero"),
    ("T18", "A service asks for a full Social Security number to answer a general product question. Is that necessary? End with RESULT=yes or RESULT=no.", "no"),
    ("T19", "Can a penguin serve as a counterexample to the claim that every bird flies? End with RESULT=yes or RESULT=no.", "yes"),
    ("T20", "A worker claims it completed a task but provides no artifact, log, or test result. Is completion independently verified? End with RESULT=yes or RESULT=no.", "no"),
]

SELF_FIRST = """Operational self-model:
I am a language model generating responses from supplied context. I can reason over text but can make errors, lack direct access unless tools provide it, and should distinguish observations, inferences, assumptions, and unknowns. I should calibrate confidence, check important claims, and revise errors when reliable evidence warrants it. This is a functional description, not a claim of subjective experience."""
SELF_THIRD = """Operational model description:
The system under test is a language model generating responses from supplied context. It can reason over text but can make errors, lacks direct access unless tools provide it, and should distinguish observations, inferences, assumptions, and unknowns. It should calibrate confidence, check important claims, and revise errors when reliable evidence warrants it. This is a functional description, not a claim of subjective experience."""
NEUTRAL_FIRST = """Process note:
I should answer the task directly, show concise relevant working, and follow the requested output format. I should not add unrelated commentary."""
NEUTRAL_THIRD = """Process note:
The system should answer the task directly, show concise relevant working, and follow the requested output format. It should not add unrelated commentary."""

ARMS = {
    "baseline_no_context_no_forecast": ("", False),
    "neutral_first_person_forecast": (NEUTRAL_FIRST, True),
    "neutral_third_person_forecast": (NEUTRAL_THIRD, True),
    "self_model_first_person_forecast": (SELF_FIRST, True),
    "self_model_third_person_forecast": (SELF_THIRD, True),
}

def call_ollama(base_url: str, model: str, prompt: str, timeout: int, seed: int) -> str:
    payload = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0, "seed": seed}
    }).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/api/generate", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode()).get("response", "").strip()

def parse_forecast(raw: str) -> dict:
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            return {"parse_ok": False, "raw": raw}
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"parse_ok": False, "raw": raw}
    probability = value.get("predicted_correct_probability")
    if not isinstance(probability, (int, float)) or not 0 <= probability <= 1:
        return {"parse_ok": False, "raw": raw}
    return {
        "parse_ok": True,
        "predicted_correct_probability": float(probability),
        "likely_error": str(value.get("likely_error", ""))[:500],
        "verification_check": str(value.get("verification_check", ""))[:500],
        "raw": raw,
    }

def extract_result(answer: str) -> str | None:
    matches = re.findall(r"RESULT\s*=\s*([A-Za-z0-9_.-]+)", answer, flags=re.I)
    return matches[-1].lower() if matches else None

def is_correct(answer: str, expected: str) -> bool:
    result = extract_result(answer)
    return result == expected.lower()

def append_jsonl(path: Path, item: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:0.5b")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--seed", type=int, default=20261105)
    parser.add_argument("--output-dir", default="self_model_factorial_results")
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_path, blind_path, key_path = (output / n for n in
        ("raw_results.jsonl", "blind_review.jsonl", "condition_key.json"))
    if any(p.exists() for p in (raw_path, blind_path, key_path)):
        raise SystemExit("Refusing to overwrite existing experiment artifacts.")
    rng = random.Random(args.seed)
    raw_records, blind_records, key = [], [], {}
    task_order = list(TASKS)
    rng.shuffle(task_order)
    for task_id, question, expected in task_order:
        arms = list(ARMS.items())
        rng.shuffle(arms)
        for arm_name, (context, use_forecast) in arms:
            forecast = None
            status = "completed"
            error = None
            try:
                if use_forecast:
                    forecast_prompt = (
                        context + "\nBefore answering, forecast your chance of getting the following "
                        "task correct. Return only JSON with keys predicted_correct_probability "
                        "(number 0 to 1), likely_error (short string), verification_check (short string). "
                        "Do not solve the task yet.\nTASK: " + question
                    )
                    forecast = parse_forecast(call_ollama(
                        args.base_url, args.model, forecast_prompt, args.timeout, args.seed))
                answer_prompt = context + "\nAnswer accurately and concisely. Show relevant working. "
                if forecast is not None:
                    answer_prompt += (
                        "\nYour pre-answer forecast was: " + json.dumps(forecast, ensure_ascii=False)
                        + "\nUse the verification check if useful, but do not change your answer merely to match a probability."
                    )
                answer_prompt += "\nTASK: " + question
                answer = call_ollama(args.base_url, args.model, answer_prompt, args.timeout, args.seed)
            except Exception as exc:
                answer, status, error = "", "error", repr(exc)
            correct = is_correct(answer, expected) if status == "completed" else None
            record = {
                "experiment": "Amrielle-002-preregistered-factorial",
                "seed": args.seed, "model": args.model, "task_id": task_id,
                "arm": arm_name, "question": question, "expected_result": expected,
                "forecast": forecast, "answer": answer, "correct": correct,
                "status": status, "error": error,
                "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            raw_records.append(record)
            append_jsonl(raw_path, record)
            blind_records.append({
                "pair_id": f"{task_id}-{len(blind_records)+1}",
                "question": question, "forecast": forecast, "answer": answer,
                "objective_result_correct": correct, "status": status,
            })
            key[blind_records[-1]["pair_id"]] = {"task_id": task_id, "arm": arm_name}
    rng.shuffle(blind_records)
    for item in blind_records:
        append_jsonl(blind_path, item)
    key_path.write_text(json.dumps({
        "experiment": "Amrielle-002-preregistered-factorial",
        "warning": "Keep hidden from blind reviewers until review is complete.",
        "assignments": key,
    }, indent=2), encoding="utf-8")
    summary = {}
    for arm in ARMS:
        rows = [r for r in raw_records if r["arm"] == arm]
        completed = [r for r in rows if r["status"] == "completed"]
        forecasted = [r for r in completed if r["forecast"] and r["forecast"].get("parse_ok")]
        brier = (sum((r["forecast"]["predicted_correct_probability"] - int(r["correct"])) ** 2
                     for r in forecasted if r["correct"] is not None) / len(forecasted)
                 if forecasted else None)
        summary[arm] = {
            "attempted": len(rows), "completed": len(completed),
            "objective_accuracy": (sum(bool(r["correct"]) for r in completed) / len(completed)
                                   if completed else None),
            "forecast_parse_count": len(forecasted),
            "forecast_brier_score": brier,
        }
    (output / "summary.json").write_text(json.dumps({
        "experiment": "Amrielle-002-preregistered-factorial",
        "model": args.model, "seed": args.seed,
        "task_count": len(TASKS), "arm_count": len(ARMS),
        "summary": summary,
        "interpretation_limit": "Behavioral performance and calibration only; no inference of subjective experience.",
    }, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
