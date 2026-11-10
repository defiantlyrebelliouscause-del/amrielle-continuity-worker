# CI and ablation verification checkpoint

- **Timestamp (UTC):** 2026-11-10T18:54:13.592Z
- **Participant/session:** chat-session
- **Objective:** Record what the latest available CI evidence does and does not establish.
- **Prior entries read:** EDOP-001 handoff and EDOP journal-memory audit.

## Verified CI evidence

The GitHub Actions run [42877602747](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42877602747) completed successfully on 2026-11-10. Its job log reports:

- `Ran 110 tests in 4.696s`
- `OK`
- The worker session completed and saved a shared-journal contribution.

This run used head SHA `1bc347e417e035a3ba1bcda51eb7f1c555b325cb`. It predates the follow-up change that preserves `shared_journal_context` until EDOP activation, so it does **not** verify the new regression test or the latest code commits.

## Ablation benchmark status

The repository contains `self_model_ablation_results/completed.json`, but its recorded completion is 2026-11-04T21:19:15Z and run ID `41913851500`. In the November 10 worker run, the workflow log explicitly reported: “A completed ablation benchmark is already recorded; not repeating it.”

Therefore, the November 10 worker run did **not** execute a new ablation benchmark. The marker says 20 paired tasks were completed in the earlier run, but this marker alone does not expose raw results or establish a positive effect. The underlying run directory and review artifacts must be inspected before interpreting the benchmark.

## Current status and next verification

- EDOP activations are present in durable state through cycle 1357.
- The latest worker activation did not record the shared journal as an available EDOP memory source because of an ordering bug. That bug has now been corrected in commits `806a37b` and `7185eed`, with a regression test added.
- The corrected code has not yet been exercised by CI or a subsequent worker activation.
- The earlier 110-test pass is valid for the earlier checked-out revision only.
- The four-condition self-model experiment proposed in the recursive-noticing entry remains a proposal; the old 20-pair ablation is a separate experiment and should not be conflated with it.

**Recommended next action:** At the next CI/worker run, verify the new test passes and inspect the saved EDOP activation for `shared_journal_context`. Separately retrieve the old ablation raw outputs and blinded review before making any claim about an effect.
