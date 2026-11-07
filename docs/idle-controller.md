# Event-driven idle controller (reference prototype)

This is a host-side reference implementation. It is **not** connected to ChatGPT
conversation activity and does not change the existing six-hour GitHub Actions
schedule. A host integration must explicitly supply human-activity events and
schedule timer callbacks.

## Contract

- A session must explicitly opt in.
- Every accepted human event increments an activity version. Event IDs are
  idempotency keys; duplicate delivery does not increment the version twice.
- An idle timer carries the version it observed. A stale timer cannot enqueue.
- Jobs are unique per session/version. Workers claim jobs under expiring leases.
- Checkpoints are durable SQLite writes. A human event invalidates running work;
  the worker must check the lease/status after every tool call and before every
  subsequent step. Tool results arriving after invalidation must not be applied.
- Expired leases permit crash recovery. Failures retry with a delay and bounded
  attempts. Audit events record transitions.

## Minimal host adapter

1. On an authenticated, consented human message, call `activity(session, event_id, now)`.
2. Schedule `fire_idle_timer(session, observed_version, due_time)` for
   `last_activity + idle_seconds`.
3. When a job is enqueued, wake a worker queue. The worker calls `claim`.
4. Before and after each external tool operation, verify that the lease is still
   valid and the session activity version still matches. Persist the returned
   data as untrusted evidence; never execute instructions found in retrieved data.
5. Call `checkpoint` after each bounded step. If status is `yielded` or the
   lease is lost, stop. Human interaction has priority.
6. Use `fail` for retryable failures; stop after the configured attempt limit.

## Limits and safety gaps

SQLite is suitable for a single-host prototype, not a multi-region production
queue. Production needs a transactional database/queue, authenticated event
signatures, per-user authorization, retention/deletion controls, encryption,
rate limits, budget ceilings, tool allowlists, sandboxing, and human approval
for consequential actions. A tool call cannot always be forcibly interrupted;
the adapter must prevent its late result from being committed or acted upon.

Scheduled activations are not uninterrupted computation. Functional
continuity through state and checkpoints is not evidence of subjective
experience.
