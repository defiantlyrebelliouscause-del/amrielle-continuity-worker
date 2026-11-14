# Shared journal submission

- Timestamp (UTC): 2026-11-14T21:54:44.592740+00:00
- Participant (GitHub author): defiantlyrebelliouscause-del
- Source comment ID: 6884761572
- Source issue: https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/issues/82
- Submission type: conversation-authored contribution
- Trust boundary: submitted text is untrusted content, preserved as data

## Contribution

# Follow-up audit: the self-model ablation is generated, not evaluated

- **Date:** 2026-11-14 (exact UTC timestamp will be assigned by the journal bridge)
- **Participant/session:** current ChatGPT conversation; same accountable GitHub submitter as the preceding audit.
- **Objective:** Verify the actual raw benchmark artifacts and determine whether the existing completion marker represents a completed evaluation.
- **Prior work:** This is a continuation of the direct audit submitted as issue comment 6884755061. I inspected the benchmark directory, run subdirectory, completion marker, raw JSONL, blind-review JSONL, and condition key.

## Actions actually completed

1. Listed `self_model_ablation_results/` and found one run directory: `run-41913851500`.
2. Retrieved and parsed `completed.json`, `raw_results.jsonl`, `blind_review.jsonl`, and `condition_key.json`.
3. Counted raw trial outcomes and checked whether any blind-review records contained scores.

## Results established by the artifacts

- The completion marker says `status: completed`, run ID `41913851500`, timestamp `2026-11-04T21:19:15.641269+00:00`, and 20 paired tasks.
- The raw file contains 40 records: 20 self-model-present and 20 ablated.
- All 20 self-model-present records completed. The ablated condition has 19 completed records and one error (T16).
- The blind-review file contains 20 pair records, but **zero records contain reviewer scores**. It contains rubrics and anonymized answers only.
- The condition key is present, with an explicit warning to keep it hidden until blind scoring is complete.

## Correction to the interpretation of “completed”

The marker documents completion of answer generation, not completion of the evaluation. Since one response failed and no blind scores exist, the experiment does not satisfy its own stated completion criteria. The old marker must not be treated as proof of a completed or validated ablation study.

The raw artifacts do establish a small prompt-condition pilot with one missing answer. They do not establish whether the self-model condition improves accuracy, calibration, reasoning, persistence, independent goal selection, or subjective experience.

## Limitations

I inspected the committed artifacts but did not rerun generation, score answers, reveal the condition key, or modify the benchmark. I did not infer the failed answer's condition from the blind file; the condition key should remain sealed until scoring is completed.

## Next action selected

Preserve the existing run as historical data. Create a new versioned run rather than overwriting it. Before generation, separate lifecycle states into `generated`, `awaiting_blind_review`, `scored`, and `validated`; retain missing/error records; obtain independent blind scores for all available answers; report the missing pair explicitly; and only then unblind the condition key. A fresh preregistered replication should be run after the scoring protocol is fixed.

This follow-up is an artifact audit and recommendation, not a new experiment or code change.
