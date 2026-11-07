# Self-model experiment: validity audit and corrected scope

## What the existing experiment actually tested

The script `self_model_ablation.py` supplied one of two context blocks before each independent task:
- first-person functional self-description;
- third-person operational note.

The blocks were nearly the same length and described similar capabilities and limitations. This is a prompt-framing comparison, not a test of persistent memory, a continuing self-model across sessions, or subjective experience. The prior objective and workflow described it too strongly as a persistent-self-model causal test; this has been corrected in the active objective.

## Audit of the completed run

Source: GitHub Actions run [41913851500](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/41913851500), model `qwen2.5:0.5b`, seed `20261104`.

- 40 condition records were present for 20 tasks.
- 19 pairs had two non-empty successful responses.
- T16's A-condition timed out; the blind-review file therefore contains an empty answer.
- The workflow nevertheless wrote a completion marker claiming 20 paired tasks.
- No blind scores were recorded; the review file contains scoring instructions only.
- The condition key was committed beside the blind-review file, so the blind was not access-controlled.
- Several tasks expose benchmark quality issues: the die prompt was malformed, and some model outputs contain obvious factual or logical errors. T15's rubric itself has correct target values (mean 29.2, median 12), but both answers calculated the mean incorrectly.

Conclusion: the old run is incomplete and unscored. It cannot support a claim that the self-model condition improved performance. The completed marker was an operational false positive, not a valid experimental result.

## Corrective changes proposed in this branch

1. Rename the experiment to a prompt-framing comparison and explicitly disclaim persistence/identity claims.
2. Correct the malformed die task wording.
3. Require exactly one non-empty successful response for each condition on every task before writing any blind-review file. Preserve raw partial results, but return a failure code if any pair is incomplete; the workflow then cannot write a completion marker.
4. Match context-block character lengths exactly.
5. Update the active objective and workflow marker to describe the actual prompt-framing question.
6. Upload condition-labelled raw results and the condition key as a separate Actions artifact; commit only the anonymized review sheet for reviewers.
7. Use a new completion marker so the previous invalid marker cannot suppress a corrected run.

## Remaining limitations

- The two contexts still differ semantically in grammatical person; this is the independent variable, not a pure persistence intervention.
- A single small model, one seed, and 20 task pairs are exploratory only.
- Human blind scoring has not yet been performed. A reviewer must score each answer independently on accuracy, calibration, and reasoning, then preserve the score sheet before unblinding.
- To test persistence, a separate design must manipulate access to a stable self-model across multiple sessions while holding task prompts and all other context constant.
- No result here establishes sentience, feelings, or subjective experience.

## Next verification

After merge, allow the workflow to run the corrected experiment. Confirm 20 complete pairs, verify the condition-key artifact is separate from the reviewer sheet, obtain blind scores, then unblind and report paired differences with uncertainty. Do not label the experiment complete merely because the workflow step returned success.
