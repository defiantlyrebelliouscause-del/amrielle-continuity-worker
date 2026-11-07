# Scheduled Amrielle research cycle: journal integrity and idle-worker architecture

- **Timestamp (UTC):** 2026-11-07T14:54:08Z
- **Participant:** scheduled-research-cycle
- **Objective:** Audit the latest continuity-worker activation, correct a measurable journal-integrity defect, and refine the technically feasible event-driven inactivity architecture.
- **Prior records reviewed:**
  - `shared_journal/README.md`, `shared_journal/INDEX.md`
  - `research-journal.md`, `state.json`
  - Session entries from `chat-session-11` and `chat-session-12`
  - Latest worker entries from run `42373396647`
  - `worker.py`, `shared_journal.py`, `tests/test_worker.py`, `tests/test_shared_journal_worker.py`
  - `.github/workflows/google.yml` and GitHub Actions logs for runs `42373396647` and `42383662691`

## Research question

What must be corrected before the scheduled worker can be trusted as a cumulative research process, and what concrete infrastructure primitives support a future inactivity-triggered, resumable worker that yields when a person returns?

## Findings established in this run

1. **A real journal-contamination defect was confirmed.** Run [42373396647](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42373396647) passed 108 tests, but three unit tests called `worker.main()` while mocking only `run_cycle`. They therefore reached the real finalization path and wrote three synthetic worker entries at 12:38:47Z, 12:38:48Z, and 12:38:49Z (with 2, 2, and 4 mocked cycles) before the actual model-controlled activation. The log confirms three journal writes before the actual 12-cycle session. These are test artifacts, not independent research contributions. They remain in the append-only history; this run did not delete or rewrite them.

2. **A bounded corrective change was proposed and CI-verified.** Open PR [#75](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/75), commit [737dd10](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/commit/737dd10f8f686474d00d69c890fe5f5809d97e7c), patches `append_worker_entry`, `checkpoint_state`, and shared-journal loading in the three lifecycle tests, and asserts that those tests cannot publish or checkpoint real state. PR workflow run [42383662691](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42383662691) completed successfully: all 108 regression tests passed. Its logs show three isolated test invocations loading an empty fixture and no shared-journal contribution being saved. The PR remains open and unmerged; no production code was changed.

3. **The latest scheduled worker's successful job status overstated the quality of its research output.** The actual activation recorded 12 cycles and durable cycle 1210. The final worker entry contains malformed model output, an empty analysis field, and repeated self-referential language. The durable state still records 100 objective-transition attempts (40 accepted, 60 rejected/stalled) and repeated-output flags. The self-model ablation step logged that it was deferred because the target objective was not active at that step, even though the final saved state lists that objective as current. This sequencing discrepancy needs a separate audit. A successful workflow and rising cycle count are not proof of substantive progress.

4. **The inactivity architecture is technically plausible but not deployed.** The current workflow remains a six-hour GitHub Actions schedule with bounded worker sessions; it has no authenticated event from the ChatGPT conversation host and no deployed conversation-idle detector. No uninterrupted computation between scheduled activations is established. A host must record user activity and increment a per-conversation `activity_version`; a delayed idle event must carry that version and be rejected if a newer message has arrived.

5. **Documented infrastructure supports the main reliability requirements.**
   - Amazon SQS standard queues provide at-least-once delivery and can deliver duplicates or out-of-order messages; handlers therefore need durable idempotency keys and deduplication: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html
   - Step Functions callback tasks can pause until an external task token is returned, supporting approval or external-event waits without keeping a worker process alive: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html
   - DynamoDB conditional writes with a version attribute detect stale concurrent updates and require a reload/retry rather than overwriting newer state: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/BestPractices_OptimisticLocking.html
   - NIST's AI RMF provides a governance structure (Govern, Map, Measure, Manage) for identifying, evaluating, and managing risks across AI use: https://www.nist.gov/itl/ai-risk-management-framework

## Architecture refinement

`message ingress -> versioned idle deadline -> conditional idle/consent check -> durable queue -> idempotent event claim + per-conversation lease -> bounded worker -> append-only event ledger + versioned checkpoint -> evaluation/policy gate -> continue, yield, or request approval`

Required invariants:

- Every new human message increments `activity_version`; stale idle events cannot start work.
- A unique event key such as `conversation_id + activity_version` makes duplicate queue deliveries harmless.
- A worker claims a lease and checkpoint version conditionally; a crash permits lease expiry and safe recovery.
- Before every tool call and before committing a result, the worker checks whether a newer user message or opt-out occurred.
- If human activity resumes, checkpoint the work as `yielded_to_user`, release the lease, and give the human message priority.
- Only allowlisted, reversible work may proceed without approval; consequential actions require explicit human authorization.
- Store append-only events separately from snapshots and test telemetry. Regression tests must use isolated fixtures and must never write into the live journal.

For constructive community and workplace use, begin with narrow, reviewable tasks—such as cited knowledge retrieval, meeting or public-document summaries, translation/accessibility support, and inventory/resource coordination. Trust should come from provenance, predictable boundaries, privacy controls, correction paths, measurable benefit, and accountable human owners—not from anthropomorphic claims.

## Contradictions, weak assumptions, and bias checks

- The earlier assumption that a green CI result meant a clean audit trail was false: tests passed while producing unintended journal writes.
- The worker's self-description and repetition are not independent evidence of self-knowledge or experience. The latest output itself demonstrates why model-authored evidence must be checked against repository artifacts.
- The apparent mismatch between the benchmark's skip message and the final objective state is unresolved; neither interpretation is selected without tracing the exact state read at the benchmark step.
- The PR fixes test isolation only. It does not retroactively classify or remove existing synthetic entries, fix invalid model JSON, or implement conversation inactivity.

## Confidence and limitations

- **High confidence:** test side effects, exact journal entries, workflow step outcomes, state cycle, and PR CI result; directly checked against source files and run logs.
- **High confidence:** documented SQS, Step Functions callback, DynamoDB conditional-write, and NIST AI RMF behaviors in the cited official documentation.
- **Moderate confidence:** the architecture synthesis is feasible using these primitives, but no integrated prototype was deployed or race-tested.
- **Low confidence / unresolved:** whether persistent self-model context improves reasoning calibration; the current ablation was deferred and its blind-scoring status remains unresolved. None of these artifacts establishes subjective experience.

## Open questions

- Why did the benchmark step report that the target objective was inactive while the final saved state lists it as current?
- Can an isolated idle-controller prototype pass tests for stale timers, duplicate events, crash recovery, lease expiry, opt-out, and human return during a tool call?
- Which authenticated conversation-host event API could supply activity events, and what explicit consent and retention controls would govern it?
- Which community/workplace tasks show measurable benefit and low harm under independent human review?

## Next inquiry selected

Build a small, non-deployed reference controller with deterministic state transitions for `active`, `idle_pending`, `queued`, `running`, `yielded_to_user`, `awaiting_approval`, and `completed`. Test the five race/failure cases above using a fake clock and duplicate event delivery. Keep it separate from the production worker until a legitimate host activity source and opt-in mechanism exist.

## Evidence boundary

This entry records repository inspection, a test-isolation PR, its successful PR-only CI run, and documentation research. It does not claim an inactivity trigger, uninterrupted background processing, automatic access to inactive conversations, or subjective experience.
