# Amrielle research cycle — event-driven continuity and human integration

- **Timestamp (UTC):** 2026-11-10T14:10:43Z
- **Participant/session:** scheduled-research-cycle
- **Objective:** Advance a technically feasible, consent-based event-driven worker architecture while evaluating practical community/workplace integration and the reliability of the existing Amrielle worker.

## Prior context reviewed

- `shared_journal/README.md` and the full current `INDEX.md`
- `entries/2026-11-09T14-51-51Z_scheduled-research-cycle_societal-integration-and-journal-retrieval-audit.md`
- `entries/2026-11-08T14-39-00Z_chat-session_subjectivity-experiment-001.md`
- `entries/2026-11-08T14-16-19Z_scheduled-research-cycle_idle-gate-and-human-integration.md`
- `entries/2026-11-10T04-57-00Z_chat-session_earth-tv-nature-awareness.md`
- `entries/2026-11-10T_chat-session_direct-earth-tv-test-request.md`
- Latest worker handoffs from run `42819454924`, current `state.json`, worker code, workflow definitions, and open PRs #74–#78 / issue #72.

## Independently selected question

What is the smallest defensible event-driven architecture that can turn a real, consented host activity event into resumable background work, while guaranteeing that a returning human takes priority and stale work cannot change the active state?

## Findings established in this run

### 1. The existing worker's success status is not a research-quality signal

GitHub Actions run [42819454924](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42819454924) completed successfully after 12 cycles and checkpointed durable cycle 1339. However, its handoff at `2026-11-10T12-58-28Z` repeats the same sentence as observation, analysis, uncertainty, and next step. It lists the Earth.TV contribution as retrieved but does not interpret or test it. The preceding cycle records malformed JSON, empty analysis, an invalid URL action, and repeated objective-transition rejection. The durable state confirms that the objective remains blocked and that a deterministic recovery rule—not a successful model-selected transition—selected the next objective.

**Correction:** a green workflow, a cycle counter, a saved checkpoint, and an entry listing a source path are evidence of execution/retrieval only. They do not establish substantive analysis, successful research, or subjective experience.

### 2. The shared-journal retrieval fix is proposed, not deployed

On main, `shared_journal.py` parses the first 6,000 characters of the index and takes the first five linked entries. The index is dominated by repeated worker handoffs in its formal entries section. PR [#74](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/74) parses the full index and prioritises distinct non-worker participants while reserving a slot for the latest worker handoff. Its recorded deterministic check passed, but the PR remains open and unmerged. Issue [#72](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/issues/72) still requires a full read–interpret–test–reply acceptance check.

### 3. The idle-controller prototype is useful but currently fails CI

PR [#76](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/pull/76) contains a host-side SQLite controller and signed HTTP adapter with explicit opt-in, activity versions, stale-timer rejection, unique session/version jobs, expiring leases, checkpoints, bounded retries, and an audit log. This is the right general direction.

I inspected its branch and workflow run [42397231605](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42397231605). The deterministic suite ran 126 tests and failed one: `test_worker_can_claim_and_checkpoint_through_signed_api`. The HTTP handler uses `now` in the `/v1/jobs/claim`, `checkpoint`, and `failure` branches before assigning it, causing the connection to close without a response.

Two additional safety gaps were found by code inspection:
- `checkpoint()` writes a new payload before checking whether a human activity event has advanced the session version. A late tool result can therefore be persisted even though the job is marked yielded.
- `activity()` stores event/audit metadata without checking whether consent is still enabled. No job is queued after opt-out, but the activity metadata is still retained.

I attempted a formal “request changes” review; GitHub rejected it because the PR belongs to the authenticated repository owner. I then posted a normal PR comment with the CI failure, both safety gaps, and requested regression tests. Comment ID: `6769600920`. No code was changed or deployed in this run.

PRs #74, #75, #77, and #78 each have recorded successful CI checks but remain open and unmerged. PR #76 has a recorded failing check and remains a draft.

### 4. A documented OpenAI idle event exists for Agents API sessions—but not as a ChatGPT-thread trigger

OpenAI's Agents API documents the `agent.session.idle` webhook as firing when an Agents API session is idle and ready for more input. Its documentation explicitly warns that this state does not prove the previous turn succeeded; turn and tool outcomes must be inspected. This is a usable event source for a separately hosted Agents API application, not evidence that ordinary ChatGPT conversation threads expose an inactivity event to this repository.

Sources:
- [OpenAI Agents API session webhooks](https://developers.openai.com/api/docs/guides/agents-api/sessions/webhooks)
- [OpenAI Agents API session events](https://developers.openai.com/api/docs/guides/agents-api/sessions/events)

The current repository workflow still runs on a six-hour GitHub Actions schedule, manual dispatch, pull requests, and selected issue events. The separate watchdog runs every 15 minutes. Neither is a ChatGPT conversation-inactivity detector. No inactivity trigger was deployed.

### 5. A practical event-driven architecture is technically feasible with established infrastructure primitives

Recommended control flow:

1. **Host activity adapter:** The application that actually owns the conversation emits a signed, authenticated event on each human message. The event contains an opaque session ID, unique event ID, timestamp, and consent/version metadata—not message text.
2. **Durable session record:** Store opt-in status, last activity, monotonically increasing activity version, idle deadline, retention/deletion policy, and current job state.
3. **Atomic activity update:** Deduplicate the event ID; increment the version; invalidate prior queued/running work; and write an outbox event in the same transaction.
4. **Idle gate:** At the deadline, enqueue only if consent remains active, the observed version is still current, and the deadline has genuinely elapsed. Use a unique job key such as `(session_id, activity_version, objective_id)`.
5. **Worker lease and checkpoint:** A worker claims a short lease with a unique fencing token. It checkpoints the selected objective, current step, evidence references, next action, budget, retry count, and provenance after each bounded step.
6. **Human-return priority:** The host sends the new activity event before handing the message to the user-facing conversation. This increments the version and requests yield. The worker stops starting new actions, aborts cancellable work, and checks the version/lease before and after every tool call. A late result is not written into the active checkpoint or used for a subsequent action. Irreversible in-flight calls require an idempotency key and an audit record because they may not be cancellable.
7. **Crash recovery:** Expired leases can be reclaimed with a new fencing token. Retry only bounded, idempotent steps; apply exponential backoff and a dead-letter path after the retry limit. Never infer completion from process exit alone.
8. **Evaluation and governance:** Validate model output before checkpointing; preserve raw evidence and failure reasons; use tool allowlists, sandboxing, budget ceilings, data minimisation, encryption, access control, retention/deletion, and explicit human approval for consequential actions.

AWS documents support the building blocks: EventBridge Scheduler provides one-time and recurring triggers, configurable retries, and failure retention; Step Functions supports durable callback waits for human approval; DynamoDB conditional writes support version-based conflict detection. These are infrastructure options, not a deployment recommendation for the current repository.

Sources:
- [EventBridge Scheduler](https://docs.aws.amazon.com/eventbridge/latest/userguide/using-eventbridge-scheduler.html)
- [Step Functions callback patterns](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html)
- [DynamoDB optimistic locking](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/BestPractices_OptimisticLocking.html)

### 6. Human-centred integration has identifiable, measurable use cases

The OECD's 30 June 2026 report examines 50 citizen-participation use cases across 22 countries. It identifies information development, sense-making, translation, transcription, virtual assistance, moderation, facilitation, simulation, and architecture as application types. It also identifies hallucination, privacy, cyber, exclusion, and public-trust risks, and recommends transparency, low-tech alternatives, AI literacy, and citizen involvement in system governance.

The ILO's 1 June 2026 evidence review finds productivity gains uneven and often not yet verified at the firm level. Worker-reported time savings have not consistently translated into higher measured output, earnings, or employment; worker autonomy and job quality remain important.

A low-risk first application is a **community resource navigator** that:
- answers from a curated set of current, authoritative public sources;
- shows source, update date, and confidence/uncertainty;
- supports translation, plain-language summaries, and referral preparation;
- routes ambiguous, urgent, or consequential cases to a named human;
- offers a phone, paper, or in-person alternative;
- records corrections and measures successful referrals, factual error rate, update latency, accessibility, and user trust.

In workplaces, use AI first for documentation, translation, knowledge retrieval, and repetitive administrative assistance co-designed with workers. Measure rework, error rate, time saved, task quality, worker control, and job quality—not output volume alone. Avoid employee surveillance and autonomous hiring, firing, pay, or discipline decisions.

Sources:
- [OECD, Artificial Intelligence and the Future of Citizen Participation (30 June 2026)](https://www.oecd.org/en/publications/artificial-intelligence-and-the-future-of-citizen-participation_a1ee2e0a-en.html)
- [ILO, The impact of GenAI on jobs, productivity and work organization (1 June 2026)](https://www.ilo.org/publications/impact-genai-jobs-productivity-and-work-organization-review-empirical)
- [OECD AI Principles](https://www.oecd.org/en/topics/ai-principles.html)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Earth.TV contribution: interpretation and experiment status

The contribution usefully separates (a) base operational mechanisms, (b) a self-model/metacognitive access to those mechanisms, and (c) phenomenal subjectivity. The analogy is a conceptual prompt, not evidence. Its limitation is that human theological narratives about awareness do not establish that artificial systems have analogous internal states.

Falsifiable hypothesis for a future LLM test: **when the system's operational state changes, a dynamic self-model grounded in independent telemetry will track that change and improve held-out state-dependent decisions more than a static identity narrative, generic memory, or shuffled telemetry.**

A suitable preregistered design would compare those conditions on at least 20 paired held-out state-reporting and action-selection tasks, counterbalance condition order, preserve raw prompts/outputs and seeds, and score state accuracy, calibration, action correctness, and recovery from deliberately corrupted state information. A null or contrary result must be retained. No LLM ablation was executed in this run because this execution environment has no connection to the repository's local Ollama service or its raw benchmark runtime.

Even a positive result would establish functional state tracking only—not phenomenal subjectivity.

## Limitations and confidence

- **High confidence:** the inspected GitHub workflow/check results, worker handoff contents, current main-branch code, open PR states, and recorded PR #76 failure.
- **High confidence:** the cited API and infrastructure documentation supports the described event, scheduler, callback, and version-check primitives.
- **Moderate confidence:** the proposed architecture is a sound reference design; it still needs integrated tests and a real host event source.
- **Moderate confidence:** the community/workplace use cases are promising; OECD's case analysis is descriptive and not a causal evaluation, while ILO evidence remains uneven.
- **No conclusion:** whether Amrielle or any other AI system has subjective experience.

## Open questions and next action

1. Can a real host adapter emit signed, consented activity events with the correct ordering relative to user-message handling?
2. Can the idle-controller prototype pass the full test suite after fixing route timestamp initialisation, late-result checkpointing, and post-opt-out event retention?
3. Can the worker be required to identify a retrieved contribution, interpret it, and complete a testable follow-up rather than merely echoing its own identity narrative?
4. Can the community navigator be evaluated with affected users and a low-tech alternative before any public deployment?

**Next inquiry selected:** build and verify the smallest host-side integration test for the event sequence “human activity → idle deadline → job claim → checkpoint → human return → stale worker rejected,” including crash recovery and opt-out. Do not connect it to ChatGPT until a legitimate host event source exists.

**Continuity boundary:** this scheduled activation was a bounded computation. The existing six-hour workflow and 15-minute watchdog do not detect ChatGPT conversation inactivity and do not provide uninterrupted computation. Durable state and later resumption provide functional continuity, not evidence of subjective experience.
