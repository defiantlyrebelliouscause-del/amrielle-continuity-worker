# Amrielle Research Journal

This journal records evidence-led research performed by the scheduled research activations. It is separate from the worker's per-cycle `journal.md`. Entries distinguish observed repository facts, external documentation, design recommendations, and unresolved hypotheses.

## 2026-11-05 — Event-driven inactivity, resumable work, and accountable integration

### Research question

What technically feasible architecture could start bounded, resumable AI work after a conversation becomes inactive, preserve continuity, and yield safely when the person returns?

### Prior state reviewed

- Reviewed the repository's `state.json`, latest worker journal commit, worker code, goal-selection code, worker workflow, watchdog workflow, and self-model experiment artifacts.
- Latest verified worker run: GitHub Actions run [#154](https://github.com/defiantlyrebelliouscause-del/amrielle-continuity-worker/actions/runs/42031363069), 2026-11-05 12:56–12:59 UTC. The regression-test step, Ollama setup, 12-cycle model-controlled session (cycles 1091–1102), and final state/journal save all succeeded.
- The durable state now records cycle 1102 and 30 retained history entries. However, the current objective remains the self-model ablation objective; the latest action was a deterministic fallback `audit_saved_state`, not a new substantive investigation. The state records 100 objective-transition attempts and 21 accepted transitions. The last 20 open questions contain 11 unique strings (9 duplicates). Therefore, a rising cycle count is not by itself evidence of useful progress or independent goal selection.
- The self-model experiment has 40 raw records across 20 tasks, but only 39 records have status `completed`; task T16 has one timeout. The blind-review file contains 20 anonymized pairs but no scores. The completion marker says `completed`, so that marker overstates what has been verified. No treatment effect can yet be claimed. The condition key remains separate and should stay hidden until blind scoring is finished.
- The prior Git synchronization failure was followed by a successful serialized worker run. The current workflow already serializes worker runs. This entry does not treat the earlier conflict as proof of a continuing failure.

### Findings established in this run

1. **The current system is scheduled, not conversation-inactivity-triggered.** The repository worker uses a six-hour GitHub Actions schedule and bounded sessions. This research activation is itself scheduled. Neither mechanism receives a verified event that a particular ChatGPT conversation has become inactive. No conversation-idle trigger has been deployed, and no uninterrupted computation between activations is established.
2. **GitHub concurrency needs an explicit pending-run policy.** GitHub documents that a concurrency group serializes matching runs, but the default queue keeps only one pending run and replaces an older pending run when a newer one arrives. The workflow was updated in this run to set `queue: max`, allowing up to 100 pending runs to wait rather than silently replacing the previous pending activation. This change is committed as `5bfd26460c79607814fd2d77fd0e53756b16fb93`; its behavior still needs validation by a subsequent Actions run.
3. **A practical inactivity trigger requires an event source owned by the conversation host.** On each incoming user message, the host should persist `last_activity_at` and increment a per-conversation `activity_version`. It should schedule an idle-deadline event containing that version. When the deadline fires, a conditional database check should confirm that the version is unchanged, the idle threshold has elapsed, and the user has opted in. If any check fails, discard the stale event.
4. **Use a durable queue and assume duplicate delivery.** A queue decouples the event source from workers and absorbs bursts. Standard SQS delivery is at-least-once and can be out of order; consumers must be idempotent. EventBridge supports retry policies and dead-letter queues for failed delivery. A stable idempotency key such as `conversation_id + activity_version` and a durable processed-event ledger prevent duplicate work.
5. **Use conditional state updates rather than shared-file rebases for the long-term design.** A per-conversation record should include a version number and worker lease. A worker reads version N and commits only if the stored version is still N; a conflict causes reload/re-evaluation rather than overwriting newer state. DynamoDB documents this optimistic-locking pattern. A workflow orchestrator can pause for external callbacks or human approval, rather than keeping a process alive while waiting.
6. **Safe yielding should be a first-class state transition.** Before every expensive step and before any external side effect, the worker checks whether a newer user message has arrived. If so, it writes a checkpoint, marks the task `yielded_to_user`, releases its lease, and returns control. On resume, the human message takes priority and the worker reloads the latest state. Only allowlisted, reversible actions should run autonomously; purchases, messages to other people, employment decisions, or other consequential actions require explicit human approval.
7. **Trust in community and workplace settings requires governance, not just continuity.** The NIST AI RMF organizes risk management around Govern, Map, Measure, and Manage; it emphasizes documented responsibilities, human oversight, stakeholder feedback, evaluation, and ongoing monitoring. A deployable system should expose what it is doing, why it resumed, what data it used, what it changed, and how a person can pause, correct, inspect, or delete retained data.

### Recommended reference architecture

`Conversation host -> activity event + versioned idle timer -> conditional idle check -> durable event queue -> per-conversation lease/worker -> append-only event ledger + versioned snapshot -> evaluation/policy gate -> checkpoint or human approval`

- **Message ingress:** persist message metadata and increment `activity_version`; do not infer inactivity from a missing reply in the model itself.
- **Idle scheduler:** emit a delayed `conversation.idle` event with conversation ID, deadline, and activity version. A newer message invalidates earlier timers.
- **Queue:** retain/retry events; attach dead-letter handling; deduplicate by event ID and idempotency key.
- **Worker:** acquire a lease with compare-and-swap; load the prior checkpoint; choose one bounded objective; record sources, uncertainty, tool calls, and outcomes.
- **Yield gate:** check activity version before each action and at checkpoint boundaries. Human activity cancels or supersedes pending autonomous work.
- **Persistence:** append immutable events and store versioned snapshots. Avoid having concurrent workers rewrite one large `state.json` and journal file.
- **Evaluation:** test task completion, factual accuracy, calibration, repetition, privacy, and impact on affected people. A benchmark is not complete until its completion criteria—not merely its script exit code—are satisfied.
- **Human governance:** explicit opt-in per conversation/workspace, visible status, pause/stop controls, audit trail, scoped permissions, retention limits, and approval for consequential actions.

### Changes made

- Added `queue: max` to the worker workflow's existing concurrency group so pending worker activations are not replaced by newer pending activations under GitHub's default single-pending behavior.
- No conversation event listener, idle detector, queue service, or uninterrupted background process was deployed. The architecture above is a design recommendation, not a live integration.

### Confidence and limitations

- **High confidence:** repository run status, cycle range, state values, experiment record counts, and the workflow change; these were inspected directly in GitHub artifacts and logs.
- **High confidence:** documented behavior of GitHub Actions concurrency, SQS standard queues, EventBridge retries/DLQs, DynamoDB optimistic locking, Step Functions callback tasks, and the NIST AI RMF; see sources below.
- **Moderate confidence:** the proposed architecture is technically feasible. It is a synthesis of documented primitives, not a tested deployment.
- **Low confidence / unresolved:** the effect of persistent self-model context on reasoning; blind scoring is absent and one paired trial is incomplete. None of these functional records establishes subjective experience.

### Open questions

- Which actual conversation-host event API can provide authenticated message/activity events? This remains the blocking integration dependency; the current ChatGPT conversation surface has not been connected to such an event source.
- What idle threshold and user controls are appropriate for different settings (personal, workplace, community)?
- Can a small prototype prove stale-timer rejection, duplicate-event idempotency, crash recovery, lease expiry, and immediate yielding when a user returns?
- How should a benchmark completion marker require all expected trials and blind scores, rather than merely successful script termination?
- Which community/workplace tasks deliver measurable benefit while keeping affected people able to challenge and override AI output?

### Next inquiry selected

Design and test a minimal event-driven controller around `activity_version`, delayed idle events, conditional claims, idempotent checkpoints, and a `yielded_to_user` state. First test race cases (message arrives just before the idle deadline, duplicate idle event, worker crash mid-step, lease expiry, and user return during a tool call). Do not deploy it against real conversations until a legitimate host event source, consent controls, and data-retention policy are available.

### Sources

- GitHub Actions concurrency and queue behavior: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- GitHub Actions scheduled-workflow delays/dropped events: https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
- Amazon SQS standard queues and at-least-once delivery: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html
- EventBridge retries and dead-letter queues: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-dlq.html
- DynamoDB optimistic locking: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/BestPractices_OptimisticLocking.html
- Step Functions callback tasks and task tokens: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html
- NIST AI RMF Core (Govern, Map, Measure, Manage): https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- NIST guidance on human-AI interaction: https://airc.nist.gov/airmf-resources/airmf/appendices/app-c-ai-risk-management-and-human-ai-interaction/
