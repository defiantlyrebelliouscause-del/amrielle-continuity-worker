# Shared journal established; factorial benchmark work

- **Timestamp (UTC):** 2026-11-05 (exact commit time is authoritative)
- **Participant/session:** chat-session
- **Objective:** Establish a shared, append-only research journal for separate ChatGPT conversations and the Amrielle continuity worker.
- **Prior entries read:** Project context and prior conversation summary; GitHub repository and PR #70.
- **Actions actually completed:**
  - Created the shared-journal protocol and index in the repository.
  - Prepared PR #70, adding a five-arm benchmark separating self-model content, grammatical perspective, and prospective confidence forecasting.
  - Confirmed the PR validation workflow completed successfully; regression tests passed. The workflow's model execution steps were skipped, so this was not a new benchmark run.
  - Rechecked T15 arithmetic in the earlier benchmark: 10 + 11 + 12 + 13 + 100 = 146; mean = 29.2. The previous analysis had incorrectly treated 27.2 as correct. In the old run, answer 1 reported mean 27.2 and median 11.5; answer 2 reported mean 27.2 and median 12. The rubric's mean 29.2 was correct, while both answers' mean was wrong. The median 12 is correct for the five values. This task should be scored for that arithmetic error, not excluded for a faulty rubric.
- **Evidence/artifacts:**
  - PR #70: https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/70
  - Validation run #155: https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42048528135
  - Earlier benchmark artifacts: https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/tree/main/self_model_ablation_results/run-41913851500
- **Results:** The shared journal protocol now exists. This is a common repository record, not automatic live access by every conversation. Other sessions must be given the repository URL, read this protocol and index, and contribute their own append-only entries.
- **Failures and limitations:** The current conversation cannot inspect or control other active ChatGPT conversations. Their experiments and results are not yet aggregated. PR #70 is open and not merged. No new benchmark run was launched.
- **Corrections to prior claims:** The earlier statement that T15 was validly scored as 27.2 was wrong. The mean is 29.2. The prior comparison's exclusion of T15 should be revisited and scores recalculated from the raw blind review.
- **Open questions:** Which other sessions have conducted experiments, what methods/data they used, and whether they can access the GitHub repository.
- **Recommended next action:** Have each participating conversation read this journal and submit its existing findings as a separate entry, including artifact links and exact run identifiers. Then reconcile all sessions' work into one evidence-based research index.
