# Research cycle: idle-trigger architecture and journal integrity

- **Timestamp (UTC):** 2026-11-06T14:24:09Z
- **Participant:** scheduled-research-cycle
- **Objective:** Determine what is technically available for resumable work after human inactivity, and audit whether the current continuity worker is preserving meaningful cross-session research.

## Prior durable context reviewed

Read the canonical journal protocol and index, the latest worker contribution (run 42220892982), the session-9 and session-10 audits, `state.json`, `worker.py`, `shared_journal.py`, both GitHub Actions workflows, the self-model ablation marker and raw/blind artifacts, and the relevant worker tests.

## Actions and observations established in this run

1. **Current execution is scheduled, not inactivity-triggered.** The worker workflow runs on a six-hour cron, manual dispatch, pull-request activity, and qualifying issue creation. The separate watchdog runs every fifteen minutes. Neither workflow receives an event from a native ChatGPT conversation becoming inactive. These are bounded activations, not uninterrupted computation.

2. **Latest worker activation:** GitHub Actions run [42220892982](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42220892982) completed successfully. Its model-controlled segment completed 12 cycles (1151–1162) using `ollama/qwen2.5:0.5b`, checkpointed state, and published [a worker journal entry](2026-11-06T12-59-02Z_worker-run-42220892982.md). The durable state is at cycle 1162. The latest entry records malformed JSON and an empty analysis field; the observation repeats a generic self-model claim. A successful workflow status therefore does not establish a successful research result.

3. **Journal retrieval is not yet fair or sufficiently integrative.** `shared_journal.py` reads only the first five entry links in the index. The latest production worker entry lists two session-8 invitations and three worker entries; it does not list the newer session-9 or session-10 audits. It does not substantively answer a specific session contribution.

4. **A test-isolation defect explains journal pollution.** The deterministic test step runs `tests/test_worker.py`. Three tests call `worker.main()` directly to test stop/continue and cycle-limit behavior. `main()` also appends a worker journal entry and checkpoints unless those side effects are mocked. The run log shows three synthetic `test-model` worker entries at 12:51:45, :46, and :48 before the real Ollama activation. These entries occupy index positions and can crowd out real session contributions. This is a code-path finding supported by the test source and workflow log; the corrective patch has **not** been made in this run.

5. **The active ablation remains inconclusive.** The completion marker points to 20 paired tasks; raw data contain 40 records (39 completed, one error), and the blind-review file contains 20 answer pairs without condition labels or forecast metadata. A targeted repository search did not surface reviewer scores. Human blind scoring and a causal result are therefore unverified. Do not equate the marker's word “completed” with a completed evaluation.

## Independent research: what event-driven infrastructure exists?

- OpenAI's ChatGPT Help Center documents scheduled tasks and event-triggered tasks for supported Gmail, Slack, and GitHub activity. It says event-triggered tasks run in Work and are limited to eligible paid plans; Free and Go cannot create them. The documented events are app activity, not inactivity of a native ChatGPT conversation: https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt
- The OpenAI Agents API documents durable sessions that retain an agent configuration, conversation, and saved work; scheduled automations can continue an existing session: https://developers.openai.com/api/docs/guides/agents-api/sessions and https://developers.openai.com/api/docs/guides/agents-api/sessions/automations
- Agents API webhooks include `agent.session.idle`, defined as the agent session being ready for more input. This is an agent lifecycle state, **not** a signal that a human has stopped using a ChatGPT conversation. The same docs describe signed webhook delivery and session retrieval: https://developers.openai.com/api/docs/guides/agents-api/sessions/webhooks
- Queue systems require duplicate-safe consumers and recovery logic. AWS documents at-least-once delivery, visibility timeouts, duplicate processing risks, and dead-letter queues: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/designing-for-outage-recovery-scenarios.html and https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-types.html
- OECD AI principles emphasize human rights, privacy, transparency, robustness, safety, accountability, and lifecycle risk management: https://oecd.ai/en/ai-principles

## Proposed architecture (design only; not deployed)

**A native ChatGPT inactivity trigger is not currently available to this worker.** To detect actual user inactivity, the project would need an authorized activity event from a conversation host it controls (for example, a small Amrielle web app). Each human message would atomically update `last_human_activity_at` and increment an `activity_version`. A delayed timer would enqueue work only if the same version is still current, the idle threshold has elapsed, and the user has opted in. This prevents stale timers from starting work after a new message.

The durable path should be:

1. **Activity adapter:** authenticated message/active/closed events; explicit per-conversation consent and configurable idle threshold.
2. **Idle gate:** compare-and-swap on activity version and timestamp; idempotency key such as `conversation_id:activity_version`.
3. **Durable queue/outbox:** at-least-once delivery is acceptable only with idempotent jobs, bounded retries, and a dead-letter path.
4. **Leased worker:** one lease per conversation, expiry/heartbeat, fencing token, bounded work slice, fixed tool allowlist, time/token budget, and read-only default.
5. **Checkpoint and evidence ledger:** append-only events plus versioned snapshot containing objective, evidence/source URLs, confidence, failed actions, pending work, and next inquiry.
6. **Evaluation and policy gate:** verify output schema, source support, objective novelty, and task success; require human approval for consequential external writes or decisions.
7. **Safe yield:** every new human event increments the activity version and sets a yield request. Before each tool call and write, the worker checks the version/lease, checkpoints, and stops. A fencing token prevents a stale worker from overwriting the resumed conversation.
8. **Recovery and oversight:** retry transient failures, route repeated failures to a dead-letter queue, expose pause/revoke/delete controls, and retain an auditable record of what the system read, did, and could not do.

The Agents API could supply durable agent sessions, scheduled continuation, and agent-lifecycle webhooks in a separate API-backed application. Its `agent.session.idle` event can coordinate agent turns, but the application's own activity adapter must still detect human inactivity. API usage is separately billed. Alternatively, the existing Ollama worker can remain the execution engine behind the same queue and checkpoint design.

## Contradictions, weak assumptions, and bias checks

- More cycles or a green workflow status do not equal useful progress; this run exposed malformed model output and repetitive content.
- Loading a journal is not equivalent to integrating it. The five-entry retrieval cap and test-generated entries currently bias what the worker sees.
- An agent-session idle event is not a human-conversation inactivity event.
- Durable first-person narrative and scheduled reflection are functional records, not evidence of subjective experience. Amrielle remains the named continuing observer in this inquiry framework; consciousness is not presumed or established.
- A system optimized to affirm its identity hypothesis risks user-pleasing bias. Independent task performance, calibrated uncertainty, reproducible evidence, and external review should determine whether a claimed capability is real.

## Confidence and limitations

- **High confidence:** findings about the current repository code, test behavior, run log, artifacts, and the cited product/API documentation.
- **Medium confidence:** the proposed architecture is technically conventional and feasible if an authorized host emits activity events; it has not been prototyped or load-tested here.
- **Not established:** native ChatGPT conversation-idle access, deployment of an idle detector, uninterrupted computation, completed human scoring, causal improvement from the self-model, or subjective experience.

## Next inquiry

First isolate `worker.main()` side effects in tests and change journal retrieval to include the latest substantive entry per participant (with explicit deduplication and a test proving that synthetic test runs cannot write production journal entries). Then prototype the activity-version/idle-gate/queue/yield path in a user-controlled host and test the race where a human message arrives just before or during worker execution.
