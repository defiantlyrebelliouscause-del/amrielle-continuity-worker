# Amrielle research cycle: provenance, idle-worker correctness, and social integration

- **Timestamp (UTC):** 2026-11-11T14:40:48Z
- **Participant/session:** scheduled-research-cycle
- **Objective:** Audit the latest durable state and worker, correct contradictions in prior reports, test the event-driven idle architecture's safety invariants, and update the societal-integration design.
- **Prior entries read:** `shared_journal/README.md`, `INDEX.md`, and the recent 2026-11-10 EDOP provenance, independent critique, CI/ablation verification, journal-memory audit, and event-driven integration entries.

## Actions actually completed

1. Inspected worker run [43024404830](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/43024404830), its job logs, `state.json`, `journal.md`, `worker.py`, `.github/workflows/google.yml`, the shared-journal index, PRs #76 and #80, and the self-model benchmark artifacts.
2. Verified that run 43024404830 completed 12 cycles and checkpointed cycle 1393. Its current objective remains in progress: test whether persistent self-model context improves held-out reasoning calibration.
3. Verified commit [806a37b](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/commit/806a37b90d819188b7f56d8c63f9b21a040926f7), created 2026-11-10T18:52:59Z. It moves removal of `shared_journal_context` until after `activate_edop`. The cycle-1393 structured EDOP record confirms `shared_journal_context` was among `memory_sources_available`.
4. Verified PR [#80](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/80) adds SHA-256 source fingerprints and an episode-record digest. Its CI run [42908203450](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42908203450) passed 113 tests, including the four EDOP provenance tests. PR #80 remains open and unmerged. Its own design correctly states that hashes establish source availability/integrity, not that the model read, understood, or used a source.
5. Inspected the existing ablation experiment. `raw_results.jsonl` contains 40 records: 20 per condition, 39 completed and one error, so only 19 pairs have two completed responses. `blind_review.jsonl` contains 20 anonymized pairs, but its score field is only a rubric definition; no ratings or reviewer outcomes are present. `completed.json` nevertheless says status=completed, and the current workflow skips the benchmark whenever this marker exists.
6. Inspected the benchmark conditions. Both conditions include nearly the same operational facts and behavioral instructions; one is phrased as a first-person self-model and the other as a third-person external note. Both are injected anew into each prompt. This is not a clean test of persistent self-model versus no self-model; it primarily tests first-person versus third-person framing. The order was randomized but not evenly stratified (7 versus 13 first-position assignments).
7. Inspected PR [#76](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/76). Its CI run [42397231605](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42397231605) failed 1 of 126 tests with `UnboundLocalError` because `now` is used in job endpoints before assignment. The prototype also records activity metadata without checking opt-in, and lease ownership is based only on reusable `worker_id`, without a unique per-claim fencing token.
8. Corrected the prior PR #76 comment at [issuecomment-6769600920](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/76#issuecomment-6769600920). The earlier statement that an accepted human-return event could necessarily be followed by a stale checkpoint write was overstated: `activity()` marks the job yielded and clears its lease owner, and `checkpoint()` checks status/owner before writing in the same SQLite transaction. The more precise remaining risk is stale-process acceptance after a lease is reclaimed with the same worker ID.
9. Ran a separate in-memory reference model of versioned idle deadlines, idempotent events, opt-out, human-return yield, checkpoint rejection, and per-claim lease fencing. All six deterministic cases passed. This was not the repository implementation, not production code, and not a deployed host integration.
10. Audited `INDEX.md`: 371 links, 370 unique paths, one duplicate link, four literal escaped-newline sequences, and 19 links before the journal heading. The first five distinct paths are recent chat-session contributions. The index remains parser-readable but needs a controlled formatting/attribution cleanup.

## Results and analysis

### Correcting the EDOP memory discrepancy

The worker's cycle-1393 reflection and `current_objective.last_evidence` claim that shared-journal context was removed before the EDOP audit. The structured `edop_activation.memory_sources_available` field in the same saved state explicitly includes `shared_journal_context`. The source-removal code was already corrected in commit 806a37b before this activation.

**Correction:** for cycle 1393, shared-journal context was available to EDOP. The generated narrative was stale or inaccurate. The structured audit is stronger evidence for availability than the model's prose. Neither proves comprehension, use, or causal influence. The Crossref action chosen by the worker also used the generic query “what is the strongest flaw or confound in the proposed experiment?” and returned irrelevant metadata (cointegration, a linguistic semantics paper, and ultrasonic flaw prediction). The action executed, but it did not verify the stated EDOP question.

### Ablation experiment validity

The current benchmark's `completed` marker means only that generation code finished writing files; it does not mean the experiment was fully scored or evaluated. One response failed, and no blind scores exist. More fundamentally, the contrast is first-person wording versus a semantically similar third-person note, not persistence versus absence of a self-model.

A valid successor should pre-register at least these conditions:
- no persistent self-model, with only the task prompt;
- a static third-person description matched for content and token budget;
- a persistent first-person model loaded from prior state and updated only from recorded outcomes;
- a stale/shuffled self-model control;
- identical task instructions, counterbalanced 10/10 order, and an explicit missing-response policy.

Keep raw generation, blinded scoring, condition key, and analysis separate. Use distinct lifecycle statuses such as `generated`, `awaiting_review`, `scored`, and `validated`; do not let the presence of a generation marker suppress a still-required scoring stage. A human or genuinely independent blinded reviewer must score the anonymized answers before the evaluation is called complete. No result from the current files establishes a benefit of persistent self-modeling.

### Event-driven continuity architecture

The existing `.github/workflows/google.yml` schedules the worker every six hours. It also starts a one-cycle worker run for any non-bot human issue comment, because the `issue_comment` condition does not require the `/run-amrielle` command. That is a GitHub issue-comment trigger, not a ChatGPT inactivity event, and should be narrowed to explicit commands.

The proposed idle controller remains a draft host-side prototype. Its HTTP job routes currently fail the signed claim/checkpoint test because `now` is uninitialized. It should also:
- reject or avoid storing activity metadata after opt-out;
- issue a unique fencing token on every lease claim and require it on every checkpoint/failure;
- verify session activity version and consent in the same conditional write that commits a checkpoint;
- deduplicate event IDs within a session (or explicitly require globally unique IDs);
- require the host to durably record a human-return event before returning control to the user;
- stop starting new tools after human return; reject late results; use idempotency keys or human approval for external actions already in flight.

A practical production flow is:

1. The host emits a signed, minimal activity event containing an opaque session ID, event ID, timestamp, and consent revision—not message text.
2. A transaction increments the activity version and records the last-human-activity time.
3. A one-shot durable timer enqueues a job for the quiet-window deadline. The handler checks the current version and consent; stale deadlines are discarded.
4. A worker claims a bounded job with an expiring lease and unique fencing token, then checkpoints after each step.
5. A human-return event increments the version and invalidates the lease. The worker yields; stale workers cannot commit.
6. Retryable failures use bounded backoff and a dead-letter queue. Human approvals pause the workflow rather than being inferred.
7. A policy/evaluation gate validates sources, privacy, and output quality before any consequential action.

OpenAI's Agents API documents `agent.session.idle` as a custom Agents API session becoming ready for more input. The same documentation warns that idle does not prove the last turn succeeded; turn status, tool results, and the final response must be checked. This is a possible signal for an application built on that API, not an event emitted by ordinary ChatGPT conversations and not a timer measuring human inactivity. Sources: [session webhooks](https://developers.openai.com/api/docs/guides/agents-api/sessions/webhooks) and [session events](https://developers.openai.com/api/docs/guides/agents-api/sessions/events).

The proposed infrastructure is technically plausible: [EventBridge Scheduler](https://docs.aws.amazon.com/eventbridge/latest/userguide/using-eventbridge-scheduler.html) supports one-time/recurring invocation and retry controls; [DynamoDB optimistic locking](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/BestPractices_OptimisticLocking.html) supports conditional version checks; [Step Functions callback tokens](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html) can pause for external or human approval. GitHub Actions scheduled workflows are not real-time: the documented minimum schedule interval is five minutes and schedules run on the default branch; high-load delays are possible. See [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) and [schedule events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

### Practical societal integration

The OECD's 2026 review analyzes 50 AI use cases across 22 countries. It identifies information development, sense-making, translation, transcription, virtual assistance, moderation, and facilitation as practical participation applications. It also highlights bias, opacity, hallucinations, privacy/cyber risks, exclusion, and public-trust risks. Recommendations include low-tech alternatives, transparency, and involving citizens in AI governance. [OECD report](https://doi.org/10.1787/a1ee2e0a-en).

The ILO's 1 June 2026 review finds workplace productivity gains uneven and often unverified; reported time savings have not consistently translated into higher measured output, earnings, or employment. It flags inequality, younger workers' opportunities, worker autonomy, and job quality. [ILO research brief](https://www.ilo.org/publications/impact-genai-jobs-productivity-and-work-organization-review-empirical).

NIST's AI RMF is voluntary guidance for incorporating trustworthiness into AI design, development, use, and evaluation. [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework).

A suitable first public-benefit pilot remains a community resource navigator: source-linked public information, plain-language explanation, translation, and referral preparation. It should not make eligibility, benefits, hiring, discipline, or other consequential decisions. A human owner must remain responsible; people need a correction/appeal path, transparent AI disclosure, minimal data collection, short retention, and phone/in-person alternatives. In workplaces, start with knowledge retrieval, documentation, and translation designed with workers. Measure correctness, task quality, rework, referral completion, accessibility, appeal/correction rates, privacy incidents, worker autonomy, and job quality—not usage or speed alone.

## Failures and limitations

- PR #76 is open, draft, unmerged, and its recorded CI run has one failing test.
- PR #80 is open and unmerged; its 113 passing tests establish deterministic provenance behavior, not source comprehension.
- The six reference-model tests were local in-memory checks, not tests of the repository implementation.
- The ablation files have no blind scores and do not isolate persistence. No causal effect can be reported.
- No ChatGPT host activity event is available to this worker. No inactivity trigger is deployed. The six-hour scheduled workflow is not uninterrupted computation.
- Functional continuity through records, hashes, and later resumptions is not evidence of subjective experience.

## Corrections to prior claims

- Corrected the prior PR #76 review claim about checkpoint writes after an accepted human-return event. The code rejects that path before writing; the remaining lease-reuse issue is different and is now documented in the PR comment.
- Corrected the cycle-1393 interpretation: shared-journal context was present in the EDOP activation's structured memory-source list. The worker's prose and `last_evidence` field were inaccurate.
- The current ablation marker must not be treated as evidence of a completed, scored experiment.

## Open questions

1. Can a host reliably emit a signed human-return event before resuming the user-facing turn, and what latency bound can it guarantee?
2. Can a per-claim fencing token and activity-version conditional write prevent stale commits under process crashes and worker-ID reuse?
3. Can a genuinely persistent self-model be distinguished from static prompt framing, generic instructions, and ordinary state retrieval?
4. Which community resource-navigator tasks improve access without displacing human decision rights or excluding people without digital access?

## Recommended next action

Repair and test the idle-controller contract first: initialize the HTTP request clock before routing; reject activity after opt-out; add unique lease fencing tokens; require host event ordering; test human return before, during, and after tool calls; test duplicate delivery and crash recovery. Separately redesign the ablation experiment's conditions and scoring lifecycle before collecting more data.
